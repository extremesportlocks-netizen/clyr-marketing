#!/usr/bin/env python3
"""Add index/follow, canonical, and JSON-LD to public sitemap pages (non-journal)."""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
ROBOTS = '<meta name="robots" content="index, follow, max-image-preview:large">'
SKIP_URLS = {
    "https://www.clyr.health/intake-wellness.html",  # noindex form — not for Google
}
SKIP_PREFIX = "https://www.clyr.health/journal/"


def url_to_path(url: str) -> Path | None:
    path = url.replace("https://www.clyr.health", "")
    if path == "/":
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path[1:] / "index.html"
    return ROOT / path[1:]


def extract_title(html: str) -> str:
    m = re.search(r"<title>([^<]+)</title>", html, re.I)
    return m.group(1).strip() if m else "CLYR Health"


def extract_description(html: str) -> str:
    m = re.search(r'<meta name="description" content="([^"]*)"', html, re.I)
    return m.group(1) if m else ""


def json_ld(url: str, title: str, desc: str, page_type: str = "WebPage") -> str:
    data = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title.split("·")[0].strip() if "·" in title else title,
        "description": desc,
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "CLYR Health", "url": "https://www.clyr.health/"},
        "publisher": {"@type": "Organization", "name": "CLYR Health", "url": "https://www.clyr.health/"},
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def upsert_meta(html: str, prop: str, content: str, *, name: str | None = None) -> str:
    if name:
        pat = rf'<meta name="{re.escape(name)}" content="[^"]*">'
        tag = f'<meta name="{name}" content="{content}">'
    else:
        pat = rf'<meta property="{re.escape(prop)}" content="[^"]*">'
        tag = f'<meta property="{prop}" content="{content}">'
    if re.search(pat, html):
        return re.sub(pat, tag, html, count=1)
    return html.replace("<meta charset", tag + "\n<meta charset", 1)


def polish_file(path: Path, canonical: str) -> bool:
    html = path.read_text(encoding="utf-8")
    if re.search(r'<meta name="robots"[^>]*noindex', html, re.I):
        return False

    orig = html
    title = extract_title(html)
    desc = extract_description(html)

    if 'name="robots"' not in html:
        html = html.replace("<meta charset", ROBOTS + "\n<meta charset", 1)
    elif "max-image-preview" not in html:
        html = re.sub(
            r'<meta name="robots" content="[^"]*">',
            ROBOTS,
            html,
            count=1,
        )

    canon_tag = f'<link rel="canonical" href="{canonical}">'
    if 'rel="canonical"' not in html:
        html = html.replace("</head>", canon_tag + "\n</head>", 1)
    else:
        html = re.sub(
            r'<link rel="canonical" href="[^"]*">',
            canon_tag,
            html,
            count=1,
        )

    extras = (
        ('property', 'og:site_name', 'CLYR Health'),
        ('property', 'og:locale', 'en_US'),
        ('name', 'twitter:site', '@ClyrHealth'),
    )
    for kind, key, val in extras:
        if kind == "name":
            if f'name="{key}"' not in html:
                html = html.replace("</head>", f'<meta name="{key}" content="{val}">\n</head>', 1)
        elif f'property="{key}"' not in html:
            html = html.replace("</head>", f'<meta property="{key}" content="{val}">\n</head>', 1)

    html = upsert_meta(html, "og:url", canonical)

    if "application/ld+json" not in html:
        ptype = "MedicalWebPage" if path.suffix == ".html" and path.name not in {
            "privacy.html", "terms.html", "contact.html", "telehealth-consent.html", "sms-terms.html"
        } else "WebPage"
        html = html.replace("</head>", json_ld(canonical, title, desc, ptype) + "\n</head>", 1)

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def refresh_sitemap(urls: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    today = date.today().isoformat()
    for skip in SKIP_URLS:
        text = re.sub(
            rf"\s*<url><loc>{re.escape(skip)}</loc>.*?</url>\s*",
            "\n",
            text,
            flags=re.S,
        )
    text = re.sub(
        r"(<url><loc>https://www\.clyr\.health/[^<]+</loc>)<lastmod>[^<]*</lastmod>",
        rf"\1<lastmod>{today}</lastmod>",
        text,
    )
    path.write_text(text, encoding="utf-8")


def main():
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = [
        u.find("sm:loc", NS).text
        for u in tree.getroot().findall("sm:url", NS)
        if u.find("sm:loc", NS) is not None
    ]
    polished = 0
    for url in urls:
        if url in SKIP_URLS or url.startswith(SKIP_PREFIX) or url == f"{SKIP_PREFIX.rstrip('/')}/":
            continue
        path = url_to_path(url)
        if not path or not path.exists():
            print("SKIP missing", url)
            continue
        if polish_file(path, url):
            print("✓", path.relative_to(ROOT))
            polished += 1

    keep = [u for u in urls if u not in SKIP_URLS]
    refresh_sitemap(keep)
    print(f"\nPolished {polished} pages; removed {len(SKIP_URLS)} noindex URL(s) from sitemap")

if __name__ == "__main__":
    main()