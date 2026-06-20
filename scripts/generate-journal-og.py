#!/usr/bin/env python3
"""Generate 1200x630 OG PNG cards for journal articles from content JSON."""
from __future__ import annotations
import json
import os
import sys
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow required: pip install Pillow")

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "scripts" / "journal-content"
OUT = ROOT / "img" / "journal-og"

GRADIENTS = {
    "metabolic": ((13, 27, 46), (26, 48, 69)),
    "nad": ((232, 244, 248), (192, 232, 236)),
    "research": ((26, 42, 63), (13, 27, 46)),
    "longevity": ((240, 250, 251), (232, 244, 248)),
    "peptides": ((240, 237, 229), (227, 220, 200)),
    "cost": ((241, 244, 246), (226, 231, 235)),
}

def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def gradient_bg(draw, size, key):
    c1, c2 = GRADIENTS.get(key, GRADIENTS["research"])
    for y in range(size[1]):
        t = y / size[1]
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))

def render_card(c, out_path):
    key = (c.get("categoryKey") or "research").strip().lower()
    if key not in GRADIENTS:
        key = "research"
    W, H = 1200, 630
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    gradient_bg(draw, (W, H), key)

    teal = (0, 180, 197)
    dark = (26, 26, 26)
    muted = (107, 124, 138)
    light = (255, 255, 255) if key in ("nad", "longevity", "peptides", "cost") else (255, 255, 255)

    font_brand = load_font(28, True)
    font_cat = load_font(20, True)
    font_title = load_font(52, True)
    font_deck = load_font(26)

    draw.text((80, 72), "CLYR", fill=dark if key in ("nad", "longevity", "peptides", "cost") else light, font=font_brand)
    draw.text((168, 72), "JOURNAL", fill=teal, font=font_brand)
    draw.text((80, 118), c.get("category", "Research").upper(), fill=muted, font=font_cat)

    title = c["title"]
    lines = textwrap.wrap(title, width=28)[:3]
    y = 200
    for line in lines:
        draw.text((80, y), line, fill=dark if key in ("nad", "longevity", "peptides", "cost") else light, font=font_title)
        y += 62

    deck_lines = textwrap.wrap(c.get("deck", ""), width=52)[:2]
    y += 12
    for line in deck_lines:
        draw.text((80, y), line, fill=muted, font=font_deck)
        y += 34

    draw.rectangle([(80, H - 48), (W - 80, H - 44)], fill=teal)
    draw.text((80, H - 100), "www.clyr.health/journal", fill=muted, font=font_cat)

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)

def main():
    paths = sys.argv[1:] or sorted(CONTENT.glob("*.json"))
    if not paths:
        sys.exit("no journal-content JSON files found")
    for p in paths:
        c = json.loads(Path(p).read_text(encoding="utf-8"))
        slug = c["slug"].strip("/")
        out = OUT / f"{slug}.png"
        render_card(c, out)
        print(f"✓ {out}")

if __name__ == "__main__":
    main()