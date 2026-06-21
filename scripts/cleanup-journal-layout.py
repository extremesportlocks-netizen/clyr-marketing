#!/usr/bin/env python3
"""Clean up the journal index:
 - Keep only 3 cards in 'Featured picks'; move the rest into one filterable grid.
 - Order the Browse chips by article count (desc), so Weight Loss leads.
 - Hide the Featured section when a category filter is active.
Run from repo root: python3 scripts/cleanup-journal-layout.py
"""
import re, pathlib

INDEX = pathlib.Path("journal/index.html")
FEATURED_N = 3
LABEL = {"antiparasitic": "Antiparasitic", "skin": "Skin & Hair", "hormones": "Hormones",
         "sexual": "Sexual Health", "peptides": "Peptides", "longevity": "Longevity & NAD",
         "access": "Cost & Access", "weightloss": "Weight Loss"}

def block(html, open_re):
    m = re.search(open_re, html)
    if not m:
        raise SystemExit(f"open tag not found: {open_re}")
    open_end = m.end(); depth = 1
    for tok in re.finditer(r'<div\b|</div>', html[open_end:]):
        depth += 1 if tok.group() == '<div' else -1
        if depth == 0:
            return m.start(), open_end, open_end + tok.start(), open_end + tok.end()
    raise SystemExit("unbalanced div")

def main():
    html = INDEX.read_text(encoding="utf-8")
    card_re = re.compile(r'<a\b[^>]*class="(?:feature-card|article-card)[^"]*"[^>]*>.*?</a>', re.S)

    fs, foe, fcs, fce = block(html, r'<div class="featured-grid"[^>]*>')
    as_, aoe, acs, ace = block(html, r'<div class="article-grid"[^>]*>')
    if not (fs < fcs < as_ < acs):
        raise SystemExit("unexpected grid order")

    cards = card_re.findall(html[foe:fcs]) + card_re.findall(html[aoe:acs])
    if len(cards) < 10:
        raise SystemExit(f"only found {len(cards)} cards; aborting")

    featured = cards[:FEATURED_N]
    grid = cards[FEATURED_N:]

    # featured: first is primary, others not
    def setprimary(card, primary):
        card = re.sub(r'\s*is-primary', '', card)
        if primary:
            card = re.sub(r'(class="feature-card)(")', r'\1 is-primary\2', card, count=1)
        return card
    featured = [setprimary(c.replace('article-card', 'feature-card'), i == 0) for i, c in enumerate(featured)]

    # grid: everything becomes a (small) article-card
    grid = [re.sub(r'\s*is-primary', '', c.replace('feature-card', 'article-card')) for c in grid]

    new_featured = "\n      " + "\n      ".join(featured) + "\n    "
    new_grid = "\n      " + "\n      ".join(grid) + "\n    "

    # splice (featured block first in document)
    html = (html[:foe] + new_featured + html[fcs:aoe] + new_grid + html[acs:])

    # recompute counts and rebuild chips ordered by count desc
    counts = {}
    for c in re.findall(r'data-category="([^"]+)"', html):
        counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values())
    ordered = sorted([k for k in counts], key=lambda k: -counts[k])
    chips = [f'<button class="filter-btn is-active" data-filter="all">All<span class="count">{total}</span></button>']
    for k in ordered:
        chips.append(f'<button class="filter-btn" data-filter="{k}">{LABEL.get(k,k)}<span class="count">{counts[k]}</span></button>')
    chips_html = "\n    " + "\n    ".join(chips) + "\n  "
    html = re.sub(r'(<span class="filter-label">Browse</span>).*?(\s*</div>\s*</div>)',
                  lambda m: m.group(1) + chips_html + m.group(2), html, count=1, flags=re.S)

    # id on Featured heading + hide featured section when filtering
    html = html.replace('<h2 class="section-title">Featured <span class="serif">picks</span></h2>',
                        '<h2 class="section-title" id="featHead">Featured <span class="serif">picks</span></h2>', 1)
    html = html.replace('<h2 class="section-title">Latest <span class="serif">articles</span></h2>',
                        '<h2 class="section-title">All <span class="serif">articles</span></h2>', 1)
    html = html.replace('var filter=btn.dataset.filter;',
        "var filter=btn.dataset.filter;var _ff=document.querySelector('.featured-grid'),_fh=document.getElementById('featHead'),_sf=(filter==='all');if(_ff)_ff.style.display=_sf?'':'none';if(_fh)_fh.style.display=_sf?'':'none';", 1)

    INDEX.write_text(html, encoding="utf-8")
    print(f"featured: {len(featured)}  grid: {len(grid)}  total: {total}")
    print("chip order:", [(LABEL.get(k,k), counts[k]) for k in ordered])

if __name__ == "__main__":
    main()
