#!/usr/bin/env python3
"""Move root-level preview SKUs/hubs under /preview/ and strip live hub wiring."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "preview" / "products"
HUBS_DIR = ROOT / "preview" / "hubs"

PRODUCT_SLUGS = [
    "testosterone-cypionate", "testosterone-cream", "testosterone-hypo-spray",
    "enclomiphene", "hcg", "anastrozole",
    "estradiol-patches", "biest-progesterone-cream", "progesterone-capsules",
    "dhea-pregnenolone", "estradiol-vaginal-cream", "womens-testosterone-cream",
    "trimix", "tadalafil-apomorphine", "oxytocin-nasal", "tadalafil-troches",
    "sildenafil-tadalafil-gummy", "pt141-strips",
    "semaglutide-odt", "tirzepatide-sublingual", "metformin-er", "liraglutide",
    "nad-face-cream", "tretinoin", "estriol-ghk-cu-cream", "hydroquinone-triple-cream",
    "doxycycline-acne", "finasteride-oral",
    "bpc-157", "tb-500", "ghk-cu-injectable", "naltrexone-ldn",
    "niagen", "minoxidil", "clyr-tri-gel", "hair-spray-women",
]

HUB_SLUGS = ["mens-hormone", "womens-hormone", "peptides", "recovery", "skin-hair"]

LIVE_HUBS = ["daily-wellness.html", "weight-loss.html", "sexual-health.html"]


def _rewrite_preview_links(text: str) -> str:
    for slug in PRODUCT_SLUGS:
        text = text.replace(f'href="/{slug}.html"', f'href="/preview/products/{slug}.html"')
    for slug in HUB_SLUGS:
        text = text.replace(f'href="/{slug}.html"', f'href="/preview/hubs/{slug}.html"')
    return text


def move_preview_pages():
    PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
    HUBS_DIR.mkdir(parents=True, exist_ok=True)
    moved = []
    for slug in PRODUCT_SLUGS:
        src = ROOT / f"{slug}.html"
        if not src.exists():
            continue
        dst = PRODUCTS_DIR / f"{slug}.html"
        text = _rewrite_preview_links(src.read_text())
        dst.write_text(text)
        src.unlink()
        moved.append(f"products/{slug}.html")
    for slug in HUB_SLUGS:
        src = ROOT / f"{slug}.html"
        if not src.exists():
            continue
        dst = HUBS_DIR / f"{slug}.html"
        text = _rewrite_preview_links(src.read_text())
        dst.write_text(text)
        src.unlink()
        moved.append(f"hubs/{slug}.html")
    return moved


def strip_preview_section(path: Path):
    text = path.read_text()
    new = re.sub(
        r'\n<section class="products"[^>]*id="preview"[^>]*>.*?</section>',
        "",
        text,
        count=1,
        flags=re.S,
    )
    if new != text:
        path.write_text(new)


def patch_preview_tree():
    for html in (ROOT / "preview").rglob("*.html"):
        text = html.read_text()
        new = _rewrite_preview_links(text)
        if new != text:
            html.write_text(new)


def main():
    moved = move_preview_pages()
    for name in LIVE_HUBS:
        p = ROOT / name
        if p.exists():
            strip_preview_section(p)
    patch_preview_tree()
    print(f"Quarantined {len(moved)} preview pages under /preview/")
    for m in moved:
        print(f"  {m}")


if __name__ == "__main__":
    main()