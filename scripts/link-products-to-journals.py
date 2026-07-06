#!/usr/bin/env python3
"""Inject CLYR Journal deep-links on product pages that have matching articles."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "scripts" / "journal-content"

# Preview product filename stem -> journal slug
PREVIEW_MAP = {
    "testosterone-cypionate": "testosterone-cypionate-trt-explained",
    "testosterone-cream": "testosterone-cream-topical-trt",
    "testosterone-hypo-spray": "testosterone-hypo-spray-transdermal",
    "enclomiphene": "enclomiphene-fertility-preserving-testosterone",
    "hcg": "hcg-trt-adjunct-explained",
    "anastrozole": "anastrozole-trt-estrogen-management",
    "estradiol-patches": "estradiol-patches-hrt-explained",
    "biest-progesterone-cream": "biest-progesterone-compounded-hrt",
    "progesterone-capsules": "progesterone-capsules-hrt-sleep",
    "dhea-pregnenolone": "dhea-pregnenolone-adrenal-precursors",
    "estradiol-vaginal-cream": "estradiol-vaginal-cream-gsm",
    "womens-testosterone-cream": "womens-testosterone-cream-libido",
    "trimix": "trimix-injection-ed-rescue",
    "tadalafil-5mg": "tadalafil-5mg-daily-benefits",
    "tadalafil-apomorphine": "tadalafil-apomorphine-dual-ed",
    "oxytocin-nasal": "oxytocin-nasal-spray-bonding",
    "tadalafil-troches": "tadalafil-troches-sublingual-ed",
    "sildenafil-tadalafil-gummy": "sildenafil-tadalafil-dual-gummy-ed",
    "semaglutide-odt": "semaglutide-odt-nausea-managed-oral-glp1",
    "tirzepatide-sublingual": "tirzepatide-sublingual-drops-explained",
    "metformin-er": "metformin-er-glp1-companion",
    "liraglutide": "liraglutide-weight-loss-glp1",
    "nad-face-cream": "nad-face-cream-topical-longevity",
    "tretinoin": "tretinoin-retinoid-starter-guide",
    "estriol-ghk-cu-cream": "estriol-ghk-cu-anti-aging-cream",
    "hydroquinone-triple-cream": "hydroquinone-triple-cream-hyperpigmentation",
    "doxycycline-acne": "doxycycline-oral-acne-antibiotic",
    "bpc-157": "bpc-157-peptide-recovery-explained",
    "tb-500": "tb-500-recovery-peptide",
    "ghk-cu-injectable": "ghk-cu-injectable-copper-peptide",
    "pt141-strips": "pt141-bremelanotide-libido",
    "finasteride-oral": "finasteride-oral-hair-loss-dht",
    "naltrexone-ldn": "naltrexone-ldn-wellness-protocol",
    "clyr-tri-gel": "clyr-tri-gel-triple-therapy-acne",
    "minoxidil": "compounded-hair-regrowth-quad-stack-men",
    "hair-spray-women": "womens-hair-regrowth-topical-stack",
    "niagen": "niagen-nicotinamide-riboside-explained",
}

# Live root-level product pages
LIVE_MAP = {
    "tirzepatide": "semaglutide-vs-tirzepatide",
    "semaglutide": "compounded-semaglutide-cost",
    "pt141": "pt141-bremelanotide-libido",
    "nad": "what-is-nad-plus",
    "sermorelin": "sermorelin-explained",
    "glutathione": "glutathione-master-antioxidant",
    "tadalafil": "tadalafil-troches-sublingual-ed",
    "sildenafil-gummy": "sildenafil-tadalafil-dual-gummy-ed",
    "sild-tadal-oxy": "tadalafil-apomorphine-dual-ed",
    "zepbound": "surmount-5-deep-dive",
    "wegovy-tablets": "semaglutide-odt-nausea-managed-oral-glp1",
}

MARKER = 'class="journal-guide"'


def journal_meta(slug: str) -> tuple[str, str]:
    path = CONTENT / f"{slug}.json"
    if path.exists():
        c = json.loads(path.read_text(encoding="utf-8"))
        return c["title"], c.get("deck", "")
    html = ROOT / "journal" / slug / "index.html"
    if html.exists():
        text = html.read_text(encoding="utf-8")
        t = re.search(r"<title>([^<|]+)", text)
        d = re.search(r'<meta name="description" content="([^"]*)"', text)
        return (
            (t.group(1).strip() if t else slug),
            (d.group(1) if d else ""),
        )
    return slug.replace("-", " ").title(), ""


def guide_block(slug: str) -> str:
    title, deck = journal_meta(slug)
    deck = deck[:180] + ("…" if len(deck) > 180 else "")
    url = f"/journal/{slug}/"
    return f'''<section class="journal-guide" style="padding:48px 40px;max-width:900px;margin:0 auto">
  <div style="background:linear-gradient(135deg,#f0fafb 0%,#e8f4f8 100%);border:1px solid #E2E7EB;border-radius:16px;padding:32px 36px">
    <div class="section-label">CLYR Journal</div>
    <h2 class="section-heading" style="font-size:28px;margin-bottom:10px">Want the <span class="serif">full clinical guide?</span></h2>
    <p style="font-size:16px;color:#6B7C8A;line-height:1.6;margin-bottom:20px"><strong style="color:#1A1A1A;font-weight:600">{title}</strong>{(" — " + deck) if deck else ""}</p>
    <a href="{url}" style="display:inline-flex;align-items:center;gap:8px;color:#00B4C5;font-weight:600;text-decoration:none;font-size:15px">Read the article &rarr;</a>
  </div>
</section>
'''


def inject(path: Path, journal_slug: str) -> bool:
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return False
    if f'/journal/{journal_slug}/' in html:
        return False
    block = guide_block(journal_slug)
    for anchor in ('<section class="faq">', '<section class="faq"'):
        if anchor in html:
            html = html.replace(anchor, block + anchor, 1)
            path.write_text(html, encoding="utf-8")
            return True
    return False


def main():
    n = 0
    for stem, jslug in PREVIEW_MAP.items():
        path = ROOT / "preview" / "products" / f"{stem}.html"
        if path.exists() and inject(path, jslug):
            print(f"✓ preview/products/{stem}.html → /journal/{jslug}/")
            n += 1
    for stem, jslug in LIVE_MAP.items():
        path = ROOT / f"{stem}.html"
        if path.exists() and inject(path, jslug):
            print(f"✓ {stem}.html → /journal/{jslug}/")
            n += 1
    print(f"\nLinked {n} product pages to journal articles")


if __name__ == "__main__":
    main()