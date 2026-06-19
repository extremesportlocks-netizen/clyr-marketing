#!/usr/bin/env python3
"""Build CLYR pharmacy launch kit: briefs, specs, master preview hub."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "preview" / "launch-kit"
BRIEFS = KIT / "briefs"

# slug, title, vertical, hub, status, pharmacy_dispense, standard_strength, package, positioning, competitor, volume_ask, notes
CATALOG = [
    # Weight Loss
    ("tirzepatide", "Tirzepatide", "Weight Loss", "weight-loss", "live",
     "Tirzepatide Olympia compounded", "Up to 15mg/week titration", "Multi-dose vial",
     "Compounded GLP-1/GIP — primary revenue vertical", "Hims/Ro $299–499/mo", "500+ pts/mo at scale",
     "Industry standard: dose-titrated compounded tirzepatide matching Zepbound/Mounjaro protocols."),
    ("semaglutide", "Semaglutide", "Weight Loss", "weight-loss", "live",
     "Semaglutide Olympia compounded", "Up to 2.4mg/week", "Multi-dose vial",
     "Compounded GLP-1 — entry weight loss SKU", "Ro/Hims $199–349/mo", "500+ pts/mo",
     "Standard obesity dosing per FDA semaglutide 2.4mg target."),
    ("zepbound", "Zepbound", "Weight Loss", "weight-loss", "live",
     "Mounjaro/Zepbound brand pen", "2.5–15mg weekly", "Brand pen",
     "Brand-name tirzepatide option", "Cash pay $500+/mo", "100+ pts/mo",
     "Lead with 2.5mg starter pen — industry titration ladder."),
    ("wegovy-tablets", "Wegovy Tablets", "Weight Loss", "weight-loss", "live",
     "Oral semaglutide brand", "Per FDA oral label", "Bottle",
     "Oral brand GLP-1 — needle-free", "Brand cash pricing", "50+ pts/mo", ""),
    ("foundayo", "Foundayo Oral GLP-1", "Weight Loss", "weight-loss", "live",
     "Foundayo compounded oral", "Per provider protocol", "Bottle",
     "CLYR-branded oral GLP-1", "Competitor oral GLP-1 telehealth", "200+ pts/mo", ""),
    ("lipo-mino", "Lipo-Mino + L-Carnitine", "Weight Loss", "weight-loss", "live",
     "Lipo-Mino Olympia injection", "Per vial protocol", "10ml vial",
     "GLP-1 companion lipotropic", "Med spa bundles", "300+ pts/mo", ""),
    ("semaglutide-odt", "Semaglutide ODT + Ondansetron", "Weight Loss", "weight-loss", "preview",
     "Semaglutide 4mg / Ondansetron 2mg ODT", "4mg sema + 2mg ondansetron", "30-count ODT",
     "Nausea-managed oral GLP-1 — unique differentiator", "No direct telehealth comp", "200+ pts/mo",
     "PICK: 4mg/2mg — mid-titration industry sweet spot; ondansetron built in."),
    ("tirzepatide-sublingual", "Tirzepatide Sublingual Drops", "Weight Loss", "weight-loss", "preview",
     "Tirzepatide sublingual drops Olympia", "Titrated per protocol", "Dropper bottle",
     "Needle-free tirzepatide", "None at scale", "150+ pts/mo", "Lead SKU for needle-averse segment."),
    ("metformin-er", "Metformin ER", "Weight Loss", "weight-loss", "preview",
     "Metformin ER", "500mg", "90-count",
     "GLP-1 companion / insulin sensitivity", "Generic $10–20/mo retail", "400+ pts/mo",
     "PICK: 500mg ER — standard starting dose, pairs with every GLP-1 patient."),
    ("liraglutide", "Liraglutide", "Weight Loss", "weight-loss", "preview",
     "Liraglutide Olympia", "Up to 3mg daily", "Multi-dose pen/vial",
     "Alternative GLP-1 for sema-intolerant", "Saxenda-class $300+", "75+ pts/mo", ""),
    # Daily Wellness
    ("nad", "NAD+ Injections", "Daily Wellness", "daily-wellness", "live",
     "NAD+ liquid - Olympia - 100mg/ml 10ml Vial", "100mg/ml", "10ml vial",
     "Flagship longevity SKU", "IV clinics $300–800/session", "400+ pts/mo",
     "PICK: 100mg/ml 10ml — matches live CLYR page."),
    ("niagen", "Injectable Niagen", "Daily Wellness", "daily-wellness", "preview",
     "Niagen 100mg/ml - 5ml Vial Olympia", "100mg/ml", "5ml vial",
     "NAD+ precursor (NR) — pairs NAD+ page", "NR supplements $50–80/mo", "200+ pts/mo",
     "PICK: 100mg/ml 5ml Olympia vial."),
    ("sermorelin", "Sermorelin", "Daily Wellness", "daily-wellness", "live",
     "Sermorelin Olympia", "Per peptide protocol", "Vial",
     "Growth hormone secretagogue", "Peptide clinics $149–249/mo", "300+ pts/mo", ""),
    ("glutathione", "Glutathione", "Daily Wellness", "daily-wellness", "live",
     "Glutathione Injection Olympia 200mg/ml x 5ml", "200mg/ml", "5ml vial",
     "Master antioxidant injection", "IV/wellness $99–149/mo", "250+ pts/mo",
     "PICK: 200mg/ml 5ml — standard wellness vial size."),
    ("micc", "MICC + B12", "Daily Wellness", "daily-wellness", "live",
     "MICC-B12 - Olympia -Injection 25/50/50/330mcg x 10ml", "MICC blend", "10ml vial",
     "Lipotropic + B12 metabolic", "Weight loss clinics $129/mo", "300+ pts/mo", ""),
    ("bpc-157", "BPC-157", "Peptides", "peptides", "preview",
     "BPC-157 injection Olympia", "500mcg daily typical", "Vial",
     "Tissue repair peptide", "Peptide sellers $150–200/mo", "150+ pts/mo",
     "Industry protocol: 250–500mcg daily subQ."),
    ("tb-500", "TB-500", "Peptides", "peptides", "preview",
     "Thymosin Beta-4 (TB-500)", "2.5mg 2x/week typical", "Vial",
     "Recovery peptide", "Peptide market $175+/mo", "100+ pts/mo", ""),
    ("ghk-cu-injectable", "GHK-Cu Injectable", "Peptides", "peptides", "preview",
     "GHK-Cu injectable", "1–2mg daily typical", "Vial",
     "Copper peptide collagen support", "Med spa injectables", "75+ pts/mo", ""),
    ("naltrexone-ldn", "Low-Dose Naltrexone", "Recovery", "recovery", "preview",
     "Naltrexone Capsule compounded LDN", "4.5mg", "90-count",
     "LDN wellness protocol", "LDN specialists $45–75/mo", "200+ pts/mo",
     "PICK: 4.5mg — standard LDN maintenance dose."),
    # Men's Hormone
    ("testosterone-cypionate", "Testosterone Cypionate", "Men's Hormone", "mens-hormone", "preview",
     "Testosterone Cypionate 200mg/ml x 10ml", "200mg/ml", "10ml vial",
     "Primary TRT injectable — highest margin vertical", "Hone/Marek $120–249/mo", "400+ pts/mo",
     "PICK: 200mg/ml 10ml — industry standard TRT vial (most telehealth uses this)."),
    ("testosterone-cream", "Testosterone Cream", "Men's Hormone", "mens-hormone", "preview",
     "Testosterone 1% (10mg/gm) Cream - 30g", "1%", "30g tube",
     "Topical TRT — needle-free", "Compounded cream $89–149/mo", "150+ pts/mo",
     "PICK: 1% 30g — standard starting topical strength."),
    ("testosterone-hypo-spray", "Testosterone Hypo Spray", "Men's Hormone", "mens-hormone", "preview",
     "Testosterone 20mg/0.2ml Hypo Spray - 14ml", "20mg/0.2ml", "14ml spray",
     "Metered transdermal — premium UX", "Limited comp competition", "100+ pts/mo",
     "PICK: 20mg/0.2ml — mid-strength industry protocol."),
    ("enclomiphene", "Enclomiphene", "Men's Hormone", "mens-hormone", "preview",
     "Enclomiphene 12.5mg Capsules", "12.5mg", "30-count",
     "Fertility-preserving T stimulation", "Entarin $89–129/mo", "200+ pts/mo",
     "PICK: 12.5mg — standard starting dose (titrate to 25mg)."),
    ("hcg", "HCG Injection", "Men's Hormone", "mens-hormone", "preview",
     "Chorionic Gonadotropin - HCG (Fresenius Kabi)", "10,000 IU", "Vial",
     "TRT adjunct / fertility", "TRT clinics $99–149/mo", "250+ pts/mo",
     "PICK: 10,000 IU vial — industry standard HCG kit."),
    ("anastrozole", "Anastrozole", "Men's Hormone", "mens-hormone", "preview",
     "Anastrozole 0.5mg Capsules", "0.5mg", "30-count",
     "Estrogen management on TRT", "Bundled TRT $15–30/mo", "300+ pts/mo",
     "PICK: 0.5mg — standard TRT adjunct (not 1mg oncology dose)."),
    # Women's Hormone
    ("estradiol-patches", "Estradiol Patches", "Women's Hormone", "womens-hormone", "preview",
     "Estradiol 0.05 mg / Day Patch x 8pack", "0.05mg/day", "8-pack",
     "Transdermal HRT foundation", "Midi/Alloy $80–120/mo", "300+ pts/mo",
     "PICK: 0.05mg/day — most common maintenance patch dose."),
    ("biest-progesterone-cream", "Biest + Progesterone Cream", "Women's Hormone", "womens-hormone", "preview",
     "Biestrogen 50:50 0.1% / Progesterone 4% cream", "Biest 0.1% / Prog 4%", "30g",
     "Compounded bioidentical HRT", "Wiley/Women's comp $75–110/mo", "200+ pts/mo", ""),
    ("progesterone-capsules", "Progesterone Capsules", "Women's Hormone", "womens-hormone", "preview",
     "Progesterone Capsule micronized", "100mg", "30-count",
     "Oral micronized progesterone", "Standard HRT $30–50/mo", "350+ pts/mo",
     "PICK: 100mg — standard nightly HRT dose."),
    ("dhea-pregnenolone", "DHEA + Pregnenolone", "Women's Hormone", "womens-hormone", "preview",
     "DHEA/Pregnenolone compounded", "Per protocol", "30-count",
     "Adrenal hormone precursors", "Longevity/HRT crossover", "100+ pts/mo", ""),
    ("estradiol-vaginal-cream", "Estradiol Vaginal Cream", "Women's Hormone", "womens-hormone", "preview",
     "Estradiol Vaginal Topical Cream", "0.01% (1mg/g)", "30g",
     "GSM / local estrogen", "Premarin-class $40–80/mo", "200+ pts/mo", ""),
    ("womens-testosterone-cream", "Women's Testosterone Cream", "Women's Hormone", "womens-hormone", "preview",
     "Women Testosterone cream low dose", "0.5–1mg/day typical", "30g",
     "Female libido / energy support", "Womens HRT clinics", "150+ pts/mo",
     "PICK: low-dose cream — sub-male physiological dosing."),
    # Sexual Health
    ("tadalafil", "Tadalafil + Vardenafil", "Sexual Health", "sexual-health", "live",
     "Tadalafil compounded daily", "2.5–5mg daily class", "30 tablets",
     "Daily dual PDE5 — live CLYR SKU", "Hims/Rugiet $30–99/mo", "500+ pts/mo", ""),
    ("sildenafil-gummy", "Sildenafil Gummy", "Sexual Health", "sexual-health", "live",
     "Sildenafil 50mg Gummy", "50mg", "10 gummies",
     "On-demand ED gummy format", "Hims gummies $40+/mo", "400+ pts/mo",
     "PICK: 50mg — standard on-demand dose."),
    ("sild-tadal-oxy", "Combo ODT", "Sexual Health", "sexual-health", "live",
     "Sildenafil + Tadalafil + Oxytocin ODT", "Triple combo", "10 ODT",
     "CLYR differentiator — triple action", "No direct comp", "300+ pts/mo", ""),
    ("pt141", "PT-141 + Oxytocin", "Sexual Health", "sexual-health", "live",
     "PT-141 + Oxytocin ODT", "Per troche", "8 ODT",
     "Libido peptide combo", "Rugiet/others $100+/mo", "250+ pts/mo", ""),
    ("trimix", "Trimix Injection", "Sexual Health", "sexual-health", "preview",
     "TRIMIX T105", "30mg/1mg/10mcg per 0.1ml", "2.5ml vial",
     "Injectable ED rescue therapy", "Compounding pharmacies $80–150/mo", "150+ pts/mo",
     "PICK: T105 (10mcg PGE) — standard starting trimix (T106 for non-responders)."),
    ("tadalafil-apomorphine", "Tadalafil + Apomorphine", "Sexual Health", "sexual-health", "preview",
     "Tadalafil+Apomorphine Troches", "22mg / 2mg", "8 troches",
     "Dual on-demand ED", "Limited telehealth", "200+ pts/mo",
     "PICK: 22mg/2mg — lower apomorphine, standard tadalafil troche dose."),
    ("oxytocin-nasal", "Oxytocin Nasal Spray", "Sexual Health", "sexual-health", "preview",
     "Oxytocin Nasal Spray", "Per spray protocol", "Nasal bottle",
     "Bonding / arousal support", "Niche comp", "100+ pts/mo", ""),
    ("tadalafil-troches", "Tadalafil Troches", "Sexual Health", "sexual-health", "preview",
     "Tadalafil 22mg Troches x 8", "22mg", "8 troches",
     "Sublingual on-demand ED", "Compounding $60–90/mo", "250+ pts/mo",
     "PICK: 22mg — industry standard compounded troche."),
    ("sildenafil-tadalafil-gummy", "Sildenafil + Tadalafil Gummy", "Sexual Health", "sexual-health", "preview",
     "Sildenafil 40mg / Tadalafil 10mg Gummy x 8", "40mg / 10mg", "8 gummies",
     "Dual PDE5 gummy", "Rugiet-style", "200+ pts/mo", ""),
    ("pt141-strips", "PT-141 Strips", "Sexual Health", "sexual-health", "preview",
     "PT141 Strip", "Per strip protocol", "Strips",
     "Alternative libido format", "Novel format", "75+ pts/mo", ""),
    # Skin & Hair
    ("clyr-tri-gel", "CLYR Tri Gel", "Skin & Hair", "skin-hair", "preview",
     "CUSTOM: CLYR Master Formulation", "Clinda 1.2% / Ada 0.15% / BPO 3.1% / Nia 4%", "50g airless pump",
     "Proprietary acne — Cabtreo-class + niacinamide", "Cabtreo $300+ cash", "300+ pts/mo",
     "503A proprietary — NOT Cabtreo copy. Custom compound request."),
    ("minoxidil", "CLYR Hair Regrowth Spray (Men)", "Skin & Hair", "skin-hair", "preview",
     "Minoxdil/Tretinoin/Fluocinolone/Finasteride Spray", "7/0.025/0.025/0.2%", "60ml",
     "4-mechanism hair spray men", "Hims 5% minox $45/mo", "400+ pts/mo",
     "PICK: 7% quad stack 60ml — pharmacy row 191."),
    ("hair-spray-women", "CLYR Hair Regrowth Spray (Women)", "Skin & Hair", "skin-hair", "preview",
     "Minoxidil/Tretinoin/Fluocinolone/Biotin/Melatonin Spray", "7/0.025/0.025/0.8/0.5%", "60ml",
     "Finasteride-free women's stack", "Women's minox competitors", "300+ pts/mo",
     "PICK: 7% + biotin/melatonin 60ml — pharmacy row 190."),
    ("nad-face-cream", "NAD+ Face Cream", "Skin & Hair", "skin-hair", "preview",
     "NAD+ Pump Face Cream", "10% NAD+", "Pump bottle",
     "Topical NAD+ anti-aging", "Med spa topicals $80+", "150+ pts/mo",
     "PICK: 10% NAD+ pump cream from pharmacy sheet."),
    ("tretinoin", "Tretinoin Cream", "Skin & Hair", "skin-hair", "preview",
     "Tretinoin Cream", "0.025%", "45g",
     "Gold-standard retinoid", "Curology/derm $30–60/mo", "350+ pts/mo",
     "PICK: 0.025% 45g — industry starter strength (titrate to 0.05%)."),
    ("estriol-ghk-cu-cream", "Estriol + GHK-Cu Cream", "Skin & Hair", "skin-hair", "preview",
     "Estriol /Niacinamide/GHK-Cu /Hyaluronic Acid Cream", "Compounded anti-aging", "30g",
     "Women's longevity topical", "Alastin/med spa $100+", "125+ pts/mo", ""),
    ("hydroquinone-triple-cream", "Hydroquinone Triple Cream", "Skin & Hair", "skin-hair", "preview",
     "Hydroquionone/Tretinoin/Fluocinolone Acetonide", "Standard triple combo", "30g",
     "Prescription hyperpigmentation", "Derm compound $60–90", "100+ pts/mo", ""),
    ("doxycycline-acne", "Doxycycline (Acne)", "Skin & Hair", "skin-hair", "preview",
     "Doxycycline Capsules", "100mg", "30-count",
     "Oral acne anti-inflammatory", "Generic $15–30", "200+ pts/mo",
     "PICK: 100mg — standard anti-acne antibiotic dose."),
    ("finasteride-oral", "Finasteride Oral", "Skin & Hair", "skin-hair", "preview",
     "Finasteride", "1mg", "30-count",
     "Systemic DHT block hair + prostate", "Hims fin 1mg $30/mo", "400+ pts/mo",
     "PICK: 1mg — only FDA-approved hair loss dose."),
    # Protocols
    ("ivermectin", "Ivermectin Protocol", "Protocols", "antiparasitic", "live",
     "Ivermectin 18mg Capsules", "18mg", "30 capsules",
     "Antiparasitic protocol — niche loyalty", "N/A niche", "200+ pts/mo",
     "PICK: 18mg 30-cap — live CLYR protocol."),
    ("ivermectin-mebendazole", "Ivermectin + Mebendazole", "Protocols", "antiparasitic", "live",
     "Ivermectin + Mebendazole combined", "25mg/250mg", "30 capsules",
     "Broader antiparasitic coverage", "N/A niche", "100+ pts/mo", ""),
]

BRIEF_TEMPLATE = """# CLYR Health — Pharmacy Partner Brief
## {title}

**Document:** Launch Kit · {slug}  
**Brand:** CLYR Health (www.clyr.health)  
**Status:** {status}  
**Vertical:** {vertical}  
**Prepared for:** Olympia / Dispense Pro wholesale negotiation  
**Date:** June 2026

---

## 1. CLYR SKU summary

| Field | Specification |
|---|---|
| **CLYR brand name** | {title} |
| **Pharmacy dispense name** | {pharmacy_dispense} |
| **Standard strength (CLYR pick)** | {standard_strength} |
| **Package** | {package} |
| **Page (live/preview)** | [www.clyr.health/{slug}.html](https://www.clyr.health/{slug}.html) |
| **Marketing brief** | [Pharmacy brief](https://www.clyr.health/preview/launch-kit/briefs/{slug}.html) |

> **Strength selection note:** {notes}

---

## 2. Market positioning

{positioning}

**Competitive anchor (retail market):** {competitor}

CLYR operates LegitScript-certified telehealth with licensed physician networks. Doctors write prescriptions; CLYR owns patient acquisition, brand, compliance, and refill management. We are **not** a compounding pharmacy — we are a prescription platform routing volume to your 503A facility.

---

## 3. Volume commitment (negotiation ask)

| Metric | Target |
|---|---|
| **Projected patients at scale** | {volume_ask} |
| **Launch wave** | {wave} |
| **Relationship ask** | Tiered wholesale discount at committed monthly volume; dedicated account rep; 48hr turnaround |

We are indexing **52 SKUs** from your catalog with a path to **253 SKUs**. Early wholesale partners on Wave 1–3 SKUs receive prioritized marketing spend and volume routing.

---

## 4. Marketing plan

### Target patient
{target_patient}

### Key messages
{key_messages}

### Cross-sell paths
{cross_sell}

### Go-live requirements from pharmacy
1. Confirm **{pharmacy_dispense}** available at quoted wholesale
2. Confirm strength **{standard_strength}** as default SKU (single offering per CLYR page)
3. Provide COA / beyond-use dating for patient-facing quality section
4. Confirm shipping SLA (CLYR promises discreet 3–5 business day delivery)
5. Custom branding request (if applicable): CLYR label on {package}

---

## 5. Compliance

- 503A patient-specific prescription required
- Provider telehealth review before every fill
- LegitScript-certified marketing (www.clyr.health)
- HIPAA-compliant intake and patient records
- No insurance billing — cash/subscription model

---

## 6. Contact

**Orlando Smith · CLYR Health**  
Platform: https://www.clyr.health  
Launch kit: https://www.clyr.health/preview/launch-kit/

*This brief is part of the CLYR 52-product pharmacy partner pack. Master index: /preview/launch-kit/*
"""

TARGETS = {
    "Weight Loss": ("Adults 25–65 seeking GLP-1 weight loss, BMI-qualified", "• Medical-grade compounded + brand options\n• No membership fee — transparent pricing\n• Provider-supervised titration", "GLP-1 → Lipo-Mino → Metformin → NAD+"),
    "Daily Wellness": ("Health optimizers 35–65, longevity-focused", "• Injectable cofactors and peptides\n• Provider-monitored protocols\n• Pairs with weight loss outcomes", "GLP-1 patient → NAD+ → Sermorelin → Glutathione"),
    "Peptides": ("Athletes, recovery-focused, biohackers 30–55", "• Pharmacy-grade peptides\n• Provider supervision\n• Not research-chemical gray market", "Wellness → BPC after GLP-1 → GHK topical cross-sell"),
    "Men's Hormone": ("Men 35–65 with low-T symptoms, fertility-preserving segment", "• Full TRT stack in one platform\n• No $25/mo membership (Hone model)\n• Enclomiphene + HCG alternatives", "Weight loss men → TRT → Sexual health → Peptides"),
    "Women's Hormone": ("Peri/menopausal women 40–65", "• Bioidentical depth competitors lack\n• GLP-1 cross-sell (weight + hormones)\n• No Midi-style membership lock-in", "GLP-1 women → HRT → Skin longevity → NAD face cream"),
    "Sexual Health": ("Men and women 30–65, libido and ED", "• Multi-mechanism single doses (CLYR differentiator)\n• Combo ODT, gummies, troches, trimix depth\n• Discreet subscription delivery", "TRT → ED stack; PT-141 libido; Oxytocin bonding"),
    "Skin & Hair": ("Adults 18–55 acne and hair loss", "• Multi-mechanism topicals (not plain minox)\n• CLYR Tri Gel proprietary 503A\n• Pharmacy-depth vs Hims single-ingredient", "Acne: Tri Gel + Doxycycline; Hair: spray + finasteride; Longevity: NAD cream"),
    "Recovery": ("LDN and wellness protocol patients", "• Niche loyalty community\n• Provider-gated protocols", "Wellness → LDN; Ivermectin patient trust transfer"),
    "Protocols": ("Protocol-motivated patients, provider-directed", "• Niche trust vertical\n• Provider-supervised antiparasitic protocols", "Protocol patient → full wellness catalog"),
}

WAVES = {
    "preview": "Wave 2–5 (preview built, awaiting wholesale)",
    "live": "Live — requesting volume discount on existing fills",
}


def _inline(text: str) -> str:
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(
        r'(?<!["\'>])(https?://[^\s<]+)',
        r'<a href="\1">\1</a>',
        text,
    )
    return text


def brief_html(md: str, title: str) -> str:
    lines_out: list[str] = []
    in_table = False
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            lines_out.append('</ul>')
            in_ul = False
        if in_ol:
            lines_out.append('</ol>')
            in_ol = False

    def close_table():
        nonlocal in_table
        if in_table:
            lines_out.append('</table>')
            in_table = False

    for line in md.split('\n'):
        if line.startswith('|') and '|' in line[1:]:
            close_lists()
            if not in_table:
                lines_out.append('<table>')
                in_table = True
            if re.match(r'^\|[-| ]+\|$', line):
                continue
            cells = [_inline(c.strip()) for c in line.strip('|').split('|')]
            tag = 'th' if lines_out[-1] == '<table>' else 'td'
            lines_out.append('<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>')
            continue
        close_table()

        if m := re.match(r'^# (.+)$', line):
            close_lists()
            lines_out.append(f'<h1>{_inline(m.group(1))}</h1>')
        elif m := re.match(r'^## (.+)$', line):
            close_lists()
            lines_out.append(f'<h2>{_inline(m.group(1))}</h2>')
        elif m := re.match(r'^### (.+)$', line):
            close_lists()
            lines_out.append(f'<h3>{_inline(m.group(1))}</h3>')
        elif line.startswith('> '):
            close_lists()
            lines_out.append(f'<blockquote>{_inline(line[2:])}</blockquote>')
        elif line.startswith('• ') or line.startswith('- '):
            if not in_ul:
                close_lists()
                lines_out.append('<ul>')
                in_ul = True
            lines_out.append(f'<li>{_inline(line[2:])}</li>')
        elif m := re.match(r'^(\d+)\. (.+)$', line):
            if not in_ol:
                close_lists()
                lines_out.append('<ol>')
                in_ol = True
            lines_out.append(f'<li>{_inline(m.group(2))}</li>')
        elif line.strip() == '---':
            close_lists()
            lines_out.append('<hr>')
        elif line.strip():
            close_lists()
            lines_out.append(f'<p>{_inline(line)}</p>')

    close_lists()
    close_table()
    content = '\n'.join(lines_out)
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="robots" content="noindex">
<title>{title} · Pharmacy Brief | CLYR</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{{font-family:'DM Sans',sans-serif;max-width:820px;margin:0 auto;padding:40px 24px 80px;color:#1A1A1A;line-height:1.65}}
h1{{font-size:28px;margin-bottom:8px}}h2{{font-size:20px;margin-top:36px;color:#00B4C5}}h3{{font-size:16px;margin-top:24px}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}}th,td{{border:1px solid #E2E7EB;padding:10px 14px;text-align:left;vertical-align:top}}th{{background:#0d1b2e;color:#fff}}
ul,ol{{margin:12px 0 16px 24px;font-size:15px}}li{{margin-bottom:6px}}
blockquote{{background:#f0fafb;border-left:4px solid #00B4C5;padding:12px 16px;margin:16px 0;font-size:14px}}
.print-bar{{display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap}}.print-btn{{display:inline-block;padding:10px 20px;background:#00B4C5;color:#fff;border-radius:8px;font-weight:600;text-decoration:none;font-size:13px}}.print-btn:hover{{background:#0095A4}}
a{{color:#00B4C5}}.back{{display:inline-block;margin-bottom:24px;color:#00B4C5;font-weight:600;text-decoration:none}}
@media print{{body{{padding:20px}}}}</style></head><body>
<a class="back" href="/preview/launch-kit/">← Launch Kit</a>
<div class="print-bar"><a class="print-btn" href="javascript:window.print()">Print / Save PDF</a></div>
{content}
</body></html>'''


def strip_internal_from_product_page(text: str) -> str:
    """Remove pharmacy negotiation UI from customer-facing product pages."""
    text = re.sub(
        r'<div class="admin-strip"[^>]*>.*?</div>\s*',
        '',
        text,
        flags=re.S,
    )
    text = re.sub(
        r'<div class="launch-spec"[^>]*>.*?</div>\s*',
        '',
        text,
        flags=re.S,
    )
    # Strip preview strips that expose internal launch-kit / pharmacy brief links
    text = re.sub(
        r'<div class="preview-strip">[^<]*(?:launch-kit|Pharmacy brief|Pharmacy pack)[^<]*</div>\s*',
        '',
        text,
        flags=re.I | re.S,
    )
    return text


def patch_product_page(slug: str, status: str):
    """Customer product pages must never show wholesale/pharmacy negotiation blocks."""
    path = ROOT / f"{slug}.html"
    if not path.exists():
        return
    text = strip_internal_from_product_page(path.read_text())
    if status == 'preview':
        customer_strip = (
            '<div class="preview-strip">Preview — pricing confirmed at consultation. '
            '<a href="/intake-wellness.html">Join waitlist</a></div>'
        )
        if 'preview-strip' in text:
            text = re.sub(r'<div class="preview-strip">.*?</div>', customer_strip, text, count=1, flags=re.S)
        elif '<body>' in text:
            text = text.replace('<body>', '<body>\n' + customer_strip, 1)
    path.write_text(text)


def main():
    BRIEFS.mkdir(parents=True, exist_ok=True)
    kit_data = []

    for row in CATALOG:
        (slug, title, vertical, hub, status, pharm, strength, pkg, positioning,
         competitor, volume, notes) = row
        tp, km, cs = TARGETS.get(vertical, ("General wellness patients", "• Provider-supervised\n• Pharmacy-compounded", "Cross-vertical CLYR catalog"))
        wave = WAVES[status]
        md = BRIEF_TEMPLATE.format(
            title=title, slug=slug, status=status.upper(), vertical=vertical,
            pharmacy_dispense=pharm, standard_strength=strength, package=pkg,
            positioning=positioning, competitor=competitor, volume_ask=volume,
            notes=notes or "Single industry-standard strength selected from pharmacy menu.",
            wave=wave, target_patient=tp, key_messages=km.replace('\n', '\n\n'), cross_sell=cs,
        )
        (BRIEFS / f"{slug}.md").write_text(md)
        (BRIEFS / f"{slug}.html").write_text(brief_html(md, title))

        patch_product_page(slug, status)

        kit_data.append({
            "slug": slug, "title": title, "vertical": vertical, "hub": hub,
            "status": status, "strength": strength, "package": pkg,
            "pharmacy": pharm, "page": f"/{slug}.html",
            "brief": f"/preview/launch-kit/briefs/{slug}.html",
        })

    # JSON
    (KIT / "launch-kit.json").write_text(json.dumps({"products": kit_data, "count": len(kit_data)}, indent=2))

    # Master pharmacy pack MD
    pack_lines = ["# CLYR Health — Pharmacy Partner Pack\n", "**52 products · June 2026 · Orlando Smith**\n", "Send this pack with the launch kit link: https://www.clyr.health/preview/launch-kit/\n", "---\n"]
    by_v: dict[str, list] = {}
    for k in kit_data:
        by_v.setdefault(k["vertical"], []).append(k)
    for v in sorted(by_v):
        pack_lines.append(f"\n## {v}\n")
        for k in by_v[v]:
            pack_lines.append(
                f"- **{k['title']}** — `{k['strength']}` · {k['package']} · "
                f"[Product page](https://www.clyr.health{k['page']}) · "
                f"[Pharmacy brief](https://www.clyr.health{k['brief']})"
            )
    (KIT / "PHARMACY-PARTNER-PACK.md").write_text('\n'.join(pack_lines))

    # Index HTML
    sections = []
    for v in sorted(by_v):
        cards = []
        for k in by_v[v]:
            badge = 'LIVE' if k['status'] == 'live' else 'PREVIEW'
            bc = '#10B981' if k['status'] == 'live' else '#00B4C5'
            cards.append(f'''<div class="card" data-title="{k['title'].lower()}" data-vertical="{v.lower()}">
  <a class="card-hit" href="{k['page']}">
    <span class="badge" style="background:{bc}">{badge}</span>
    <h3>{k['title']}</h3>
    <p class="spec">{k['strength']} · {k['package']}</p>
    <p class="pharm">{k['pharmacy'][:70]}{'…' if len(k['pharmacy'])>70 else ''}</p>
  </a>
  <div class="links">
    <a href="{k['page']}">Product page</a>
    <a href="{k['brief']}">Pharmacy brief</a>
    <a href="/{k['hub']}.html">Hub</a>
  </div>
</div>''')
        sections.append(f'<section class="vertical" id="{v.lower().replace(" ","-")}"><h2>{v} <span>{len(by_v[v])}</span></h2><div class="grid">{"".join(cards)}</div></section>')

    index = f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CLYR Launch Kit · 52 Products · Pharmacy Partner Pack</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
:root{{--teal:#00B4C5;--dark:#0A0E1A;--gray:#6B7C8A}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'DM Sans',sans-serif;background:#0A0E1A;color:#e8ecf0;line-height:1.5}}
.top{{background:linear-gradient(135deg,#0d1b2e 0%,#1a3045 50%,#0d2a35 100%);padding:48px 24px 56px;text-align:center;border-bottom:1px solid rgba(0,180,197,.2)}}
.top h1{{font-size:clamp(32px,5vw,48px);font-weight:700;letter-spacing:-.03em}}.top h1 em{{font-family:'Instrument Serif',serif;font-style:italic;color:var(--teal)}}
.top p{{color:rgba(255,255,255,.55);max-width:640px;margin:12px auto 28px;font-size:17px}}
.actions{{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:14px 28px;border-radius:100px;font-weight:700;font-size:14px;text-decoration:none;transition:transform .2s}}
.btn:hover{{transform:translateY(-2px)}}.btn-primary{{background:var(--teal);color:#fff}}.btn-ghost{{background:rgba(255,255,255,.08);color:#fff;border:1px solid rgba(255,255,255,.15)}}
.stats{{display:flex;gap:20px;justify-content:center;margin-top:32px;flex-wrap:wrap}}
.stat{{text-align:center}}.stat strong{{display:block;font-size:28px;color:var(--teal)}}.stat span{{font-size:12px;color:rgba(255,255,255,.45);text-transform:uppercase;letter-spacing:.08em}}
.toolbar{{max-width:1200px;margin:0 auto;padding:24px 20px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
.toolbar input{{flex:1;min-width:200px;padding:12px 18px;border-radius:12px;border:1px solid #2a3544;background:#141c28;color:#fff;font-size:15px}}
.toolbar input::placeholder{{color:#6B7C8A}}
.filter{{padding:10px 18px;border-radius:100px;border:1px solid #2a3544;background:#141c28;color:#94A3B0;font-size:13px;font-weight:600;cursor:pointer}}
.filter.active{{border-color:var(--teal);color:var(--teal);background:rgba(0,180,197,.1)}}
main{{max-width:1200px;margin:0 auto;padding:0 20px 80px}}
.vertical{{margin-bottom:48px}}.vertical h2{{font-size:20px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:10px;color:#fff}}
.vertical h2 span{{font-size:12px;background:#141c28;padding:4px 12px;border-radius:100px;color:var(--gray);font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}}
.card{{background:#141c28;border:1px solid #2a3544;border-radius:16px;padding:0;position:relative;transition:border-color .2s;display:flex;flex-direction:column;overflow:hidden}}
.card:hover{{border-color:rgba(0,180,197,.4)}}.card.hidden{{display:none}}
.card-hit{{display:block;padding:20px 20px 12px;text-decoration:none;color:inherit;flex:1;position:relative}}
.card-hit:hover h3{{color:var(--teal)}}
.badge{{position:absolute;top:14px;right:14px;font-size:9px;font-weight:800;padding:4px 10px;border-radius:100px;color:#fff;letter-spacing:.06em}}
.card h3{{font-size:17px;font-weight:700;margin:8px 0 8px;padding-right:56px;color:#fff;transition:color .2s}}
.spec{{font-size:13px;color:var(--teal);font-weight:600;margin-bottom:6px}}.pharm{{font-size:12px;color:var(--gray);margin-bottom:14px;line-height:1.45}}
.links{{display:flex;gap:14px;flex-wrap:wrap;padding:0 20px 20px}}.links a{{font-size:12px;font-weight:600;color:var(--teal);text-decoration:none}}.links a:hover{{text-decoration:underline}}
.footer-note{{text-align:center;padding:40px 20px;font-size:13px;color:var(--gray);border-top:1px solid #2a3544;max-width:1200px;margin:0 auto}}
</style></head><body>
<div class="top">
  <h1>Launch Kit · <em>52 products</em></h1>
  <p><strong>Internal only</strong> — pharmacy wholesale negotiation. Not linked from live product pages. Every SKU: product page + marketing brief + industry-standard strength picked from Olympia menu.</p>
  <div class="actions">
    <a class="btn btn-primary" href="/preview/launch-kit/PHARMACY-PARTNER-PACK.html">Open Partner Pack</a>
    <a class="btn btn-ghost" href="/preview/launch-kit/PHARMACY-PARTNER-PACK.md">Partner Pack (MD)</a>
    <a class="btn btn-ghost" href="/preview/launch-kit/CLYR-TRI-GEL-COMPOUNDING-REQUEST.html">Tri Gel compound request</a>
    <a class="btn btn-ghost" href="/preview/launch-kit/launch-kit.json">JSON export</a>
    <a class="btn btn-ghost" href="/preview/catalog/">Catalog index</a>
    <a class="btn btn-ghost" href="/">← CLYR Health</a>
  </div>
  <div class="stats">
    <div class="stat"><strong>{len(kit_data)}</strong><span>Total SKUs</span></div>
    <div class="stat"><strong>{sum(1 for k in kit_data if k['status']=='live')}</strong><span>Live</span></div>
    <div class="stat"><strong>{sum(1 for k in kit_data if k['status']=='preview')}</strong><span>Preview</span></div>
    <div class="stat"><strong>253</strong><span>Pharmacy depth</span></div>
  </div>
</div>
<div class="toolbar">
  <input type="search" id="q" placeholder="Search products…" oninput="filterCards()">
  <button class="filter active" data-v="all" onclick="setV('all',this)">All</button>
  <button class="filter" data-v="weight loss" onclick="setV('weight loss',this)">Weight</button>
  <button class="filter" data-v="men's hormone" onclick="setV('men\\'s hormone',this)">Men's HRT</button>
  <button class="filter" data-v="women's hormone" onclick="setV('women\\'s hormone',this)">Women's HRT</button>
  <button class="filter" data-v="sexual health" onclick="setV('sexual health',this)">Sexual</button>
  <button class="filter" data-v="skin & hair" onclick="setV('skin & hair',this)">Skin/Hair</button>
  <button class="filter" data-v="daily wellness" onclick="setV('daily wellness',this)">Wellness</button>
  <button class="filter" data-v="peptides" onclick="setV('peptides',this)">Peptides</button>
  <button class="filter" data-v="recovery" onclick="setV('recovery',this)">Recovery</button>
  <button class="filter" data-v="protocols" onclick="setV('protocols',this)">Protocols</button>
</div>
<main>{"".join(sections)}</main>
<div class="footer-note">CLYR Health · LegitScript certified · Doctors write scripts, CLYR owns the brand · June 2026</div>
<script>
var curV='all';
function setV(v,el){{curV=v;document.querySelectorAll('.filter').forEach(function(f){{f.classList.remove('active')}});el.classList.add('active');filterCards()}}
function filterCards(){{
  var q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('.card').forEach(function(c){{
    var t=c.dataset.title, v=c.dataset.vertical;
    var show=(curV==='all'||v===curV)&&(!q||t.includes(q)||v.includes(q)||c.textContent.toLowerCase().includes(q));
    c.classList.toggle('hidden',!show);
  }});
  document.querySelectorAll('.vertical').forEach(function(s){{
    var vis=s.querySelectorAll('.card:not(.hidden)').length;
    s.style.display=vis?'block':'none';
  }});
}}
</script></body></html>'''
    (KIT / "index.html").write_text(index)

    # Partner pack HTML — full clickable table
    pack_rows = []
    for v in sorted(by_v):
        for k in by_v[v]:
            pack_rows.append(
                f'<tr><td><strong>{k["title"]}</strong><br><span style="color:#6B7C8A;font-size:12px">{v}</span></td>'
                f'<td><code>{k["strength"]}</code><br>{k["package"]}</td>'
                f'<td><a href="{k["page"]}">Product page</a></td>'
                f'<td><a href="{k["brief"]}">Pharmacy brief</a></td></tr>'
            )
    pack_html = f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="robots" content="noindex">
<title>Pharmacy Partner Pack · CLYR Health</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>body{{font-family:'DM Sans',sans-serif;max-width:1100px;margin:0 auto;padding:40px 24px 80px;color:#1A1A1A;line-height:1.65}}
h1{{font-size:28px;margin-bottom:8px}}p.lede{{color:#6B7C8A;max-width:720px;margin-bottom:28px}}
table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}}th,td{{border:1px solid #E2E7EB;padding:12px 14px;text-align:left;vertical-align:top}}th{{background:#0d1b2e;color:#fff}}
a{{color:#00B4C5;font-weight:600;text-decoration:none}}a:hover{{text-decoration:underline}}
.back,.print-btn{{display:inline-block;margin-bottom:24px;color:#00B4C5;font-weight:600;text-decoration:none}}
.print-btn{{background:#00B4C5;color:#fff;padding:10px 20px;border-radius:8px;margin-left:12px}}code{{background:#f0fafb;padding:2px 6px;border-radius:4px;font-size:13px}}
@media print{{body{{padding:20px}}}}</style></head><body>
<a class="back" href="/preview/launch-kit/">← Launch Kit</a>
<a class="print-btn" href="javascript:window.print()">Print / Save PDF</a>
<h1>CLYR Health — Pharmacy Partner Pack</h1>
<p class="lede"><strong>52 products · June 2026</strong> — Every row links to the live product page and pharmacy marketing brief. Industry-standard strength picked per SKU.</p>
<table>
<tr><th>Product</th><th>CLYR standard offering</th><th>Page</th><th>Brief</th></tr>
{"".join(pack_rows)}
</table>
<p style="margin-top:32px;color:#6B7C8A;font-size:13px">Launch kit: <a href="https://www.clyr.health/preview/launch-kit/">www.clyr.health/preview/launch-kit/</a></p>
</body></html>'''
    (KIT / "PHARMACY-PARTNER-PACK.html").write_text(pack_html)

    # CLYR Tri Gel formal compounding request
    tri_gel_doc = """# CLYR Tri Gel — 503A Compounding Request

**Brand:** CLYR Health (www.clyr.health)  
**Prepared for:** Olympia / Dispense Pro  
**Date:** June 2026  
**Status:** Wave 1 proprietary SKU — NOT a Cabtreo copy

---

## Requested formulation

| Ingredient | Strength | Notes |
|---|---|---|
| Clindamycin phosphate | 1.2% | Antibiotic — acne anti-inflammatory |
| Adapalene | 0.15% | Retinoid — comedolytic |
| Benzoyl peroxide | 3.1% | Antimicrobial — P. acnes |
| Niacinamide | 4% | **CLYR differentiator** — barrier support, not in Cabtreo |

**Vehicle:** Proprietary base suitable for airless pump  
**Package:** 50g airless glass pump (CLYR-branded label request)  
**Beyond-use dating:** Per 503A stability data — request COA

---

## Why this compound

- Cabtreo-class triple therapy at **fraction of brand cash pricing** ($300+/mo retail)
- 4% niacinamide is CLYR's proprietary add — legitimate 503A differentiation
- Target: adults 18–45 with moderate inflammatory acne
- Cross-sell: Doxycycline 100mg oral + Tretinoin 0.025% for non-responders

---

## Volume projection

| Metric | Target |
|---|---|
| Patients at scale | 300+ pts/mo |
| Launch wave | Wave 1 (preview built) |
| Marketing | LegitScript-certified telehealth — CLYR owns patient acquisition |

---

## Links

- Product page: https://www.clyr.health/clyr-tri-gel.html
- Pharmacy brief: https://www.clyr.health/preview/launch-kit/briefs/clyr-tri-gel.html
- Launch kit: https://www.clyr.health/preview/launch-kit/

*Part of the CLYR 52-product pharmacy partner pack.*
"""
    (KIT / "CLYR-TRI-GEL-COMPOUNDING-REQUEST.md").write_text(tri_gel_doc)
    (KIT / "CLYR-TRI-GEL-COMPOUNDING-REQUEST.html").write_text(brief_html(tri_gel_doc, "CLYR Tri Gel Compounding Request"))

    print(f"Launch kit: {len(kit_data)} products")
    print(f"Briefs: {len(list(BRIEFS.glob('*.md')))} markdown + HTML")
    print(f"Index: {KIT / 'index.html'}")


if __name__ == "__main__":
    main()