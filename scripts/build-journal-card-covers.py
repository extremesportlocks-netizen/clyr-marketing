#!/usr/bin/env python3
"""Generate distinct, topic-aware cover art for EVERY journal index card.
Replaces each card's cover-svg with a themed illustration chosen by the article's
topic (weight loss -> downtrend, NAD/hormones -> molecule, peptides -> chain,
skin/hair -> droplet, geo -> map pin, cost -> bars, sexual health -> pulse,
oral meds -> capsule, legitscript -> shield). Palette (navy / teal / warm / slate)
is chosen by category. Idempotent. Run from repo root.
"""
import re, pathlib

INDEX = pathlib.Path("journal/index.html")

NAVY  = dict(bg1="#0d1b2e", bg2="#17293f", ink="#EAF6F8", teal="#3fd0e0", sub="#7f9aa4", acc="#3fd0e0", grid="#3fd0e0", go="0.14")
TEAL  = dict(bg1="#eaf6f8", bg2="#d2ecf0", ink="#103038", teal="#0098a8", sub="#5f8088", acc="#0098a8", grid="#0098a8", go="0.12")
WARM  = dict(bg1="#f4f0e7", bg2="#e7ddc9", ink="#2c2417", teal="#0098a8", sub="#7a6f57", acc="#b8923f", grid="#b8923f", go="0.14")
SLATE = dict(bg1="#eef2f6", bg2="#dbe3ec", ink="#1a2536", teal="#0098a8", sub="#5f6b7a", acc="#5b7c93", grid="#5b7c93", go="0.12")

PAL = {"metabolic": NAVY, "research": NAVY, "nad": TEAL, "longevity": TEAL,
       "florida": TEAL, "peptides": WARM, "cost": SLATE, "pennsylvania": SLATE,
       "texas": SLATE}

STATES = ("florida","texas","california","michigan","illinois","new-york","ohio",
          "pennsylvania","north-carolina","georgia","near-me")

def pick_pal(key): return PAL.get(key, TEAL)

def scene_for(slug, cat):
    t = (slug + " " + cat).lower()
    has = lambda *w: any(x in t for x in w)
    if has("legitscript", "certification", "rogue", "safely-online", "buy-ivermectin", "counterfeit", "verify"): return "shield"
    if has(*STATES) or "telehealth-weight-loss" in slug or "weight-loss-telehealth" in slug: return "pin"
    if has("cost", "price", "insurance", "afford"): return "bars"
    if has("sexual", "libido", "-ed", "ed-", "erectile", "pt141", "trimix", "tadalafil", "sildenafil", "oxytocin", "apomorphine", "bremelanotide"): return "pulse"
    if has("peptide", "bpc", "tb-500", "ghk", "sermorelin", "recovery"): return "chain"
    if has("nad", "niagen", "nmn", "glutathione", "longevity", "iv-vs", "what-is-nad"): return "molecule"
    if has("testosterone", "trt", "estradiol", "estriol", "progesterone", "dhea", "enclomiphene", "hcg", "anastrozole", "biest", "hormone"): return "molecule"
    if has("hair", "finasteride", "minoxidil", "tretinoin", "acne", "hydroquinone", "skin", "tri-gel", "face", "regrowth", "doxycycline"): return "droplet"
    if has("troche", "sublingual", "odt", "tablet", "oral", "capsule", "gummy"): return "capsule"
    if has("weight", "glp", "semaglutide", "tirzepatide", "zepbound", "wegovy", "metabolic", "lipo", "micc", "metformin", "liraglutide", "surmount", "select", "plateau", "foundayo", "naltrexone"): return "trend"
    return "molecule"

def sc_trend(p):
    pts = "62,108 132,138 202,164 272,190 342,214 420,240"
    return (f'<path d="M62,108 132,138 202,164 272,190 342,214 420,240 L420,300 L62,300 Z" fill="{p["acc"]}" opacity="0.13"/>'
            f'<polyline points="{pts}" fill="none" stroke="{p["acc"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{p["acc"]}"/>' for x,y in
                      [(62,108),(132,138),(202,164),(272,190),(342,214),(420,240)])
            + f'<path d="M398,236 l22,4 -8,-21 z" fill="{p["acc"]}" opacity="0.9"/>')

def sc_molecule(p):
    cx, cy, r = 250, 158, 50
    verts = [(cx + r*c, cy + r*s) for c,s in
             [(1,0),(0.5,0.866),(-0.5,0.866),(-1,0),(-0.5,-0.866),(0.5,-0.866)]]
    hexpath = "M" + " ".join(f"{x:.0f},{y:.0f}" for x,y in verts) + " Z"
    sats = [(cx+105, cy-58),(cx-110, cy+50),(cx+96, cy+74)]
    bonds = "".join(f'<line x1="{verts[i][0]:.0f}" y1="{verts[i][1]:.0f}" x2="{sx}" y2="{sy}" stroke="{p["acc"]}" stroke-width="2" opacity="0.6"/>'
                    for i,(sx,sy) in zip((0,3,2), sats))
    nodes = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{p["acc"]}"/>' for x,y in verts)
    snodes = "".join(f'<circle cx="{sx}" cy="{sy}" r="11" fill="{p["acc"]}" opacity="0.85"/>' for sx,sy in sats)
    return (f'<path d="{hexpath}" fill="none" stroke="{p["acc"]}" stroke-width="2.4" opacity="0.85"/>'
            f'{bonds}{nodes}{snodes}')

def sc_chain(p):
    el = []
    prev = None
    for i in range(8):
        x = 64 + i*48
        y = 165 + (28 if i % 2 else -28)
        rr = 13 if i % 2 == 0 else 9
        if prev:
            el.append(f'<line x1="{prev[0]}" y1="{prev[1]}" x2="{x}" y2="{y}" stroke="{p["acc"]}" stroke-width="2.2" opacity="0.55"/>')
        el.append(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{p["acc"]}" opacity="{0.55 + 0.05*(i%3)}"/>')
        prev = (x, y)
    return "".join(el)

def sc_droplet(p):
    rings = "".join(f'<circle cx="250" cy="150" r="{r}" fill="none" stroke="{p["acc"]}" stroke-width="1.6" opacity="{op}"/>'
                    for r,op in [(34,0.5),(64,0.3),(96,0.16)])
    drop = (f'<path d="M250,96 C284,140 300,162 300,186 a50,50 0 1 1 -100,0 C200,162 216,140 250,96 Z" '
            f'fill="{p["acc"]}" opacity="0.85"/>'
            f'<circle cx="234" cy="196" r="12" fill="#ffffff" opacity="0.35"/>')
    return rings + drop

def sc_pin(p):
    contour = "".join(f'<path d="M40,{y} C140,{y-18} 240,{y+18} 440,{y-10}" fill="none" stroke="{p["acc"]}" stroke-width="1.4" opacity="0.22"/>'
                      for y in (120,168,216,264))
    pin = (f'<path d="M250,92 a46,46 0 0 1 46,46 c0,34 -46,86 -46,86 c0,0 -46,-52 -46,-86 a46,46 0 0 1 46,-46 Z" '
           f'fill="{p["acc"]}" opacity="0.9"/>'
           f'<circle cx="250" cy="138" r="17" fill="#ffffff" opacity="0.92"/>')
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{p["acc"]}" opacity="0.5"/>' for x,y in [(120,150),(360,130),(380,220),(140,240)])
    return contour + dots + pin

def sc_bars(p):
    xs = [(132,70),(200,108),(268,150),(336,196),(404,150)]
    bars = "".join(f'<rect x="{x}" y="{262-h}" width="40" height="{h}" rx="3" fill="{p["acc"]}" opacity="{0.32+0.13*i}"/>'
                   for i,(x,h) in enumerate(xs))
    coins = "".join(f'<ellipse cx="96" cy="{250-i*16}" rx="30" ry="9" fill="{p["acc"]}" opacity="{0.5-0.08*i}"/>' for i in range(3))
    base = f'<line x1="62" y1="262" x2="430" y2="262" stroke="{p["acc"]}" stroke-width="1.4" opacity="0.4"/>'
    return coins + bars + base

def sc_pulse(p):
    ring = "".join(f'<circle cx="368" cy="120" r="{r}" fill="none" stroke="{p["acc"]}" stroke-width="1.6" opacity="{op}"/>' for r,op in [(26,0.5),(48,0.25)])
    line = (f'<polyline points="48,170 130,170 158,170 178,120 202,224 226,150 250,170 432,170" '
            f'fill="none" stroke="{p["acc"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    node = f'<circle cx="202" cy="224" r="5" fill="{p["acc"]}"/>'
    return ring + line + node

def sc_capsule(p):
    g = (f'<g transform="rotate(-28 250 165)">'
         f'<rect x="170" y="146" width="160" height="40" rx="20" fill="none" stroke="{p["acc"]}" stroke-width="2.5" opacity="0.85"/>'
         f'<rect x="170" y="146" width="80" height="40" rx="20" fill="{p["acc"]}" opacity="0.8"/>'
         f'<line x1="250" y1="146" x2="250" y2="186" stroke="{p["acc"]}" stroke-width="2.5" opacity="0.85"/>'
         f'</g>')
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="{p["acc"]}" opacity="0.4"/>' for x,y in [(120,110),(360,210),(140,235),(380,120)])
    return g + dots

SCENES = {"trend": sc_trend, "molecule": sc_molecule, "chain": sc_chain,
          "droplet": sc_droplet, "pin": sc_pin, "bars": sc_bars, "pulse": sc_pulse,
          "capsule": sc_capsule, "shield": None}

def sc_shield(p):
    s = (f'<path d="M250,86 l64,24 v52 c0,52 -36,82 -64,96 c-28,-14 -64,-44 -64,-96 v-52 Z" '
         f'fill="none" stroke="{p["acc"]}" stroke-width="2.6" opacity="0.9"/>'
         f'<path d="M250,96 l54,20 v44 c0,44 -30,70 -54,82 z" fill="{p["acc"]}" opacity="0.16"/>'
         f'<polyline points="222,168 242,190 286,142" fill="none" stroke="{p["acc"]}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    return s
SCENES["shield"] = sc_shield

def build_cover(slug, key, cat, idx):
    sc = scene_for(slug, cat)
    # Safety/legitimacy pieces (shield) read best on the serious navy palette,
    # regardless of their data-img key. Everything else keeps its category palette.
    p = NAVY if sc == "shield" else pick_pal(key)
    scene = SCENES[sc](p)
    gid = f"cg{idx}"
    return (
        f'<svg class="cover-svg" viewBox="0 0 480 330" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>'
        f'<pattern id="{gid}p" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M 44 0 L 0 0 0 44" fill="none" stroke="{p["grid"]}" stroke-width="0.5" opacity="{p["go"]}"/></pattern>'
        f'</defs>'
        f'<rect width="480" height="330" fill="url(#{gid})"/>'
        f'<rect width="480" height="330" fill="url(#{gid}p)"/>'
        f'{scene}'
        f'</svg>'
    )

def main():
    html = INDEX.read_text(encoding="utf-8")
    card_re = re.compile(r'(<a\b[^>]*class="(?:feature-card|article-card)[^"]*"[^>]*>)(.*?)(</a>)', re.S)
    st = {"n": 0, "done": 0}
    def fix(m):
        opentag, inner, close = m.group(1), m.group(2), m.group(3)
        st["n"] += 1
        hm = re.search(r'href="/journal/([^/"]+)/?"', opentag)
        slug = hm.group(1) if hm else ""
        dm = re.search(r'data-img="([^"]*)"', opentag)
        key = dm.group(1) if dm else "research"
        cm = re.search(r'-card-cat">([^<]*)<', inner)
        cat = cm.group(1).strip() if cm else ""
        svg = build_cover(slug, key, cat, st["n"])
        newinner, k = re.subn(r'(<div class="(?:feature|article)-card-img"[^>]*>)(.*?)(</div>)',
                              lambda im: im.group(1) + svg + im.group(3), inner, count=1, flags=re.S)
        if k:
            st["done"] += 1
            return opentag + newinner + close
        return m.group(0)
    INDEX.write_text(card_re.sub(fix, html), encoding="utf-8")
    print(f"cards: {st['n']}, covers rebuilt: {st['done']}")

if __name__ == "__main__":
    main()
