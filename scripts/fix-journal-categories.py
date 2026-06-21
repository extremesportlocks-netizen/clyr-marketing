#!/usr/bin/env python3
"""Fix journal index categorization:
 1) Re-tag every card's data-category to its true topic (by slug).
 2) Normalize the visible category label to match.
 3) Rebuild the Browse filter chips for the full taxonomy with DYNAMIC counts.
 4) Make the category filter act on ALL cards (feature + article), not just the 14 article-cards.
Run from repo root: python3 scripts/fix-journal-categories.py
"""
import re, pathlib

INDEX = pathlib.Path("journal/index.html")

# (key, label) — order matters; first match wins
CATS = [
    ("antiparasitic", "Antiparasitic"),
    ("skin",          "Skin & Hair"),
    ("hormones",      "Hormones"),
    ("sexual",        "Sexual Health"),
    ("peptides",      "Peptides"),
    ("longevity",     "Longevity & NAD"),
    ("access",        "Cost & Access"),
    ("weightloss",    "Weight Loss"),
]
LABEL = dict(CATS)

def categorize(slug):
    t = slug.lower()
    has = lambda *w: any(x in t for x in w)
    if has("ivermectin", "mebendazole", "antiparasitic"): return "antiparasitic"
    if has("hair", "regrowth", "finasteride", "minoxidil", "tretinoin", "acne",
           "hydroquinone", "tri-gel", "doxycycline", "anti-aging", "face-cream"): return "skin"
    if has("testosterone", "-trt", "trt-", "estradiol", "estriol", "progesterone",
           "dhea", "enclomiphene", "hcg", "anastrozole", "biest", "hormone"): return "hormones"
    if (has("pt141", "bremelanotide", "trimix", "tadalafil", "sildenafil", "apomorphine",
            "oxytocin", "sexual", "libido", "ed-rescue", "dual-ed") or t.endswith("-ed")): return "sexual"
    if has("bpc-157", "tb-500", "ghk-cu", "sermorelin", "peptide", "naltrexone", "ldn"): return "peptides"
    if has("niagen", "nmn", "glutathione", "longevity") or "nad" in t: return "longevity"
    if has("legitscript", "certification"): return "access"
    if has("semaglutide", "tirzepatide", "zepbound", "wegovy", "glp1", "glp-1", "weight-loss",
           "lipo-mino", "micc", "metformin", "liraglutide", "surmount", "select-trial",
           "plateau", "foundayo"): return "weightloss"
    if has("cost", "near-me", "telehealth", "how-it-works", "price", "insurance"): return "access"
    return "access"

def main():
    html = INDEX.read_text(encoding="utf-8")
    counts = {k: 0 for k, _ in CATS}
    dist = []

    card_re = re.compile(r'(<a\b[^>]*class="(?:feature-card|article-card)[^"]*"[^>]*>)(.*?)(</a>)', re.S)
    def fix(m):
        opentag, inner, close = m.group(1), m.group(2), m.group(3)
        hm = re.search(r'href="/journal/([^/"]+)/?"', opentag)
        slug = hm.group(1) if hm else ""
        key = categorize(slug)
        counts[key] += 1
        dist.append((slug, key))
        # set data-category on the <a>
        if re.search(r'data-category="[^"]*"', opentag):
            opentag = re.sub(r'data-category="[^"]*"', f'data-category="{key}"', opentag)
        else:
            opentag = opentag[:-1] + f' data-category="{key}">'
        # normalize the visible label
        inner = re.sub(r'(class="(?:feature|article)-card-cat">)[^<]*(</div>)',
                       lambda im: im.group(1) + LABEL[key] + im.group(2), inner, count=1)
        return opentag + inner + close
    html = card_re.sub(fix, html)

    # rebuild Browse chips with dynamic counts (only categories that have articles)
    total = sum(counts.values())
    chips = [f'<button class="filter-btn is-active" data-filter="all">All<span class="count">{total}</span></button>']
    for key, label in CATS:
        if counts[key]:
            chips.append(f'<button class="filter-btn" data-filter="{key}">{label}<span class="count">{counts[key]}</span></button>')
    chips_html = "\n    " + "\n    ".join(chips) + "\n  "
    # replace everything between the Browse label and the closing of filter-inner
    html = re.sub(r'(<span class="filter-label">Browse</span>).*?(\s*</div>\s*</div>)',
                  lambda m: m.group(1) + chips_html + m.group(2), html, count=1, flags=re.S)

    # make the filter act on ALL cards, and ensure feature-cards can hide
    html = html.replace(
        "var articleCards=document.querySelectorAll('.article-grid .article-card');",
        "var articleCards=document.querySelectorAll('.feature-card, .article-grid .article-card');")
    if ".feature-card.is-hidden" not in html:
        html = html.replace(".article-card.is-hidden{",
                            ".feature-card.is-hidden{display:none!important}\n.article-card.is-hidden{")

    INDEX.write_text(html, encoding="utf-8")
    print("category counts:", {LABEL[k]: counts[k] for k, _ in CATS if counts[k]})
    print("total cards:", total)

if __name__ == "__main__":
    main()
