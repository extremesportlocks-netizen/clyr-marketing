#!/usr/bin/env python3
"""Generate a branded X Article cover PNG (16:9)."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

NAVY = (13, 27, 42)
TEAL = (0, 229, 229)
WHITE = (240, 244, 248)
MUTED = (100, 116, 139)


def make_cover(out: Path, title: str, subtitle: str = "CLYR Journal") -> None:
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), NAVY)
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / h
        r = int(NAVY[0] * (1 - t * 0.15))
        g = int(NAVY[1] * (1 - t * 0.1))
        b = int(NAVY[2] * (1 - t * 0.05))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    draw.rectangle([(0, 0), (w, 8)], fill=TEAL)
    draw.ellipse([(1180, -120), (1680, 380)], fill=(0, 229, 229, 20) if False else (0, 80, 90))

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64)
        brand_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
        sub_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
    except OSError:
        title_font = ImageFont.load_default()
        brand_font = title_font
        sub_font = title_font

    draw.text((80, 72), "CLYR", font=brand_font, fill=WHITE)
    tw = draw.textlength("CLYR", font=brand_font)
    draw.text((80 + tw, 72), "R", font=brand_font, fill=TEAL)
    draw.text((80 + tw + 34, 82), "HEALTH", font=sub_font, fill=MUTED)

    words = title.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        test = " ".join(current + [word])
        if draw.textlength(test, font=title_font) > w - 160 and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))

    y = 220
    for line in lines[:4]:
        draw.text((80, y), line, font=title_font, fill=WHITE)
        y += 78

    draw.rectangle([(80, y + 20), (220, y + 24)], fill=TEAL)
    draw.text((80, h - 110), subtitle, font=sub_font, fill=TEAL)
    draw.text((80, h - 70), "Licensed providers · LegitScript certified", font=sub_font, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"✓ Cover → {out}")


if __name__ == "__main__":
    slug = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else slug.replace("-", " ").title()
    out = Path(__file__).resolve().parent / "covers" / f"{slug}.png"
    make_cover(out, title)