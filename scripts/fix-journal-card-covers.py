#!/usr/bin/env python3
"""One-time fix: inject a clean branded cover-svg into every journal index card
that has an empty cover (feature-card-img / article-card-img with no cover-svg).
Themed light/dark by the card's data-img. Idempotent: skips cards already filled.
Run from repo root: python3 scripts/fix-journal-card-covers.py
"""
import re, sys, pathlib

INDEX = pathlib.Path("journal/index.html")
DARK_KEYS = {"metabolic", "research"}

def palette(key):
    if key in DARK_KEYS:
        return dict(c1="#0d1b2e", c2="#1a3045", grid="#00B4C5", go=0.16,
                    accent="#00B4C5", ao=0.55, bar="#00B4C5", brand="#EAF6F8",
                    teal="#46d5e3", muted="#7d97a0", line="#00B4C5", lo=0.4)
    return dict(c1="#f0fafb", c2="#dceef2", grid="#00B4C5", go=0.14,
                accent="#00B4C5", ao=0.45, bar="#00B4C5", brand="#0d2a35",
                teal="#007a8b", muted="#5b7b83", line="#00B4C5", lo=0.4)

def seeded(cat, n, lo, hi):
    s = sum(ord(ch) for ch in (cat or "x"))
    return lo + ((s * (n + 3) * 31) % (hi - lo + 1))

def cover_svg(key, cat, idx):
    p = palette(key)
    cat = (cat or "CLYR").upper()
    gid = f"g{idx}"
    # four bars of varied height, baseline at y=262
    bars = []
    xs = [232, 280, 328, 376]
    for i, x in enumerate(xs):
        h = seeded(cat, i, 34, 110)
        op = 0.30 + 0.16 * i
        bars.append(f'<rect x="{x}" y="{262-h}" width="36" height="{h}" rx="2" fill="{p["bar"]}" opacity="{op:.2f}"/>')
    bars = "".join(bars)
    # a pulse polyline
    py = seeded(cat, 7, 120, 170)
    pulse = (f'<polyline points="60,{py} 110,{py} 130,{py-34} 152,{py+30} 172,{py} 250,{py}" '
             f'fill="none" stroke="{p["accent"]}" stroke-width="2.4" opacity="{p["ao"]}" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    dots = "".join(
        f'<circle cx="{70+i*26}" cy="{300}" r="3" fill="{p["accent"]}" opacity="{0.25+0.07*(i%4)}"/>'
        for i in range(6))
    return (
        f'<svg class="cover-svg" viewBox="0 0 480 330" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{p["c1"]}"/><stop offset="1" stop-color="{p["c2"]}"/></linearGradient>'
        f'<pattern id="{gid}p" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M 40 0 L 0 0 0 40" fill="none" stroke="{p["grid"]}" stroke-width="0.5" opacity="{p["go"]}"/></pattern>'
        f'</defs>'
        f'<rect width="480" height="330" fill="url(#{gid})"/>'
        f'<rect width="480" height="330" fill="url(#{gid}p)"/>'
        f'<line x1="60" y1="262" x2="430" y2="262" stroke="{p["line"]}" stroke-width="1.2" opacity="{p["lo"]}"/>'
        f'{bars}{pulse}{dots}'
        f'<text x="60" y="62" font-family="DM Sans, sans-serif" font-size="20" font-weight="700" fill="{p["brand"]}" letter-spacing="0.5">CLYR <tspan fill="{p["teal"]}">JOURNAL</tspan></text>'
        f'<text x="60" y="90" font-family="DM Sans, sans-serif" font-size="12" font-weight="700" fill="{p["muted"]}" letter-spacing="2">{cat}</text>'
        f'</svg>'
    )

def main():
    html = INDEX.read_text(encoding="utf-8")
    # process each card <a ...class="feature-card|article-card"...> ... </a>
    card_re = re.compile(r'(<a\b[^>]*class="(?:feature-card|article-card)[^"]*"[^>]*>)(.*?)(</a>)', re.S)
    state = {"n": 0, "filled": 0}
    def fix_card(m):
        opentag, inner, close = m.group(1), m.group(2), m.group(3)
        state["n"] += 1
        if "cover-svg" in inner:
            return m.group(0)  # already has a cover
        dm = re.search(r'data-img="([^"]*)"', opentag)
        key = dm.group(1) if dm else "research"
        cm = re.search(r'-card-cat">([^<]*)<', inner)
        cat = cm.group(1).strip() if cm else "CLYR Journal"
        svg = cover_svg(key, cat, state["n"])
        # inject into the (empty) card-img div, preserving its attributes
        newinner, k = re.subn(r'(<div class="(?:feature|article)-card-img"[^>]*>)(.*?)(</div>)',
                              lambda im: im.group(1) + svg + im.group(3), inner, count=1, flags=re.S)
        if k:
            state["filled"] += 1
            return opentag + newinner + close
        return m.group(0)
    out = card_re.sub(fix_card, html)
    INDEX.write_text(out, encoding="utf-8")
    print(f"cards seen: {state['n']}, covers injected: {state['filled']}")

if __name__ == "__main__":
    main()
