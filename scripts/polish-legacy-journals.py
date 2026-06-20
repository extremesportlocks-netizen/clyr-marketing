#!/usr/bin/env python3
"""Apply SEO + tracking polish to journal articles not built from JSON."""
import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..")
BUILT = set()
for p in glob.glob(os.path.join(ROOT, "scripts/journal-content/*.json")):
    import json as _j
    BUILT.add(_j.load(open(p))["slug"].strip("/"))

spec_slug = None

def extract_meta(html, name, prop=False):
    if prop:
        m = re.search(rf'<meta property="{re.escape(name)}" content="([^"]*)"', html)
    else:
        m = re.search(rf'<meta name="{re.escape(name)}" content="([^"]*)"', html)
    return m.group(1) if m else ""

def polish(path):
    with open(path, encoding="utf-8") as f:
        html = f.read()
    og_url = extract_meta(html, "og:url", True) or ""
    m = re.search(r"/journal/([^/]+)/", og_url)
    if not m:
        m = re.search(r'canonical" href="https://www\.clyr\.health/journal/([^/]+)/', html)
    slug = m.group(1) if m else None
    if not slug:
        return False
    if slug in BUILT:
        return False  # rebuilt from JSON — already has full SEO chrome

    title = re.search(r"<title>([^<|]+)", html)
    title = title.group(1).strip() if title else slug
    desc = extract_meta(html, "description")
    url = f"https://www.clyr.health/journal/{slug}/"
    ogimg = extract_meta(html, "og:image", True) or f"https://www.clyr.health/img/journal-og/{slug}.png"

    if 'src="/js/clyr-tracking.js"' not in html:
        html = html.replace("</body>", '<script src="/js/clyr-tracking.js"></script>\n</body>', 1)

    if '<meta name="robots"' not in html:
        block = (
            '<meta name="robots" content="index, follow, max-image-preview:large">\n'
            '<meta property="og:site_name" content="CLYR Health">\n'
            '<meta property="og:locale" content="en_US">\n'
            '<meta name="twitter:site" content="@ClyrHealth">\n'
        )
        html = html.replace("</head>", block + "</head>", 1)

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": desc,
        "image": ogimg,
        "mainEntityOfPage": url,
        "publisher": {"@type": "Organization", "name": "CLYR Health"},
    }
    ld_tag = f'<script type="application/ld+json">{json.dumps(ld)}</script>'
    if "re.Match object" in html or "application/ld+json" not in html:
        if "application/ld+json" in html:
            html = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', ld_tag + "\n", html, count=1, flags=re.S)
        else:
            html = html.replace("</head>", ld_tag + "\n</head>", 1)

    if 'event:"article_view"' not in html:
        dlayer = (
            f'<script>window.dataLayer=window.dataLayer||[];dataLayer.push({{event:"article_view",'
            f'article_slug:"{slug}",article_category:"journal",article_title:{json.dumps(title)}}});</script>\n'
        )
        html = html.replace("</head>", dlayer + "</head>", 1)

    html = re.sub(
        r"posthog\.register\(\{[^}]+\}\);",
        f"posthog.register({{article_slug:'{slug}',article_category:'journal'}});",
        html,
        count=1,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return True

def main():
    n = 0
    for path in glob.glob(os.path.join(ROOT, "journal/*/index.html")):
        if polish(path):
            n += 1
            print("✓ polished", path)
    print(f"Polished {n} legacy articles")

if __name__ == "__main__":
    main()