#!/usr/bin/env python3
"""Generate CLYR preview product pages + category hubs from product manifest."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# slug, title, category_label, hub_slug, hub_name, badge, subtitle, pharmacy_ref, benefits[3], img
PRODUCTS = [
    # Wave 1 (already exist — skip generation)
    # Men's Hormone / TRT
    ("testosterone-cypionate", "Testosterone Cypionate", "Men's Hormone · TRT", "mens-hormone", "Men's Hormone", "TRT", "Injectable testosterone cypionate for clinically low testosterone. Compounded from your Olympia TRT menu — provider-supervised dosing and lab monitoring.", "Testosterone Cypionate injectable", ["Restores physiologic T levels", "Weekly or biweekly injection protocols", "Highest-margin hormone vertical"], "/preview/assets/heroes/testosterone-cypionate.png")),
    ("testosterone-cream", "Testosterone Cream", "Men's Hormone · TRT", "mens-hormone", "Men's Hormone", "Topical", "Transdermal testosterone 1% cream — 30g tube. Needle-free alternative for patients who prefer topical delivery.", "Testosterone 1% (10mg/gm) Cream - 30g", ["Daily topical application", "Steady absorption profile", "Pairs with enclomiphene or HCG"], "/preview/assets/heroes/testosterone-cream.png")),
    ("testosterone-hypo-spray", "Testosterone Hypo Spray", "Men's Hormone · TRT", "mens-hormone", "Men's Hormone", "HypoSpray", "Metered testosterone hypospray — rapid transdermal delivery without injections. Multiple strengths on pharmacy menu.", "Testosterone Hypo Spray 12–14ml", ["No needle protocol option", "Precise metered dosing", "Differentiator vs Hims/Ro shallow TRT"], "/preview/assets/heroes/testosterone-hypo-spray.png")),
    ("enclomiphene", "Enclomiphene", "Men's Hormone · Fertility", "mens-hormone", "Men's Hormone", "Fertility+", "Enclomiphene citrate — stimulates endogenous testosterone while preserving fertility. Alternative to exogenous TRT for appropriate candidates.", "Enclomiphene", ["Raises LH/FSH-driven T production", "Preserves sperm production", "Growing telehealth demand"], "/preview/assets/heroes/enclomiphene.png")),
    ("hcg", "HCG Injection", "Men's Hormone · Adjunct", "mens-hormone", "Men's Hormone", "HCG", "Chorionic gonadotropin (HCG) — TRT adjunct, monotherapy, or fertility support. Fresenius Kabi / Pregnyl options on menu.", "Chorionic Gonadotropin - HCG", ["Testicular function support on TRT", "Fertility preservation", "Monotherapy option"], "/preview/assets/heroes/hcg.png")),
    ("anastrozole", "Anastrozole", "Men's Hormone · Support", "mens-hormone", "Men's Hormone", "AI", "Anastrozole for estrogen management on testosterone therapy. Provider-prescribed aromatase inhibitor.", "Anastrazole", ["Estrogen balance on TRT", "Provider-monitored dosing", "Complete hormone stack"], "/preview/assets/heroes/anastrozole.png")),
    # Women's HRT
    ("estradiol-patches", "Estradiol Patches", "Women's Hormone · HRT", "womens-hormone", "Women's Hormone", "HRT", "Transdermal estradiol patches for menopausal symptom relief — steady hormone delivery from your HRT catalog.", "Estradiol Patches", ["Gold-standard transdermal HRT", "Steady estradiol levels", "39-SKU HRT menu depth"], "/preview/assets/heroes/estradiol-patches.png")),
    ("biest-progesterone-cream", "Biest + Progesterone Cream", "Women's Hormone · HRT", "womens-hormone", "Women's Hormone", "Compounded", "Bi-estrogen (50:50 estriol/estradiol) with progesterone cream — compounded menopause support.", "Biestrogen / Progesterone cream", ["Bioidentical hormone combination", "Custom strength compounding", "Midi/Alloy competitor counter"], "/preview/assets/heroes/biest-progesterone-cream.png")),
    ("progesterone-capsules", "Progesterone Capsules", "Women's Hormone · HRT", "womens-hormone", "Women's Hormone", "HRT", "Oral micronized progesterone for endometrial protection and sleep support in HRT protocols.", "Progesterone Capsule", ["Endometrial protection on estrogen", "Sleep and mood support", "Standard HRT pairing"], "/preview/assets/heroes/progesterone-capsules.png")),
    ("dhea-pregnenolone", "DHEA + Pregnenolone", "Women's Hormone · Longevity", "womens-hormone", "Women's Hormone", "Precursors", "DHEA and pregnenolone combination — adrenal hormone precursors for aging and vitality support.", "DHEA/Pregnenolone", ["Adrenal hormone precursors", "Longevity crossover SKU", "Pairs with NAD+ / Niagen"], "/preview/assets/heroes/dhea-pregnenolone.png")),
    ("estradiol-vaginal-cream", "Estradiol Vaginal Cream", "Women's Hormone · HRT", "womens-hormone", "Women's Hormone", "Local", "Low-dose estradiol vaginal cream for genitourinary syndrome of menopause (GSM).", "Estradiol Vaginal Topical Cream", ["Local GSM relief", "Minimal systemic exposure", "High patient demand"], "/preview/assets/heroes/estradiol-vaginal-cream.png")),
    ("womens-testosterone-cream", "Women's Testosterone Cream", "Women's Hormone · Libido", "womens-hormone", "Women's Hormone", "Libido", "Low-dose testosterone cream for women — libido and energy support when clinically appropriate.", "Women Testosterone cream", ["Female androgen insufficiency", "Libido + energy crossover", "Sexual health + HRT bridge"], "/preview/assets/heroes/womens-testosterone-cream.png")),
    # Sexual wellness depth
    ("trimix", "Trimix Injection", "Sexual Health · ED", "sexual-health", "Sexual Health", "Trimix", "Trimix (alprostadil/papaverine/phentolamine) injectable for severe ED when oral PDE5 inhibitors are insufficient.", "Trimix T105/T106", ["Rescue therapy for refractory ED", "High pharmacy margin", "37 sexual wellness SKUs — you sell 4"], "/preview/assets/heroes/trimix.png")),
    ("tadalafil-apomorphine", "Tadalafil + Apomorphine", "Sexual Health · ED", "sexual-health", "Sexual Health", "Dual", "Tadalafil + apomorphine troches — PDE5 plus dopamine agonist for on-demand erectile response.", "Tadalafil+Apomorphine Troches", ["Dual-mechanism on-demand", "Extends combo ODT story", "Differentiator vs single-ingredient"], "/preview/assets/heroes/tadalafil-apomorphine.png")),
    ("oxytocin-nasal", "Oxytocin Nasal Spray", "Sexual Health · Bonding", "sexual-health", "Sexual Health", "Oxytocin", "Oxytocin nasal spray for intimacy, connection, and arousal support — pairs with PT-141 line.", "Oxytocin Nasal Spray", ["Bonding and arousal support", "Cross-sell with PT-141 ODT", "Unique pharmacy SKU"], "/preview/assets/heroes/oxytocin-nasal.png")),
    ("tadalafil-troches", "Tadalafil Troches", "Sexual Health · ED", "sexual-health", "Sexual Health", "Troche", "Sublingual tadalafil troches — 22mg rapid-absorption ED option from pharmacy menu.", "Tadalafil 22mg Troches x 8", ["Sublingual absorption", "On-demand flexibility", "Expands beyond daily tablet"], "/preview/assets/heroes/tadalafil-troches.png")),
    ("sildenafil-tadalafil-gummy", "Sildenafil + Tadalafil Gummy", "Sexual Health · ED", "sexual-health", "Sexual Health", "Dual Gummy", "Dual PDE5 gummy — sildenafil 40mg / tadalafil 10mg. On-demand with your existing gummy UX.", "Sildenafil 40mg / Tadalafil 10mg Gummy x 8", ["Two PDE5s one dose", "Matches your gummy brand", "High conversion format"], "/preview/assets/heroes/sildenafil-tadalafil-gummy.png")),
    # Metabolic / GLP-1 innovation
    ("semaglutide-odt", "Semaglutide ODT + Ondansetron", "Weight Loss · Oral", "weight-loss", "Weight Loss", "Anti-Nausea", "Oral semaglutide ODT with ondansetron built in — nausea-managed GLP-1 from your pharmacy menu.", "Semaglutide / Ondansetron ODT", ["Nausea managed in formulation", "Oral GLP-1 innovation layer", "Only platform with brand + compound + ODT"], "/preview/assets/heroes/semaglutide-odt.png")),
    ("tirzepatide-sublingual", "Tirzepatide Sublingual Drops", "Weight Loss · Oral", "weight-loss", "Weight Loss", "Sublingual", "Tirzepatide sublingual drops — needle-free GLP-1/GIP option for needle-averse patients.", "Tirzepatide sublingual drops", ["Needle-free tirzepatide", "Expands three-door pricing story", "Pharmacy menu exclusive"], "/preview/assets/heroes/tirzepatide-sublingual.png")),
    ("metformin-er", "Metformin ER", "Weight Loss · Metabolic", "weight-loss", "Weight Loss", "Metabolic", "Metformin extended-release for insulin sensitivity and GLP-1 companion therapy.", "Metformin ER", ["GLP-1 companion therapy", "Insulin sensitivity support", "Low-cost metabolic anchor"], "/preview/assets/heroes/metformin-er.png")),
    ("liraglutide", "Liraglutide", "Weight Loss · GLP-1", "weight-loss", "Weight Loss", "GLP-1", "Liraglutide injection — established GLP-1 for weight management, alternative to sema/tirz.", "Liraglutide Olympia", ["Established GLP-1 option", "Saxenda-class therapy compounded", "Depth vs competitors"], "/preview/assets/heroes/liraglutide.png")),
    # Skin care depth
    ("nad-face-cream", "NAD+ Face Cream", "Skin & Hair · Anti-Aging", "skin-hair", "Skin & Hair", "10% NAD", "10% NAD+ pump face cream — topical cellular energy for skin, pairs with injectable NAD+ line.", "NAD+ Pump Face Cream", ["Topical NAD+ delivery", "Longevity + skin crossover", "Unique vs med spas"], "/preview/assets/heroes/nad-face-cream.png")),
    ("tretinoin", "Tretinoin Cream", "Skin & Hair · Anti-Aging", "skin-hair", "Skin & Hair", "Retinoid", "Prescription tretinoin — gold-standard retinoid for photoaging, acne maintenance, and skin turnover.", "Tretinoin cream", ["Gold-standard retinoid", "Acne + anti-aging bridge", "26 skin SKUs available"], "/preview/assets/heroes/tretinoin.png")),
    ("estriol-ghk-cu-cream", "Estriol + GHK-Cu Cream", "Skin & Hair · Anti-Aging", "skin-hair", "Skin & Hair", "Peptide", "Estriol / niacinamide / GHK-Cu / hyaluronic acid cream — compounded anti-aging stack.", "Estriol /Niacinamide/GHK-Cu /Hyaluronic Acid Cream", ["Four-mechanism topical", "Women's longevity crossover", "Med spa competitor counter"], "/preview/assets/heroes/estriol-ghk-cu-cream.png")),
    ("hydroquinone-triple-cream", "Hydroquinone Triple Cream", "Skin & Hair · Pigmentation", "skin-hair", "Skin & Hair", "Brightening", "Hydroquinone / tretinoin / fluocinolone — prescription hyperpigmentation and melasma protocol.", "Hydroquionone/Tretinoin/Fluocinolone Acetonide", ["Prescription brightening", "Dermatology-grade compound", "High demand SKU"], "/preview/assets/heroes/hydroquinone-triple-cream.png")),
    ("doxycycline-acne", "Doxycycline (Acne)", "Skin & Hair · Acne", "skin-hair", "Skin & Hair", "Oral", "Oral doxycycline for moderate inflammatory acne — pairs with CLYR Tri Gel topical stack.", "Doxycycline Capsules", ["Systemic acne support", "Pairs with CLYR Tri Gel", "Complete acne vertical"], "/preview/assets/heroes/doxycycline-acne.png")),
    # Peptides / wellness expansion
    ("bpc-157", "BPC-157", "Daily Wellness · Peptides", "peptides", "Peptides & Recovery", "Peptide", "BPC-157 peptide injection — tissue repair and gut-joint recovery support, growing peptide demand.", "BPC-157 injection", ["Tissue repair peptide", "Recovery + performance niche", "36 wellness SKUs depth"], "/preview/assets/heroes/bpc-157.png")),
    ("tb-500", "TB-500", "Daily Wellness · Peptides", "peptides", "Peptides & Recovery", "Peptide", "Thymosin beta-4 (TB-500) — recovery and flexibility peptide from wellness catalog.", "TB-500 / Thymosin Beta-4", ["Recovery peptide", "Athletic + longevity crossover", "Provider-supervised"], "/preview/assets/heroes/tb-500.png")),
    ("ghk-cu-injectable", "GHK-Cu Injectable", "Daily Wellness · Peptides", "peptides", "Peptides & Recovery", "Copper", "GHK-Cu injectable — copper peptide for collagen synthesis and tissue remodeling.", "GHK-Cu injectable", ["Collagen remodeling", "Pairs with topical GHK cream", "Peptide stack depth"], "/preview/assets/heroes/ghk-cu-injectable.png")),
    ("pt141-strips", "PT-141 Strips", "Sexual Health · Libido", "sexual-health", "Sexual Health", "Strip", "PT-141 sublingual strips — on-demand libido support, alternative format to your ODT.", "PT141 Strip", ["Alternative to ODT format", "On-demand libido", "37 sexual SKUs — expand"], "/preview/assets/heroes/pt141-strips.png")),
    # Hair + recovery
    ("finasteride-oral", "Finasteride Oral", "Skin & Hair · Hair", "skin-hair", "Skin & Hair", "DHT Block", "Oral finasteride 1mg for androgenetic alopecia — systemic DHT block, pairs with topical sprays.", "Finasteride", ["Systemic DHT reduction", "Pairs with 7% spray stacks", "Complete hair vertical"], "/preview/assets/heroes/finasteride-oral.png")),
    ("naltrexone-ldn", "Low-Dose Naltrexone", "Recovery · Wellness", "recovery", "Recovery & Wellness", "LDN", "Low-dose naltrexone (LDN) — autoimmune, chronic pain, and wellness protocol from substance-use catalog.", "Naltrexone Capsule", ["LDN wellness protocol", "Niche loyalty vertical", "Provider-monitored"], "/preview/assets/heroes/naltrexone-ldn.png")),
]

HUBS = {
    "mens-hormone": {
        "title": "Men's Hormone & TRT",
        "meta": "Testosterone, enclomiphene, HCG, and aromatase support. Prescribed by licensed providers.",
        "hero": "Own your <span class=\"serif\">hormones.</span>",
        "lede": "21 TRT SKUs on your Olympia menu. Ro and Hims treat this as an afterthought — you have the pharmacy depth, LegitScript, and provider network to dominate.",
        "benefits": [
            ("Highest-margin sleeper", "Industry audit: $30 wholesale → $249 retail potential on testosterone."),
            ("Full stack", "Cypionate, cream, hypo spray, enclomiphene, HCG, anastrozole — one platform."),
            ("Doctors write scripts", "You own the brand, funnel, and patient relationship."),
        ],
    },
    "womens-hormone": {
        "title": "Women's Hormone & HRT",
        "meta": "Estradiol, biest, progesterone, DHEA, and libido support. Provider-supervised HRT.",
        "hero": "Menopause care, <span class=\"serif\">your way.</span>",
        "lede": "39 HRT SKUs — patches, creams, capsules, and libido crossovers. None of your GLP-1 competitors have this depth plus weight loss cross-sell.",
        "benefits": [
            ("Bioidentical depth", "Patches, biest/progesterone creams, vaginal estrogen, DHEA."),
            ("Longevity crossover", "Pairs with NAD+, Niagen, and estriol/GHK anti-aging topicals."),
            ("No membership fee", "Transparent pricing once wholesale locked — vs Midi/Alloy models."),
        ],
    },
    "peptides": {
        "title": "Peptides & Recovery",
        "meta": "BPC-157, TB-500, GHK-Cu, and recovery peptides. Compounded, provider-supervised.",
        "hero": "Recover <span class=\"serif\">faster.</span>",
        "lede": "Peptide demand is exploding. Your wellness catalog has the injections — brand them CLYR, prescribe through your doctors, own the vertical.",
        "benefits": [
            ("Recovery niche", "BPC-157 and TB-500 for tissue repair and athletic recovery."),
            ("Collagen stack", "GHK-Cu injectable pairs with topical anti-aging creams."),
            ("Cross-sell engine", "GLP-1 patients → peptides → NAD+ → hormones."),
        ],
    },
    "recovery": {
        "title": "Recovery & Wellness Protocols",
        "meta": "Low-dose naltrexone and wellness protocols. Provider-reviewed, pharmacy-compounded.",
        "hero": "Protocols that <span class=\"serif\">work.</span>",
        "lede": "Niche loyalty verticals compound over time. LDN and wellness protocols build a patient base that stays — and cross-buys GLP-1, NAD+, and hormones.",
        "benefits": [
            ("LDN community", "Established low-dose naltrexone patient demand."),
            ("Provider gate", "Licensed review before every prescription."),
            ("Catalog depth", "14 substance-use SKUs available when you're ready."),
        ],
    },
}

EXISTING = {
    "tirzepatide", "semaglutide", "lipo-mino", "foundayo", "zepbound", "wegovy-tablets",
    "sermorelin", "nad", "glutathione", "micc", "niagen",
    "tadalafil", "sildenafil-gummy", "sild-tadal-oxy", "pt141",
    "ivermectin", "ivermectin-mebendazole",
    "clyr-tri-gel", "minoxidil", "hair-spray-women",
}

PREVIEW_STRIP = '<div class="preview-strip">Preview launch — pricing confirmed at consultation. <a href="/preview/strategy/CLYR-CEO-PLAYBOOK-JUN2026.md">CEO playbook</a> · <a href="/preview/catalog/">50-product roadmap</a></div>'

NAV_SKIN = '''      <div class="nav-item" data-nav="skin-hair">
        <a href="/skin-hair.html">Skin &amp; Hair <svg class="chev" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg></a>
        <div class="megamenu">
          <div class="mm-grid">
            <a href="/clyr-tri-gel.html" class="mm-link"><img src="/img/clyr-tri-gel-pump.svg" alt="" style="width:34px;height:48px;object-fit:contain"><span class="mm-link-text"><strong>CLYR Tri Gel</strong><span>Master acne formulation</span></span></a>
            <a href="/minoxidil.html" class="mm-link"><img src="/img/cardv2/nad.webp" alt=""><span class="mm-link-text"><strong>Hair Regrowth (Men)</strong><span>7% quad-stack</span></span></a>
            <a href="/nad-face-cream.html" class="mm-link"><img src="/img/cardv2/nad.webp" alt=""><span class="mm-link-text"><strong>NAD+ Face Cream</strong><span>Topical longevity</span></span></a>
          </div>
          <div class="mm-footer"><span class="mm-count">Skin &amp; hair catalog</span><a href="/skin-hair.html">Explore &rarr;</a></div>
        </div>
      </div>'''

NAV_MENS = '''      <div class="nav-item" data-nav="mens-hormone">
        <a href="/mens-hormone.html">Men's Hormone <svg class="chev" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg></a>
        <div class="megamenu">
          <div class="mm-grid">
            <a href="/testosterone-cypionate.html" class="mm-link"><img src="/img/vial-sermorelin-new.png" alt="" style="width:34px;height:48px;object-fit:contain"><span class="mm-link-text"><strong>Testosterone Cypionate</strong><span>Injectable TRT</span></span></a>
            <a href="/enclomiphene.html" class="mm-link"><img src="/img/cardv2/pill-tadalafil-tad25-new.webp" alt=""><span class="mm-link-text"><strong>Enclomiphene</strong><span>Fertility-preserving T</span></span></a>
            <a href="/hcg.html" class="mm-link"><img src="/img/vial-nad-new.png" alt="" style="width:34px;height:48px;object-fit:contain"><span class="mm-link-text"><strong>HCG</strong><span>TRT adjunct</span></span></a>
          </div>
          <div class="mm-footer"><span class="mm-count">21 TRT SKUs</span><a href="/mens-hormone.html">Explore &rarr;</a></div>
        </div>
      </div>'''

NAV_WOMENS = '''      <div class="nav-item" data-nav="womens-hormone">
        <a href="/womens-hormone.html">Women's Hormone <svg class="chev" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg></a>
        <div class="megamenu">
          <div class="mm-grid">
            <a href="/estradiol-patches.html" class="mm-link"><img src="/img/cardv2/glutathione.webp" alt=""><span class="mm-link-text"><strong>Estradiol Patches</strong><span>Transdermal HRT</span></span></a>
            <a href="/biest-progesterone-cream.html" class="mm-link"><img src="/img/cardv2/glutathione.webp" alt=""><span class="mm-link-text"><strong>Biest + Progesterone</strong><span>Compounded cream</span></span></a>
            <a href="/progesterone-capsules.html" class="mm-link"><img src="/img/cardv2/pill-tadalafil-tad25-new.webp" alt=""><span class="mm-link-text"><strong>Progesterone</strong><span>Oral capsules</span></span></a>
          </div>
          <div class="mm-footer"><span class="mm-count">39 HRT SKUs</span><a href="/womens-hormone.html">Explore &rarr;</a></div>
        </div>
      </div>'''

BASE_CSS = """
:root{--white:#FFF;--dark:#1A1A1A;--teal:#00B4C5;--teal-dark:#009BAA;--teal-light:#E0F7FA;--gray-50:#F8FAFB;--gray-100:#F1F4F6;--gray-200:#E2E7EB;--gray-400:#94A3B0;--gray-500:#6B7C8A;--gray-600:#4A5568;--green:#10B981;--serif:'Instrument Serif',Georgia,serif;--sans:'DM Sans',-apple-system,sans-serif;--radius:16px;--radius-sm:10px;--radius-lg:24px;--shadow-md:0 4px 20px rgba(0,0,0,0.06);--shadow-teal:0 8px 30px rgba(0,180,197,0.2)}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}body{font-family:var(--sans);color:var(--dark);background:var(--white);overflow-x:hidden;line-height:1.6}
.preview-strip{background:linear-gradient(90deg,#0d1b2e,#1a3045);color:#fff;text-align:center;padding:10px 20px;font-size:13px;font-weight:600;letter-spacing:0.02em}.preview-strip a{color:#00e5e5;text-decoration:none;margin-left:8px}
.nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,0.92);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,0,0,0.05);padding:0 40px}.nav-inner{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:72px}.nav-links{display:flex;align-items:center;gap:28px}.nav-links a{font-size:15px;font-weight:500;color:var(--gray-600);text-decoration:none}.nav-cta{background:var(--teal)!important;color:#fff!important;padding:10px 28px!important;border-radius:100px!important;font-weight:600!important;font-size:14px!important}.nav-portal{color:var(--teal)!important;font-weight:600!important}.mobile-menu-btn{display:none;background:none;border:none;cursor:pointer;padding:8px}.mobile-menu-btn span{display:block;width:22px;height:2px;background:var(--dark);margin:5px 0;border-radius:2px}
.nav-item{position:relative}.nav-item > a{padding:26px 0;display:inline-flex;align-items:center}.nav-item > a .chev{margin-left:4px}.nav-item:hover > a .chev{transform:rotate(180deg)}.nav-item.nav-active > a,.nav-links a.nav-active{color:var(--teal);font-weight:600}
.megamenu{position:absolute;top:100%;left:50%;transform:translateX(-50%);background:#fff;border:1px solid #E2E7EB;border-radius:20px;box-shadow:0 20px 50px rgba(15,30,60,0.14);padding:22px;min-width:520px;opacity:0;visibility:hidden;transition:all .2s;pointer-events:none;z-index:200}.nav-item:hover .megamenu{opacity:1;visibility:visible;pointer-events:auto;transform:translateX(-50%) translateY(8px)}
.mm-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}.mm-link{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:12px;text-decoration:none;color:inherit}.mm-link:hover{background:#F8FAFB}.mm-link img{width:34px;height:48px;object-fit:contain}.mm-link-text strong{font-size:14px;display:block}.mm-link-text span{font-size:12px;color:#6B7C8A}
.mm-footer{margin-top:12px;padding-top:12px;border-top:1px solid #F1F4F6;display:flex;justify-content:space-between;font-size:12px;color:#6B7C8A}.mm-footer a{color:var(--teal);font-weight:600;text-decoration:none}
.breadcrumb{max-width:1200px;margin:0 auto;padding:16px 40px;font-size:13px;color:var(--gray-400)}.breadcrumb a{color:var(--gray-500);text-decoration:none}
.product-hero{max-width:1200px;margin:0 auto;padding:0 40px 60px;display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start}
.product-image{background:linear-gradient(135deg,#f0fafb,#e8f4f8);border-radius:var(--radius-lg);aspect-ratio:1;display:flex;align-items:center;justify-content:center;position:relative;padding:32px;font-size:0}
.product-badge{position:absolute;top:20px;left:20px;background:var(--teal);color:#fff;padding:6px 14px;border-radius:100px;font-size:12px;font-weight:700;text-transform:uppercase}
.product-category{font-size:13px;font-weight:600;color:var(--teal);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
.product-title{font-size:42px;font-weight:700;line-height:1.1;letter-spacing:-.03em;margin-bottom:8px}.product-title .serif{font-family:var(--serif);font-style:italic;font-weight:400;color:var(--teal)}
.product-subtitle{font-size:17px;color:var(--gray-500);margin-bottom:24px;line-height:1.5}
.product-price .amount{font-size:32px;font-weight:800}.product-price-note{font-size:13px;color:var(--gray-500);margin-bottom:28px}
.product-cta{display:inline-flex;align-items:center;gap:10px;background:var(--teal);color:#fff;padding:16px 36px;border-radius:100px;font-size:16px;font-weight:700;text-decoration:none}.product-cta:hover{background:var(--teal-dark)}
.product-includes{margin-top:32px;display:flex;flex-direction:column;gap:12px}.product-includes-item{display:flex;align-items:center;gap:10px;font-size:14px;color:var(--gray-600)}.product-includes-item svg{color:var(--teal);flex-shrink:0}
.benefits{padding:80px 40px;max-width:1200px;margin:0 auto}.section-label{font-size:13px;font-weight:600;color:var(--teal);text-transform:uppercase;letter-spacing:.1em;margin-bottom:14px}
.section-heading{font-size:36px;font-weight:700;line-height:1.15;margin-bottom:14px}.section-heading .serif{font-family:var(--serif);font-style:italic;font-weight:400}
.section-sub{font-size:16px;color:var(--gray-500);max-width:560px;margin-bottom:48px}.benefits-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.benefit-card{background:var(--gray-50);border:1px solid var(--gray-100);border-radius:var(--radius);padding:28px}.benefit-card h3{font-size:17px;font-weight:700;margin-bottom:8px}.benefit-card p{font-size:14px;color:var(--gray-500);line-height:1.6}
.pharmacy-ref{margin-top:24px;padding:18px 20px;background:var(--gray-50);border:1px solid var(--gray-200);border-radius:12px;font-size:13px;color:var(--gray-600)}.pharmacy-ref strong{color:var(--dark)}
.cta-section{background:linear-gradient(135deg,#0d1b2e,#162a40);padding:80px 40px;text-align:center;color:#fff}.cta-section h2{font-size:36px;font-weight:700;margin-bottom:14px}.cta-section h2 .serif{font-family:var(--serif);font-style:italic;color:var(--teal)}.cta-section p{color:rgba(255,255,255,.5);margin-bottom:32px}.cta-btn{display:inline-flex;align-items:center;gap:10px;background:var(--teal);color:#fff;padding:16px 40px;border-radius:100px;font-weight:700;text-decoration:none}
.footer{background:#0A0A0A;padding:60px 40px 36px;color:#94A3B0}.footer-inner{max-width:1280px;margin:0 auto}.footer-top{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:48px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,.08)}.footer-col h4{font-size:13px;text-transform:uppercase;margin-bottom:16px}.footer-col a{display:block;color:#6B7C8A;text-decoration:none;padding:5px 0;font-size:14px}.footer-bottom{padding-top:28px;font-size:13px;color:#6B7C8A}
@media(max-width:900px){.nav-item .megamenu{display:none}.mobile-menu-btn{display:block}.nav-links{display:none}.nav.mobile-open .nav-links{display:flex;flex-direction:column;position:absolute;top:72px;left:0;right:0;background:#fff;padding:20px;gap:16px;border-bottom:1px solid var(--gray-200)}}
@media(max-width:768px){.product-hero{grid-template-columns:1fr}.benefits-grid{grid-template-columns:1fr}.product-title{font-size:32px}}
"""

HUB_CSS = BASE_CSS + """
.hero{background:linear-gradient(135deg,#0d1b2e,#1a3045,#0d2a35);padding:100px 40px 60px;color:#fff}.hero-inner{max-width:1200px;margin:0 auto}.hero .label{color:var(--teal);font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.1em;margin-bottom:16px;display:block}.hero h1{font-size:52px;font-weight:700;line-height:1.1;margin-bottom:18px;max-width:700px}.hero h1 .serif{font-family:var(--serif);font-style:italic;color:var(--teal)}.hero p{font-size:18px;color:rgba(255,255,255,.55);max-width:600px;margin-bottom:32px}
.section{padding:80px 40px;max-width:1200px;margin:0 auto}.section-sub{font-size:13px;font-weight:600;color:var(--teal);text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px}.section h2{font-size:36px;font-weight:700;margin-bottom:10px}.section h2 .serif{font-family:var(--serif);font-style:italic;font-weight:400}.section-desc{font-size:16px;color:var(--gray-500);margin-bottom:48px}
.pg{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.pc{background:#fff;border:1px solid var(--gray-200);border-radius:var(--radius);overflow:hidden;text-decoration:none;color:inherit;transition:all .3s;display:flex;flex-direction:column}.pc:hover{border-color:var(--teal);transform:translateY(-4px);box-shadow:var(--shadow-md)}.ci{background:linear-gradient(135deg,#f0fafb,#e8f4f8);aspect-ratio:1;display:flex;align-items:center;justify-content:center;padding:20px;position:relative}.ci img{max-width:72%;max-height:72%;object-fit:contain}.cb{position:absolute;top:12px;right:12px;background:var(--teal);color:#fff;padding:4px 12px;border-radius:100px;font-size:11px;font-weight:700}.cd{padding:24px;flex:1;display:flex;flex-direction:column}.cc{font-size:11px;font-weight:600;color:var(--teal);text-transform:uppercase;margin-bottom:8px}.cd h3{font-size:20px;font-weight:700;margin-bottom:6px}.cd .ds{font-size:14px;color:var(--gray-500);flex:1;margin-bottom:16px}.pr-tbd{font-size:16px;font-weight:700;color:var(--gray-500)}.ct{background:var(--teal);color:#fff;padding:12px;text-align:center;border-radius:var(--radius-sm);font-size:14px;font-weight:700}
.benefits{background:var(--gray-50);padding:80px 40px}.benefits-inner{max-width:1200px;margin:0 auto}.benefits-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:40px}.benefit{background:#fff;border:1px solid var(--gray-200);border-radius:var(--radius);padding:28px}.benefit h3{font-size:17px;font-weight:700;margin-bottom:8px}.benefit p{font-size:14px;color:var(--gray-500)}
@media(max-width:1024px){.pg{grid-template-columns:repeat(2,1fr)}}
@media(max-width:768px){.pg{grid-template-columns:1fr}.hero h1{font-size:34px}}
"""

CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/></svg>'


def title_parts(title: str) -> tuple[str, str]:
    words = title.split()
    if len(words) <= 1:
        return title, ""
    return " ".join(words[:-1]), words[-1]


def nav_block(active: str = "") -> str:
    active_attr = ' nav-active' if active else ''
    return f'''    <div class="nav-links">
      <div class="nav-item" data-nav="weight-loss"><a href="/weight-loss.html">Weight Loss</a></div>
      <div class="nav-item" data-nav="daily-wellness"><a href="/daily-wellness.html">Daily Wellness</a></div>
      {NAV_MENS}
      {NAV_WOMENS}
      {NAV_SKIN}
      <div class="nav-item" data-nav="sexual-health"><a href="/sexual-health.html">Sexual Health</a></div>
      <div class="nav-item" data-nav="peptides"><a href="/peptides.html">Peptides</a></div>
      <a href="/wellness.html">All Treatments</a>
      <a href="/portal/" class="nav-portal">Patient Portal</a>
      <a href="/wellness.html" class="nav-cta">Get Started</a>
    </div>'''


def footer_block() -> str:
    return '''<footer class="footer"><div class="footer-inner"><div class="footer-top">
      <div><svg viewBox="0 0 120 32" width="100"><text x="0" y="26" font-family="DM Sans" font-weight="700" font-size="28"><tspan fill="#fff">CLY</tspan><tspan fill="#00B4C5">R</tspan></text></svg></div>
      <div class="footer-col"><h4>Verticals</h4><a href="/weight-loss.html">Weight Loss</a><a href="/mens-hormone.html">Men's Hormone</a><a href="/womens-hormone.html">Women's Hormone</a><a href="/skin-hair.html">Skin &amp; Hair</a><a href="/preview/catalog/">Full Catalog</a></div>
      <div class="footer-col"><h4>Strategy</h4><a href="/preview/strategy/CLYR-CEO-PLAYBOOK-JUN2026.md">CEO Playbook</a><a href="/preview/catalog/">50-Product Roadmap</a></div>
      <div class="footer-col"><h4>Legal</h4><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div>
    </div><div class="footer-bottom"><p>&copy; 2026 CLYR Health. Preview pages — noindex until wholesale pricing locked.</p></div></div></footer>
<script>function toggleFaq(b){{b.classList.toggle('open');b.nextElementSibling.classList.toggle('open')}}</script>'''


def product_page(p) -> str:
    slug, title, cat, hub_slug, hub_name, badge, subtitle, pharm, benefits, img = p
    t1, t2 = title_parts(title)
    serif = f' <span class="serif">{t2}</span>' if t2 else ""
    plain_title = f'{t1}{serif}' if t2 else title
    ben_html = "".join(f'<div class="benefit-card"><h3>{b[0] if isinstance(b,tuple) else b}</h3><p>{b[1] if isinstance(b,tuple) else ""}</p></div>' for b in [(benefits[i], benefits[i]) if not isinstance(benefits[i], str) else (benefits[i], "") for i in range(3)])
    # fix benefits - they're plain strings
    ben_html = "".join(f'<div class="benefit-card"><h3>{b}</h3><p>Provider-supervised protocol from your Olympia pharmacy menu.</p></div>' for b in benefits)
    includes = [
        f"Compounded {title} from licensed 503A pharmacy",
        "Licensed provider consultation included",
        "Free discreet shipping",
        "Ongoing refill management",
    ]
    inc_html = "".join(f'<div class="product-includes-item">{CHECK}{x}</div>' for x in includes)
    intake_key = slug.replace("-", "_")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="/favicon.ico">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · {cat} | CLYR Health</title>
<meta name="description" content="{subtitle[:155]}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>{BASE_CSS}</style>
</head>
<body>
{PREVIEW_STRIP}
<nav class="nav" id="nav"><div class="nav-inner">
  <a href="/"><svg viewBox="0 0 120 32" height="32"><text x="0" y="26" font-family="DM Sans" font-weight="700" font-size="28"><tspan fill="#1A1A1A">CLY</tspan><tspan fill="#00B4C5">R</tspan></text></svg></a>
{nav_block()}
  <button class="mobile-menu-btn" onclick="document.getElementById('nav').classList.toggle('mobile-open')"><span></span><span></span><span></span></button>
</div></nav>
<div class="breadcrumb"><a href="/">CLYR Health</a> &nbsp;/&nbsp; <a href="/{hub_slug}.html">{hub_name}</a> &nbsp;/&nbsp; {title}</div>
<section class="product-hero">
  <div class="product-image"><div class="product-badge">{badge}</div><img src="{img}" alt="{title}" style="width:82%;height:82%;object-fit:contain;filter:drop-shadow(0 18px 40px rgba(0,0,0,.12))"></div>
  <div class="product-info">
    <div class="product-category">{cat}</div>
    <h1 class="product-title">{plain_title}</h1>
    <p class="product-subtitle">{subtitle}</p>
    <div class="product-price"><span class="amount">Pricing at consultation</span></div>
    <p class="product-price-note">Wholesale-backed rate — fill <a href="/preview/strategy/CLYR-Pricing-Framework-Wave1.xlsx" style="color:var(--teal);font-weight:600">pricing framework</a> before go-live.</p>
    <a href="/intake-wellness.html?product={intake_key}" class="product-cta">Join the waitlist →</a>
    <div class="pharmacy-ref"><strong>Pharmacy SKU:</strong> {pharm}</div>
    <div class="product-includes">{inc_html}</div>
  </div>
</section>
<section class="benefits">
  <div class="section-label">Why CLYR</div>
  <h2 class="section-heading">Built for your <span class="serif">market.</span></h2>
  <p class="section-sub">Doctors write scripts. You own the brand, funnel, and patient relationship at industry-low wholesale.</p>
  <div class="benefits-grid">{ben_html}</div>
</section>
<section class="cta-section">
  <h2>Join the <span class="serif">waitlist.</span></h2>
  <p>Preview launch — provider consultations open when wholesale pricing is locked.</p>
  <a href="/intake-wellness.html?product={intake_key}" class="cta-btn">Join the waitlist →</a>
</section>
{footer_block()}
</body></html>'''


def hub_page(slug: str, info: dict, products: list) -> str:
    cards = []
    for p in products:
        s, title, cat, hub_slug, hub_name, badge, subtitle, pharm, benefits, img = p
        cards.append(f'''<a href="/{s}.html" class="pc"><div class="ci"><div class="cb">{badge}</div><img src="{img}" alt="{title}"></div><div class="cd"><div class="cc">{cat.split("·")[-1].strip()}</div><h3>{title}</h3><p class="ds">{subtitle[:120]}…</p><div class="pr-tbd">Pricing at consultation</div><div class="ct">Learn more →</div></div></a>''')
    ben = "".join(f'<div class="benefit"><h3>{t}</h3><p>{d}</p></div>' for t, d in info["benefits"])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="/favicon.ico">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{info["title"]} | CLYR Health</title>
<meta name="description" content="{info["meta"]}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>{HUB_CSS}</style>
</head>
<body>
{PREVIEW_STRIP}
<nav class="nav" id="nav"><div class="nav-inner">
  <a href="/"><svg viewBox="0 0 120 32" height="32"><text x="0" y="26" font-family="DM Sans" font-weight="700" font-size="28"><tspan fill="#1A1A1A">CLY</tspan><tspan fill="#00B4C5">R</tspan></text></svg></a>
{nav_block()}
</div></nav>
<section class="hero"><div class="hero-inner"><span class="label">{info["title"]}</span><h1>{info["hero"]}</h1><p>{info["lede"]}</p></div></section>
<section class="section"><div class="section-sub">Treatments</div><h2>Choose your <span class="serif">protocol.</span></h2><p class="section-desc">Preview pages — pricing confirmed at consultation after wholesale locked.</p><div class="pg">{"".join(cards)}</div></section>
<section class="benefits"><div class="benefits-inner"><div class="section-sub">Why this vertical</div><h2>Competitive <span class="serif">moat.</span></h2><div class="benefits-grid">{ben}</div></div></section>
<section class="cta-section"><h2>See the full <span class="serif">roadmap.</span></h2><p>50 products by end of 2026 — <a href="/preview/catalog/" style="color:var(--teal)">view catalog index</a>.</p><a href="/preview/catalog/" class="cta-btn">50-Product Roadmap →</a></section>
{footer_block()}
</body></html>'''


def main():
    generated = []
    by_hub: dict[str, list] = {}
    for p in PRODUCTS:
        slug = p[0]
        if (ROOT / f"{slug}.html").exists():
            print(f"skip exists {slug}.html")
            continue
        html = product_page(p)
        (ROOT / f"{slug}.html").write_text(html)
        generated.append(slug)
        hub = p[3]
        by_hub.setdefault(hub, []).append(p)

    for slug, info in HUBS.items():
        prods = by_hub.get(slug, [])
        if not prods:
            continue
        (ROOT / f"{slug}.html").write_text(hub_page(slug, info, prods))
        print(f"hub {slug}.html ({len(prods)} products)")

    # manifest
    all_products = []
    for p in PRODUCTS:
        all_products.append({"slug": p[0], "title": p[1], "hub": p[3], "category": p[2], "pharmacy": p[7], "status": "preview"})
    existing_list = [
        {"slug": s, "status": "live" if s not in {"niagen","minoxidil","hair-spray-women","clyr-tri-gel"} else "preview"}
        for s in sorted(EXISTING)
    ]
    manifest = {"target": 50, "generated": generated, "preview_new": len(generated), "existing": existing_list, "products": all_products}
    out = ROOT / "preview/strategy/product-manifest.json"
    out.write_text(json.dumps(manifest, indent=2))
    print(f"manifest: {len(existing_list)} existing + {len(generated)} new preview = {len(existing_list)+len(generated)} tracked")
    print(f"generated: {', '.join(generated)}")


if __name__ == "__main__":
    main()