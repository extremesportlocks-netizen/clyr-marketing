#!/usr/bin/env python3
"""Wire Google Business Profile into site footers and homepage schema."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Resolved from share.google/x5NcYmvHECext8PTi → kgmid /g/11z94cc8v_
GBP_MAPS_URL = (
    "https://www.google.com/maps/search/CLYR+Health/"
    "@27.2684733,-82.459881,15z/data=!4m2!2m1!6e6!16s%2Fg%2F11z94cc8v_"
)
GBP_FOOTER_LINK = (
    f'<a href="{GBP_MAPS_URL}" target="_blank" rel="noopener">Google Business Profile</a>'
)
CONTACT_CARD = f"""      <div class="sidebar-card">
        <div class="sidebar-card-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        </div>
        <h3>Find Us on Google</h3>
        <p>View our verified Google Business Profile for hours, location, and reviews.<br><a href="{GBP_MAPS_URL}" target="_blank" rel="noopener">CLYR Health on Google Maps</a></p>
      </div>
"""


def add_footer_link(html: str) -> str:
    if "Google Business Profile" in html or GBP_MAPS_URL in html:
        return html
    patterns = [
        (
            r'(<a href="/contact\.html">Contact(?: Us)?</a>\s*)',
            rf"\1        {GBP_FOOTER_LINK}\n",
        ),
        (
            r'(<a href="/contact\.html">Contact</a>\s*)',
            rf"\1        {GBP_FOOTER_LINK}\n",
        ),
    ]
    for pat, repl in patterns:
        if re.search(pat, html):
            return re.sub(pat, repl, html, count=1)
    return html


def update_index_schema(html: str) -> str:
    same_as = [
        "https://www.instagram.com/clyr.health",
        GBP_MAPS_URL,
    ]
    address = {
        "@type": "PostalAddress",
        "streetAddress": "5020 Clark Rd #159",
        "addressLocality": "Sarasota",
        "addressRegion": "FL",
        "postalCode": "34233",
        "addressCountry": "US",
    }

    def patch_medical_business(block: str) -> str:
        block = re.sub(
            r'"address"\s*:\s*\{[^}]+\}',
            '"address": ' + json.dumps(address, ensure_ascii=False),
            block,
            count=1,
        )
        block = re.sub(
            r'"sameAs"\s*:\s*\[[^\]]*\]',
            '"sameAs": ' + json.dumps(same_as, ensure_ascii=False),
            block,
            count=1,
        )
        if '"hasMap"' not in block:
            block = block.replace(
                '"areaServed": "US",',
                '"areaServed": "US",\n      "hasMap": '
                + json.dumps(GBP_MAPS_URL, ensure_ascii=False)
                + ",",
            )
        return block

    return re.sub(
        r'(\{\s*"@type":\s*"MedicalBusiness"[\s\S]*?\})(?=\s*,\s*\{)',
        lambda m: patch_medical_business(m.group(1)),
        html,
        count=1,
    )


def update_contact_sidebar(html: str) -> str:
    if "Find Us on Google" in html:
        return html
    marker = '      <div class="sidebar-card">\n        <div class="sidebar-card-icon">\n          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    if marker in html:
        return html.replace(marker, CONTACT_CARD + "\n" + marker, 1)
    return html


def main() -> None:
    changed: list[str] = []
    skip_dirs = {"preview", "node_modules", ".git"}

    for path in sorted(ROOT.rglob("*.html")):
        if any(part in skip_dirs for part in path.parts):
            continue
        html = path.read_text(encoding="utf-8")
        orig = html
        if "<h4>Company</h4>" in html:
            html = add_footer_link(html)
        if path.name == "index.html" and path.parent == ROOT:
            html = update_index_schema(html)
        if path.name == "contact.html" and path.parent == ROOT:
            html = update_contact_sidebar(html)
        if html != orig:
            path.write_text(html, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    print(f"Updated {len(changed)} files")
    for rel in changed[:20]:
        print(f"  {rel}")
    if len(changed) > 20:
        print(f"  ... and {len(changed) - 20} more")


if __name__ == "__main__":
    main()