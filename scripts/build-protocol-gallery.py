#!/usr/bin/env python3
"""Build indexable protocol gallery for Google Images."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / 'protocol-gallery'
IMAGES = GALLERY / 'images'
ASSETS = Path('/Users/orlandosmith/.grok/sessions/%2FUsers%2Forlandosmith/019ee192-f1db-7982-a7d7-0885c7830c6a/assets')

ITEMS = [
    {
        'src': 'image-90b79997-d710-45f3-8ed7-50d1c2e75cfa.jpg',
        'slug': 'ivermectin-protocol-doctor-prescribed',
        'file': 'ivermectin-protocol-doctor-prescribed-clyr-health.jpg',
        'title': 'Ivermectin Protocol — Doctor-Prescribed Antiparasitic Care | CLYR Health',
        'alt': 'CLYR Health ivermectin protocol and combo protocol pricing from licensed US providers',
        'caption': 'Doctor-prescribed ivermectin antiparasitic protocols from $139/mo. Licensed US providers, 503A pharmacy.',
    },
    {
        'src': 'image-1978e0d0-034d-4383-afe1-8f183b733d3e.jpg',
        'slug': 'ivermectin-mebendazole-combo-protocol',
        'file': 'ivermectin-mebendazole-combo-protocol-clyr-health.jpg',
        'title': 'Ivermectin + Mebendazole Combo Protocol from $169/mo | CLYR Health',
        'alt': 'Ivermectin and mebendazole dual-coverage antiparasitic protocol CLYR Health',
        'caption': 'Physician-guided Ivermectin plus Mebendazole protocol. Broader coverage from $169/mo.',
    },
    {
        'src': 'image-059b95bd-05c2-436e-88ad-e63c667c1919.jpg',
        'slug': 'ivermectin-protocol-spring-special',
        'file': 'ivermectin-antiparasitic-protocol-spring-clyr-health.jpg',
        'title': 'Ivermectin Antiparasitic Protocol — Spring Special | CLYR Health',
        'alt': 'CLYR Health spring special ivermectin protocol 15 percent off antiparasitic care',
        'caption': 'Invest in how you feel. Antiparasitic protocols with licensed clinicians from $139.',
    },
    {
        'src': 'image-10ae24a8-5a57-4ce8-9743-b8370017f079.jpg',
        'slug': 'antiparasitic-parasite-cleanse-protocol',
        'file': 'antiparasitic-parasite-cleanse-protocol-clyr.jpg',
        'title': 'Antiparasitic Protocol — Parasite Cleanse & Advanced Protocol | CLYR Health',
        'alt': 'CLYR parasite cleanse and advanced antiparasitic protocol ivermectin',
        'caption': 'Explore antiparasitic protocols. Parasite cleanse $139, advanced protocol $169.',
    },
    {
        'src': 'image-e1e77ae7-d812-47ec-b3ed-2d9a9383195a.jpg',
        'slug': 'which-ivermectin-protocol-right-for-you',
        'file': 'which-ivermectin-protocol-right-for-you-clyr.jpg',
        'title': 'Which Ivermectin Protocol Is Right for You? | CLYR Health',
        'alt': 'Compare ivermectin protocol vs combo protocol CLYR Health telehealth',
        'caption': 'Ivermectin from $139/mo or combo protocol from $169/mo. Telehealth consultation included.',
    },
    {
        'src': 'image-607cabac-2e45-45f1-84ae-4a5748326831.jpg',
        'slug': 'ivermectin-protocol-5-minute-intake',
        'file': 'ivermectin-protocol-5-minute-intake-clyr-health.jpg',
        'title': 'Ivermectin Protocol — 5-Minute Intake | CLYR Health',
        'alt': '5 minute intake for ivermectin antiparasitic protocol matched with licensed US provider',
        'caption': '5-minute intake. Matched with a licensed US provider. Antiparasitic protocols from $139/mo.',
    },
    {
        'src': 'image-630c1806-60b2-44ec-a5c2-897e858ab038.jpg',
        'slug': 'ivermectin-protocol-legitscript-certified',
        'file': 'ivermectin-protocol-legitscript-hipaa-clyr.jpg',
        'title': 'Ivermectin Protocol — LegitScript Certified Telehealth | CLYR Health',
        'alt': 'LegitScript certified HIPAA compliant ivermectin protocol licensed US providers 503A pharmacy',
        'caption': 'Doctor-prescribed antiparasitic protocols. LegitScript certified. From $139/mo.',
    },
    {
        'src': 'image-99c50b40-bfc7-4deb-a3d0-a96fb284ad3b.jpg',
        'slug': 'physician-guided-ivermectin-protocol',
        'file': 'physician-guided-ivermectin-antiparasitic-protocol-clyr.jpg',
        'title': 'Physician-Guided Ivermectin Antiparasitic Protocol | CLYR Health',
        'alt': 'Physician guided ivermectin antiparasitic care core and comprehensive protocol CLYR',
        'caption': 'Core protocol $139, comprehensive protocol $169. 503A pharmacy, ships most states.',
    },
    {
        'src': 'image-84702dda-e7a2-4659-9b34-c3afa45e069f.jpg',
        'slug': 'ivermectin-protocol-invest-in-wellness',
        'file': 'ivermectin-protocol-monthly-pricing-clyr-health.jpg',
        'title': 'Ivermectin Protocol from $139/mo — CLYR Health',
        'alt': 'Ivermectin antiparasitic protocol and ivermectin mebendazole dual coverage CLYR Health pricing',
        'caption': 'Popular ivermectin protocol from $139/mo. Dual coverage combo from $169/mo.',
    },
    {
        'src': 'image-0d180ad6-ccb8-4ebb-9acc-09d7cb836209.jpg',
        'slug': 'ivermectin-protocol-licensed-providers',
        'file': 'ivermectin-protocol-licensed-us-providers-clyr.jpg',
        'title': 'Ivermectin Protocol — Licensed US Providers | CLYR Health',
        'alt': 'Ivermectin protocol and ivermectin mebendazole dual coverage protocol physician guided CLYR Health',
        'caption': 'Antiparasitic protocols with licensed US providers. Ivermectin $139/mo, combo $169/mo.',
    },
]

DEST = 'https://www.clyr.health/ads/x/antiparasitic.html?utm_source=google&utm_medium=organic&utm_campaign=protocol-gallery'
BASE = 'https://www.clyr.health'


def page_html(item):
    img_url = f'{BASE}/protocol-gallery/images/{item["file"]}'
    page_url = f'{BASE}/protocol-gallery/{item["slug"]}.html'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="/favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{item["title"]}</title>
<meta name="description" content="{item["caption"]} Start at CLYR Health — LegitScript-certified telehealth.">
<meta name="keywords" content="ivermectin, ivermectin protocol, antiparasitic protocol, mebendazole, CLYR Health, telehealth protocol">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{page_url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CLYR Health">
<meta property="og:title" content="{item["title"]}">
<meta property="og:description" content="{item["caption"]}">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{img_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img_url}">
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@type": "ImageObject",
    "name": item["title"],
    "description": item["caption"],
    "contentUrl": img_url,
    "thumbnailUrl": img_url,
    "author": {"@type": "Organization", "name": "CLYR Health", "url": BASE},
    "copyrightHolder": {"@type": "Organization", "name": "CLYR Health"},
    "license": f"{BASE}/terms.html",
    "acquireLicensePage": DEST,
    "creditText": "CLYR Health",
    "creator": {"@type": "Organization", "name": "CLYR Health"},
    "isPartOf": {"@type": "WebPage", "url": page_url, "name": item["title"]},
}, separators=(',', ':'))}</script>
<style>
body{{font-family:system-ui,sans-serif;margin:0;background:#f4f7f6;color:#0D1B2A}}
.wrap{{max-width:520px;margin:0 auto;padding:24px 16px 40px}}
a{{color:#00a89e}}
img{{width:100%;height:auto;border-radius:12px;display:block}}
h1{{font-size:1.25rem;line-height:1.3;margin:16px 0 8px}}
p{{color:#4A5568;font-size:.95rem;line-height:1.55}}
.cta{{display:block;text-align:center;background:#00a89e;color:#fff;text-decoration:none;padding:14px 20px;border-radius:999px;font-weight:700;margin:20px 0}}
.small{{font-size:.75rem;color:#6B7C8A}}
</style>
</head>
<body>
<main class="wrap">
  <a href="{DEST}"><img src="/protocol-gallery/images/{item["file"]}" alt="{item["alt"]}" width="576" height="1024" loading="eager"></a>
  <h1>{item["title"]}</h1>
  <p>{item["caption"]}</p>
  <a class="cta" href="{DEST}">Start free intake at CLYR Health →</a>
  <p class="small">Compounded products not FDA-approved. Prescription required when clinically appropriate. <a href="{BASE}/">clyr.health</a></p>
</main>
</body>
</html>'''


def index_html():
    cards = []
    for item in ITEMS:
        cards.append(
            f'<a class="card" href="/protocol-gallery/{item["slug"]}.html">'
            f'<img src="/protocol-gallery/images/{item["file"]}" alt="{item["alt"]}" loading="lazy" width="280" height="498">'
            f'<span>{item["title"].split("|")[0].strip()}</span></a>'
        )
    cards_html = '\n'.join(cards)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="/favicon.ico">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ivermectin Protocol Gallery | CLYR Health</title>
<meta name="description" content="Ivermectin protocol and antiparasitic protocol information from CLYR Health. Physician-guided care, licensed US providers, LegitScript certified.">
<meta name="keywords" content="ivermectin, ivermectin protocol, antiparasitic protocol, CLYR Health">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{BASE}/protocol-gallery/">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":"Ivermectin Protocol Gallery","url":f"{BASE}/protocol-gallery/","publisher":{"@type":"Organization","name":"CLYR Health","url":BASE}}, separators=(',',':'))}</script>
<style>
body{{font-family:system-ui,sans-serif;margin:0;background:#f4f7f6;color:#0D1B2A}}
.wrap{{max-width:960px;margin:0 auto;padding:28px 16px 48px}}
h1{{font-size:1.75rem;margin:0 0 8px}}
p{{color:#4A5568}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;margin-top:24px}}
.card{{text-decoration:none;color:inherit;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.06)}}
.card img{{width:100%;display:block;aspect-ratio:9/16;object-fit:cover}}
.card span{{display:block;padding:12px;font-size:.85rem;font-weight:600}}
.cta{{display:inline-block;margin-top:16px;background:#00a89e;color:#fff;text-decoration:none;padding:12px 20px;border-radius:999px;font-weight:700}}
</style>
</head>
<body>
<main class="wrap">
  <h1>Ivermectin Protocol Gallery</h1>
  <p>Physician-guided antiparasitic protocols from CLYR Health. <a href="{DEST}">Start free intake →</a></p>
  <div class="grid">{cards_html}</div>
  <a class="cta" href="{DEST}">Go to CLYR Health</a>
</main>
</body>
</html>'''


def main():
    GALLERY.mkdir(parents=True, exist_ok=True)
    IMAGES.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in ITEMS:
        src = ASSETS / item['src']
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, IMAGES / item['file'])
        (GALLERY / f'{item["slug"]}.html').write_text(page_html(item))
        manifest.append(item)
    (GALLERY / 'index.html').write_text(index_html())
    (GALLERY / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')

    sitemap_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        f'  <url><loc>{BASE}/protocol-gallery/</loc><changefreq>weekly</changefreq><priority>0.85</priority></url>',
    ]
    for item in manifest:
        page = f'{BASE}/protocol-gallery/{item["slug"]}.html'
        img = f'{BASE}/protocol-gallery/images/{item["file"]}'
        sitemap_lines.append('  <url>')
        sitemap_lines.append(f'    <loc>{page}</loc>')
        sitemap_lines.append('    <changefreq>weekly</changefreq>')
        sitemap_lines.append('    <priority>0.8</priority>')
        sitemap_lines.append('    <image:image>')
        sitemap_lines.append(f'      <image:loc>{img}</image:loc>')
        sitemap_lines.append(f'      <image:title>{item["title"]}</image:title>')
        sitemap_lines.append(f'      <image:caption>{item["caption"]}</image:caption>')
        sitemap_lines.append('    </image:image>')
        sitemap_lines.append('  </url>')
    sitemap_lines.append('</urlset>')
    (ROOT / 'sitemap-images.xml').write_text('\n'.join(sitemap_lines) + '\n')
    print(f'Built {len(manifest)} gallery pages + image sitemap')


if __name__ == '__main__':
    main()