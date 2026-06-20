#!/usr/bin/env python3
"""Wire preview/assets heroes into preview product + hub pages only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "preview" / "assets" / "manifest.json"
PRODUCTS_DIR = ROOT / "preview" / "products"
HUBS_DIR = ROOT / "preview" / "hubs"
PREVIEW_HTML = (ROOT / "preview",)

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
}


def _hero_img_tag(hero: str, alt: str) -> str:
    return (
        f'<img src="{hero}" alt="{alt}" '
        'style="width:88%;height:88%;object-fit:contain;display:block;'
        'filter:drop-shadow(0 18px 40px rgba(0,0,0,0.15))" loading="lazy">'
    )


def patch_product_page(slug: str, hero: str, card: str):
    path = PRODUCTS_DIR / f"{slug}.html"
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
    text = re.sub(
        rf'(<a href="/preview/products/{slug}\.html" class="mm-link"><img src=")[^"]+(")',
        rf'\1{card}\2',
        text,
        count=1,
    )
    path.write_text(text)


def patch_preview_megamenu_for_slug(slug: str, card: str):
    for html in ROOT.joinpath("preview").rglob("*.html"):
        text = html.read_text()
        new = re.sub(
            rf'(<a href="/preview/products/{slug}\.html" class="mm-link"><img src=")[^"]+(")',
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
    path = HUBS_DIR / f"{hub}.html"
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
            rf'<a href="/preview/products/{slug}\.html" class="pc">.*?</a>',
            _replace_pc_card,
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
        patch_preview_megamenu_for_slug(p["slug"], p["card"])

    card_map = {p["slug"]: p["card"] for p in products}
    for hub, slugs in HUB_SLUGS.items():
        patch_hub(hub, [(s, card_map[s]) for s in slugs if s in card_map])

    update_catalog_generator_manifest()
    print(f"Applied assets to {len(products)} preview SKUs under /preview/")


if __name__ == "__main__":
    main()