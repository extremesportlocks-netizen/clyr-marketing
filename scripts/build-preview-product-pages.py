#!/usr/bin/env python3
"""
Build polished CLYR preview product pages to the Niagen gold standard.

Reuses the niagen.html boilerplate VERBATIM (head styles, megamenu nav, Quality &
Safety, How It Works, footer, scripts) by extracting those chunks at runtime, and
injects hand-authored, PATIENT-FACING content per SKU. No wholesale language, no
"Pharmacy SKU", no pricing-framework links. Preview pages stay noindex,nofollow.

Only writes the slugs present in CONTENT, so the 4 already-polished pages
(niagen, clyr-tri-gel, minoxidil, hair-spray-women) are never touched.

Run:  python3 scripts/build-preview-product-pages.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "preview" / "products"
GOLD = PRODUCTS / "niagen.html"

src = GOLD.read_text(encoding="utf-8")

def cut(start_marker, end_marker, *, include_end=True, after=0):
    i = src.index(start_marker, after)
    j = src.index(end_marker, i) + (len(end_marker) if include_end else 0)
    return src[i:j], j

# ── Reusable verbatim chunks from the gold standard ──
HEAD_OPEN = src[src.index("<!DOCTYPE"):src.index("<title>")]                 # doctype..viewport (GTM, favicons, robots noindex)
FONTS_STYLE = src[src.index('<link rel="preconnect"'):src.index("</head>")] # preconnect, fonts, product-page.css, full <style> blocks
NAV, nav_end = cut('<nav class="nav"', "</nav>")
QUALITY, _ = cut('<section class="quality">', "</section>")
HOW, _ = cut('<section class="how-it-works">', "</section>")
HOW = HOW.replace("injectable Niagen is appropriate for you", "this treatment is appropriate for you")
FOOTER, _ = cut('<footer class="footer">', "</footer>")
SCRIPTS = src[src.index("<script>\nfunction toggleFaq"):src.index("</html>") + len("</html>")]

for name, chunk in [("HEAD_OPEN", HEAD_OPEN), ("FONTS_STYLE", FONTS_STYLE), ("NAV", NAV),
                    ("QUALITY", QUALITY), ("HOW", HOW), ("FOOTER", FOOTER), ("SCRIPTS", SCRIPTS)]:
    if not chunk or len(chunk) < 40:
        sys.exit(f"FATAL: failed to extract {name} from niagen.html")

CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>'
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'

# Six reusable benefit icons (path d only) cycled across the 6 benefit cards.
BICONS = [
    'M13 2 3 14h9l-1 8 10-12h-9l1-8z',
    'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
    'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z',
    'M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 14a4 4 0 1 1 4-4 4 4 0 0 1-4 4z',
    'M18 20V10M12 20V4M6 20v-6',
    'M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11',
]
ICON_WI = [  # what's-included icons
    'M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z',
    'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l9.84-9.84a5.5 5.5 0 0 0-1-6.78z',
    'M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
    'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0zM12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
]

def benefits_html(items):
    cards = []
    for i, (h, p) in enumerate(items):
        cards.append(f'    <div class="benefit-card"><div class="benefit-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{BICONS[i%len(BICONS)]}"/></svg></div><h3>{h}</h3><p>{p}</p></div>')
    return "\n".join(cards)

def includes_html(items):
    return "\n".join(f'      <div class="product-includes-item">{CHECK}{t}</div>' for t in items)

def wi_html(items):
    out = []
    for i, (h, p) in enumerate(items):
        out.append(f'''      <div class="included-item">
        <div class="icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="{ICON_WI[i%len(ICON_WI)]}"/></svg></div>
        <div><h4>{h}</h4><p>{p}</p></div>
      </div>''')
    return "\n".join(out)

def faq_html(items, name):
    plus = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'
    return "\n".join(f'  <div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">{q}{plus}</button><div class="faq-a"><p>{a}</p></div></div>' for q, a in items)

def nav_for(hub):
    n = NAV.replace('class="nav-item nav-active" data-nav="daily-wellness"', 'class="nav-item" data-nav="daily-wellness"')
    n = n.replace(f'class="nav-item" data-nav="{hub}"', f'class="nav-item nav-active" data-nav="{hub}"', 1)
    return n

def page(c):
    slug = c["slug"]
    hero = c.get("hero_img", f"/preview/assets/heroes/{slug}.png")
    head_meta = (
        f'<title>{c["title_plain"]} | CLYR Health</title>\n'
        f'<meta name="description" content="{c["meta_desc"]}">\n'
        f'<meta property="og:title" content="{c["title_plain"]} | CLYR Health">\n'
        f'<meta property="og:description" content="{c["meta_desc"]}">\n'
        f'<meta property="og:type" content="website">\n'
        f'<meta property="og:url" content="https://www.clyr.health/preview/products/{slug}.html">\n'
        f'<meta property="og:image" content="https://www.clyr.health/preview/assets/cards/{slug}.png">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:image" content="https://www.clyr.health/preview/assets/cards/{slug}.png">\n'
        f'<link rel="canonical" href="https://www.clyr.health/preview/products/{slug}.html">\n'
    )
    return f'''{HEAD_OPEN}{head_meta}{FONTS_STYLE}</head>
<body>
<div class="preview-strip">Preview — pricing confirmed at consultation. <a href="/intake-wellness.html?product={c["intake"]}">Join waitlist</a></div>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-T4FVQ87G"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

{nav_for(c["hub"])}

<div class="breadcrumb">
  <a href="/">CLYR Health</a> &nbsp;/&nbsp; <a href="{c["hub_url"]}">{c["hub_name"]}</a> &nbsp;/&nbsp; {c["title_plain"]}
</div>

<section class="product-hero">
  <div class="product-image"><div class="product-badge">{c["badge"]}</div><img src="{hero}" alt="{c["title_plain"]}" style="width:88%;height:88%;object-fit:contain;display:block;filter:drop-shadow(0 18px 40px rgba(0,0,0,0.15))" loading="lazy"></div>
  <div class="product-info">
    <div class="product-category">{c["category"]}</div>
    <h1 class="product-title">{c["title_html"]}</h1>
    <p class="product-subtitle">{c["subtitle"]}</p>
    <div class="product-price price-tbd">
      <span class="amount">Pricing at consultation</span>
    </div>
    <p class="product-price-note">Your provider confirms final pricing after review. Provider consultation and free shipping included.</p>
    <a href="/intake-wellness.html?product={c["intake"]}" class="product-cta">
      Join the waitlist
      {ARROW}
    </a>
    <div class="product-includes">
{includes_html(c["includes"])}
    </div>
  </div>
</section>

<section class="benefits">
  <div class="section-label">Benefits</div>
  <h2 class="section-heading">{c["benefits_heading"]}</h2>
  <p class="section-sub">{c["benefits_sub"]}</p>
  <div class="benefits-grid">
{benefits_html(c["benefits"])}
  </div>
</section>

<section class="included">
  <div class="included-inner">
    <div>
      <div class="section-label">What's Included</div>
      <h2 class="section-heading">Everything you need,<br><span class="serif">delivered.</span></h2>
      <p class="section-sub">Every plan includes the medication, provider consultation, ongoing care, and shipping. No hidden fees. Longer plans lower your monthly rate.</p>
    </div>
    <div class="included-list">
{wi_html(c["whats_included"])}
    </div>
  </div>
</section>

{QUALITY}

{HOW}

<section class="faq">
  <div class="section-label" style="display:flex;justify-content:center;">Frequently Asked</div>
  <h2 class="section-heading" style="text-align:center">{c["faq_heading"]}</h2>
{faq_html(c["faq"], c["title_plain"])}
</section>

<section class="isi-banner">
  <div class="isi-inner">
    <h3>Important Safety Information</h3>
    <p>{c["isi"]}</p>
  </div>
</section>

<section class="cta-section">
  <h2>{c["cta_heading"]}</h2>
  <p>Complete your consultation in about 5 minutes. If approved, your medication ships within days.</p>
  <a href="/intake-wellness.html?product={c["intake"]}" class="cta-btn">Join the waitlist<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></a>
</section>

{FOOTER}

{SCRIPTS}
'''

# ── Shared what's-included templates by delivery form ──
def wi_topical(med):
    return [(med, "Compounded by a licensed US pharmacy to a consistent, labeled strength."),
            ("Simple daily routine", "Applied at home in seconds, with provider guidance on how and when to use it."),
            ("Provider consultation", "A licensed provider reviews your profile and prescribes the appropriate formulation."),
            ("Free discreet shipping", "Plain, tracked packaging delivered to your door.")]
def wi_oral(med):
    return [(med, "Compounded or dispensed by a licensed US pharmacy, labeled with your name and prescriber."),
            ("Easy oral dosing", "Taken at home per your provider's instructions. No injections, no clinic visits."),
            ("Provider consultation", "A licensed provider reviews your profile and prescribes the appropriate dose."),
            ("Free discreet shipping", "Plain, tracked packaging delivered to your door.")]

inc_topical = lambda med: [f"{med}, compounded by a licensed US pharmacy",
                           "Applicator and clear usage instructions included",
                           "Licensed provider consultation included",
                           "Free discreet shipping", "Ongoing provider care and refill management"]
inc_oral = lambda med: [f"{med}, dispensed by a licensed US pharmacy",
                        "No needles, simple oral dosing",
                        "Licensed provider consultation included",
                        "Free discreet shipping", "Ongoing provider care and refill management"]

def wi_inject(med):
    return [(med, "Compounded by a licensed US pharmacy to a consistent, labeled strength."),
            ("Injection supplies", "Syringes and alcohol pads included for easy self-administration."),
            ("Provider consultation", "A licensed provider reviews your profile and prescribes the appropriate dose."),
            ("Free discreet shipping", "Plain, tracked packaging delivered to your door. Cold-chain when required.")]
inc_inject = lambda med: [f"{med}, compounded by a licensed US pharmacy",
                          "Syringes and alcohol pads included",
                          "Licensed provider consultation included",
                          "Free discreet shipping", "Ongoing provider care and dose management"]

SKIN  = dict(hub="skin-hair",       hub_name="Skin & Hair",     hub_url="/preview/hubs/skin-hair.html")
MENS  = dict(hub="mens-hormone",    hub_name="Men's Hormone",   hub_url="/preview/hubs/mens-hormone.html")
WOMEN = dict(hub="womens-hormone",  hub_name="Women's Hormone", hub_url="/preview/hubs/womens-hormone.html")
WL    = dict(hub="weight-loss",     hub_name="Weight Loss",     hub_url="/weight-loss.html")
SEX   = dict(hub="sexual-health",   hub_name="Sexual Health",   hub_url="/sexual-health.html")
WELL  = dict(hub="daily-wellness",  hub_name="Daily Wellness",  hub_url="/daily-wellness.html")

# ════════════════════════════════════════════════════════════════════
# WAVE 1 — Skin & Hair (6)
# ════════════════════════════════════════════════════════════════════
CONTENT = [
  dict(**SKIN, slug="nad-face-cream", intake="nad_face_cream",
    title_plain="NAD+ Face Cream", title_html='NAD+ Face <span class="serif">Cream</span>',
    badge="10% NAD+", category="Skin & Hair · Anti-Aging",
    meta_desc="Compounded 10% NAD+ topical face cream. Prescribed by licensed providers after medical review.",
    subtitle='A <strong>10% NAD+ pump face cream</strong> that delivers nicotinamide directly to the skin. A topical companion to CLYR\'s injectable <a href="/nad.html" style="color:var(--teal);font-weight:600">NAD+</a> and <a href="/preview/products/niagen.html" style="color:var(--teal);font-weight:600">Niagen</a> line, formulated for a simple once-daily routine.',
    includes=inc_topical("10% NAD+ face cream"),
    benefits_heading='Topical support for<br>skin <span class="serif">vitality.</span>',
    benefits_sub="NAD+ is a coenzyme central to how skin cells produce energy and manage repair. Here is what the cream is formulated to do, described in mechanism terms.",
    benefits=[("Topical NAD+ delivery","Applies nicotinamide directly to the skin as part of a daily skincare step."),
              ("Antioxidant environment","NAD+-related pathways are tied to how cells handle oxidative stress."),
              ("Supports the skin barrier","Formulated to sit comfortably in a daily moisturizing routine."),
              ("Pairs with your longevity stack","A topical complement to injectable NAD+ and Niagen for patients already focused on cellular health."),
              ("Once-daily simplicity","One pump-cream step, designed to be easy to stay consistent with."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent, labeled strength.")],
    whats_included=wi_topical("10% NAD+ face cream"),
    faq_heading='Questions about<br><span class="serif">NAD+ cream?</span>',
    faq=[("What is NAD+ face cream?","A compounded topical cream containing nicotinamide (a form of vitamin B3 tied to the NAD+ pathway), formulated for daily application to the face."),
         ("How is it different from NAD+ injections?","Injections deliver NAD+ or its precursors systemically. This cream is a topical, applied to the skin as part of a skincare routine. Many patients use them as complements."),
         ("How do I use it?","Typically one application to clean, dry skin per your provider's guidance. A patch test on a small area first is sensible for any new topical."),
         ("When might I notice anything?","Topical skincare changes are gradual and vary from person to person. Consistency over weeks matters more than any single application."),
         ("Who should not use it?","Avoid on broken or irritated skin and if you have a known sensitivity to any ingredient. Tell your provider if you are pregnant or breastfeeding so they can advise.")],
    isi="NAD+ face cream is a prescription, compounded topical product. These statements have not been evaluated by the Food and Drug Administration, and this product is not intended to diagnose, treat, cure, or prevent any disease. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. For external use only; avoid the eyes and broken skin, and stop use if irritation develops. Inform your provider of all medications, allergies, and conditions, including pregnancy or breastfeeding. The decision to begin any compounded medication should be made with a licensed provider who knows your full history. Individual results may vary.",
    cta_heading='Interested in topical<br><span class="serif">NAD+?</span>'),

  dict(**SKIN, slug="tretinoin", intake="tretinoin",
    title_plain="Tretinoin Cream", title_html='Tretinoin <span class="serif">Cream</span>',
    badge="Retinoid", category="Skin & Hair · Anti-Aging",
    meta_desc="Prescription tretinoin cream for skin renewal and acne maintenance. Prescribed by licensed providers after review.",
    subtitle='Prescription <strong>tretinoin</strong>, a vitamin A-derived retinoid that increases skin-cell turnover. A long-standing dermatology staple for photoaging and acne maintenance, dosed and ramped under provider guidance.',
    includes=inc_topical("Compounded tretinoin cream"),
    benefits_heading='The retinoid<br>dermatology <span class="serif">relies on.</span>',
    benefits_sub="Tretinoin works by accelerating how quickly skin cells turn over. Here is how it is used, in mechanism terms, with the ramp-up your provider will guide.",
    benefits=[("Accelerates cell turnover","Tretinoin speeds the rate at which surface skin cells are replaced."),
              ("Supports collagen pathways","Retinoids are tied to the skin's collagen-remodeling processes over time."),
              ("Acne maintenance","Helps keep pores clear as part of a longer-term routine."),
              ("Texture and tone","Used to smooth texture and even the look of tone with consistent use."),
              ("Prescription strength","A true prescription retinoid, not an over-the-counter retinol."),
              ("Provider-guided ramp","Started low and slow to limit irritation while your skin adjusts.")],
    whats_included=wi_topical("Compounded tretinoin cream"),
    faq_heading='Questions about<br><span class="serif">tretinoin?</span>',
    faq=[("What is tretinoin?","A prescription topical retinoid (a vitamin A derivative) used for skin renewal and acne maintenance."),
         ("How do I use it?","Usually a pea-sized amount at night on clean, dry skin, starting a few nights per week and building up as tolerated. Your provider will set your schedule."),
         ("Will my skin get worse first?","An adjustment period with dryness, flaking, or temporary breakouts is common in the first weeks. Going slow and moisturizing helps."),
         ("Do I need sunscreen?","Yes. Retinoids increase sun sensitivity, so daily broad-spectrum SPF is important while using tretinoin."),
         ("Who should not use it?","Tretinoin should not be used during pregnancy or while trying to conceive, or while breastfeeding. Tell your provider about any skin conditions or medications.")],
    isi="Tretinoin is a prescription, compounded topical retinoid. These statements have not been evaluated by the Food and Drug Administration. Tretinoin should not be used during pregnancy, while trying to conceive, or while breastfeeding. It increases sensitivity to sunlight; use daily broad-spectrum sunscreen and limit sun exposure. For external use only; expect an adjustment period and avoid the eyes, mouth, and broken skin. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Inform your provider of all medications, allergies, and conditions. The decision to begin any prescription medication should be made with a licensed provider. Individual results may vary.",
    cta_heading='Ready for a<br><span class="serif">retinoid?</span>'),

  dict(**SKIN, slug="doxycycline-acne", intake="doxycycline_acne",
    title_plain="Doxycycline (Acne)", title_html='Doxycycline <span class="serif">for Acne</span>',
    badge="Oral", category="Skin & Hair · Acne",
    meta_desc="Oral doxycycline for moderate inflammatory acne, prescribed by licensed providers after medical review.",
    subtitle='Oral <strong>doxycycline</strong>, a tetracycline-class antibiotic with anti-inflammatory properties used for moderate inflammatory acne. Often paired with a topical routine such as <a href="/preview/products/clyr-tri-gel.html" style="color:var(--teal);font-weight:600">CLYR Tri Gel</a> for a complete plan.',
    includes=inc_oral("Doxycycline capsules"),
    benefits_heading='Systemic support for<br>inflammatory <span class="serif">acne.</span>',
    benefits_sub="Doxycycline addresses acne from the inside, with both antibacterial and anti-inflammatory actions. Here is how it fits a provider-guided plan.",
    benefits=[("Targets acne-associated bacteria","Doxycycline acts on bacteria involved in inflammatory acne."),
              ("Anti-inflammatory action","Tetracyclines also calm the inflammation behind red, painful breakouts."),
              ("For moderate cases","A systemic option when topicals alone are not enough."),
              ("Pairs with a topical stack","Designed to work alongside a topical routine for fuller coverage."),
              ("Defined course","Used as a time-limited course with antibiotic stewardship in mind."),
              ("Provider-monitored","Your provider reviews suitability, duration, and a step-down plan.")],
    whats_included=wi_oral("Doxycycline capsules"),
    faq_heading='Questions about<br><span class="serif">doxycycline?</span>',
    faq=[("What is doxycycline?","An oral tetracycline-class antibiotic used, among other things, for moderate inflammatory acne because it is both antibacterial and anti-inflammatory."),
         ("How do I take it?","With a full glass of water, staying upright for a while afterward, per your provider's directions. Avoid taking it at the same time as dairy, antacids, or iron, which can reduce absorption."),
         ("How long will I take it?","Antibiotics for acne are typically used as a defined course alongside a topical routine, then stepped down. Your provider sets the plan."),
         ("Does it affect sun exposure?","Yes, doxycycline can increase sun sensitivity. Use sunscreen and limit prolonged sun exposure while taking it."),
         ("Who should not take it?","It is not for use in pregnancy, breastfeeding, or in young children. Tell your provider about all medications, allergies, and conditions before starting.")],
    isi="Doxycycline is a prescription antibiotic. These statements have not been evaluated by the Food and Drug Administration. Doxycycline should not be used during pregnancy or breastfeeding or in children under 8 years. It can increase sensitivity to sunlight; use sunscreen and limit sun exposure. Take with adequate fluid and remain upright afterward to reduce the risk of throat irritation. Antibiotics should be used only as prescribed; overuse contributes to antibiotic resistance. Inform your provider of all medications, allergies, and conditions. The decision to begin any prescription medication should be made with a licensed provider. Individual results may vary.",
    cta_heading='Tackle acne<br><span class="serif">from within?</span>'),

  dict(**SKIN, slug="finasteride-oral", intake="finasteride_oral",
    title_plain="Finasteride (Oral)", title_html='Finasteride <span class="serif">Oral</span>',
    badge="DHT Block", category="Skin & Hair · Hair",
    meta_desc="Oral finasteride for male pattern hair loss, prescribed by licensed providers after medical review.",
    subtitle='Oral <strong>finasteride 1mg</strong>, a 5-alpha-reductase inhibitor that lowers scalp DHT, the hormone most associated with male pattern hair loss. A once-daily tablet that pairs well with topical regrowth routines.',
    includes=inc_oral("Finasteride 1mg tablets"),
    benefits_heading='Address hair loss<br>at the <span class="serif">source.</span>',
    benefits_sub="Finasteride works upstream by reducing DHT, the hormone tied to follicle miniaturization in male pattern hair loss. Here is how it is used.",
    benefits=[("Reduces scalp DHT","Finasteride inhibits the enzyme that converts testosterone to DHT."),
              ("Once-daily tablet","A simple, consistent oral routine."),
              ("Pairs with topicals","Often combined with topical regrowth sprays for a layered approach."),
              ("Maintenance-focused","Most useful for slowing loss and holding ground over time."),
              ("Provider-supervised","Reviewed for suitability, with side effects discussed up front."),
              ("Consistency matters","Benefits depend on continued daily use and fade if stopped.")],
    whats_included=wi_oral("Finasteride 1mg tablets"),
    faq_heading='Questions about<br><span class="serif">finasteride?</span>',
    faq=[("What is finasteride?","An oral prescription medication that lowers DHT, a hormone involved in male pattern hair loss, by inhibiting the 5-alpha-reductase enzyme."),
         ("How long until I notice anything?","Hair changes are slow. Most protocols are evaluated over several months of daily use, and results vary between individuals."),
         ("What are the possible side effects?","A minority of men report sexual side effects such as changes in libido or function. Discuss these honestly with your provider before starting, and report any that occur."),
         ("What happens if I stop?","Any benefit is maintained only with continued use. Stopping generally leads to a return of the prior pattern over time."),
         ("Who should not take it?","Finasteride is for men. It must not be used or handled by women who are or may become pregnant, as it can affect a developing fetus. It can also affect PSA testing; tell your provider you take it.")],
    isi="Finasteride is a prescription medication for men. These statements have not been evaluated by the Food and Drug Administration. Finasteride must not be used by women, and women who are or may become pregnant should not handle crushed or broken tablets, as the drug can harm a developing male fetus. Some men report sexual side effects; report any changes to your provider. Finasteride lowers PSA levels, which can affect prostate cancer screening, so inform any provider ordering that test. Inform your provider of all medications and conditions. The decision to begin any prescription medication should be made with a licensed provider. Individual results may vary.",
    cta_heading='Ready to protect<br>your <span class="serif">hair?</span>'),

  dict(**SKIN, slug="hydroquinone-triple-cream", intake="hydroquinone_triple_cream",
    title_plain="Hydroquinone Triple Cream", title_html='Hydroquinone <span class="serif">Triple Cream</span>',
    badge="Brightening", category="Skin & Hair · Pigmentation",
    meta_desc="Compounded hydroquinone, tretinoin, and fluocinolone cream for hyperpigmentation, prescribed after provider review.",
    subtitle='A compounded <strong>hydroquinone, tretinoin, and fluocinolone</strong> triple cream, a dermatology-grade approach to melasma and stubborn hyperpigmentation. Used as a short, provider-guided course.',
    includes=inc_topical("Hydroquinone triple cream"),
    benefits_heading='A focused approach to<br>uneven <span class="serif">pigment.</span>',
    benefits_sub="Three complementary actives target excess pigment from different angles. Here is the role each plays, used under provider supervision.",
    benefits=[("Targets excess pigment","Hydroquinone acts on the pathway that produces melanin in the skin."),
              ("Three complementary actives","Pairs a brightening agent, a retinoid, and a mild corticosteroid."),
              ("For melasma and dark spots","A prescription-grade option for stubborn discoloration."),
              ("Short, defined course","Used in cycles rather than continuously, per dermatology practice."),
              ("Prescription-grade","Compounded by a licensed US pharmacy, not an OTC brightener."),
              ("Provider-guided","Your provider sets the schedule, sun protection, and stopping points.")],
    whats_included=wi_topical("Hydroquinone triple cream"),
    faq_heading='Questions about<br><span class="serif">the triple cream?</span>',
    faq=[("What is in the triple cream?","A compounded combination of hydroquinone (a pigment-lightening agent), tretinoin (a retinoid), and fluocinolone (a mild corticosteroid)."),
         ("How do I use it?","Usually a thin layer at night for a defined period set by your provider, rather than indefinitely. Daily sunscreen is essential during and after."),
         ("Why is sun protection so important?","Sun exposure drives pigmentation and can undo progress. Broad-spectrum SPF and sun avoidance are part of the protocol."),
         ("How long is a course?","Hydroquinone is typically used in time-limited cycles. Your provider will tell you when to pause and reassess."),
         ("Who should not use it?","Avoid during pregnancy or breastfeeding (it contains a retinoid), and on broken or irritated skin. Patch testing and provider guidance are advised.")],
    isi="This is a prescription, compounded topical containing hydroquinone, tretinoin, and fluocinolone. These statements have not been evaluated by the Food and Drug Administration. It should not be used during pregnancy, while trying to conceive, or while breastfeeding. It increases sun sensitivity; use daily broad-spectrum sunscreen. Hydroquinone is intended for time-limited use, and the corticosteroid component is not for prolonged continuous application; follow your provider's schedule. For external use only; avoid the eyes and broken skin. Compounded medications are not FDA-approved. Inform your provider of all medications, allergies, and conditions. Individual results may vary.",
    cta_heading='Even out<br><span class="serif">your tone?</span>'),

  dict(**SKIN, slug="estriol-ghk-cu-cream", intake="estriol_ghk_cu_cream",
    title_plain="Estriol + GHK-Cu Cream", title_html='Estriol + <span class="serif">GHK-Cu Cream</span>',
    badge="Peptide", category="Skin & Hair · Anti-Aging",
    meta_desc="Compounded estriol, niacinamide, GHK-Cu, and hyaluronic acid anti-aging cream, prescribed after provider review.",
    subtitle='A compounded <strong>estriol, niacinamide, GHK-Cu, and hyaluronic acid</strong> cream, a four-ingredient topical that brings a copper peptide, a barrier-supporting vitamin, a humectant, and topical estriol into one anti-aging step.',
    includes=inc_topical("Estriol + GHK-Cu cream"),
    benefits_heading='Four actives,<br>one <span class="serif">routine.</span>',
    benefits_sub="Each ingredient plays a distinct role in the skin. Here is what each contributes, in a compounded cream used under provider guidance.",
    benefits=[("Copper peptide (GHK-Cu)","GHK-Cu is a copper-binding peptide associated with skin remodeling pathways."),
              ("Hydration with hyaluronic acid","A humectant that helps the skin hold moisture."),
              ("Niacinamide for the barrier","Vitamin B3 is tied to skin-barrier support and a calmer complexion."),
              ("Topical estriol","A gentle estrogen used topically as part of a compounded anti-aging formula."),
              ("One simple step","Four actives delivered together to keep the routine easy."),
              ("Compounded to order","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Estriol + GHK-Cu cream"),
    faq_heading='Questions about<br><span class="serif">the cream?</span>',
    faq=[("What is in this cream?","A compounded blend of estriol (a topical estrogen), niacinamide (vitamin B3), GHK-Cu (a copper peptide), and hyaluronic acid (a humectant)."),
         ("How do I use it?","Applied to clean skin per your provider's directions, usually once daily. A patch test first is sensible for any new topical."),
         ("Does it contain a hormone?","Yes, estriol is a form of estrogen used here topically. Because of that, a provider reviews your history before prescribing."),
         ("When might I notice anything?","Topical skincare results are gradual and vary by person. Consistency over weeks matters most."),
         ("Who should not use it?","Because it contains estriol, it is generally avoided in pregnancy, breastfeeding, and with hormone-sensitive conditions. Tell your provider your full history.")],
    isi="This is a prescription, compounded topical containing estriol (an estrogen), niacinamide, GHK-Cu, and hyaluronic acid. These statements have not been evaluated by the Food and Drug Administration. Because it contains a hormone, it is generally avoided during pregnancy or breastfeeding and in individuals with hormone-sensitive conditions; a licensed provider reviews your history before prescribing. For external use only; avoid the eyes and broken skin, and stop use if irritation develops. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Inform your provider of all medications, allergies, and conditions. Individual results may vary.",
    cta_heading='Build a smarter<br><span class="serif">routine?</span>'),

  # ════════ WAVE 2 — Men's Hormone (6) ════════
  dict(**MENS, slug="testosterone-cypionate", intake="testosterone_cypionate",
    title_plain="Testosterone Cypionate", title_html='Testosterone <span class="serif">Cypionate</span>',
    badge="TRT", category="Men's Hormone · TRT",
    meta_desc="Injectable testosterone cypionate for clinically low testosterone, prescribed and lab-monitored by licensed providers.",
    subtitle='Injectable <strong>testosterone cypionate</strong> for men with clinically low testosterone confirmed on labs. A long-established TRT option, dosed on a weekly or biweekly schedule with provider supervision and ongoing monitoring.',
    includes=inc_inject("Testosterone cypionate"),
    benefits_heading='Hormone therapy,<br>done <span class="serif">properly.</span>',
    benefits_sub="Testosterone replacement is appropriate only for diagnosed deficiency and works best with monitoring. Here is how a supervised protocol is structured.",
    benefits=[("Confirmed on labs first","Started only after bloodwork confirms clinically low testosterone."),
              ("Physiologic dosing","Weekly or biweekly protocols aimed at restoring levels into a normal range."),
              ("Provider-monitored","Follow-up labs track testosterone, hematocrit, and estradiol over time."),
              ("Injectable consistency","A well-understood delivery route with predictable dosing."),
              ("Stack-ready","Can be paired with HCG or an aromatase inhibitor when clinically appropriate."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent, labeled strength.")],
    whats_included=wi_inject("Testosterone cypionate vial"),
    faq_heading='Questions about<br><span class="serif">TRT?</span>',
    faq=[("Who is a candidate for TRT?","Men with symptoms of low testosterone confirmed by blood tests. A provider reviews your labs, symptoms, and history before prescribing."),
         ("How is it taken?","Testosterone cypionate is injected on a schedule your provider sets, commonly weekly or every two weeks. You will be shown how to self-administer."),
         ("What monitoring is involved?","Follow-up labs typically check testosterone, hematocrit (red blood cell levels), and estradiol so your provider can adjust the dose safely."),
         ("Will it affect fertility?","Exogenous testosterone can reduce sperm production. If fertility matters to you, discuss options like HCG or enclomiphene with your provider."),
         ("Who should not use it?","Men with prostate or breast cancer, untreated severe sleep apnea, uncontrolled heart failure, or very high red blood cell counts should not start TRT without specialist input.")],
    isi="Testosterone cypionate is a prescription, controlled medication. These statements have not been evaluated by the Food and Drug Administration. Testosterone therapy is intended for men with diagnosed low testosterone and is not for women, for use in pregnancy, or for athletic enhancement. It should not be used by men with prostate or breast cancer and requires ongoing lab monitoring of testosterone, hematocrit, and estradiol. Possible effects include elevated red blood cell counts, acne, fluid retention, reduced fertility, and changes in mood. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider who knows your full medical history. Individual results may vary.",
    cta_heading='Ready to address<br><span class="serif">low T?</span>'),

  dict(**MENS, slug="testosterone-cream", intake="testosterone_cream",
    title_plain="Testosterone Cream", title_html='Testosterone <span class="serif">Cream</span>',
    badge="Topical TRT", category="Men's Hormone · TRT",
    meta_desc="Transdermal testosterone cream for low testosterone, a needle-free option prescribed and monitored by licensed providers.",
    subtitle='Transdermal <strong>testosterone cream</strong>, a needle-free testosterone replacement option for men who prefer a daily topical. Provider-supervised, with lab monitoring like any TRT protocol.',
    includes=inc_topical("Testosterone cream"),
    benefits_heading='Testosterone therapy,<br>no <span class="serif">needles.</span>',
    benefits_sub="A topical route to testosterone replacement for diagnosed deficiency. Here is how the daily-cream approach works under supervision.",
    benefits=[("Needle-free delivery","A daily cream for men who would rather not inject."),
              ("Steady daily routine","Applied once daily to maintain consistent levels."),
              ("Confirmed on labs first","Prescribed only after bloodwork confirms low testosterone."),
              ("Provider-monitored","Follow-up labs guide dose adjustments over time."),
              ("Pairs with the stack","Works alongside enclomiphene or HCG when appropriate."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Testosterone cream"),
    faq_heading='Questions about<br><span class="serif">testosterone cream?</span>',
    faq=[("How does the cream work?","It delivers testosterone through the skin, avoiding injections. Levels are checked with labs and the dose adjusted as needed."),
         ("How do I apply it?","To clean, dry skin once daily per your provider, then wash your hands. Avoid skin-to-skin transfer to women and children at the application site."),
         ("Is transfer a real concern?","Yes. Topical testosterone can transfer by direct skin contact, so cover the area and wash hands carefully, especially around women and children."),
         ("What monitoring is involved?","Follow-up labs track testosterone, hematocrit, and estradiol so your provider can keep the dose in a safe range."),
         ("Who should not use it?","Men with prostate or breast cancer, and women or children, should not use it. Tell your provider your full history before starting.")],
    isi="Testosterone cream is a prescription, controlled medication for men with diagnosed low testosterone. These statements have not been evaluated by the Food and Drug Administration. Topical testosterone can transfer to others through skin contact; cover the application site and wash hands to protect women and children. It is not for women, pregnancy, or athletic enhancement, and should not be used by men with prostate or breast cancer. Ongoing lab monitoring is required. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Prefer a<br><span class="serif">topical?</span>'),

  dict(**MENS, slug="testosterone-hypo-spray", intake="testosterone_hypo_spray",
    title_plain="Testosterone Hypo Spray", title_html='Testosterone <span class="serif">Hypo Spray</span>',
    badge="HypoSpray", category="Men's Hormone · TRT",
    meta_desc="Metered transdermal testosterone hypospray, a needle-free TRT option prescribed and monitored by licensed providers.",
    subtitle='A metered <strong>testosterone hypospray</strong>, a needle-free transdermal option that delivers a measured dose with each actuation. Provider-supervised testosterone replacement for diagnosed low testosterone.',
    includes=inc_topical("Testosterone hypospray"),
    benefits_heading='Measured doses,<br>no <span class="serif">needles.</span>',
    benefits_sub="A precise transdermal spray for testosterone replacement. Here is how the metered approach fits a supervised protocol.",
    benefits=[("Metered dosing","Each actuation delivers a measured amount for consistency."),
              ("Needle-free","A transdermal alternative to injections."),
              ("Confirmed on labs first","Prescribed only after testing confirms low testosterone."),
              ("Provider-monitored","Follow-up labs guide ongoing adjustments."),
              ("Fast to apply","A quick daily step that is easy to keep up."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Testosterone hypospray"),
    faq_heading='Questions about<br><span class="serif">the hypospray?</span>',
    faq=[("What is a testosterone hypospray?","A transdermal spray that delivers a metered dose of testosterone through the skin, an alternative to injections or creams."),
         ("How do I use it?","Applied to clean, dry skin per your provider, letting it dry before dressing. Wash hands after to avoid transfer."),
         ("Can it transfer to others?","As with other topical testosterone, skin contact can transfer it. Let it dry, cover the site, and protect women and children."),
         ("What monitoring is involved?","Labs track testosterone, hematocrit, and estradiol so your provider can keep dosing safe."),
         ("Who should not use it?","Men with prostate or breast cancer, and women or children, should not use it. Share your full history with your provider.")],
    isi="Testosterone hypospray is a prescription, controlled medication for men with diagnosed low testosterone. These statements have not been evaluated by the Food and Drug Administration. Topical testosterone can transfer to others through skin contact; let it dry, cover the site, and wash hands to protect women and children. It is not for women, pregnancy, or athletic enhancement and should not be used by men with prostate or breast cancer. Ongoing lab monitoring is required. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Want metered<br><span class="serif">dosing?</span>'),

  dict(**MENS, slug="enclomiphene", intake="enclomiphene",
    title_plain="Enclomiphene", title_html='Enclo<span class="serif">miphene</span>',
    badge="Fertility-Sparing", category="Men's Hormone · Fertility",
    meta_desc="Enclomiphene citrate to support the body's own testosterone production while preserving fertility, prescribed by licensed providers.",
    subtitle='<strong>Enclomiphene citrate</strong>, an oral option that prompts the body to make more of its own testosterone by acting on the pituitary, while preserving fertility. An alternative to external testosterone for appropriate candidates.',
    includes=inc_oral("Enclomiphene capsules"),
    benefits_heading='Raise testosterone,<br>keep <span class="serif">fertility.</span>',
    benefits_sub="Enclomiphene works upstream on the pituitary rather than adding external testosterone. Here is what that means in practice.",
    benefits=[("Stimulates your own production","Acts on the pituitary to raise LH and FSH, which signal the testes to make testosterone."),
              ("Preserves fertility","Unlike external testosterone, it tends to maintain sperm production."),
              ("Oral and once-daily","A capsule routine rather than injections or creams."),
              ("For the right candidate","An option when fertility preservation is a priority."),
              ("Provider-monitored","Labs confirm the response and guide dosing."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Enclomiphene capsules"),
    faq_heading='Questions about<br><span class="serif">enclomiphene?</span>',
    faq=[("How is it different from TRT?","External testosterone replaces the hormone directly and can suppress sperm production. Enclomiphene signals your own body to make more testosterone, which tends to preserve fertility."),
         ("How do I take it?","As a daily oral capsule per your provider, with follow-up labs to confirm the response."),
         ("Who is it best for?","Men with low testosterone who want to preserve fertility or prefer to avoid external testosterone. Your provider decides if it fits."),
         ("What monitoring is involved?","Labs check testosterone and related hormones so your provider can adjust the dose."),
         ("Who should not use it?","Men with certain hormone-sensitive conditions or specific eye or liver issues may not be candidates. Share your full history with your provider.")],
    isi="Enclomiphene is a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. It is intended for men and is not for use in women or pregnancy. Possible effects include mood changes, headache, and visual disturbances; report visual symptoms to your provider promptly. Ongoing lab monitoring is recommended. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Protect your<br><span class="serif">fertility?</span>'),

  dict(**MENS, slug="hcg", intake="hcg",
    title_plain="HCG Injection", title_html='HCG <span class="serif">Injection</span>',
    badge="HCG", category="Men's Hormone · Adjunct",
    meta_desc="HCG injection to support testicular function and fertility alongside or instead of TRT, prescribed by licensed providers.",
    subtitle='<strong>Human chorionic gonadotropin (HCG)</strong>, used to support testicular function and fertility, either alongside testosterone therapy or on its own for appropriate candidates.',
    includes=inc_inject("HCG"),
    benefits_heading='Support the system<br>behind your <span class="serif">hormones.</span>',
    benefits_sub="HCG mimics a signaling hormone that keeps the testes active. Here is how it is used within a hormone plan.",
    benefits=[("Maintains testicular function","Mimics LH to keep the testes active during testosterone therapy."),
              ("Fertility support","Often used to help preserve sperm production on TRT."),
              ("Flexible role","Used as a TRT adjunct, monotherapy, or fertility support."),
              ("Provider-directed","Dosing and schedule set after review of your goals and labs."),
              ("Injectable protocol","A small, routine subcutaneous injection."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("HCG vial"),
    faq_heading='Questions about<br><span class="serif">HCG?</span>',
    faq=[("What does HCG do in men?","It mimics luteinizing hormone (LH), signaling the testes to stay active, which supports testosterone production and fertility."),
         ("Why use it with TRT?","External testosterone can shrink testicular activity and reduce fertility. HCG is often added to counter that."),
         ("How is it taken?","As a small subcutaneous injection on a schedule your provider sets. You will be shown how to self-administer."),
         ("Can it be used alone?","In some cases, yes, as monotherapy or for fertility support. Your provider determines the best approach."),
         ("Who should not use it?","Those with certain hormone-sensitive cancers or specific conditions may not be candidates. Share your full history with your provider.")],
    isi="HCG is a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. It is used under provider supervision and is not for athletic enhancement or weight loss. Possible effects include injection-site reactions, fluid retention, and mood changes. Inform your provider of all conditions and medications, including any history of hormone-sensitive cancer. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Round out your<br><span class="serif">protocol?</span>'),

  dict(**MENS, slug="anastrozole", intake="anastrozole",
    title_plain="Anastrozole", title_html='Anastro<span class="serif">zole</span>',
    badge="AI", category="Men's Hormone · Support",
    meta_desc="Anastrozole, an aromatase inhibitor for estrogen management on testosterone therapy, prescribed and monitored by licensed providers.",
    subtitle='<strong>Anastrozole</strong>, an aromatase inhibitor used to manage estrogen levels in men on testosterone therapy when labs and symptoms indicate it. Always provider-directed and used sparingly.',
    includes=inc_oral("Anastrozole tablets"),
    benefits_heading='Keep your hormones<br>in <span class="serif">balance.</span>',
    benefits_sub="On testosterone therapy, some men convert too much testosterone to estrogen. Anastrozole is a tool to manage that, used carefully.",
    benefits=[("Manages estrogen on TRT","Reduces the conversion of testosterone to estrogen when it runs high."),
              ("Lab-guided","Used only when bloodwork and symptoms support it."),
              ("Low, careful dosing","Estrogen is necessary, so it is dosed conservatively."),
              ("Completes the stack","A support medication within a monitored TRT protocol."),
              ("Provider-directed","Started, adjusted, and stopped based on your labs."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Anastrozole tablets"),
    faq_heading='Questions about<br><span class="serif">anastrozole?</span>',
    faq=[("What does anastrozole do?","It lowers estrogen by blocking aromatase, the enzyme that converts testosterone into estrogen. In men on TRT it is used when estrogen runs high."),
         ("Is it always needed on TRT?","No. Many men never need it. It is used only when labs and symptoms point to high estrogen."),
         ("How is it taken?","As a low-dose oral tablet on a schedule set by your provider, with labs to guide it."),
         ("Can estrogen go too low?","Yes, and low estrogen causes its own problems. That is why dosing is conservative and lab-guided."),
         ("Who should not use it?","It is used in men only as part of a monitored protocol. Share your full history and all medications with your provider.")],
    isi="Anastrozole is a prescription, compounded medication used here as a support to testosterone therapy in men. These statements have not been evaluated by the Food and Drug Administration. Estrogen is necessary for bone, cardiovascular, and metabolic health, so anastrozole is used conservatively and only when labs support it; over-suppression of estrogen can cause joint pain, mood changes, and bone loss. It is not for use in women or pregnancy. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Dial in your<br><span class="serif">balance?</span>'),

  # ════════ WAVE 3 — Women's Hormone (6) ════════
  dict(**WOMEN, slug="estradiol-patches", intake="estradiol_patches",
    title_plain="Estradiol Patches", title_html='Estradiol <span class="serif">Patches</span>',
    badge="HRT", category="Women's Hormone · HRT",
    meta_desc="Transdermal estradiol patches for menopausal symptom relief, prescribed and monitored by licensed providers.",
    subtitle='Transdermal <strong>estradiol patches</strong> for menopausal symptom relief. A widely used form of hormone therapy that delivers steady estradiol through the skin, prescribed after a provider review of your history.',
    includes=inc_topical("Estradiol patches"),
    benefits_heading='Menopause support,<br>delivered <span class="serif">steadily.</span>',
    benefits_sub="Transdermal estradiol is a well-established route for menopausal hormone therapy. Here is how the patch approach works.",
    benefits=[("Steady delivery","A patch releases estradiol gradually for stable levels between changes."),
              ("Transdermal route","Skips first-pass liver metabolism associated with some oral estrogens."),
              ("Simple schedule","Changed on a set cadence, with minimal daily effort."),
              ("Pairs with progesterone","Combined with progesterone if you have a uterus, for endometrial protection."),
              ("Provider-reviewed","Prescribed after your history and risk factors are reviewed."),
              ("Compounded or dispensed","Sourced through a licensed US pharmacy.")],
    whats_included=wi_topical("Estradiol patches"),
    faq_heading='Questions about<br><span class="serif">estradiol patches?</span>',
    faq=[("What are estradiol patches for?","They deliver estradiol through the skin to help with menopausal symptoms such as hot flashes, under provider guidance."),
         ("How do I use them?","Applied to clean, dry skin and changed on the schedule your provider sets, rotating sites to reduce irritation."),
         ("Do I also need progesterone?","If you still have a uterus, estrogen is generally paired with progesterone to protect the uterine lining. Your provider will advise."),
         ("Why a patch instead of a pill?","Transdermal estrogen avoids first-pass liver metabolism, which some providers prefer depending on your risk profile."),
         ("Who should not use it?","Those with a history of certain cancers, blood clots, stroke, or liver disease may not be candidates. Share your full history with your provider.")],
    isi="Estradiol is a prescription hormone medication. These statements have not been evaluated by the Food and Drug Administration. Estrogen therapy is not appropriate for everyone; it should not be used by individuals with a history of estrogen-sensitive cancers, blood clots, stroke, or active liver disease, or during pregnancy. If you have a uterus, estrogen is generally combined with a progestogen to protect the uterine lining. Hormone therapy carries individualized risks and benefits that should be discussed with a licensed provider who knows your full medical history. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Ease your<br><span class="serif">menopause symptoms?</span>'),

  dict(**WOMEN, slug="biest-progesterone-cream", intake="biest_progesterone_cream",
    title_plain="Biest + Progesterone Cream", title_html='Biest + <span class="serif">Progesterone</span>',
    badge="Compounded", category="Women's Hormone · HRT",
    meta_desc="Compounded bi-estrogen and progesterone cream for menopausal support, prescribed by licensed providers.",
    subtitle='A compounded <strong>bi-estrogen (estriol and estradiol) with progesterone</strong> cream, a bioidentical hormone combination for menopausal support, compounded to a strength your provider directs.',
    includes=inc_topical("Biest + progesterone cream"),
    benefits_heading='Bioidentical support,<br>compounded to <span class="serif">you.</span>',
    benefits_sub="A topical that combines two estrogens with progesterone in one cream. Here is how the compounded approach works.",
    benefits=[("Two estrogens plus progesterone","Combines estriol and estradiol with progesterone in a single cream."),
              ("Custom strength","Compounded to the ratio and strength your provider prescribes."),
              ("Topical route","Applied to the skin as part of a daily routine."),
              ("Progesterone included","Helps balance estrogen as part of the formulation."),
              ("Provider-reviewed","Prescribed after your history and risk factors are reviewed."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Biest + progesterone cream"),
    faq_heading='Questions about<br><span class="serif">Biest cream?</span>',
    faq=[("What is Biest?","Biest refers to a combination of two estrogens, typically estriol and estradiol. Here it is compounded together with progesterone in a cream."),
         ("How do I use it?","Applied to the skin per your provider, often rotating application sites. Wash hands after and avoid transfer to others."),
         ("Why compounded?","Compounding allows the ratio and strength to be tailored, which some providers prefer for individualized hormone therapy."),
         ("Is progesterone necessary?","If you have a uterus, progesterone helps protect the uterine lining when using estrogen. Your provider will advise."),
         ("Who should not use it?","Those with a history of hormone-sensitive cancers, blood clots, stroke, or liver disease may not be candidates. Share your full history with your provider.")],
    isi="This is a prescription, compounded hormone cream containing estrogens and progesterone. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Hormone therapy is not appropriate for everyone and should not be used by individuals with a history of estrogen-sensitive cancers, blood clots, stroke, or active liver disease, or during pregnancy. Topical hormones can transfer through skin contact; wash hands and protect others. The risks and benefits should be discussed with a licensed provider who knows your full history. Individual results may vary.",
    cta_heading='Explore bioidentical<br><span class="serif">HRT?</span>'),

  dict(**WOMEN, slug="progesterone-capsules", intake="progesterone_capsules",
    title_plain="Progesterone Capsules", title_html='Progesterone <span class="serif">Capsules</span>',
    badge="HRT", category="Women's Hormone · HRT",
    meta_desc="Oral micronized progesterone for endometrial protection and sleep support within HRT, prescribed by licensed providers.",
    subtitle='Oral <strong>micronized progesterone</strong> capsules, used for endometrial protection alongside estrogen and valued for their calming, sleep-supportive effect when taken at night.',
    includes=inc_oral("Micronized progesterone capsules"),
    benefits_heading='The other half of<br>balanced <span class="serif">HRT.</span>',
    benefits_sub="Progesterone is a standard partner to estrogen in women with a uterus. Here is the role it plays.",
    benefits=[("Endometrial protection","Protects the uterine lining when taken with estrogen."),
              ("Sleep and calm","Often taken at night for its calming, sleep-supportive effect."),
              ("Micronized form","A bioidentical, micronized formulation."),
              ("Standard HRT pairing","Commonly prescribed alongside estradiol."),
              ("Provider-reviewed","Prescribed after your history is reviewed."),
              ("Compounded or dispensed","Sourced through a licensed US pharmacy.")],
    whats_included=wi_oral("Micronized progesterone capsules"),
    faq_heading='Questions about<br><span class="serif">progesterone?</span>',
    faq=[("Why is progesterone used with estrogen?","In women with a uterus, progesterone protects the uterine lining from the effects of estrogen alone."),
         ("Why take it at night?","Oral progesterone can have a calming, drowsy effect, so it is commonly taken at bedtime."),
         ("Do I need it if I have had a hysterectomy?","Often estrogen alone is used after hysterectomy, but your provider decides based on your situation."),
         ("Is this bioidentical?","Micronized progesterone is structurally identical to the progesterone your body makes."),
         ("Who should not use it?","Those with certain cancers, liver disease, or a history of blood clots may not be candidates. Share your full history with your provider.")],
    isi="Progesterone is a prescription hormone medication. These statements have not been evaluated by the Food and Drug Administration. It is used as part of hormone therapy, commonly to protect the uterine lining in women taking estrogen. It can cause drowsiness, so it is often taken at bedtime; do not drive until you know how it affects you. It is not appropriate for everyone, including those with certain cancers, liver disease, or a history of blood clots, or during pregnancy unless directed. Discuss risks and benefits with a licensed provider who knows your full history. Individual results may vary.",
    cta_heading='Balance your<br><span class="serif">hormones?</span>'),

  dict(**WOMEN, slug="dhea-pregnenolone", intake="dhea_pregnenolone",
    title_plain="DHEA + Pregnenolone", title_html='DHEA + <span class="serif">Pregnenolone</span>',
    badge="Precursors", category="Women's Hormone · Longevity",
    meta_desc="Compounded DHEA and pregnenolone, adrenal hormone precursors used in longevity and vitality protocols, prescribed by licensed providers.",
    subtitle='A compounded <strong>DHEA and pregnenolone</strong> combination, two adrenal hormone precursors the body can use to produce other hormones. A longevity-leaning option that pairs with NAD+ and Niagen routines.',
    includes=inc_oral("DHEA + pregnenolone capsules"),
    benefits_heading='Upstream hormone<br><span class="serif">precursors.</span>',
    benefits_sub="DHEA and pregnenolone sit early in the hormone pathway. Here is how they are positioned, used under supervision.",
    benefits=[("Adrenal precursors","Building blocks the body can convert into downstream hormones."),
              ("Decline with age","Levels of both tend to fall over time, which drives interest in supplementation."),
              ("Longevity crossover","Often part of a broader vitality and healthy-aging routine."),
              ("Pairs with NAD+ work","Complements injectable NAD+ and Niagen for longevity-focused patients."),
              ("Provider-reviewed","Prescribed after your history and goals are reviewed."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("DHEA + pregnenolone capsules"),
    faq_heading='Questions about<br><span class="serif">DHEA?</span>',
    faq=[("What are DHEA and pregnenolone?","Both are hormones made largely by the adrenal glands that serve as precursors the body can convert into other hormones."),
         ("Why combine them?","They sit at different points early in the hormone pathway, so some protocols use them together under provider guidance."),
         ("How are they taken?","As oral capsules per your provider, with periodic labs where appropriate."),
         ("Who tends to use these?","People focused on healthy aging and vitality, often alongside other longevity routines, when a provider considers it appropriate."),
         ("Who should not use them?","Those with hormone-sensitive conditions or certain cancers should avoid them. They are not for use in pregnancy. Share your full history with your provider.")],
    isi="DHEA and pregnenolone are prescription, compounded hormones in this formulation. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Because they are hormone precursors, they should be avoided by individuals with hormone-sensitive conditions or cancers and during pregnancy or breastfeeding. Possible effects include acne, hair changes, and mood changes. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Support healthy<br><span class="serif">aging?</span>'),

  dict(**WOMEN, slug="estradiol-vaginal-cream", intake="estradiol_vaginal_cream",
    title_plain="Estradiol Vaginal Cream", title_html='Estradiol <span class="serif">Vaginal Cream</span>',
    badge="Local", category="Women's Hormone · HRT",
    meta_desc="Low-dose estradiol vaginal cream for genitourinary symptoms of menopause, prescribed by licensed providers.",
    subtitle='Low-dose <strong>estradiol vaginal cream</strong> for the genitourinary symptoms of menopause, such as dryness and discomfort. A local therapy designed for minimal systemic absorption.',
    includes=inc_topical("Estradiol vaginal cream"),
    benefits_heading='Targeted relief,<br>applied <span class="serif">locally.</span>',
    benefits_sub="Local vaginal estrogen addresses genitourinary symptoms directly. Here is how the low-dose approach works.",
    benefits=[("Local action","Delivers estradiol where symptoms occur, such as dryness and irritation."),
              ("Low systemic exposure","Designed for minimal absorption into the bloodstream."),
              ("For GSM symptoms","Targets the genitourinary syndrome of menopause."),
              ("Simple applicator","Used on a schedule your provider sets."),
              ("Provider-reviewed","Prescribed after your history is reviewed."),
              ("Compounded or dispensed","Sourced through a licensed US pharmacy.")],
    whats_included=wi_topical("Estradiol vaginal cream"),
    faq_heading='Questions about<br><span class="serif">vaginal estradiol?</span>',
    faq=[("What is it used for?","Local relief of menopausal genitourinary symptoms like vaginal dryness, irritation, and discomfort."),
         ("How is it different from a patch or pill?","It acts locally with minimal absorption into the bloodstream, rather than treating the whole body."),
         ("How do I use it?","With the provided applicator on the schedule your provider sets, often an initial period followed by a maintenance cadence."),
         ("Do I need progesterone with it?","Low-dose local estrogen usually does not require added progesterone, but your provider will advise based on your situation."),
         ("Who should not use it?","Those with a history of estrogen-sensitive cancers or unexplained vaginal bleeding should consult their provider first. Share your full history.")],
    isi="Estradiol vaginal cream is a prescription hormone medication. These statements have not been evaluated by the Food and Drug Administration. Even low-dose vaginal estrogen is a hormone therapy and is not appropriate for everyone, including those with a history of estrogen-sensitive cancers, unexplained vaginal bleeding, blood clots, or active liver disease. Report any unusual vaginal bleeding to your provider. Discuss risks and benefits with a licensed provider who knows your full medical history. Individual results may vary.",
    cta_heading='Find local<br><span class="serif">relief?</span>'),

  dict(**WOMEN, slug="womens-testosterone-cream", intake="womens_testosterone_cream",
    title_plain="Women's Testosterone Cream", title_html='Women&rsquo;s Testosterone <span class="serif">Cream</span>',
    badge="Libido", category="Women's Hormone · Libido",
    meta_desc="Low-dose testosterone cream for women, for libido and energy when clinically appropriate, prescribed by licensed providers.",
    subtitle='A low-dose <strong>testosterone cream for women</strong>, used for libido and energy when clinically appropriate. Dosed conservatively and prescribed only after a provider review.',
    includes=inc_topical("Women's testosterone cream"),
    benefits_heading='A small lever for<br>libido and <span class="serif">energy.</span>',
    benefits_sub="Testosterone is part of female physiology too, at much lower levels. Here is how a low-dose, supervised approach is framed.",
    benefits=[("Low-dose for women","Formulated at the much lower doses appropriate for female physiology."),
              ("Libido and energy","Used when low testosterone may be contributing to these concerns."),
              ("Topical routine","A simple daily cream rather than injections."),
              ("Provider-reviewed","Prescribed only after your history and labs are considered."),
              ("Bridges HRT and sexual health","Sits between hormone therapy and sexual wellness."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Women's testosterone cream"),
    faq_heading='Questions about<br><span class="serif">the cream?</span>',
    faq=[("Do women need testosterone?","Women produce testosterone at low levels, and some experience symptoms when it is low. A provider decides whether a low-dose cream is appropriate."),
         ("How is it dosed?","At much lower doses than male testosterone therapy, applied topically per your provider, with monitoring."),
         ("How do I apply it?","To clean, dry skin on the schedule your provider sets. Wash hands after and avoid transfer to others."),
         ("What should I watch for?","Report unwanted effects such as acne, hair changes, or voice changes to your provider, who can adjust the dose."),
         ("Who should not use it?","It is not for use in pregnancy or breastfeeding, or with certain hormone-sensitive conditions. Share your full history with your provider.")],
    isi="Women's testosterone cream is a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. It is dosed conservatively for female physiology and is not for use in pregnancy or breastfeeding. Possible effects include acne, unwanted hair growth, and, rarely, voice changes; report these to your provider. Topical hormones can transfer through skin contact; wash hands and protect others. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Address libido and<br><span class="serif">energy?</span>'),

  # ════════ WAVE 4 — Weight Loss previews (4) ════════
  dict(**WL, slug="metformin-er", intake="metformin_er",
    title_plain="Metformin ER", title_html='Metformin <span class="serif">ER</span>',
    badge="Metabolic", category="Weight Loss · Metabolic",
    meta_desc="Metformin extended-release for insulin sensitivity and as a GLP-1 companion, prescribed by licensed providers.",
    subtitle='<strong>Metformin extended-release</strong>, a long-established metabolic medication that supports insulin sensitivity. Often used as a companion to GLP-1 therapy within a provider-guided weight plan.',
    includes=inc_oral("Metformin ER tablets"),
    benefits_heading='A metabolic anchor<br>for your <span class="serif">plan.</span>',
    benefits_sub="Metformin has decades of use for blood-sugar and insulin support. Here is how it fits a weight-management plan.",
    benefits=[("Insulin sensitivity","Supports how your body responds to insulin."),
              ("GLP-1 companion","Frequently paired with GLP-1 therapy under provider guidance."),
              ("Extended-release","The ER form is designed to ease gastrointestinal side effects."),
              ("Long track record","One of the most widely used metabolic medications."),
              ("Provider-monitored","Suitability and kidney function reviewed before and during use."),
              ("Compounded or dispensed","Sourced through a licensed US pharmacy.")],
    whats_included=wi_oral("Metformin ER tablets"),
    faq_heading='Questions about<br><span class="serif">metformin?</span>',
    faq=[("What is metformin used for here?","It supports insulin sensitivity and is often used alongside GLP-1 therapy as part of a metabolic weight plan."),
         ("Why extended-release?","The ER form releases gradually, which tends to reduce the gastrointestinal upset some people get with immediate-release metformin."),
         ("How do I take it?","Usually with food per your provider, often starting low and increasing gradually to limit side effects."),
         ("What monitoring is involved?","Providers typically review kidney function and may check B12 over time."),
         ("Who should not take it?","Those with significant kidney impairment or certain other conditions should not use it. Tell your provider your full history before any procedure with contrast dye.")],
    isi="Metformin is a prescription medication. These statements have not been evaluated by the Food and Drug Administration. It is not appropriate for everyone, including those with significant kidney impairment or certain acute conditions, due to a rare but serious risk of lactic acidosis. Temporary discontinuation may be needed around imaging with contrast dye or surgery. Possible effects include gastrointestinal upset and, with long-term use, reduced vitamin B12. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Add a metabolic<br><span class="serif">anchor?</span>'),

  dict(**WL, slug="semaglutide-odt", intake="semaglutide_odt",
    title_plain="Semaglutide ODT", title_html='Semaglutide <span class="serif">ODT</span>',
    badge="Oral GLP-1", category="Weight Loss · Oral",
    meta_desc="Oral semaglutide ODT with ondansetron for nausea management, a needle-free GLP-1 option prescribed by licensed providers.",
    subtitle='An oral <strong>semaglutide orally-disintegrating tablet (ODT)</strong> formulated with ondansetron to help manage nausea. A needle-free way to access GLP-1 therapy, prescribed after medical review.',
    includes=inc_oral("Semaglutide ODT"),
    benefits_heading='GLP-1 support,<br>no <span class="serif">needles.</span>',
    benefits_sub="A dissolvable tablet that brings GLP-1 therapy into an oral format with built-in nausea support. Here is how it is positioned.",
    benefits=[("Needle-free GLP-1","An orally-disintegrating tablet rather than an injection."),
              ("Nausea managed in formula","Includes ondansetron to help with the nausea that can accompany GLP-1 therapy."),
              ("Dissolves on the tongue","No water needed; convenient for daily use."),
              ("Same GLP-1 class","Semaglutide acts on the GLP-1 receptor, like the injectable form."),
              ("Provider-supervised","Prescribed and dose-managed after medical review."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Semaglutide ODT"),
    faq_heading='Questions about<br><span class="serif">semaglutide ODT?</span>',
    faq=[("What is an ODT?","An orally-disintegrating tablet that dissolves in the mouth without water, here delivering semaglutide in a needle-free format."),
         ("Why is ondansetron included?","Ondansetron is an anti-nausea medicine. Including it is intended to help with the nausea that GLP-1 therapy can cause, especially early on."),
         ("How is it different from the injection?","It is the same GLP-1 class delivered orally instead of by injection. Your provider will discuss which format suits you."),
         ("How do I take it?","Placed on the tongue to dissolve per your provider's directions, typically with gradual dose increases."),
         ("Who should not use it?","People with a personal or family history of medullary thyroid carcinoma or MEN 2, or with certain conditions, should not use GLP-1 therapy. Share your full history with your provider.")],
    isi="This is a prescription, compounded medication containing semaglutide and ondansetron. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. GLP-1 medications should not be used by individuals with a personal or family history of medullary thyroid carcinoma or multiple endocrine neoplasia syndrome type 2, and carry risks including pancreatitis, gallbladder problems, and gastrointestinal effects. Ondansetron can affect heart rhythm in susceptible individuals. Not for use in pregnancy. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Try oral<br><span class="serif">GLP-1?</span>'),

  dict(**WL, slug="tirzepatide-sublingual", intake="tirzepatide_sublingual",
    title_plain="Tirzepatide Sublingual Drops", title_html='Tirzepatide <span class="serif">Sublingual</span>',
    badge="Sublingual", category="Weight Loss · Oral",
    meta_desc="Needle-free sublingual tirzepatide drops, a GLP-1 and GIP option prescribed by licensed providers after review.",
    subtitle='<strong>Tirzepatide sublingual drops</strong>, a needle-free way to take the dual GLP-1 and GIP medication for patients who prefer to avoid injections. Prescribed and dose-managed after medical review.',
    includes=inc_oral("Tirzepatide sublingual drops"),
    benefits_heading='Dual-action support,<br>under the <span class="serif">tongue.</span>',
    benefits_sub="A sublingual route to tirzepatide for the needle-averse. Here is how it is positioned within the GLP-1 lineup.",
    benefits=[("Needle-free format","Sublingual drops instead of a weekly injection."),
              ("Dual GLP-1 and GIP","Tirzepatide acts on two receptors involved in appetite and metabolism."),
              ("Simple daily routine","Taken under the tongue per your provider's directions."),
              ("For the needle-averse","An option for patients who would not otherwise start injections."),
              ("Provider-supervised","Prescribed and titrated after medical review."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Tirzepatide sublingual drops"),
    faq_heading='Questions about<br><span class="serif">sublingual tirzepatide?</span>',
    faq=[("What does sublingual mean?","Taken under the tongue, where it is held briefly before swallowing, rather than injected."),
         ("How is it different from the injection?","It is the same dual GLP-1 and GIP medication in a needle-free format. Your provider will discuss which option fits you."),
         ("How do I take it?","Placed under the tongue per your provider's directions, typically starting low and increasing gradually."),
         ("What side effects are common?","As with other GLP-1 therapies, nausea and other gastrointestinal effects can occur, especially when increasing the dose."),
         ("Who should not use it?","People with a personal or family history of medullary thyroid carcinoma or MEN 2, or with certain conditions, should not use it. Share your full history with your provider.")],
    isi="Tirzepatide sublingual drops are a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. GLP-1 and GIP medications should not be used by individuals with a personal or family history of medullary thyroid carcinoma or multiple endocrine neoplasia syndrome type 2, and carry risks including pancreatitis, gallbladder problems, and gastrointestinal effects. Not for use in pregnancy. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Skip the<br><span class="serif">needle?</span>'),

  dict(**WL, slug="liraglutide", intake="liraglutide",
    title_plain="Liraglutide", title_html='Lira<span class="serif">glutide</span>',
    badge="GLP-1", category="Weight Loss · GLP-1",
    meta_desc="Liraglutide, a daily GLP-1 medication for weight management, prescribed by licensed providers after review.",
    subtitle='<strong>Liraglutide</strong>, an established daily GLP-1 medication for weight management. A well-studied option for patients and providers who prefer a daily cadence, prescribed after medical review.',
    includes=inc_inject("Liraglutide"),
    benefits_heading='A daily GLP-1<br>with a long <span class="serif">history.</span>',
    benefits_sub="Liraglutide is one of the longer-established GLP-1 medications. Here is how it fits the lineup.",
    benefits=[("Established GLP-1","One of the earlier GLP-1 medications, with a long clinical history."),
              ("Daily cadence","A once-daily injection, which some patients prefer over weekly."),
              ("Appetite pathway","Acts on the GLP-1 receptor involved in appetite and fullness."),
              ("Alternative option","An option when a different GLP-1 is a better fit for you."),
              ("Provider-supervised","Prescribed and titrated after medical review."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("Liraglutide vial"),
    faq_heading='Questions about<br><span class="serif">liraglutide?</span>',
    faq=[("How is liraglutide different from semaglutide or tirzepatide?","All act on the GLP-1 pathway. Liraglutide is dosed once daily rather than weekly. Your provider will discuss which fits your goals and history."),
         ("How is it taken?","As a once-daily subcutaneous injection, typically starting low and increasing gradually to limit side effects."),
         ("What side effects are common?","Nausea and other gastrointestinal effects are the most common, particularly when increasing the dose."),
         ("Why choose a daily option?","Some patients tolerate a daily rhythm better, or prefer it. It comes down to fit, which your provider helps determine."),
         ("Who should not use it?","People with a personal or family history of medullary thyroid carcinoma or MEN 2, or with certain conditions, should not use it. Share your full history with your provider.")],
    isi="Liraglutide is a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. GLP-1 medications should not be used by individuals with a personal or family history of medullary thyroid carcinoma or multiple endocrine neoplasia syndrome type 2, and carry risks including pancreatitis, gallbladder problems, and gastrointestinal effects. Not for use in pregnancy. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Prefer a daily<br><span class="serif">GLP-1?</span>'),

  # ════════ WAVE 5 — Sexual Health previews (6) ════════
  dict(**SEX, slug="trimix", intake="trimix",
    title_plain="Trimix Injection", title_html='Trimix <span class="serif">Injection</span>',
    badge="Trimix", category="Sexual Health · ED",
    meta_desc="Trimix injectable for erectile dysfunction when oral options are not enough, prescribed and titrated by licensed providers.",
    subtitle='<strong>Trimix</strong>, a compounded injectable combining alprostadil, papaverine, and phentolamine for erectile dysfunction when oral PDE5 medications are not enough. Carefully dosed and titrated by a provider.',
    includes=inc_inject("Trimix"),
    benefits_heading='An option when pills<br>are not <span class="serif">enough.</span>',
    benefits_sub="Trimix works through a different mechanism than oral ED tablets. Because it is potent, it is titrated carefully under supervision.",
    benefits=[("Three-agent formula","Combines alprostadil, papaverine, and phentolamine."),
              ("Different mechanism","Works locally, an option when oral PDE5 inhibitors are insufficient."),
              ("Carefully titrated","Started low and adjusted by your provider to find the right dose."),
              ("On-demand use","Used before activity per provider instructions."),
              ("Provider-directed","Initial dosing and technique guided by your provider."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("Trimix vial"),
    faq_heading='Questions about<br><span class="serif">Trimix?</span>',
    faq=[("What is Trimix?","A compounded injectable for erectile dysfunction that combines three medications. It is typically considered when oral options have not worked."),
         ("How is it used?","A small injection is administered before activity, using the dose and technique your provider establishes. Careful titration is essential."),
         ("Why is titration so important?","Because Trimix is potent, the dose must be found gradually to get an adequate response while avoiding a prolonged erection."),
         ("What is the main risk?","A prolonged erection (priapism) lasting over four hours is a medical emergency. Your provider will tell you exactly what to do if it happens."),
         ("Who should not use it?","Men with certain anatomical conditions, bleeding disorders, or who are at high risk of priapism should not use it. Share your full history with your provider.")],
    isi="Trimix is a prescription, compounded injectable medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Trimix requires careful, provider-directed dose titration. A prolonged erection (priapism) lasting more than four hours is a medical emergency requiring immediate care. Other risks include injection-site reactions, scarring, and bleeding. It is not appropriate for men with certain conditions or at high risk of priapism. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Explore advanced<br><span class="serif">ED therapy?</span>'),

  dict(**SEX, slug="tadalafil-troches", intake="tadalafil_troches",
    title_plain="Tadalafil Troches", title_html='Tadalafil <span class="serif">Troches</span>',
    badge="Troche", category="Sexual Health · ED",
    meta_desc="Sublingual tadalafil troches for erectile dysfunction, a fast-dissolving format prescribed by licensed providers.",
    subtitle='<strong>Tadalafil troches</strong>, a sublingual, fast-dissolving format of the well-known PDE5 inhibitor. An on-demand ED option for patients who prefer not to swallow a tablet.',
    includes=inc_oral("Tadalafil troches"),
    benefits_heading='A familiar medicine,<br>a flexible <span class="serif">format.</span>',
    benefits_sub="Tadalafil is a widely used ED medication. The troche format changes how it is taken, not the active ingredient.",
    benefits=[("Sublingual dissolve","Dissolves under the tongue, no water needed."),
              ("Well-known PDE5 inhibitor","Tadalafil is among the most established ED medications."),
              ("On-demand flexibility","Used before activity per your provider's directions."),
              ("Alternative to tablets","A format option for those who dislike swallowing pills."),
              ("Provider-reviewed","Prescribed after a review of your heart health and medications."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Tadalafil troches"),
    faq_heading='Questions about<br><span class="serif">tadalafil troches?</span>',
    faq=[("What is a troche?","A small lozenge that dissolves in the mouth, here delivering tadalafil without needing to swallow a tablet."),
         ("How is it used?","Placed under the tongue before activity per your provider's directions. Onset and duration depend on the dose."),
         ("Can I take it with nitrates?","No. PDE5 inhibitors like tadalafil must not be combined with nitrate medications, as the combination can cause a dangerous drop in blood pressure."),
         ("Does alcohol matter?","Heavy alcohol use with PDE5 inhibitors can increase side effects like dizziness and low blood pressure. Use sensibly."),
         ("Who should not use it?","Men taking nitrates, or with certain heart conditions, should not use it. Share your full history and medications with your provider.")],
    isi="Tadalafil is a prescription PDE5 inhibitor; this is a compounded troche formulation. These statements have not been evaluated by the Food and Drug Administration. Tadalafil must not be taken with nitrate medications or certain other drugs, as dangerous drops in blood pressure can occur. It is not appropriate for men with certain cardiovascular conditions. Seek emergency care for an erection lasting more than four hours or sudden vision or hearing changes. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Want a flexible<br><span class="serif">ED option?</span>'),

  dict(**SEX, slug="tadalafil-apomorphine", intake="tadalafil_apomorphine",
    title_plain="Tadalafil + Apomorphine", title_html='Tadalafil + <span class="serif">Apomorphine</span>',
    badge="Dual", category="Sexual Health · ED",
    meta_desc="Compounded tadalafil with apomorphine troches, a dual-mechanism ED option prescribed by licensed providers.",
    subtitle='Compounded <strong>tadalafil with apomorphine</strong> troches, pairing a PDE5 inhibitor with a centrally-acting dopamine agonist for a dual-mechanism, on-demand approach to erectile response.',
    includes=inc_oral("Tadalafil + apomorphine troches"),
    benefits_heading='Two mechanisms,<br>one <span class="serif">troche.</span>',
    benefits_sub="This formulation combines a peripheral and a central mechanism. Here is how the pairing is positioned, used under supervision.",
    benefits=[("Dual mechanism","Combines a PDE5 inhibitor with a centrally-acting dopamine agonist."),
              ("Sublingual format","A troche that dissolves under the tongue."),
              ("On-demand","Used before activity per your provider's directions."),
              ("For a layered approach","An option when a single mechanism has been insufficient."),
              ("Provider-reviewed","Prescribed after a review of your heart health and medications."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Tadalafil + apomorphine troches"),
    faq_heading='Questions about<br><span class="serif">the combo troche?</span>',
    faq=[("Why combine two ingredients?","Tadalafil works on blood flow peripherally while apomorphine acts centrally on dopamine pathways, so the combination targets erectile response two ways."),
         ("How is it used?","Dissolved under the tongue before activity per your provider's directions."),
         ("What side effects can apomorphine cause?","Nausea, dizziness, and yawning can occur with apomorphine. Your provider will discuss what to expect."),
         ("Can I take it with nitrates?","No. The tadalafil component means it must not be combined with nitrates due to the risk of a dangerous blood-pressure drop."),
         ("Who should not use it?","Men taking nitrates, or with certain heart conditions, should not use it. Share your full history and medications with your provider.")],
    isi="This is a prescription, compounded troche containing tadalafil (a PDE5 inhibitor) and apomorphine (a dopamine agonist). These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. It must not be taken with nitrates and is not appropriate for men with certain cardiovascular conditions. Apomorphine can cause nausea, dizziness, and low blood pressure. Seek emergency care for an erection lasting more than four hours. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Try a dual-action<br><span class="serif">approach?</span>'),

  dict(**SEX, slug="sildenafil-tadalafil-gummy", intake="sildenafil_tadalafil_gummy",
    title_plain="Sildenafil + Tadalafil Gummy", title_html='Sildenafil + <span class="serif">Tadalafil Gummy</span>',
    badge="Dual Gummy", category="Sexual Health · ED",
    meta_desc="A dual PDE5 gummy combining sildenafil and tadalafil for erectile dysfunction, prescribed by licensed providers.",
    subtitle='A dual <strong>sildenafil and tadalafil gummy</strong>, pairing two PDE5 inhibitors in one chewable, on-demand format that fits the way many patients already prefer to dose.',
    includes=inc_oral("Sildenafil + tadalafil gummies"),
    benefits_heading='Two PDE5s,<br>one easy <span class="serif">format.</span>',
    benefits_sub="This gummy combines a faster-onset and a longer-acting PDE5 inhibitor. Here is how the pairing is positioned.",
    benefits=[("Two PDE5 inhibitors","Combines sildenafil and tadalafil in a single dose."),
              ("Chewable format","An easy-to-take gummy, no water or swallowing a tablet."),
              ("On-demand","Taken before activity per your provider's directions."),
              ("Complementary profiles","Pairs a faster-onset agent with a longer-acting one."),
              ("Provider-reviewed","Prescribed after a review of your heart health and medications."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Sildenafil + tadalafil gummies"),
    faq_heading='Questions about<br><span class="serif">the gummy?</span>',
    faq=[("Why two ingredients in one gummy?","Sildenafil tends to act faster while tadalafil lasts longer. Combining them is meant to balance onset and duration."),
         ("How is it taken?","Chewed before activity per your provider's directions. Do not double up doses."),
         ("Can I take it with nitrates?","No. Both ingredients are PDE5 inhibitors and must not be combined with nitrates due to the risk of a dangerous blood-pressure drop."),
         ("Does food or alcohol matter?","A heavy meal can slow sildenafil's onset, and heavy alcohol can worsen side effects. Use sensibly."),
         ("Who should not use it?","Men taking nitrates, or with certain heart conditions, should not use it. Share your full history and medications with your provider.")],
    isi="This is a prescription, compounded gummy containing sildenafil and tadalafil, both PDE5 inhibitors. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. It must not be taken with nitrates and is not appropriate for men with certain cardiovascular conditions. Do not combine with other ED medications. Seek emergency care for an erection lasting more than four hours or sudden vision or hearing changes. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Want it in a<br><span class="serif">gummy?</span>'),

  dict(**SEX, slug="oxytocin-nasal", intake="oxytocin_nasal",
    title_plain="Oxytocin Nasal Spray", title_html='Oxytocin <span class="serif">Nasal Spray</span>',
    badge="Oxytocin", category="Sexual Health · Intimacy",
    meta_desc="Compounded oxytocin nasal spray for intimacy and connection support, prescribed by licensed providers.",
    subtitle='A compounded <strong>oxytocin nasal spray</strong>, explored for its role in bonding, connection, and arousal. A needle-free option that pairs naturally with the PT-141 line.',
    includes=inc_topical("Oxytocin nasal spray"),
    benefits_heading='The connection<br><span class="serif">hormone.</span>',
    benefits_sub="Oxytocin is involved in bonding and social connection. Use for intimacy is exploratory and provider-directed; here is how it is positioned.",
    benefits=[("Bonding and connection","Oxytocin is the hormone tied to social bonding and closeness."),
              ("Needle-free","A simple nasal spray rather than an injection."),
              ("Pairs with PT-141","A natural cross-sell with the libido-focused PT-141 line."),
              ("On-demand use","Used before intimacy per your provider's directions."),
              ("Provider-directed","Prescribed after a review of your history and goals."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_topical("Oxytocin nasal spray"),
    faq_heading='Questions about<br><span class="serif">oxytocin?</span>',
    faq=[("What is oxytocin?","A naturally occurring hormone involved in bonding, trust, and connection. As a nasal spray it is used in intimacy-focused protocols."),
         ("Is the evidence strong?","Use of oxytocin for intimacy is exploratory and the human evidence is still developing. Your provider will set honest expectations."),
         ("How is it used?","As a nasal spray before intimacy per your provider's directions."),
         ("Does it pair with PT-141?","Many patients use them together, as they address different aspects of arousal and connection. Your provider advises."),
         ("Who should not use it?","Those who are pregnant or have certain cardiovascular conditions should avoid it. Share your full history with your provider.")],
    isi="Oxytocin nasal spray is a prescription, compounded product. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Use of oxytocin for intimacy is exploratory and not an established, FDA-approved use. It should be avoided in pregnancy and used with caution in individuals with cardiovascular conditions. Inform your provider of all conditions and medications. The decision to begin any compounded medication should be made with a licensed provider. Individual results may vary.",
    cta_heading='Explore connection<br><span class="serif">support?</span>'),

  dict(**SEX, slug="pt141-strips", intake="pt141_strips",
    title_plain="PT-141 Strips", title_html='PT-141 <span class="serif">Strips</span>',
    badge="Strip", category="Sexual Health · Libido",
    meta_desc="PT-141 sublingual strips for libido support, an on-demand needle-free format prescribed by licensed providers.",
    subtitle='<strong>PT-141 (bremelanotide) sublingual strips</strong>, an on-demand libido option in a discreet, needle-free format. A dissolvable alternative to the ODT for patients who prefer a strip.',
    includes=inc_oral("PT-141 sublingual strips"),
    benefits_heading='Libido support,<br>on your <span class="serif">terms.</span>',
    benefits_sub="PT-141 works on the nervous system rather than blood flow. The strip format changes how it is taken, not the active ingredient.",
    benefits=[("Central mechanism","PT-141 acts on melanocortin pathways involved in desire, not just blood flow."),
              ("For men and women","Used for libido in appropriate candidates of any sex."),
              ("Discreet strip","A dissolvable sublingual strip, easy to carry and use."),
              ("On-demand","Taken ahead of intimacy per your provider's directions."),
              ("Provider-directed","Prescribed after a review of your history and blood pressure."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("PT-141 sublingual strips"),
    faq_heading='Questions about<br><span class="serif">PT-141 strips?</span>',
    faq=[("How is PT-141 different from ED pills?","PT-141 works centrally on pathways involved in sexual desire, rather than on blood flow like PDE5 inhibitors. It targets libido."),
         ("How is the strip used?","Dissolved under the tongue ahead of intimacy per your provider's directions."),
         ("What side effects are common?","Nausea, flushing, and temporary increases in blood pressure can occur. Your provider will review your blood pressure first."),
         ("Can it be used with ED medication?","Sometimes, under provider guidance, since they work by different mechanisms. Do not combine medications on your own."),
         ("Who should not use it?","Those with uncontrolled high blood pressure or significant cardiovascular disease should avoid it. Share your full history with your provider.")],
    isi="PT-141 (bremelanotide) is a prescription, compounded medication. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. PT-141 can transiently raise blood pressure and is not appropriate for individuals with uncontrolled hypertension or significant cardiovascular disease. Common effects include nausea and flushing. Not for use in pregnancy. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Support your<br><span class="serif">libido?</span>'),

  # ════════ WAVE 6 — Peptides & Recovery (4) ════════
  dict(**WELL, slug="bpc-157", intake="bpc_157",
    title_plain="BPC-157", title_html='BPC-<span class="serif">157</span>',
    badge="Peptide", category="Daily Wellness · Peptides",
    meta_desc="BPC-157 peptide explored for tissue repair and recovery, a research-stage compound prescribed by licensed providers.",
    subtitle='<strong>BPC-157</strong>, a synthetic peptide studied in preclinical research for tissue repair and recovery. A research-stage compound offered only under provider supervision, with honest expectations about the evidence.',
    includes=inc_inject("BPC-157"),
    benefits_heading='A recovery peptide,<br>described <span class="serif">honestly.</span>',
    benefits_sub="BPC-157 is an area of active interest, but the human evidence is limited. Here is how it is positioned, in mechanism and research terms.",
    benefits=[("Tissue-repair research","Studied in animal models for healing of tendon, muscle, and gut tissue."),
              ("Recovery interest","Popular in the recovery and performance space, where demand is growing."),
              ("Early-stage evidence","Most data is preclinical; robust human trials are limited."),
              ("Provider-supervised","Offered only with provider oversight and informed expectations."),
              ("Defined protocol","Used as a time-limited, provider-directed course."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("BPC-157 vial"),
    faq_heading='Questions about<br><span class="serif">BPC-157?</span>',
    faq=[("What is BPC-157?","A synthetic peptide derived from a protein found in the body, studied mostly in animal research for tissue repair."),
         ("Is it proven in humans?","No. The bulk of evidence is preclinical. Human data is limited, and it is not an FDA-approved treatment. Your provider will set honest expectations."),
         ("How is it used?","As a small subcutaneous injection on a provider-directed schedule, typically a defined course."),
         ("Is it allowed in sport?","Peptides like BPC-157 may be prohibited by anti-doping bodies. If you compete, check your sport's rules before use."),
         ("Who should not use it?","Those who are pregnant or breastfeeding, or have active cancer, should avoid it. Share your full history with your provider.")],
    isi="BPC-157 is a prescription, compounded peptide. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. BPC-157 is a research-stage compound; the majority of evidence is from animal studies and rigorous human safety and efficacy data is limited. It should be avoided during pregnancy or breastfeeding and by individuals with active cancer, and may be prohibited in competitive sport. Inform your provider of all conditions and medications. The decision to use any compounded peptide should be made with a licensed provider. Individual results may vary.",
    cta_heading='Explore recovery<br><span class="serif">peptides?</span>'),

  dict(**WELL, slug="tb-500", intake="tb_500",
    title_plain="TB-500", title_html='TB-<span class="serif">500</span>',
    badge="Peptide", category="Daily Wellness · Peptides",
    meta_desc="TB-500 (thymosin beta-4) peptide explored for recovery and flexibility, a research-stage compound prescribed by licensed providers.",
    subtitle='<strong>TB-500</strong>, a synthetic version of a thymosin beta-4 fragment studied for recovery and flexibility. A research-stage peptide offered only under provider supervision with honest expectations.',
    includes=inc_inject("TB-500"),
    benefits_heading='A recovery peptide,<br>without the <span class="serif">hype.</span>',
    benefits_sub="TB-500 is of interest in the recovery space, but human evidence is limited. Here is how it is positioned.",
    benefits=[("Recovery research","Studied in animal models for tissue repair and flexibility."),
              ("Athletic and longevity interest","Popular in recovery circles, where demand is rising."),
              ("Early-stage evidence","Largely preclinical; robust human trials are limited."),
              ("Provider-supervised","Offered only with oversight and realistic expectations."),
              ("Defined protocol","Used as a time-limited, provider-directed course."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("TB-500 vial"),
    faq_heading='Questions about<br><span class="serif">TB-500?</span>',
    faq=[("What is TB-500?","A synthetic peptide related to thymosin beta-4, a naturally occurring protein, studied mostly in animal research for recovery."),
         ("Is it proven in humans?","No. The evidence is largely preclinical and it is not FDA-approved. Your provider will set honest expectations before use."),
         ("How is it used?","As a small subcutaneous injection on a provider-directed schedule, typically a defined course."),
         ("Is it allowed in sport?","Peptides like TB-500 may be banned by anti-doping bodies. If you compete, check your sport's rules first."),
         ("Who should not use it?","Those who are pregnant or breastfeeding, or have active cancer, should avoid it. Share your full history with your provider.")],
    isi="TB-500 is a prescription, compounded peptide. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. TB-500 is a research-stage compound; most evidence is from animal studies and rigorous human safety and efficacy data is limited. It should be avoided during pregnancy or breastfeeding and by individuals with active cancer, and may be prohibited in competitive sport. Inform your provider of all conditions and medications. Individual results may vary.",
    cta_heading='Support your<br><span class="serif">recovery?</span>'),

  dict(**WELL, slug="ghk-cu-injectable", intake="ghk_cu_injectable",
    title_plain="GHK-Cu Injectable", title_html='GHK-Cu <span class="serif">Injectable</span>',
    badge="Copper Peptide", category="Daily Wellness · Peptides",
    meta_desc="GHK-Cu injectable copper peptide explored for collagen and tissue remodeling, a research-stage compound prescribed by licensed providers.",
    subtitle='<strong>GHK-Cu</strong>, a copper-binding peptide studied for collagen synthesis and tissue remodeling. A research-stage injectable that pairs with topical GHK-Cu skin formulations, offered under provider supervision.',
    includes=inc_inject("GHK-Cu"),
    benefits_heading='The copper peptide,<br>in <span class="serif">context.</span>',
    benefits_sub="GHK-Cu is well known in skincare and studied more broadly for remodeling. Here is how the injectable is positioned.",
    benefits=[("Collagen and remodeling","Studied for its role in collagen synthesis and tissue remodeling pathways."),
              ("Copper-binding peptide","A naturally occurring peptide that binds copper."),
              ("Pairs with topicals","Complements topical GHK-Cu creams for a layered approach."),
              ("Early-stage evidence","Topical use is better studied than injectable; expectations are set honestly."),
              ("Provider-supervised","Offered only with oversight and realistic expectations."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_inject("GHK-Cu vial"),
    faq_heading='Questions about<br><span class="serif">GHK-Cu?</span>',
    faq=[("What is GHK-Cu?","A copper-binding peptide that occurs naturally in the body and is studied for collagen and tissue remodeling. It is well known in topical skincare."),
         ("Is the injectable proven?","Topical GHK-Cu is better studied than the injectable form. The injectable is research-stage and not FDA-approved; your provider will set expectations."),
         ("How is it used?","As a small subcutaneous injection on a provider-directed schedule."),
         ("Can I use it with the cream?","Many patients pair injectable and topical approaches. Your provider advises on how to combine them."),
         ("Who should not use it?","Those who are pregnant or breastfeeding, or have active cancer, should avoid it. Share your full history with your provider.")],
    isi="GHK-Cu injectable is a prescription, compounded peptide. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. The injectable form is research-stage with limited human data; topical GHK-Cu is more established. It should be avoided during pregnancy or breastfeeding and by individuals with active cancer. Inform your provider of all conditions and medications. The decision to use any compounded peptide should be made with a licensed provider. Individual results may vary.",
    cta_heading='Layer your<br><span class="serif">skin routine?</span>'),

  dict(**WELL, slug="naltrexone-ldn", intake="naltrexone_ldn",
    title_plain="Low-Dose Naltrexone", title_html='Low-Dose <span class="serif">Naltrexone</span>',
    badge="LDN", category="Daily Wellness · Recovery",
    meta_desc="Low-dose naltrexone (LDN) explored for autoimmune, chronic pain, and wellness protocols, prescribed by licensed providers.",
    subtitle='<strong>Low-dose naltrexone (LDN)</strong>, naltrexone compounded at a fraction of its standard dose and used off-label in wellness, autoimmune, and chronic-pain protocols under provider supervision.',
    includes=inc_oral("Low-dose naltrexone capsules"),
    benefits_heading='A small dose with<br>a devoted <span class="serif">following.</span>',
    benefits_sub="LDN uses naltrexone at very low doses for purposes different from its standard use. Here is how it is framed, honestly.",
    benefits=[("Very low dosing","Compounded at a small fraction of the standard naltrexone dose."),
              ("Wellness and autoimmune interest","Used off-label in autoimmune, chronic-pain, and wellness protocols."),
              ("Once-daily capsule","Typically taken at night, per your provider."),
              ("Evidence still developing","Off-label use is supported by interest and some studies; expectations are set honestly."),
              ("Provider-directed","Prescribed and monitored by a licensed provider."),
              ("Compounded quality","Prepared by a licensed US pharmacy to a consistent strength.")],
    whats_included=wi_oral("Low-dose naltrexone capsules"),
    faq_heading='Questions about<br><span class="serif">LDN?</span>',
    faq=[("What is low-dose naltrexone?","Naltrexone is an FDA-approved medication at higher doses; LDN uses a much smaller, compounded dose for off-label wellness, autoimmune, and pain protocols."),
         ("Is the off-label use proven?","Interest is strong and some studies are encouraging, but evidence is still developing. Your provider will set honest expectations."),
         ("How is it taken?","Usually a once-daily capsule, often at night, per your provider's directions."),
         ("Can I take it with opioids?","No. Naltrexone blocks opioids, so it must not be used with opioid pain medications or by those dependent on opioids. Tell your provider about all medications."),
         ("Who should not use it?","Those taking opioids, with acute hepatitis or liver failure, or who are pregnant should not use it without specialist input. Share your full history with your provider.")],
    isi="Low-dose naltrexone (LDN) is a prescription, compounded medication used off-label. These statements have not been evaluated by the Food and Drug Administration. Compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. Naltrexone blocks opioids and must not be used by individuals taking opioid medications or dependent on opioids, and is not appropriate in acute hepatitis or liver failure. Use in pregnancy requires specialist guidance. Inform your provider of all conditions and medications. The decision to begin therapy should be made with a licensed provider. Individual results may vary.",
    cta_heading='Explore an<br><span class="serif">LDN protocol?</span>'),
]

def main():
    seen = set()
    for c in CONTENT:
        if c["slug"] in seen:
            sys.exit(f"duplicate slug {c['slug']}")
        seen.add(c["slug"])
        out = PRODUCTS / f"{c['slug']}.html"
        out.write_text(page(c), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}  ({len(page(c).splitlines())} lines)")
    print(f"\n{len(CONTENT)} pages generated.")

if __name__ == "__main__":
    main()
