#!/usr/bin/env python3
"""Wire preview/assets heroes into product pages, hubs, and megamenu thumbs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "preview" / "assets" / "manifest.json"

HUB_SLUGS = {
    "mens-hormone": [
        "testosterone-cypionate", "testosterone-cream", "testosterone-hypo-spray",
        "enclomiphene", "hcg", "anastrozole",
    ],
    "womens-hormone": [
        "estradiol-patches", "biest-progesterone-cream", "progesterone-capsules",
        "dhea-pregnenolone", "estradiol-vaginal-cream", "womens-testosterone-cream",
    ],
    "peptides": ["bpc-157", "tb-500", "ghk-cu-injectable"],
    "recovery": ["naltrexone-ldn"],
    "skin-hair": [
        "clyr-tri-gel", "minoxidil", "hair-spray-women", "nad-face-cream",
        "tretinoin", "estriol-ghk-cu-cream", "hydroquinone-triple-cream",
        "doxycycline-acne", "finasteride-oral",
    ],
    "weight-loss": ["semaglutide-odt", "tirzepatide-sublingual", "metformin-er", "liraglutide"],
    "daily-wellness": ["niagen", "naltrexone-ldn"],
}


def _hero_img_tag(hero: str, alt: str) -> str:
    return (
        f'<img src="{hero}" alt="{alt}" '
        'style="width:78%;height:78%;object-fit:contain;display:block;'
        'filter:drop-shadow(0 18px 40px rgba(0,0,0,0.12))" loading="lazy">'
    )


def patch_product_page(slug: str, hero: str, card: str):
    path = ROOT / f"{slug}.html"
    if not path.exists():
        return
    text = path.read_text()
    alt_m = re.search(r'<h1 class="product-title"[^>]*>(.*?)</h1>', text, re.S)
    alt = re.sub(r"<[^>]+>", "", alt_m.group(1)).strip() if alt_m else slug.replace("-", " ").title()

    def _replace_hero_block(m: re.Match) -> str:
        block = m.group(0)
        badge_m = re.search(r'(<div class="product-badge"[^>]*>.*?</div>)', block, re.S)
        badge = badge_m.group(1) if badge_m else ""
        return f'<div class="product-image">{badge}{_hero_img_tag(hero, alt)}</div>'

    text = re.sub(
        r'<div class="product-image">.*?</div>(?=\s*<div class="product-info">)',
        _replace_hero_block,
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<div class="product-image"[^>]*>.*?<img src=")[^"]+(" alt="[^"]*"[^>]*>)',
        rf'\1{hero}\2',
        text,
        count=1,
        flags=re.S,
    )
    # megamenu thumb for this slug's own link
    text = re.sub(
        rf'(<a href="/{slug}\.html" class="mm-link"><img src=")[^"]+(")',
        rf'\1{card}\2',
        text,
        count=1,
    )
    path.write_text(text)


def patch_all_megamenu_for_slug(slug: str, card: str):
    for html in ROOT.glob("*.html"):
        if html.name.startswith("_"):
            continue
        text = html.read_text()
        new = re.sub(
            rf'(<a href="/{slug}\.html" class="mm-link"><img src=")[^"]+(")',
            rf'\1{card}\2',
            text,
        )
        if new != text:
            html.write_text(new)


def _hub_card_img(card: str, alt: str = "") -> str:
    alt_attr = f' alt="{alt}"' if alt else ""
    return (
        f'<img src="{card}"{alt_attr} loading="lazy" '
        'style="width:72%;height:72%;object-fit:contain;margin:auto">'
    )


def patch_hub(hub: str, slug_cards: list[tuple[str, str]]):
    path = ROOT / f"{hub}.html"
    if not path.exists():
        return
    text = path.read_text()
    for slug, card in slug_cards:

        def _replace_pc_card(m: re.Match) -> str:
            block = m.group(0)
            if card in block and "<svg" not in block:
                return block
            badge_m = re.search(r'(<div class="cb"[^>]*>.*?</div>)', block, re.S)
            badge = badge_m.group(1) if badge_m else ""
            alt_m = re.search(r'<h3>([^<]+)</h3>', block)
            alt = alt_m.group(1).strip() if alt_m else slug.replace("-", " ").title()
            ci_m = re.search(r'<div class="ci"([^>]*)>', block)
            ci_style = ci_m.group(1) if ci_m else ""
            img = _hub_card_img(card, alt)
            return re.sub(
                r'<div class="ci"[^>]*>.*?(?=<div class="cd">)',
                f'<div class="ci"{ci_style}>{badge}{img}</div>',
                block,
                count=1,
                flags=re.S,
            )

        text = re.sub(
            rf'<a href="/{slug}\.html" class="pc">.*?</a>',
            _replace_pc_card,
            text,
            count=1,
            flags=re.S,
        )
    path.write_text(text)


def patch_weight_loss_section():
    path = ROOT / "weight-loss.html"
    if not path.exists():
        return
    text = path.read_text()
    mapping = {
        "semaglutide-odt": "Semaglutide ODT",
        "tirzepatide-sublingual": "Tirzepatide Sublingual",
        "metformin-er": "Metformin ER",
        "liraglutide": "Liraglutide",
    }
    data = {p["slug"]: p["card"] for p in json.loads(MANIFEST.read_text())["products"]}
    for slug, label in mapping.items():
        card = data.get(slug)
        if not card:
            continue
        text = re.sub(
            rf'(<a href="/{slug}\.html" class="product-card">.*?<img src=")[^"]+(" alt="{re.escape(label)}")',
            rf'\1{card}\2',
            text,
            count=1,
            flags=re.S,
        )
    path.write_text(text)


def patch_sexual_health_section():
    path = ROOT / "sexual-health.html"
    if not path.exists():
        return
    text = path.read_text()
    data = {p["slug"]: p["card"] for p in json.loads(MANIFEST.read_text())["products"]}
    for slug in [
        "trimix", "tadalafil-troches", "tadalafil-apomorphine",
        "sildenafil-tadalafil-gummy", "oxytocin-nasal", "pt141-strips",
    ]:
        card = data.get(slug)
        if not card:
            continue
        text = re.sub(
            rf'(<a href="/{slug}\.html" class="product-card[^"]*">.*?<img src=")[^"]+(")',
            rf'\1{card}\2',
            text,
            count=1,
            flags=re.S,
        )
    path.write_text(text)


def update_catalog_generator_manifest():
    """Patch generate-catalog-pages.py img paths for future regen."""
    gen = ROOT / "scripts" / "generate-catalog-pages.py"
    text = gen.read_text()
    for p in json.loads(MANIFEST.read_text())["products"]:
        slug, hero = p["slug"], p["hero"]
        needle = f'("{slug}",'
        idx = text.find(needle)
        if idx < 0:
            continue
        end = text.find("),", idx)
        chunk = text[idx:end]
        new_chunk = re.sub(r', "/(?:img|preview)/[^"]+"\)?', f', "{hero}")', chunk)
        if new_chunk != chunk:
            text = text[:idx] + new_chunk + text[end:]
    gen.write_text(text)


def main():
    products = json.loads(MANIFEST.read_text())["products"]
    for p in products:
        patch_product_page(p["slug"], p["hero"], p["card"])
        patch_all_megamenu_for_slug(p["slug"], p["card"])

    card_map = {p["slug"]: p["card"] for p in products}
    for hub, slugs in HUB_SLUGS.items():
        patch_hub(hub, [(s, card_map[s]) for s in slugs if s in card_map])

    patch_weight_loss_section()
    patch_sexual_health_section()
    update_catalog_generator_manifest()
    print(f"Applied assets to {len(products)} preview SKUs")


if __name__ == "__main__":
    main()