#!/usr/bin/env python3
"""Add the standard inline-cta product block to journal articles that lack it,
deep-linking to the most relevant product/vertical (matches the Niagen standard).
Idempotent: skips articles that already have an inline-cta. Run from repo root.
"""
import re, glob, pathlib

ROOT = pathlib.Path(".")

# product stem -> journal slug (from link-products-to-journals.py)
PREVIEW_MAP = {
 "testosterone-cypionate":"testosterone-cypionate-trt-explained","testosterone-cream":"testosterone-cream-topical-trt",
 "testosterone-hypo-spray":"testosterone-hypo-spray-transdermal","enclomiphene":"enclomiphene-fertility-preserving-testosterone",
 "hcg":"hcg-trt-adjunct-explained","anastrozole":"anastrozole-trt-estrogen-management","estradiol-patches":"estradiol-patches-hrt-explained",
 "biest-progesterone-cream":"biest-progesterone-compounded-hrt","progesterone-capsules":"progesterone-capsules-hrt-sleep",
 "dhea-pregnenolone":"dhea-pregnenolone-adrenal-precursors","estradiol-vaginal-cream":"estradiol-vaginal-cream-gsm",
 "womens-testosterone-cream":"womens-testosterone-cream-libido","trimix":"trimix-injection-ed-rescue",
 "tadalafil-apomorphine":"tadalafil-apomorphine-dual-ed","oxytocin-nasal":"oxytocin-nasal-spray-bonding",
 "tadalafil-troches":"tadalafil-troches-sublingual-ed","sildenafil-tadalafil-gummy":"sildenafil-tadalafil-dual-gummy-ed",
 "semaglutide-odt":"semaglutide-odt-nausea-managed-oral-glp1","tirzepatide-sublingual":"tirzepatide-sublingual-drops-explained",
 "metformin-er":"metformin-er-glp1-companion","liraglutide":"liraglutide-weight-loss-glp1","nad-face-cream":"nad-face-cream-topical-longevity",
 "tretinoin":"tretinoin-retinoid-starter-guide","estriol-ghk-cu-cream":"estriol-ghk-cu-anti-aging-cream",
 "hydroquinone-triple-cream":"hydroquinone-triple-cream-hyperpigmentation","doxycycline-acne":"doxycycline-oral-acne-antibiotic",
 "bpc-157":"bpc-157-peptide-recovery-explained","tb-500":"tb-500-recovery-peptide","ghk-cu-injectable":"ghk-cu-injectable-copper-peptide",
 "pt141-strips":"pt141-bremelanotide-libido","finasteride-oral":"finasteride-oral-hair-loss-dht","naltrexone-ldn":"naltrexone-ldn-wellness-protocol",
 "clyr-tri-gel":"clyr-tri-gel-triple-therapy-acne","minoxidil":"compounded-hair-regrowth-quad-stack-men",
 "hair-spray-women":"womens-hair-regrowth-topical-stack","niagen":"niagen-nicotinamide-riboside-explained",
}
LIVE_MAP = {"tirzepatide":"semaglutide-vs-tirzepatide","semaglutide":"compounded-semaglutide-cost","pt141":"pt141-bremelanotide-libido",
 "nad":"what-is-nad-plus","sermorelin":"sermorelin-explained","glutathione":"glutathione-master-antioxidant",
 "tadalafil":"tadalafil-troches-sublingual-ed","sildenafil-gummy":"sildenafil-tadalafil-dual-gummy-ed",
 "sild-tadal-oxy":"tadalafil-apomorphine-dual-ed","zepbound":"surmount-5-deep-dive","wegovy-tablets":"semaglutide-odt-nausea-managed-oral-glp1"}

GLP_INTAKE = {"tirzepatide","semaglutide","zepbound","wegovy-tablets"}
def intake_url(stem): return (f"/intake.html?product={stem}" if stem in GLP_INTAKE else f"/intake-wellness.html?product={stem}")

# journal slug -> intake url (live preferred over preview)
SLUG_TO_URL = {}
for stem, j in PREVIEW_MAP.items(): SLUG_TO_URL.setdefault(j, intake_url(stem))
for prod, j in LIVE_MAP.items(): SLUG_TO_URL[j] = intake_url(prod)

def categorize(slug):
    t = slug.lower(); has = lambda *w: any(x in t for x in w)
    if has("ivermectin","mebendazole"): return "antiparasitic"
    if has("hair","regrowth","finasteride","minoxidil","tretinoin","acne","hydroquinone","tri-gel","doxycycline","anti-aging","face-cream"): return "skin"
    if has("testosterone","-trt","trt-","estradiol","estriol","progesterone","dhea","enclomiphene","hcg","anastrozole","biest","hormone"): return "hormones"
    if has("pt141","bremelanotide","trimix","tadalafil","sildenafil","apomorphine","oxytocin","sexual","libido","ed-rescue","dual-ed") or t.endswith("-ed"): return "sexual"
    if has("bpc-157","tb-500","ghk-cu","sermorelin","peptide","naltrexone","ldn"): return "peptides"
    if has("niagen","nmn","glutathione","longevity") or "nad" in t: return "longevity"
    if has("legitscript","certification"): return "access"
    if has("semaglutide","tirzepatide","zepbound","wegovy","glp1","glp-1","weight-loss","lipo-mino","micc","metformin","liraglutide","surmount","select-trial","plateau","foundayo"): return "weightloss"
    return "access"

# category -> (h3, p, default intake url, verb)
CTA = {
 "weightloss": ("Ready to start your weight-loss plan?", "CLYR offers compounded and brand-name GLP-1 treatments, prescribed by licensed US providers and delivered discreetly to your door.", "/intake.html?product=tirzepatide", "Start your visit"),
 "sexual": ("Want to talk to a provider about sexual health?", "CLYR offers provider-prescribed treatments for performance and libido, reviewed by licensed US clinicians and shipped discreetly.", "/intake-wellness.html?product=pt141", "Get started"),
 "hormones": ("Considering hormone therapy?", "CLYR offers provider-prescribed hormone treatments after a full medical review, with the right labs and supervision.", "/intake-wellness.html?product=testosterone-cypionate", "Get started"),
 "skin": ("Want prescription-grade skin and hair care?", "CLYR offers provider-prescribed skin and hair treatments tailored to you by a licensed US clinician.", "/intake-wellness.html?product=minoxidil", "Get started"),
 "longevity": ("Interested in a longevity protocol?", "CLYR offers NAD+ and related longevity treatments, prescribed by licensed US providers after a complete medical review.", "/intake-wellness.html?product=nad", "Get started"),
 "peptides": ("Exploring peptide therapy?", "CLYR offers provider-directed peptide protocols with honest expectations about the evidence, prescribed by licensed US clinicians.", "/intake-wellness.html?product=bpc-157", "Get started"),
 "antiparasitic": ("Want a provider-prescribed antiparasitic protocol?", "CLYR offers ivermectin protocols prescribed by licensed US providers and filled by a licensed pharmacy.", "/intake-wellness.html?product=ivermectin", "Check eligibility"),
 "access": ("Ready to get started with CLYR?", "Licensed US providers, transparent pricing, and discreet delivery. See what fits you in a quick online visit.", "/intake.html", "Start your visit"),
}
ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'

def block(slug):
    cat = categorize(slug)
    h3, p, default_url, verb = CTA[cat]
    url = SLUG_TO_URL.get(slug, default_url)
    return (f'\n<section class="inline-cta">\n  <h3>{h3}</h3>\n  <p>{p}</p>\n'
            f'  <a href="{url}">{verb}{ARROW}</a>\n</section>\n')

def main():
    added = 0; skipped = 0
    for d in sorted(glob.glob("journal/*/index.html")):
        slug = d.split("/")[1]
        html = pathlib.Path(d).read_text(encoding="utf-8")
        if 'class="inline-cta"' in html:
            skipped += 1; continue
        b = block(slug)
        # place before Sources if present, else before the related section
        for anchor in ('<div class="article-sources">', '<section class="article-related">'):
            if anchor in html:
                html = html.replace(anchor, b + anchor, 1)
                pathlib.Path(d).write_text(html, encoding="utf-8")
                added += 1
                break
        else:
            print("NO ANCHOR:", slug)
    print(f"inline-cta added: {added}  already had: {skipped}")

if __name__ == "__main__":
    main()
