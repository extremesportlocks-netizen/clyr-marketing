# Content Calendar — Q3 2026 (Jul–Sep)

## Publishing cadence
- **2 journal articles/week** (Tue + Thu)
- **1 geo/state article/month**
- **OG images** auto-generated on rebuild

---

## July 2026

| Week | Tue | Thu |
|------|-----|-----|
| W1 | MICC lipotropic injection guide | Zepbound vs compounded tirzepatide |
| W2 | Weight loss plateau on GLP-1 | Wegovy tablets oral semaglutide |
| W3 | Ivermectin wellness protocol overview | Lipo-Mino injection explained |
| W4 | Semaglutide California telehealth | Sexual health telehealth guide |

## August 2026

| Week | Tue | Thu |
|------|-----|-----|
| W1 | Glutathione push injection benefits | FoundAYO hair regrowth science |
| W2 | NAD+ stacking with GLP-1 | MIC injection vs oral supplements |
| W3 | Tirzepatide cost breakdown 2026 | Hair loss telehealth finasteride path |
| W4 | Semaglutide New York access | Antiparasitic protocol education piece |

## September 2026

| Week | Tue | Thu |
|------|-----|-----|
| W1 | Longevity stack NAD + glutathione | PT-141 vs oxytocin nasal comparison |
| W2 | Testosterone + GLP-1 body composition | Estriol cream menopause skin |
| W3 | Compounded semaglutide Ohio | Weight loss telehealth Georgia |
| W4 | Q3 recap + Surmount trial update | Holiday weight management GLP-1 |

---

## Article JSON location

`scripts/journal-content/<slug>.json` → publish:

```bash
python3 scripts/publish-journal-local.py scripts/journal-content/<slug>.json
python3 scripts/generate-journal-og.py  # if Pillow installed
python3 scripts/update-sitemap-journals.py
git add -A && git commit -m "journal: <slug>" && git push
```

---

## Social derivative (per article)

1. Pull deck → X thread (3 tweets)
2. OG image → Instagram carousel slide 1
3. H2 bullets → LinkedIn post (if applicable)

Canva templates: `~/.grok/skills/ivermectin-canva/SKILL.md`