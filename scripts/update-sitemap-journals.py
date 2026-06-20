#!/usr/bin/env python3
"""Regenerate journal URL entries in sitemap.xml and sitemap-images.xml."""
import glob
import os
import re
from datetime import date

ROOT = os.path.join(os.path.dirname(__file__), "..")
TODAY = date.today().isoformat()

def journal_slugs():
    slugs = []
    for p in glob.glob(os.path.join(ROOT, "journal/*/index.html")):
        slugs.append(os.path.basename(os.path.dirname(p)))
    return sorted(set(slugs))

def main():
    slugs = journal_slugs()
    sitemap_path = os.path.join(ROOT, "sitemap.xml")
    with open(sitemap_path, encoding="utf-8") as f:
        xml = f.read()

    head = xml.split("<url><loc>https://www.clyr.health/journal/</loc>")[0]
    journal_block = (
        f'  <url><loc>https://www.clyr.health/journal/</loc><lastmod>{TODAY}</lastmod>'
        f'<changefreq>weekly</changefreq><priority>0.85</priority></url>\n'
    )
    for slug in slugs:
        pri = "0.75"
        if slug in ("semaglutide-vs-tirzepatide", "what-is-nad-plus", "clyr-tri-gel-triple-therapy-acne",
                    "testosterone-cypionate-trt-explained", "compounded-hair-regrowth-quad-stack-men"):
            pri = "0.8"
        journal_block += (
            f'  <url><loc>https://www.clyr.health/journal/{slug}/</loc>'
            f'<lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pri}</priority></url>\n'
        )
    new_xml = head + journal_block + "</urlset>\n"
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(new_xml)
    print(f"✓ sitemap.xml — {len(slugs)} journal articles")

    # image sitemap entries for OG pngs
    img_path = os.path.join(ROOT, "sitemap-images.xml")
    entries = []
    for slug in slugs:
        og = f"https://www.clyr.health/img/journal-og/{slug}.png"
        if os.path.exists(os.path.join(ROOT, "img/journal-og", f"{slug}.png")):
            entries.append(
                f'  <url>\n'
                f'    <loc>https://www.clyr.health/journal/{slug}/</loc>\n'
                f'    <changefreq>monthly</changefreq>\n'
                f'    <priority>0.7</priority>\n'
                f'    <image:image>\n'
                f'      <image:loc>{og}</image:loc>\n'
                f'      <image:title>{slug.replace("-", " ").title()} | CLYR Journal</image:title>\n'
                f'    </image:image>\n'
                f'  </url>\n'
            )
    with open(img_path, encoding="utf-8") as f:
        old = f.read()
    proto = old.split("</url>")[0] + "</url>\n" if "<url>" in old else (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
    )
    # preserve non-journal image urls
    preserved = []
    for block in re.findall(r"<url>.*?</url>\s*", old, re.S):
        if "/journal/" not in block:
            preserved.append(block)
    body = "".join(preserved) + "".join(entries)
    new_img = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + body + "</urlset>\n"
    )
    with open(img_path, "w", encoding="utf-8") as f:
        f.write(new_img)
    print(f"✓ sitemap-images.xml — {len(entries)} journal OG images")

if __name__ == "__main__":
    main()