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

SKIN = dict(hub="skin-hair", hub_name="Skin & Hair", hub_url="/preview/hubs/skin-hair.html")

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
