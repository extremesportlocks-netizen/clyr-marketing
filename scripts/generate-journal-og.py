#!/usr/bin/env python3
"""Generate OG / X Article cover PNGs for journal articles from content JSON."""
from __future__ import annotations
import json
import math
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
    "peptides": ((245, 239, 226), (232, 219, 197)),
    "cost": ((241, 244, 246), (226, 231, 235)),
}

TEAL = (0, 180, 197)
GOLD = (200, 166, 103)
DARK = (26, 26, 26)
MUTED = (107, 124, 138)
LIGHT_KEYS = frozenset({"nad", "longevity", "peptides", "cost"})


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


def radial_glow(draw, size, cx_ratio=0.78, cy_ratio=0.28, radius_ratio=0.45):
    w, h = size
    cx, cy = int(w * cx_ratio), int(h * cy_ratio)
    r = int(min(w, h) * radius_ratio)
    for i in range(r, 0, -4):
        alpha = int(28 * (1 - i / r))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(0, 174, 191, alpha) if False else (220, 245, 248))


def wrap_by_width(text, font, max_px, max_lines=4):
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for word in words:
        test = " ".join(current + [word])
        if dummy.textlength(test, font=font) > max_px and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(" ".join(current))
    return lines


def draw_molecular_chain(draw, origin_x, origin_y, scale, light=True):
    """Peptide-chain motif matching journal hero SVGs."""
    pts = []
    for i in range(11):
        x = origin_x + i * 58 * scale
        y = origin_y + math.sin(i * 0.85) * 42 * scale
        pts.append((x, y))
    for i in range(len(pts) - 1):
        color = TEAL if i % 2 == 0 else GOLD
        draw.line([pts[i], pts[i + 1]], fill=color, width=max(2, int(2.6 * scale)))
    for i, (x, y) in enumerate(pts):
        color = TEAL if i % 2 == 0 else GOLD
        r = int(14 * scale)
        draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=max(2, int(2.4 * scale)))
        draw.ellipse([x - 5 * scale, y - 5 * scale, x + 5 * scale, y + 5 * scale], fill=color)


def draw_shield(draw, cx, cy, scale, light=True):
    """Subtle trust/shield motif for pharmacy-safety articles."""
    w, h = int(52 * scale), int(62 * scale)
    top = cy - h // 2
    pts = [
        (cx, top),
        (cx + w // 2, top + int(14 * scale)),
        (cx + w // 2, top + int(38 * scale)),
        (cx, top + h),
        (cx - w // 2, top + int(38 * scale)),
        (cx - w // 2, top + int(14 * scale)),
    ]
    stroke = TEAL if light else (255, 255, 255)
    draw.polygon(pts, outline=stroke, fill=(0, 180, 197, 30) if False else (224, 248, 250))
    draw.line([(cx, top + int(18 * scale)), (cx, top + int(46 * scale))], fill=stroke, width=max(2, int(2.2 * scale)))
    draw.line([(cx - int(12 * scale), top + int(30 * scale)), (cx, top + int(42 * scale)), (cx + int(12 * scale), top + int(24 * scale))], fill=stroke, width=max(2, int(2.2 * scale)))


def draw_motif(draw, size, key, slug, light):
    w, h = size
    scale = w / 1200
    if key in ("longevity", "peptides") or any(k in slug for k in ("ivermectin", "parasite", "antiparasitic")):
        draw_molecular_chain(draw, int(w * 0.58), int(h * 0.44), scale, light)
    if any(k in slug for k in ("buy", "safely", "rogue", "legitscript")):
        draw_shield(draw, int(w * 0.86), int(h * 0.40), scale * 1.1, light)


def render_card(c, out_path, size=(1200, 630)):
    key = (c.get("categoryKey") or "research").strip().lower()
    if key not in GRADIENTS:
        key = "research"
    slug = c.get("slug", "")
    W, H = size
    light = key in LIGHT_KEYS
    text_color = DARK if light else (255, 255, 255)

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    gradient_bg(draw, (W, H), key)
    if light:
        radial_glow(draw, (W, H))
    draw_motif(draw, (W, H), key, slug, light)

    s = W / 1200
    font_brand = load_font(int(28 * s), True)
    font_cat = load_font(int(20 * s), True)
    title_len = len(c.get("title", ""))
    title_pt = int((42 if title_len > 55 else 48) * s)
    font_title = load_font(title_pt, True)
    font_deck = load_font(int(24 * s))

    margin = int(80 * s)
    has_motif = key in ("longevity", "peptides") or any(k in slug for k in ("ivermectin", "parasite", "antiparasitic", "buy", "safely"))
    text_max = int(W * (0.50 if has_motif else 0.72))

    draw.text((margin, int(72 * s)), "CLYR", fill=text_color, font=font_brand)
    draw.text((margin + int(88 * s), int(72 * s)), "JOURNAL", fill=TEAL, font=font_brand)
    draw.text((margin, int(118 * s)), c.get("category", "Research").upper(), fill=MUTED, font=font_cat)

    y = int(185 * s)
    for line in wrap_by_width(c["title"], font_title, text_max, max_lines=4):
        draw.text((margin, y), line, fill=text_color, font=font_title)
        y += int(56 * s)

    y += int(10 * s)
    for line in wrap_by_width(c.get("deck", ""), font_deck, text_max, max_lines=3):
        draw.text((margin, y), line, fill=MUTED, font=font_deck)
        y += int(32 * s)

    draw.rectangle([(margin, H - int(48 * s)), (W - margin, H - int(44 * s))], fill=TEAL)
    draw.text((margin, H - int(100 * s)), "www.clyr.health/journal", fill=MUTED, font=font_cat)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
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