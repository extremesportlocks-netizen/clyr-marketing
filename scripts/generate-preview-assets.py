#!/usr/bin/env python3
"""Generate preview product heroes + card thumbs for 36 preview SKUs."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
VIAL_BLANK = ROOT / "preview" / "vial-review" / "final" / "clyr-vial-blank.png"
VIAL_BG_REF: dict[str, Path] = {
    "longevity": ROOT / "preview" / "vial-review" / "final" / "nad.png",
    "glp": ROOT / "preview" / "vial-review" / "final" / "semaglutide.png",
    "hormone": ROOT / "preview" / "vial-review" / "final" / "nad.png",
    "sexual": ROOT / "preview" / "vial-review" / "final" / "nad.png",
    "skin": ROOT / "preview" / "vial-review" / "final" / "glutathione.png",
}
OUT = ROOT / "preview" / "assets"
HEROES = OUT / "heroes"
CARDS = OUT / "cards"
SVG_DIR = OUT / "svg"

# slug -> (form, title, subtitle, detail, wash)
# wash: longevity | glp | sexual | hormone | skin
PREVIEW_ASSETS: dict[str, tuple[str, str, str, str, str]] = {
    "semaglutide-odt": ("oral", "Semaglutide ODT", "Oral GLP-1", "4 mg + ondansetron", "glp"),
    "tirzepatide-sublingual": ("dropper", "Tirzepatide SL", "Sublingual GLP-1", "Dropper bottle", "glp"),
    "metformin-er": ("capsule", "Metformin ER", "Metabolic Support", "500 mg", "glp"),
    "liraglutide": ("vial", "Liraglutide", "GLP-1 Therapy", "Up to 3 mg daily", "glp"),
    "niagen": ("vial", "Niagen", "NAD+ Precursor", "100 mg/ml", "longevity"),
    "bpc-157": ("vial", "BPC-157", "Tissue Repair", "500 mcg protocol", "longevity"),
    "tb-500": ("vial", "TB-500", "Recovery Peptide", "2.5 mg", "longevity"),
    "ghk-cu-injectable": ("vial", "GHK-Cu", "Copper Peptide", "Injectable", "longevity"),
    "naltrexone-ldn": ("capsule", "LDN", "Low-Dose Naltrexone", "4.5 mg", "longevity"),
    "testosterone-cypionate": ("vial", "Testosterone", "Cypionate TRT", "200 mg/ml", "hormone"),
    "testosterone-cream": ("tube", "Testosterone", "1% Cream", "30 g tube", "hormone"),
    "testosterone-hypo-spray": ("spray", "Testosterone", "Hypo Spray", "20 mg/0.2 ml", "hormone"),
    "enclomiphene": ("capsule", "Enclomiphene", "Fertility + T", "12.5 mg", "hormone"),
    "hcg": ("vial", "HCG", "Gonadotropin", "10,000 IU", "hormone"),
    "anastrozole": ("capsule", "Anastrozole", "TRT Support", "0.5 mg", "hormone"),
    "estradiol-patches": ("patch", "Estradiol", "Transdermal Patch", "0.05 mg/day", "hormone"),
    "biest-progesterone-cream": ("tube", "Biest + Prog", "HRT Cream", "30 g", "hormone"),
    "progesterone-capsules": ("capsule", "Progesterone", "Micronized", "100 mg", "hormone"),
    "dhea-pregnenolone": ("capsule", "DHEA + Preg", "Adrenal Support", "30 count", "hormone"),
    "estradiol-vaginal-cream": ("tube", "Estradiol", "Vaginal Cream", "30 g", "hormone"),
    "womens-testosterone-cream": ("tube", "Women's T", "Libido Cream", "30 g", "hormone"),
    "trimix": ("vial", "Trimix", "Injectable ED", "T105", "sexual"),
    "tadalafil-apomorphine": ("troche", "Tadalafil + Apo", "Dual ED Troche", "22 mg / 2 mg", "sexual"),
    "oxytocin-nasal": ("spray", "Oxytocin", "Nasal Spray", "Intimacy support", "sexual"),
    "tadalafil-troches": ("troche", "Tadalafil", "ED Troche", "22 mg", "sexual"),
    "sildenafil-tadalafil-gummy": ("gummy", "Dual PDE5", "Sildenafil + Tadalafil", "40 mg / 10 mg", "sexual"),
    "pt141-strips": ("strip", "PT-141", "Libido Strip", "On-demand", "sexual"),
    "clyr-tri-gel": ("pump", "CLYR Tri Gel", "Master Formulation", "50 g pump", "skin"),
    "minoxidil": ("spray", "Hair Regrowth", "Men's 7% Quad", "60 ml spray", "skin"),
    "hair-spray-women": ("spray", "Hair Regrowth", "Women's 7% Stack", "60 ml spray", "skin"),
    "nad-face-cream": ("pump", "NAD+ Face", "Anti-Aging Cream", "10% pump", "skin"),
    "tretinoin": ("tube", "Tretinoin", "Retinoid Cream", "0.025% 45 g", "skin"),
    "estriol-ghk-cu-cream": ("tube", "Estriol GHK-Cu", "Anti-Aging Cream", "30 g", "skin"),
    "hydroquinone-triple-cream": ("tube", "Triple Cream", "Hyperpigmentation", "30 g", "skin"),
    "doxycycline-acne": ("capsule", "Doxycycline", "Acne Protocol", "100 mg", "skin"),
    "finasteride-oral": ("capsule", "Finasteride", "Hair + DHT", "1 mg", "skin"),
}

WASH_BG = {
    "longevity": ((240, 248, 255), (200, 230, 255)),
    "glp": ((245, 255, 252), (180, 235, 230)),
    "sexual": ((255, 245, 250), (255, 220, 235)),
    "hormone": ((245, 248, 255), (210, 225, 245)),
    "skin": ((240, 252, 250), (190, 235, 230)),
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    reg_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    if not Path(reg_path).exists():
        reg_path = "/System/Library/Fonts/Supplemental/Helvetica.ttc"
    path = bold_path if bold else reg_path
    try:
        return ImageFont.truetype(path, size) if Path(path).exists() else ImageFont.truetype(reg_path, size)
    except OSError:
        return ImageFont.load_default()


def _fonts() -> tuple:
    return _font(52, bold=True), _font(28)


def _draw_clyr_logo(draw: ImageDraw.ImageDraw, cx: int, y: int, size: int = 36):
    f = _font(size, bold=True)
    cly = "CLY"
    r = "R"
    w_cly = draw.textlength(cly, font=f)
    x = int(cx - (w_cly + draw.textlength(r, font=f)) / 2)
    draw.text((x, y), cly, fill="#0d1b2e", font=f, anchor="lm")
    draw.text((x + w_cly, y), r, fill="#00B4C5", font=f, anchor="lm")


def _gradient_bg_from_ref(ref_path: Path, size: tuple[int, int] = (600, 600)) -> Image.Image:
    ref = Image.open(ref_path).convert("RGB")
    top = ref.getpixel((40, 40))
    bot = ref.getpixel((40, size[1] - 30))
    img = Image.new("RGBA", size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        color = (
            int(top[0] * (1 - t) + bot[0] * t),
            int(top[1] * (1 - t) + bot[1] * t),
            int(top[2] * (1 - t) + bot[2] * t),
            255,
        )
        draw.line([(0, y), (size[0], y)], fill=color)
    return img


def _extract_vial_layer(blank_path: Path) -> Image.Image:
    im = Image.open(blank_path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r > 242 and g > 242 and b > 242:
                px[x, y] = (255, 255, 255, 0)
    return im


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_w: float,
    start_size: int,
    bold: bool = True,
) -> tuple[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
    size = start_size
    while size > 14:
        f = _font(size, bold=bold)
        if draw.textlength(text, font=f) <= max_w:
            return text, f
        size -= 2
    short = textwrap.shorten(text, 12, placeholder="…")
    return short, _font(14, bold=bold)


def composite_vial(title: str, subtitle: str, detail: str, wash: str) -> Image.Image:
    """Match live finals: Canva blank vial + frosted on-glass labels (no floating card)."""
    blank = VIAL_BLANK if VIAL_BLANK.exists() else VIAL_BG_REF["longevity"]
    bg_ref = VIAL_BG_REF.get(wash, VIAL_BG_REF["longevity"])
    canvas = _gradient_bg_from_ref(bg_ref)
    canvas = Image.alpha_composite(canvas, _extract_vial_layer(blank))

    # Frost entire vial body (covers Canva CLYR print) — matches live vial-nad-new style
    frost = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(frost)
    fd.rounded_rectangle((218, 198, 382, 532), radius=6, fill=(255, 255, 255, 252))
    canvas = Image.alpha_composite(canvas, frost)

    draw = ImageDraw.Draw(canvas)
    cx = 300
    max_w = 132.0

    label_rows: list[tuple[str, int, bool, str]] = []
    if wash == "glp":
        label_rows = [
            ("Compounded", 18, False, "#4a5568"),
            (title, 32, True, "#0d1b2e"),
            (subtitle, 21, False, "#6b7c8a"),
        ]
        if detail:
            label_rows.append((detail, 19, False, "#6b7c8a"))
        y_start, y_step = 278, 32
    else:
        label_rows = [(title, 40, True, "#0d1b2e")]
        if subtitle:
            label_rows.append((subtitle, 24, False, "#6b7c8a"))
        if detail:
            label_rows.append((detail, 22, False, "#6b7c8a"))
        y_start, y_step = 295, 36

    y = y_start
    for text, size, bold, color in label_rows:
        line, font = _fit_font(draw, text, max_w, size, bold=bold)
        draw.text((cx, y), line, fill=color, font=font, anchor="mm")
        y += y_step

    _draw_clyr_logo(draw, cx, 498, 28)
    return canvas.convert("RGB")


def _svg_wrap(inner: str, wash: str) -> str:
    c1, c2 = WASH_BG.get(wash, WASH_BG["longevity"])
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" fill="none">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="rgb({c1[0]},{c1[1]},{c1[2]})"/>
      <stop offset="100%" stop-color="rgb({c2[0]},{c2[1]},{c2[2]})"/>
    </linearGradient>
    <linearGradient id="glass" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95"/>
      <stop offset="45%" stop-color="#e8f7f8" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="#b8e8ec" stop-opacity="0.55"/>
    </linearGradient>
    <linearGradient id="chrome" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f4f7f8"/>
      <stop offset="50%" stop-color="#c5d0d6"/>
      <stop offset="100%" stop-color="#8fa3ad"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#0d1b2e" flood-opacity="0.16"/>
    </filter>
  </defs>
  <rect width="400" height="480" fill="url(#bg)"/>
  <g filter="url(#shadow)">{inner}</g>
</svg>'''


def _label_block(title: str, subtitle: str, detail: str, y: int = 250) -> str:
    t = textwrap.shorten(title, 18, placeholder="…")
    s = textwrap.shorten(subtitle, 22, placeholder="…")
    d = textwrap.shorten(detail, 24, placeholder="…")
    return f'''
    <rect x="155" y="{y}" width="90" height="88" rx="8" fill="#ffffff" fill-opacity="0.85" stroke="#00B4C5" stroke-width="1.2"/>
    <text x="200" y="{y + 28}" text-anchor="middle" font-family="DM Sans, Arial, sans-serif" font-size="11" font-weight="700" fill="#007a8b">CLYR</text>
    <text x="200" y="{y + 48}" text-anchor="middle" font-family="DM Sans, Arial, sans-serif" font-size="13" font-weight="800" fill="#0d1b2e">{t}</text>
    <text x="200" y="{y + 64}" text-anchor="middle" font-family="DM Sans, Arial, sans-serif" font-size="8" font-weight="600" fill="#6b7c8a">{s}</text>
    <text x="200" y="{y + 78}" text-anchor="middle" font-family="DM Sans, Arial, sans-serif" font-size="7.5" font-weight="600" fill="#6b7c8a">{d}</text>'''


def svg_pump(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="168" y="24" width="64" height="42" rx="10" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.5"/>
    <rect x="188" y="8" width="24" height="22" rx="6" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <ellipse cx="200" cy="66" rx="34" ry="8" fill="#dfe9ec" opacity="0.9"/>
    <path d="M142 74 h116 c8 0 14 6 14 14 v250 c0 28 -24 50 -54 50 h-36 c-30 0 -54 -22 -54 -50 V88 c0 -8 6 -14 14 -14z" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <path d="M152 120 h96 v180 c0 18 -16 32 -36 32 h-24 c-20 0 -36 -14 -36 -32 V120z" fill="#00B4C5" fill-opacity="0.12"/>
    <path d="M158 95 v290" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.55"/>
    {_label_block(title, subtitle, detail)}'''
    return _svg_wrap(inner, wash)


def svg_spray(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="175" y="18" width="50" height="70" rx="8" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.5"/>
    <rect x="188" y="4" width="24" height="20" rx="5" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <ellipse cx="200" cy="88" rx="28" ry="6" fill="#dfe9ec"/>
    <path d="M138 92 h124 c10 0 18 8 18 18 v220 c0 26 -22 46 -50 46 h-60 c-28 0 -50 -20 -50 -46 V110 c0 -10 8 -18 18 -18z" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <path d="M150 130 h100 v170 c0 16 -14 28 -32 28 h-36 c-18 0 -32 -12 -32 -28 V130z" fill="#00B4C5" fill-opacity="0.1"/>
    <path d="M156 108 v250" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="0.5"/>
    {_label_block(title, subtitle, detail, 240)}'''
    return _svg_wrap(inner, wash)


def svg_tube(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="162" y="60" width="76" height="28" rx="14" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <rect x="130" y="88" width="140" height="300" rx="22" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <rect x="145" y="110" width="110" height="240" rx="14" fill="#ffffff" fill-opacity="0.75"/>
    <path d="M148 100 v280" stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.45"/>
    {_label_block(title, subtitle, detail, 200)}'''
    return _svg_wrap(inner, wash)


def svg_capsule(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="148" y="40" width="104" height="36" rx="10" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <path d="M138 76 h124 c12 0 22 10 22 22 v270 c0 24 -20 44 -44 44 h-80 c-24 0 -44 -20 -44 -44 V98 c0 -12 10 -22 22 -22z" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <rect x="155" y="130" width="90" height="170" rx="10" fill="#ffffff" fill-opacity="0.8"/>
    <ellipse cx="185" cy="330" rx="14" ry="22" fill="#00B4C5" fill-opacity="0.35"/>
    <ellipse cx="215" cy="318" rx="14" ry="22" fill="#0d1b2e" fill-opacity="0.2"/>
    {_label_block(title, subtitle, detail, 155)}'''
    return _svg_wrap(inner, wash)


def svg_patch(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="95" y="140" width="210" height="200" rx="16" fill="#ffffff" fill-opacity="0.9" stroke="#dde2e7" stroke-width="2"/>
    <rect x="120" y="175" width="160" height="130" rx="8" fill="url(#glass)" stroke="#9fd9de" stroke-width="1.5"/>
    <circle cx="200" cy="240" r="42" fill="#00B4C5" fill-opacity="0.15" stroke="#00B4C5" stroke-width="1"/>
    <text x="200" y="232" text-anchor="middle" font-family="DM Sans, Arial" font-size="12" font-weight="800" fill="#0d1b2e">{textwrap.shorten(title, 14)}</text>
    <text x="200" y="252" text-anchor="middle" font-family="DM Sans, Arial" font-size="9" fill="#6b7c8a">{textwrap.shorten(subtitle, 18)}</text>
    <text x="200" y="268" text-anchor="middle" font-family="DM Sans, Arial" font-size="8" fill="#00B4C5">{textwrap.shorten(detail, 20)}</text>'''
    return _svg_wrap(inner, wash)


def svg_oral(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="155" y="50" width="90" height="28" rx="8" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <path d="M142 78 h116 c10 0 18 8 18 18 v250 c0 28 -24 50 -54 50 h-76 c-30 0 -54 -22 -54 -50 V96 c0 -10 8 -18 18 -18z" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <rect x="168" y="200" width="64" height="64" rx="10" fill="#00B4C5" fill-opacity="0.2" stroke="#00B4C5" stroke-width="1"/>
    <text x="200" y="238" text-anchor="middle" font-family="DM Sans, Arial" font-size="10" font-weight="700" fill="#0d1b2e">ODT</text>
    {_label_block(title, subtitle, detail, 120)}'''
    return _svg_wrap(inner, wash)


def svg_dropper(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="188" y="20" width="24" height="55" rx="6" fill="url(#chrome)" stroke="#9eb4be" stroke-width="1.2"/>
    <ellipse cx="200" cy="78" rx="18" ry="6" fill="#9eb4be"/>
    <path d="M148 84 h104 c8 0 14 6 14 14 v260 c0 26 -22 46 -50 46 h-32 c-28 0 -50 -20 -50 -46 V98 c0 -8 6 -14 14 -14z" fill="url(#glass)" stroke="#9fd9de" stroke-width="2"/>
    <path d="M160 130 h80 v180" stroke="#00B4C5" stroke-width="2" fill="#00B4C5" fill-opacity="0.15"/>
    {_label_block(title, subtitle, detail, 230)}'''
    return _svg_wrap(inner, wash)


def svg_troche(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="110" y="160" width="180" height="160" rx="20" fill="#ffffff" fill-opacity="0.92" stroke="#dde2e7" stroke-width="2"/>
    <circle cx="160" cy="240" r="32" fill="#00B4C5" fill-opacity="0.25" stroke="#00B4C5" stroke-width="1.5"/>
    <circle cx="200" cy="240" r="32" fill="#00B4C5" fill-opacity="0.35" stroke="#00B4C5" stroke-width="1.5"/>
    <circle cx="240" cy="240" r="32" fill="#00B4C5" fill-opacity="0.25" stroke="#00B4C5" stroke-width="1.5"/>
    <text x="200" y="330" text-anchor="middle" font-family="DM Sans, Arial" font-size="13" font-weight="800" fill="#0d1b2e">{textwrap.shorten(title, 16)}</text>
    <text x="200" y="350" text-anchor="middle" font-family="DM Sans, Arial" font-size="9" fill="#6b7c8a">{textwrap.shorten(detail, 22)}</text>'''
    return _svg_wrap(inner, wash)


def svg_gummy(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="100" y="170" width="90" height="90" rx="22" fill="#00B4C5" fill-opacity="0.35" stroke="#00B4C5" stroke-width="1.5"/>
    <rect x="210" y="170" width="90" height="90" rx="22" fill="#0d1b2e" fill-opacity="0.15" stroke="#0d1b2e" stroke-width="1.5"/>
    <text x="145" y="228" text-anchor="middle" font-family="DM Sans, Arial" font-size="11" font-weight="700" fill="#0d1b2e">S</text>
    <text x="255" y="228" text-anchor="middle" font-family="DM Sans, Arial" font-size="11" font-weight="700" fill="#0d1b2e">T</text>
    <text x="200" y="310" text-anchor="middle" font-family="DM Sans, Arial" font-size="13" font-weight="800" fill="#0d1b2e">{textwrap.shorten(title, 16)}</text>
    <text x="200" y="330" text-anchor="middle" font-family="DM Sans, Arial" font-size="9" fill="#6b7c8a">{textwrap.shorten(detail, 22)}</text>'''
    return _svg_wrap(inner, wash)


def svg_strip(title: str, subtitle: str, detail: str, wash: str) -> str:
    inner = f'''
    <rect x="120" y="190" width="160" height="100" rx="12" fill="#ffffff" stroke="#dde2e7" stroke-width="2"/>
    <rect x="135" y="210" width="130" height="18" rx="4" fill="#00B4C5" fill-opacity="0.35"/>
    <rect x="135" y="236" width="130" height="18" rx="4" fill="#00B4C5" fill-opacity="0.25"/>
    <rect x="135" y="262" width="130" height="18" rx="4" fill="#00B4C5" fill-opacity="0.35"/>
    <text x="200" y="330" text-anchor="middle" font-family="DM Sans, Arial" font-size="13" font-weight="800" fill="#0d1b2e">{textwrap.shorten(title, 16)}</text>'''
    return _svg_wrap(inner, wash)


SVG_BUILDERS = {
    "pump": svg_pump,
    "spray": svg_spray,
    "tube": svg_tube,
    "capsule": svg_capsule,
    "patch": svg_patch,
    "oral": svg_oral,
    "dropper": svg_dropper,
    "troche": svg_troche,
    "gummy": svg_gummy,
    "strip": svg_strip,
}


def _bg_canvas(wash: str, size: tuple[int, int] = (600, 600)) -> Image.Image:
    img = Image.new("RGBA", size, (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    c1, c2 = WASH_BG.get(wash, WASH_BG["longevity"])
    for y in range(size[1]):
        t = y / size[1]
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b, 255))
    return img


def _draw_label_card(draw: ImageDraw.ImageDraw, cx: int, cy: int, title: str, subtitle: str, detail: str):
    bold, regular = _fonts()
    w, h = 200, 150
    x0, y0 = cx - w // 2, cy - h // 2
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=14, fill=(255, 255, 255, 230), outline="#00B4C5", width=2)
    t1, f1 = title, bold
    if draw.textlength(t1, font=f1) > 170:
        t1 = textwrap.shorten(t1, 14, placeholder="…")
    draw.text((cx, cy - 42), t1, fill="#0d1b2e", font=f1, anchor="mm")
    draw.text((cx, cy - 4), textwrap.shorten(subtitle, 20), fill="#6b7c8a", font=regular, anchor="mm")
    draw.text((cx, cy + 28), textwrap.shorten(detail, 22), fill="#6b7c8a", font=regular, anchor="mm")
    _draw_clyr_logo(draw, cx, cy + 58, 26)


def _glass_body(draw, bbox, fill=(232, 247, 248, 220)):
    draw.rounded_rectangle(bbox, radius=28, fill=fill, outline="#9fd9de", width=3)
    x0, y0, x1, y1 = bbox
    draw.line([(x0 + 18, y0 + 20), (x0 + 18, y1 - 20)], fill=(255, 255, 255, 140), width=8)


def render_form_pil(form: str, title: str, subtitle: str, detail: str, wash: str) -> Image.Image:
    img = _bg_canvas(wash)
    draw = ImageDraw.Draw(img)
    cx, cy = 300, 300

    if form == "pump":
        draw.rounded_rectangle((228, 40, 372, 120), radius=16, fill="#d5e0e5", outline="#9eb4be", width=2)
        draw.rounded_rectangle((252, 18, 348, 58), radius=10, fill="#e8eef1", outline="#9eb4be", width=2)
        _glass_body(draw, (168, 118, 432, 470), fill=(235, 250, 251, 235))
        draw.rectangle((198, 200, 402, 400), fill=(0, 180, 197, 28))
        _draw_label_card(draw, cx, 330, title, subtitle, detail)
    elif form == "spray":
        draw.rounded_rectangle((248, 28, 352, 150), radius=14, fill="#d5e0e5", outline="#9eb4be", width=2)
        draw.rounded_rectangle((264, 8, 336, 48), radius=8, fill="#e8eef1", outline="#9eb4be", width=2)
        _glass_body(draw, (178, 148, 422, 470), fill=(235, 250, 251, 235))
        draw.rectangle((210, 210, 390, 390), fill=(0, 180, 197, 22))
        _draw_label_card(draw, cx, 340, title, subtitle, detail)
    elif form == "tube":
        draw.rounded_rectangle((228, 88, 372, 140), radius=20, fill="#d5e0e5", outline="#9eb4be", width=2)
        _glass_body(draw, (168, 138, 432, 470), fill=(245, 250, 252, 240))
        _draw_label_card(draw, cx, 320, title, subtitle, detail)
    elif form == "capsule":
        draw.rounded_rectangle((218, 58, 382, 110), radius=12, fill="#d5e0e5", outline="#9eb4be", width=2)
        _glass_body(draw, (188, 108, 412, 470), fill=(240, 248, 252, 235))
        draw.ellipse((230, 300, 270, 360), fill=(0, 180, 197, 70))
        draw.ellipse((330, 290, 370, 350), fill=(13, 27, 46, 40))
        _draw_label_card(draw, cx, 250, title, subtitle, detail)
    elif form == "patch":
        draw.rounded_rectangle((120, 170, 480, 430), radius=20, fill=(255, 255, 255, 245), outline="#dde2e7", width=2)
        draw.rounded_rectangle((170, 220, 430, 380), radius=12, fill=(232, 247, 248, 220), outline="#9fd9de", width=2)
        draw.ellipse((cx - 55, cy - 20, cx + 55, cy + 90), outline="#00B4C5", width=2, fill=(0, 180, 197, 35))
        bold, regular = _fonts()
        draw.text((cx, cy + 10), textwrap.shorten(title, 14), fill="#0d1b2e", font=bold, anchor="mm")
        draw.text((cx, cy + 48), textwrap.shorten(detail, 20), fill="#6b7c8a", font=regular, anchor="mm")
    elif form == "oral":
        draw.rounded_rectangle((228, 68, 372, 110), radius=10, fill="#d5e0e5", outline="#9eb4be", width=2)
        _glass_body(draw, (188, 108, 412, 470), fill=(235, 250, 251, 235))
        draw.rounded_rectangle((248, 250, 352, 354), radius=14, fill=(0, 180, 197, 50), outline="#00B4C5", width=2)
        bold, _ = _fonts()
        draw.text((cx, 302), "ODT", fill="#0d1b2e", font=bold, anchor="mm")
        _draw_label_card(draw, cx, 180, title, subtitle, detail)
    elif form == "dropper":
        draw.rounded_rectangle((268, 30, 332, 120), radius=8, fill="#d5e0e5", outline="#9eb4be", width=2)
        _glass_body(draw, (198, 118, 402, 470), fill=(235, 250, 251, 235))
        draw.line([(cx, 180), (cx, 400)], fill="#00B4C5", width=3)
        _draw_label_card(draw, cx, 340, title, subtitle, detail)
    elif form == "troche":
        draw.rounded_rectangle((130, 200, 470, 400), radius=24, fill=(255, 255, 255, 245), outline="#dde2e7", width=2)
        for ox in (-70, 0, 70):
            draw.ellipse((cx + ox - 36, cy - 10, cx + ox + 36, cy + 62), fill=(0, 180, 197, 55), outline="#00B4C5", width=2)
        bold, regular = _fonts()
        draw.text((cx, 430), textwrap.shorten(title, 16), fill="#0d1b2e", font=bold, anchor="mm")
        draw.text((cx, 458), textwrap.shorten(detail, 22), fill="#6b7c8a", font=regular, anchor="mm")
    elif form == "gummy":
        draw.rounded_rectangle((150, 240, 260, 350), radius=28, fill=(0, 180, 197, 90), outline="#00B4C5", width=2)
        draw.rounded_rectangle((340, 240, 450, 350), radius=28, fill=(13, 27, 46, 35), outline="#0d1b2e", width=2)
        bold, regular = _fonts()
        draw.text((205, 295), "S", fill="#0d1b2e", font=bold, anchor="mm")
        draw.text((395, 295), "T", fill="#0d1b2e", font=bold, anchor="mm")
        draw.text((cx, 400), textwrap.shorten(title, 16), fill="#0d1b2e", font=bold, anchor="mm")
    elif form == "strip":
        draw.rounded_rectangle((150, 250, 450, 370), radius=14, fill=(255, 255, 255, 245), outline="#dde2e7", width=2)
        for i, oy in enumerate((0, 26, 52)):
            draw.rounded_rectangle((170, 270 + oy, 430, 288 + oy), radius=6, fill=(0, 180, 197, 70 if i != 1 else 50))
        bold, _ = _fonts()
        draw.text((cx, 410), textwrap.shorten(title, 16), fill="#0d1b2e", font=bold, anchor="mm")
    else:
        _draw_label_card(draw, cx, cy, title, subtitle, detail)

    return img


def make_card(hero: Path, card: Path):
    img = Image.open(hero).convert("RGBA")
    img.thumbnail((280, 380), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (280, 380), (255, 255, 255, 0))
    ox = (280 - img.width) // 2
    oy = (380 - img.height) // 2
    canvas.paste(img, (ox, oy), img)
    canvas.save(card, "PNG")


def generate_all():
    HEROES.mkdir(parents=True, exist_ok=True)
    CARDS.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for slug, (form, title, subtitle, detail, wash) in PREVIEW_ASSETS.items():
        hero_png = HEROES / f"{slug}.png"
        hero_svg = SVG_DIR / f"{slug}.svg"
        card_png = CARDS / f"{slug}.png"

        if form == "vial":
            img = composite_vial(title, subtitle, detail, wash)
        elif slug == "clyr-tri-gel":
            # Prefer existing frosted pump SVG as source; render via PIL pump template with Tri Gel copy
            img = render_form_pil("pump", title, subtitle, detail, wash)
            SVG_BUILDERS["pump"](title, subtitle, detail, wash)
            hero_svg.write_text(SVG_BUILDERS["pump"](title, subtitle, detail, wash))
        else:
            svg = SVG_BUILDERS[form](title, subtitle, detail, wash)
            hero_svg.write_text(svg)
            img = render_form_pil(form, title, subtitle, detail, wash)
        img.save(hero_png, "PNG")

        make_card(hero_png, card_png)
        manifest.append({
            "slug": slug,
            "form": form,
            "title": title,
            "subtitle": subtitle,
            "detail": detail,
            "wash": wash,
            "hero": f"/preview/assets/heroes/{slug}.png",
            "hero_svg": f"/preview/assets/svg/{slug}.svg" if form != "vial" else None,
            "card": f"/preview/assets/cards/{slug}.png",
        })

    (OUT / "manifest.json").write_text(json.dumps({"products": manifest, "count": len(manifest)}, indent=2))
    print(f"Generated {len(manifest)} preview assets → {OUT}")


def build_review_index():
    manifest = json.loads((OUT / "manifest.json").read_text())
    cards = []
    for p in manifest["products"]:
        cards.append(f'''<div class="card">
  <img src="{p['hero']}" alt="{p['title']}">
  <div class="meta">
    <strong>{p['title']}</strong>
    <span>{p['subtitle']} · {p['detail']}</span>
    <em>{p['form']} · {p['slug']}</em>
    <div class="links">
      <a href="/{p['slug']}.html">Product page</a>
      <a href="{p['card']}">Card thumb</a>
    </div>
  </div>
</div>''')
    html = f'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>CLYR Asset Review · 36 Preview SKUs</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'DM Sans',system-ui,sans-serif;background:#fafbfc;color:#1a1a1a;padding:40px 20px}}
.wrap{{max-width:1200px;margin:0 auto}}
.banner{{background:#FFD43B;color:#1a1a1a;text-align:center;padding:10px;font-size:13px;font-weight:600;border-radius:8px;margin-bottom:28px}}
h1{{font-size:28px;margin-bottom:6px}} .lead{{color:#6b7c8a;margin-bottom:32px;font-size:15px;max-width:720px;line-height:1.6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}}
.card{{background:#fff;border:1px solid #e2e7eb;border-radius:16px;overflow:hidden}}
.card img{{width:100%;aspect-ratio:1;object-fit:contain;background:linear-gradient(180deg,#f8fbff,#eef6ff);padding:12px}}
.meta{{padding:14px 16px}} .meta strong{{font-size:16px;display:block}} .meta span{{font-size:13px;color:#6b7c8a}}
.meta em{{font-size:11px;color:#94a3b0;font-style:normal;margin-top:6px;display:block;text-transform:uppercase;letter-spacing:.04em}}
.links{{margin-top:10px;display:flex;gap:12px}} .links a{{font-size:12px;font-weight:600;color:#00B4C5;text-decoration:none}}
.note{{margin-top:32px;padding:16px;background:#fff;border:1px solid #e2e7eb;border-radius:12px;font-size:13px;color:#6b7c8a;line-height:1.6}}
</style></head><body><div class="wrap">
<div class="banner">ASSET REVIEW — not live · approve here before promoting to /img/</div>
<h1>36 preview product heroes</h1>
<p class="lead">Vials composited from your Canva blank (<code>preview/vial-review/final/clyr-vial-blank.png</code>) with on-glass labels matching live <code>vial-nad-new</code> / <code>vial-semaglutide-new</code> style. Pump, spray, tube, capsule, and other forms use frosted-glass SVG templates. Wired into preview product pages only.</p>
<div class="grid">{"".join(cards)}</div>
<p class="note"><strong>Next:</strong> approve visuals here, then run <code>python3 scripts/apply-preview-assets.py</code> to refresh pages (already run once). To promote to live <code>/img/</code>, say the word after sign-off.</p>
</div></body></html>'''
    review = ROOT / "preview" / "asset-review" / "index.html"
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(html)
    print(f"Review page: {review}")


if __name__ == "__main__":
    generate_all()
    build_review_index()