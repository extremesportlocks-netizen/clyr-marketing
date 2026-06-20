#!/usr/bin/env python3
"""Generate dark/premium IMAGE-FREE product-detail previews under preview/products2/.
Clones the tirzepatide template structure; links shared /preview/assets/clyr-vibe.css.
Run from repo root: python3 scripts/build-dark-product-pages.py
"""
import os

OUT = "preview/products2"
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>'
PLUS = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'
ICONS = [
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="8" width="12" height="13" rx="2"/><path d="M9 8V4h6v4"/></svg>',
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="6" width="13" height="11" rx="1"/><path d="M14 9h4l3 3v5h-7z"/></svg>',
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9"/><path d="M3 4v5h5"/></svg>',
]

NAV = '''<nav class="nav" id="nav"><div class="nav-inner">
  <a href="/" aria-label="CLYR home"><svg viewBox="0 0 120 32" height="30"><text x="0" y="25" font-family="DM Sans,sans-serif" font-weight="700" font-size="27" letter-spacing="-1"><tspan fill="#fff">CLY</tspan><tspan fill="#00B4C5">R</tspan></text></svg></a>
  <div class="nav-links">
    <a href="/preview/weight-loss.html">Weight Loss</a>
    <a href="/preview/daily-wellness.html">Daily Wellness</a>
    <a href="/preview/hubs2/mens-hormone.html">Men's Hormone</a>
    <a href="/preview/hubs2/womens-hormone.html">Women's Hormone</a>
    <a href="/preview/hubs2/skin-hair.html">Skin &amp; Hair</a>
    <a href="/preview/sexual-health.html">Sexual Health</a>
    <a href="/preview/hubs2/peptides.html">Peptides</a>
    <a href="/portal/">Patient Portal</a>
    <a href="@@INTAKE@@" class="nav-cta">Get Started</a>
  </div>
  <button class="mob" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')"><span></span><span></span><span></span></button>
</div></nav>'''

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-T4FVQ87G');</script>
<!-- End Google Tag Manager -->
<meta charset="UTF-8">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@ | CLYR Health (preview)</title>
<meta name="description" content="@@METADESC@@">
<meta property="og:title" content="@@OGTITLE@@ | CLYR Health">
<meta property="og:description" content="@@OGDESC@@">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/preview/assets/clyr-vibe.css">
</head>
<body@@BODYSTYLE@@>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-T4FVQ87G" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

''' + NAV + '''

<header class="hero"><div class="wrap">
  <div class="hero-eyebrow">@@EYEBROW@@</div>
  <h1>@@H1MAIN@@ <span class="serif">@@H1SERIF@@</span></h1>
  <p>@@DECK@@</p>
  <div class="pills">
@@PILLS@@
  </div>
  <div class="hero-actions" style="margin-top:30px">
    <a href="@@INTAKE@@" class="btn btn-p">Start your visit ''' + ARROW + '''</a>
    <a href="#plans" class="btn btn-g">See pricing</a>
  </div>
</div></header>

<div class="strip"><div class="strip-inner">
@@STRIP@@
</div></div>

<section class="sec wrap">
  <div class="sec-label">At a Glance</div>
  <h2>The essentials, <span class="serif">up front.</span></h2>
  <div class="facts">
@@FACTS@@
  </div>
</section>

<section class="sec wrap" id="plans">
  <div class="sec-label">Pricing</div>
  <h2>@@PRICEH2MAIN@@ <span class="serif">@@PRICEH2SERIF@@</span></h2>
  <p class="lede">@@PRICELEDE@@</p>
  <div class="plans">
@@PLANS@@
  </div>
  <div class="hero-actions" style="margin-top:26px"><a href="@@INTAKE@@" class="btn btn-p">Check your eligibility ''' + ARROW + '''</a></div>
</section>

<section class="sec wrap">
  <div class="sec-label">The Details</div>
  <h2>What you are <span class="serif">actually getting.</span></h2>
  <div class="prose">
@@PROSE@@
  </div>
</section>

<section class="sec wrap">
  <div class="sec-label">How It Works</div>
  <h2>Sorted in <span class="serif">minutes.</span></h2>
  <div class="steps">
    <div class="step"><div class="n">1</div><h4>Two-minute visit</h4><p>Answer a short health questionnaire online. No appointment, no waiting room.</p></div>
    <div class="step"><div class="n">2</div><h4>A provider reviews</h4><p>A licensed U.S. provider confirms @@PNAME@@ is appropriate for you.</p></div>
    <div class="step"><div class="n">3</div><h4>It ships discreetly</h4><p>Plain packaging at your door, with refills on your schedule.</p></div>
  </div>
</section>

<section class="sec wrap">
  <div class="sec-label">Real Talk</div>
  <h2>Questions, <span class="serif">answered straight.</span></h2>
  <div class="faq" style="margin-top:34px">
@@FAQS@@
  </div>
</section>

<section class="cta"><div class="wrap">
  <h2>@@CTAH2MAIN@@ <span class="serif">@@CTAH2SERIF@@</span></h2>
  <p>@@CTAP@@</p>
  <a href="@@INTAKE@@" class="btn btn-p">Start your visit ''' + ARROW + '''</a>
</div></div></section>

<div class="isi"><div class="wrap">
  <h3>Important Safety Information</h3>
  <p>@@ISI@@</p>
</div></div>

<footer class="foot"><div class="wrap">
  <div class="foot-row">
    <p>&copy; 2026 CLYR Health. All rights reserved.</p>
    <div class="foot-legal">
      <a href="/privacy.html">Privacy</a>
      <a href="/terms.html">Terms</a>
      <a href="/telehealth-consent.html">Telehealth Consent</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
</div></footer>
</body>
</html>
'''

def f_pills(xs): return "\n".join(f'    <span class="pill">{x}</span>' for x in xs)
def f_strip(xs): return "\n".join(f'  <span>{ICONS[i%4]}{x}</span>' for i,x in enumerate(xs))
def f_facts(xs): return "\n".join(f'    <div class="fact"><div class="k">{k}</div><div class="v">{v}</div></div>' for k,v in xs)
def f_plans(xs):
    out=[]
    for p in xs:
        feat=" feat" if p.get("feat") else ""
        out.append(f'    <div class="plan{feat}"><div class="ptier">{p["tier"]}</div><div class="amt">{p["amt"]}<small> {p["small"]}</small></div><div class="sub">{p["sub"]}</div></div>')
    return "\n".join(out)
def f_prose(xs):
    out=[]
    for kind,h,body in xs:
        out.append(f'    <h3>{h}</h3>')
        if kind=="p": out.append(f'    <p>{body}</p>')
        else: out.append('    <ul>'+''.join(f'<li>{i}</li>' for i in body)+'</ul>')
    return "\n".join(out)
def f_faqs(xs):
    out=[]
    for q,a in xs:
        out.append(f'    <div class="q"><button onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">{q}{PLUS}</button><div class="a"><p>{a}</p></div></div>')
    return "\n".join(out)

ISI_GLP = ("This is a prescription medication provided only after review by a licensed provider; not everyone qualifies. "
 "GLP-1 medications should not be used by individuals with a personal or family history of medullary thyroid carcinoma or "
 "multiple endocrine neoplasia syndrome type 2, and carry risks including pancreatitis, gallbladder problems, and "
 "gastrointestinal effects. Not for use in pregnancy. Tell your provider about all medications and conditions. Individual results vary.")
ISI_GLP_C = ISI_GLP[:-46] + ("This product is compounded; compounded medications are not FDA-approved and are not reviewed by the FDA for safety, "
 "efficacy, or quality before reaching patients. Tell your provider about all medications and conditions. Individual results vary.")
ISI_ED = ("This is a prescription medication provided only after review by a licensed provider; not everyone qualifies. "
 "PDE5 inhibitors must never be combined with nitrate medications and are not appropriate for men with certain cardiovascular "
 "conditions. Seek emergency care for an erection lasting more than four hours. Some products are compounded; compounded "
 "medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, or quality before reaching patients. "
 "Tell your provider about all medications and conditions. Individual results vary.")
ISI_WELL = ("This is a prescription treatment provided only after review by a licensed provider; not everyone qualifies. "
 "This product is compounded; compounded medications are not FDA-approved and are not reviewed by the FDA for safety, efficacy, "
 "or quality before reaching patients. Avoid during pregnancy or breastfeeding unless your provider advises otherwise. "
 "Tell your provider about all medications and conditions. Individual results vary.")
ISI_ANTI = ("These are prescription protocols provided only after review by a licensed provider; not everyone qualifies. "
 "They are compounded by a licensed 503A pharmacy; compounded medications are not FDA-approved and are not reviewed by the FDA "
 "for safety, efficacy, or quality before reaching patients. Ivermectin and mebendazole can interact with other medications and "
 "are not appropriate for everyone, including during pregnancy. Tell your provider about all medications and conditions. Individual results vary.")
ISI_BRAND = ("This is an FDA-approved prescription medication provided only after review by a licensed provider; not everyone qualifies. "
 "GLP-1 medications should not be used by individuals with a personal or family history of medullary thyroid carcinoma or "
 "multiple endocrine neoplasia syndrome type 2, and carry risks including pancreatitis, gallbladder problems, and gastrointestinal "
 "effects. Not for use in pregnancy. Tell your provider about all medications and conditions. Individual results vary.")

WL='<a href="/preview/weight-loss.html" style="color:var(--teal)">Weight Loss</a>'
DW='<a href="/preview/daily-wellness.html" style="color:var(--teal)">Daily Wellness</a>'
SH='<a href="/preview/sexual-health.html" style="color:var(--teal)">Sexual Health</a>'
AP='<a href="/preview/antiparasitic.html" style="color:var(--teal)">Antiparasitic</a>'
INTAKE_W="/intake-wellness.html?product="
INTAKE_M="/intake.html?product="

P=[]
P.append(dict(slug="sermorelin",title="Sermorelin",metadesc="Sermorelin, a growth-hormone-releasing peptide for sleep, recovery, and lean mass, prescribed by licensed US providers from $149/mo.",ogtitle="Sermorelin",ogdesc="A GH peptide for sleep, recovery, and lean mass. From $149/mo. Licensed providers.",intake=INTAKE_W+"sermorelin",eyebrow=DW+" &middot; Recovery",h1m="Sermorelin",h1s="peptide.",pname="sermorelin",
 deck="A growth-hormone-releasing peptide used to support deep sleep, recovery, and lean muscle. Prescribed and supervised by a licensed US provider, compounded by a licensed US pharmacy, and delivered to your door.",
 pills=["GH-releasing peptide","Sleep &amp; recovery","Nightly subcutaneous","Provider-supervised"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("Class","GHRH peptide"),("Focus","Sleep, recovery, lean mass"),("Cadence","Nightly, as directed"),("Route","Subcutaneous")],
 ph2m="Simple monthly",ph2s="pricing.",plede="One straightforward rate, with a lower effective cost when you prepay for several months.",
 plans=[dict(tier="Monthly",amt="$149",small="/mo",sub="Provider consultation, medication, and supplies included.",feat=True),dict(tier="6-Month",amt="$894",small="/ 6 mo",sub="A lower effective monthly rate when you prepay.")],
 prose=[("p","How it works","Sermorelin prompts your own pituitary to release growth hormone in natural pulses, rather than introducing growth hormone directly. It is typically dosed at night to match the body's own rhythm."),("ul","What is included",["Provider consultation and protocol","Medication compounded by a licensed US pharmacy, plus supplies","Free, discreet shipping"])],
 faqs=[("Is this the same as HGH?","No. Sermorelin encourages your body to release its own growth hormone in natural pulses, rather than injecting growth hormone directly."),("When is it taken?","Usually at night, on an empty stomach, to align with your body's natural release of growth hormone. Your provider gives you the schedule."),("Who should not use it?","It should be avoided in pregnancy or breastfeeding and by people with active cancer. Share your full history with your provider."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Recover like",ctas="you train.",ctap="A short visit, a real provider, delivered to your door. Start when you are ready.",isi=ISI_WELL))

P.append(dict(slug="glutathione",title="Glutathione",metadesc="Injectable glutathione, the master antioxidant for detox, immune, and skin support, prescribed by licensed US providers from $109/mo.",ogtitle="Glutathione",ogdesc="The master antioxidant for detox, immune, and skin support. From $109/mo. Licensed providers.",intake=INTAKE_W+"glutathione",eyebrow=DW+" &middot; Antioxidant",h1m="Glutathione",h1s="injections.",pname="glutathione",
 deck="The body's master antioxidant, delivered as an injection to support detoxification, immune function, and skin. Prescribed and supervised by a licensed US provider and delivered to your door.",
 pills=["Master antioxidant","Detox &amp; immune","Subcutaneous","Provider-supervised"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("What it is","Glutathione antioxidant"),("Focus","Detox, immune, skin"),("Cadence","As directed"),("Route","Subcutaneous")],
 ph2m="Simple monthly",ph2s="pricing.",plede="One straightforward rate, lower per month when you prepay for several months.",
 plans=[dict(tier="Monthly",amt="$109",small="/mo",sub="Provider consultation, medication, and supplies included.",feat=True),dict(tier="6-Month",amt="$654",small="/ 6 mo",sub="A lower effective monthly rate when you prepay.")],
 prose=[("p","Why injectable","Oral glutathione is largely broken down during digestion, so the injectable route is used to deliver it more directly. It is the body's central antioxidant and supports the liver's detox pathways."),("ul","What is included",["Provider consultation and protocol","Medication compounded by a licensed US pharmacy, plus supplies","Free, discreet shipping"])],
 faqs=[("What does glutathione do?","It is the body's primary antioxidant, involved in neutralizing free radicals, supporting the immune system, and the liver's detox pathways."),("Why an injection?","Oral glutathione is poorly absorbed, so the injectable route is used to get more of it into the bloodstream."),("Who should not use it?","Avoid during pregnancy or breastfeeding unless your provider advises otherwise. Share your full history with your provider."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Feel like",ctas="yourself again.",ctap="A short visit, a real provider, delivered to your door. Start when you are ready.",isi=ISI_WELL))

P.append(dict(slug="micc",title="MICC + B12",metadesc="MICC plus B12 lipotropic injections for metabolism and steady energy, prescribed by licensed US providers from $129/mo.",ogtitle="MICC + B12",ogdesc="Methionine, inositol, choline, and B12 for metabolism and energy. From $129/mo. Licensed providers.",intake=INTAKE_W+"micc",eyebrow=DW+" &middot; Energy",h1m="MICC",h1s="+ B12.",pname="MICC",
 deck="A lipotropic blend of methionine, inositol, choline, and B12 to support fat metabolism and steady energy. Prescribed and supervised by a licensed US provider and delivered to your door.",
 pills=["Lipotropic blend","Metabolism &amp; energy","Subcutaneous","Provider-supervised"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("What it is","Methionine, inositol, choline, B12"),("Focus","Metabolism, energy"),("Cadence","As directed"),("Route","Subcutaneous")],
 ph2m="Simple monthly",ph2s="pricing.",plede="One straightforward monthly rate. Often paired with a GLP-1 plan.",
 plans=[dict(tier="Monthly",amt="$129",small="/mo",sub="Provider consultation, medication, and supplies included.",feat=True)],
 prose=[("p","What is in it","Methionine, inositol, and choline are lipotropic compounds that support the body's handling of fat, combined with B12 for energy. It is often used alongside a weight management plan."),("ul","What is included",["Provider consultation and protocol","Medication compounded by a licensed US pharmacy, plus supplies","Free, discreet shipping"])],
 faqs=[("What is a lipotropic injection?","A blend of compounds that support how the body metabolizes fat, combined here with B12 for energy."),("Can I use it with a GLP-1?","Often, yes. Many people pair MICC with a weight management plan. Your provider reviews everything together."),("Who should not use it?","Avoid during pregnancy or breastfeeding unless your provider advises otherwise. Share your full history with your provider."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Run on",ctas="full.",ctap="A short visit, a real provider, delivered to your door. Start when you are ready.",isi=ISI_WELL))

P.append(dict(slug="lipo-mino",title="Lipo-Mino + L-Carnitine",metadesc="Lipo-Mino with L-carnitine, a lipotropic injection for fat metabolism and energy, prescribed by licensed US providers from $129/mo.",ogtitle="Lipo-Mino + L-Carnitine",ogdesc="Lipotropic plus L-carnitine for fat metabolism and energy. From $129/mo. Licensed providers.",intake=INTAKE_W+"lipo-mino",eyebrow=WL+" &middot; Add-On",h1m="Lipo-Mino",h1s="+ L-Carnitine.",pname="Lipo-Mino",
 deck="A lipotropic injection with added L-carnitine to support fat metabolism and energy, designed to pair with any weight management plan. Prescribed and supervised by a licensed US provider.",
 pills=["Lipotropic + L-carnitine","Fat metabolism","Subcutaneous","Pairs with any GLP-1"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("What it is","Lipotropic blend + L-carnitine"),("Focus","Fat metabolism, energy"),("Cadence","As directed"),("Route","Subcutaneous")],
 ph2m="Simple monthly",ph2s="pricing.",plede="One straightforward monthly rate. A common add-on to a GLP-1 plan.",
 plans=[dict(tier="Monthly",amt="$129",small="/mo",sub="Provider consultation, medication, and supplies included.",feat=True)],
 prose=[("p","What is in it","A lipotropic blend that supports the body's handling of fat, with L-carnitine, which is involved in turning fat into usable energy. It is built to complement a broader weight plan."),("ul","What is included",["Provider consultation and protocol","Medication compounded by a licensed US pharmacy, plus supplies","Free, discreet shipping"])],
 faqs=[("How is this different from MICC?","Lipo-Mino adds L-carnitine to the lipotropic blend. Your provider can help you choose between them."),("Can I stack it with a GLP-1?","Yes, it is designed as an add-on to a weight management plan. Your provider reviews everything together."),("Who should not use it?","Avoid during pregnancy or breastfeeding unless your provider advises otherwise. Share your full history with your provider."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Lighter,",ctas="on your terms.",ctap="A short visit, a real provider, delivered to your door. Start when you are ready.",isi=ISI_WELL))

P.append(dict(slug="tadalafil",title="Tadalafil + Vardenafil",metadesc="Daily tadalafil with vardenafil for everyday readiness, prescribed by licensed US providers from $74.92/mo.",ogtitle="Tadalafil + Vardenafil",ogdesc="A daily ED tablet so you are ready without planning. From $74.92/mo. Licensed providers.",intake=INTAKE_W+"tadalafil",eyebrow=SH+" &middot; Daily",h1m="Tadalafil",h1s="+ Vardenafil.",pname="this treatment",
 deck="A daily tablet combining two PDE5 inhibitors so you are ready without planning around the moment. Prescribed by a licensed US provider, compounded by a licensed US pharmacy, and delivered discreetly.",
 pills=["Daily PDE5 tablet","No planning","Discreet","Provider-reviewed"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("Class","PDE5 inhibitors"),("Use","Daily"),("Onset","Always-ready approach"),("Route","Oral tablet")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A daily option priced as a low effective monthly rate, lower again when you prepay.",
 plans=[dict(tier="Monthly",amt="$74.92",small="/mo",sub="Effective monthly rate. Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","Daily, not on-demand","A low daily dose keeps a PDE5 inhibitor in your system so you do not have to time anything. It pairs tadalafil with vardenafil under provider direction."),("ul","What is included",["Provider consultation and review","Medication compounded by a licensed US pharmacy","Free, discreet shipping"])],
 faqs=[("Daily or on-demand?","This is the daily option, so you are ready without planning. If you prefer to dose before the moment, ask about the on-demand gummies or ODT."),("Can I drink alcohol with it?","Moderate alcohol is usually fine, but heavy drinking can worsen side effects and lower blood pressure. Your provider will advise."),("Who should not take it?","Anyone on nitrates, and men with certain heart conditions, should not use PDE5 inhibitors. Your provider screens for this."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Own the",ctas="moment.",ctap="A short visit, a real provider, delivered discreetly. Start when you are ready.",isi=ISI_ED))

P.append(dict(slug="sildenafil-gummy",title="Sildenafil Gummy",metadesc="Fast-acting sildenafil gummies for on-demand performance, prescribed by licensed US providers from $74/mo.",ogtitle="Sildenafil Gummy",ogdesc="Fast-acting, chewable, on-demand. From $74/mo. Licensed providers, discreet shipping.",intake=INTAKE_W+"sildenafil-gummy",eyebrow=SH+" &middot; On-Demand",h1m="Sildenafil",h1s="gummy.",pname="this treatment",
 deck="Fast-acting sildenafil in a chewable gummy, taken before the moment with no water and no pill to swallow. Prescribed by a licensed US provider and delivered discreetly.",
 pills=["On-demand PDE5","Chewable, no water","Fast onset","Provider-reviewed"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("Class","PDE5 inhibitor"),("Use","On-demand"),("Form","Chewable gummy"),("Route","Oral")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A low effective monthly rate for a month's supply, lower again when you prepay.",
 plans=[dict(tier="Monthly",amt="$74",small="/mo",sub="Effective monthly rate. Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","On-demand, made easy","A chewable format that is taken ahead of the moment, useful if you would rather not swallow a tablet. Onset is generally faster than a standard tablet."),("ul","What is included",["Provider consultation and review","Medication compounded by a licensed US pharmacy","Free, discreet shipping"])],
 faqs=[("How soon does it work?","Chewable formats are generally absorbed faster than swallowed tablets. Your provider will set expectations for timing."),("With or without food?","Heavy, fatty meals can slow absorption. Your provider will advise on timing around food."),("Who should not take it?","Anyone on nitrates, and men with certain heart conditions, should not use PDE5 inhibitors. Your provider screens for this."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Own the",ctas="moment.",ctap="A short visit, a real provider, delivered discreetly. Start when you are ready.",isi=ISI_ED))

P.append(dict(slug="sild-tadal-oxy",title="Combo ODT",metadesc="A dissolvable combining sildenafil, tadalafil, and oxytocin for triple-action on-demand support, prescribed by licensed US providers from $109/mo.",ogtitle="Combo ODT",ogdesc="Sildenafil, tadalafil, and oxytocin in one dissolvable. From $109/mo. Licensed providers.",intake=INTAKE_W+"sild-tadal-oxy",eyebrow=SH+" &middot; On-Demand",h1m="Combo",h1s="ODT.",pname="this treatment",
 deck="An orally dissolving tablet that combines two PDE5 inhibitors with oxytocin for a triple-action, on-demand option. Prescribed by a licensed US provider and delivered discreetly.",
 pills=["Two PDE5s + oxytocin","On-demand","Dissolvable","Provider-reviewed"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("What it is","Sildenafil + tadalafil + oxytocin"),("Use","On-demand"),("Form","Dissolvable tablet"),("Route","Sublingual")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A low effective monthly rate for a month's supply, lower again when you prepay.",
 plans=[dict(tier="Monthly",amt="$109",small="/mo",sub="Effective monthly rate. Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","Three actions, one tablet","Combines the fast onset of sildenafil, the longer window of tadalafil, and oxytocin, in a single dissolvable tablet taken ahead of the moment."),("ul","What is included",["Provider consultation and review","Medication compounded by a licensed US pharmacy","Free, discreet shipping"])],
 faqs=[("Why combine three ingredients?","To pair fast onset, a longer window, and oxytocin in one on-demand option. Your provider decides if it fits you."),("How is it taken?","It dissolves in the mouth ahead of the moment, so there is no pill to swallow."),("Who should not take it?","Anyone on nitrates, and men with certain heart conditions, should not use PDE5 inhibitors. Your provider screens for this."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Own the",ctas="moment.",ctap="A short visit, a real provider, delivered discreetly. Start when you are ready.",isi=ISI_ED))

P.append(dict(slug="pt141",title="PT-141",metadesc="PT-141 (bremelanotide) for desire and libido in men and women, prescribed by licensed US providers from $83/mo.",ogtitle="PT-141",ogdesc="For desire, not just performance. Works on libido for men and women. From $83/mo.",intake=INTAKE_W+"pt141",eyebrow=SH+" &middot; Desire",h1m="PT-141",h1s="for desire.",pname="PT-141",
 deck="A peptide that works on desire itself, through the brain rather than blood flow, for both men and women. Prescribed by a licensed US provider and delivered discreetly.",
 pills=["Libido peptide","Men &amp; women","On-demand","Provider-reviewed"],
 strip=["Licensed U.S. providers","Compounded at licensed US pharmacies","Discreet shipping","Cancel anytime"],
 facts=[("What it is","Bremelanotide peptide"),("Focus","Desire and libido"),("Use","On-demand"),("Route","Subcutaneous")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A low effective monthly rate, lower again when you prepay for several months.",
 plans=[dict(tier="Monthly",amt="$83",small="/mo",sub="Effective monthly rate. Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","Desire, not just plumbing","Unlike PDE5 inhibitors, which act on blood flow, PT-141 works on pathways in the brain tied to sexual desire. That makes it relevant when the issue is wanting, not just performing, and it is used by both men and women."),("ul","What is included",["Provider consultation and review","Medication compounded by a licensed US pharmacy, plus supplies","Free, discreet shipping"])],
 faqs=[("How is PT-141 different from ED pills?","ED pills act on blood flow; PT-141 acts on desire pathways in the brain. They address different parts of the picture."),("Can women use it?","Yes. PT-141 is used for low desire in both men and women, subject to provider review."),("What are common side effects?","Nausea and a temporary rise in blood pressure are the most commonly reported. Your provider will review your suitability."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Want it",ctas="again.",ctap="A short visit, a real provider, delivered discreetly. Start when you are ready.",isi=ISI_WELL))

P.append(dict(slug="ivermectin",title="Ivermectin Protocol",metadesc="Provider-prescribed compounded ivermectin, dosed by a licensed US provider and filled by a licensed 503A pharmacy, from $139/mo.",ogtitle="Ivermectin Protocol",ogdesc="Provider-prescribed, single-agent antiparasitic. From $139/mo. Licensed providers and pharmacy.",intake=INTAKE_W+"ivermectin",eyebrow=AP+" &middot; Single Agent",h1m="Ivermectin",h1s="protocol.",pname="this protocol",
 deck="A provider-prescribed, single-agent antiparasitic protocol. Compounded 18 mg ivermectin capsules, dosed by a licensed US provider and filled by a licensed 503A pharmacy. Discreet, tracked shipping.",
 pills=["Single antiparasitic","Compounded 18 mg","Provider-dosed","30-day supply"],
 strip=["Licensed U.S. providers","Licensed 503A pharmacy","Discreet 2-day shipping","Cancel anytime"],
 facts=[("What it is","Ivermectin"),("Strength","18 mg capsules"),("Supply","30 days"),("Route","Oral")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A flat monthly rate, lower per month when you prepay for three months.",
 plans=[dict(tier="Monthly",amt="$139",small="/mo",sub="Provider review, medication, and shipping included.",feat=True),dict(tier="3-Month",amt="$369",small="/ 3 mo",sub="A lower effective monthly rate when you prepay.")],
 prose=[("p","Provider-dosed, pharmacy-filled","Marketplace and offshore sellers operate without a US provider or pharmacy on record. Here, a named provider writes the prescription and a licensed 503A pharmacy compounds it to a precise dose."),("ul","What is included",["Provider review of your intake and history","Compounded ivermectin from a licensed 503A pharmacy","Free, discreet, tracked shipping"])],
 faqs=[("How is my dose decided?","It is based on your medical history and the other medications you take, which your provider reviews for interactions before approving anything."),("How is this different from buying online?","Marketplace and offshore products have no US provider or pharmacy on record. With CLYR, a named provider and a licensed US pharmacy stand behind every order."),("Should I add mebendazole?","Some people choose the dual protocol for broader coverage. Your provider will advise which fits."),("Is it legit?","A licensed U.S. provider writes the prescription and a licensed U.S. pharmacy fills it. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="See if it",ctas="fits you.",ctap="Take the two-minute eligibility check and a licensed provider reviews your case.",isi=ISI_ANTI))

P.append(dict(slug="ivermectin-mebendazole",title="Ivermectin + Mebendazole",metadesc="Provider-prescribed dual antiparasitic protocol combining ivermectin with mebendazole for broader coverage, from $169/mo.",ogtitle="Ivermectin + Mebendazole",ogdesc="Dual antiparasitic for broader coverage. From $169/mo. Licensed providers and 503A pharmacy.",intake=INTAKE_W+"ivermectin-mebendazole",eyebrow=AP+" &middot; Dual Agent",h1m="Ivermectin",h1s="+ Mebendazole.",pname="this protocol",
 deck="A provider-prescribed dual antiparasitic protocol, adding mebendazole to ivermectin for a second mechanism and broader coverage. Dosed by a licensed US provider and filled by a licensed 503A pharmacy.",
 pills=["Dual antiparasitic","18 mg + 25/250 mg","Provider-dosed","30-day supply"],
 strip=["Licensed U.S. providers","Licensed 503A pharmacy","Discreet 2-day shipping","Cancel anytime"],
 facts=[("What it is","Ivermectin + mebendazole"),("Strength","18 mg + 25/250 mg"),("Supply","30 days"),("Route","Oral")],
 ph2m="Simple monthly",ph2s="pricing.",plede="A flat monthly rate, lower per month when you prepay for three months.",
 plans=[dict(tier="Monthly",amt="$169",small="/mo",sub="Provider review, medication, and shipping included.",feat=True),dict(tier="3-Month",amt="$449",small="/ 3 mo",sub="A lower effective monthly rate when you prepay.")],
 prose=[("p","Two mechanisms","Adds mebendazole, which works differently from ivermectin, for broader coverage. Both are compounded to precise doses by a licensed 503A pharmacy under provider direction."),("ul","What is included",["Provider review of your intake and history","Compounded ivermectin and mebendazole from a licensed 503A pharmacy","Free, discreet, tracked shipping"])],
 faqs=[("Why mebendazole rather than fenbendazole?","Mebendazole is intended for human use with a long track record, and a licensed US pharmacy can compound it precisely. Fenbendazole is an animal product with no human approval."),("How is my dose decided?","Based on your medical history and other medications, which your provider reviews for interactions before approving."),("Single or dual protocol?","The dual protocol adds coverage; the single ivermectin protocol is simpler. Your provider helps you choose."),("Is it legit?","A licensed U.S. provider writes the prescription and a licensed U.S. pharmacy fills it. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="See if it",ctas="fits you.",ctap="Take the two-minute eligibility check and a licensed provider reviews your case.",isi=ISI_ANTI))

P.append(dict(slug="foundayo",title="Foundayo (Orforglipron)",metadesc="Foundayo, a daily oral GLP-1 tablet from Eli Lilly, prescribed by licensed US providers from $299/mo.",ogtitle="Foundayo (Orforglipron)",ogdesc="Daily oral GLP-1 tablet from Eli Lilly. No injections. From $299/mo. Licensed providers.",intake=INTAKE_M+"foundayo",eyebrow=WL+" &middot; Brand &middot; Oral",h1m="Foundayo",h1s="(Orforglipron).",pname="Foundayo",
 deck="A daily oral GLP-1 tablet from Eli Lilly, with no injections and no refrigeration. Prescribed by a licensed US provider and delivered to your door.",
 pills=["Brand-name GLP-1","Daily oral tablet","No injections","Provider-reviewed"],
 strip=["Licensed U.S. providers","Brand-name from Eli Lilly","Discreet shipping","Cancel anytime"],
 facts=[("Class","GLP-1 agonist"),("Maker","Eli Lilly"),("Form","Daily oral tablet"),("Route","Oral")],
 ph2m="Brand-name",ph2s="pricing.",plede="A straightforward monthly rate for the brand-name oral GLP-1.",
 plans=[dict(tier="Monthly",amt="$299",small="/mo",sub="Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","Oral, no needles","Foundayo (orforglipron) is a once-daily GLP-1 tablet, an option for people who would rather not inject and prefer a brand-name product. No refrigeration required."),("ul","What is included",["Provider consultation and ongoing management","Brand-name medication","Free, discreet shipping"])],
 faqs=[("Is this brand-name or compounded?","Brand-name, made by Eli Lilly. If you would prefer a lower-cost compounded option, ask your provider about compounded tirzepatide or semaglutide."),("Injection or pill?","Foundayo is a daily oral tablet, no injections."),("What are common side effects?","Gastrointestinal effects such as nausea are most common with GLP-1 medications, especially early on."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Lighter,",ctas="on your terms.",ctap="Two minutes online. A real provider. Delivered to your door. Start when you are ready.",isi=ISI_BRAND))

P.append(dict(slug="zepbound",title="Zepbound (Tirzepatide)",metadesc="Zepbound, FDA-approved tirzepatide from Eli Lilly in a pre-filled KwikPen, prescribed by licensed US providers from $499/mo.",ogtitle="Zepbound (Tirzepatide)",ogdesc="FDA-approved tirzepatide KwikPen from Eli Lilly. From $499/mo. Licensed providers.",intake=INTAKE_M+"zepbound",eyebrow=WL+" &middot; Brand &middot; FDA-Approved",h1m="Zepbound",h1s="(Tirzepatide).",pname="Zepbound",
 deck="FDA-approved tirzepatide from Eli Lilly, in a pre-filled KwikPen with no mixing. Prescribed by a licensed US provider and delivered to your door.",
 pills=["Brand-name GLP-1/GIP","FDA-approved","Pre-filled KwikPen","Provider-reviewed"],
 strip=["Licensed U.S. providers","FDA-approved, Eli Lilly","Discreet shipping","Cancel anytime"],
 facts=[("Class","GLP-1 / GIP agonist"),("Maker","Eli Lilly"),("Form","Pre-filled KwikPen"),("Route","Subcutaneous")],
 ph2m="Brand-name",ph2s="pricing.",plede="A straightforward monthly rate for the FDA-approved brand-name product.",
 plans=[dict(tier="Monthly",amt="$499",small="/mo",sub="Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","The brand-name dual agonist","Zepbound is the FDA-approved brand-name form of tirzepatide, the dual GLP-1 and GIP agonist, delivered in a pre-filled pen with no mixing or measuring."),("ul","What is included",["Provider consultation and ongoing management","FDA-approved brand-name medication","Free, discreet shipping"])],
 faqs=[("Brand-name or compounded?","Zepbound is the brand-name, FDA-approved product. If you would prefer a lower-cost option, ask your provider about compounded tirzepatide."),("How is it taken?","A once-weekly injection from a pre-filled KwikPen, no mixing required."),("What are common side effects?","Gastrointestinal effects such as nausea are most common, especially early on."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Lighter,",ctas="on your terms.",ctap="Two minutes online. A real provider. Delivered to your door. Start when you are ready.",isi=ISI_BRAND))

P.append(dict(slug="wegovy-tablets",title="Wegovy Tablets",metadesc="Wegovy oral semaglutide tablets from Novo Nordisk, prescribed by licensed US providers from $299/mo.",ogtitle="Wegovy Tablets",ogdesc="Daily oral semaglutide from Novo Nordisk. No needles. From $299/mo. Licensed providers.",intake=INTAKE_M+"wegovy-tablets",eyebrow=WL+" &middot; Brand &middot; Oral",h1m="Wegovy",h1s="Tablets.",pname="Wegovy",
 deck="Daily oral semaglutide tablets from Novo Nordisk, a brand-name GLP-1 with no needles. Prescribed by a licensed US provider and delivered to your door.",
 pills=["Brand-name GLP-1","Daily oral tablet","No needles","Provider-reviewed"],
 strip=["Licensed U.S. providers","Brand-name, Novo Nordisk","Discreet shipping","Cancel anytime"],
 facts=[("Class","GLP-1 agonist"),("Maker","Novo Nordisk"),("Form","Daily oral tablet"),("Route","Oral")],
 ph2m="Brand-name",ph2s="pricing.",plede="A straightforward monthly rate for the brand-name oral GLP-1.",
 plans=[dict(tier="Monthly",amt="$299",small="/mo",sub="Provider consultation, medication, and shipping included.",feat=True)],
 prose=[("p","Oral, no needles","Wegovy tablets are a once-daily oral form of semaglutide from Novo Nordisk, an option for people who prefer a brand-name product without injections."),("ul","What is included",["Provider consultation and ongoing management","Brand-name medication","Free, discreet shipping"])],
 faqs=[("Brand-name or compounded?","Brand-name, made by Novo Nordisk. If you would prefer a lower-cost compounded option, ask your provider about compounded semaglutide."),("Injection or pill?","Wegovy tablets are a daily oral form, no needles."),("What are common side effects?","Gastrointestinal effects such as nausea are most common with GLP-1 medications, especially early on."),("Is it legit?","Every prescription comes from a licensed U.S. provider and is filled by a licensed U.S. pharmacy. CLYR is LegitScript certified and HIPAA compliant.")],
 ctam="Lighter,",ctas="on your terms.",ctap="Two minutes online. A real provider. Delivered to your door. Start when you are ready.",isi=ISI_BRAND))

os.makedirs(OUT, exist_ok=True)
for p in P:
    html = (TEMPLATE
        .replace("@@BODYSTYLE@@", "")
        .replace("@@TITLE@@", p["title"])
        .replace("@@METADESC@@", p["metadesc"])
        .replace("@@OGTITLE@@", p["ogtitle"])
        .replace("@@OGDESC@@", p["ogdesc"])
        .replace("@@INTAKE@@", p["intake"])
        .replace("@@EYEBROW@@", p["eyebrow"])
        .replace("@@H1MAIN@@", p["h1m"])
        .replace("@@H1SERIF@@", p["h1s"])
        .replace("@@DECK@@", p["deck"])
        .replace("@@PILLS@@", f_pills(p["pills"]))
        .replace("@@STRIP@@", f_strip(p["strip"]))
        .replace("@@FACTS@@", f_facts(p["facts"]))
        .replace("@@PRICEH2MAIN@@", p["ph2m"])
        .replace("@@PRICEH2SERIF@@", p["ph2s"])
        .replace("@@PRICELEDE@@", p["plede"])
        .replace("@@PLANS@@", f_plans(p["plans"]))
        .replace("@@PROSE@@", f_prose(p["prose"]))
        .replace("@@PNAME@@", p["pname"])
        .replace("@@FAQS@@", f_faqs(p["faqs"]))
        .replace("@@CTAH2MAIN@@", p["ctam"])
        .replace("@@CTAH2SERIF@@", p["ctas"])
        .replace("@@CTAP@@", p["ctap"])
        .replace("@@ISI@@", p["isi"]))
    with open(os.path.join(OUT, p["slug"]+".html"), "w") as fh:
        fh.write(html)
    print("wrote", OUT+"/"+p["slug"]+".html")
print("done:", len(P), "pages")
