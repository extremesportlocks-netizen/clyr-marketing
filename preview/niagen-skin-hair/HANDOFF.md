# Niagen + Skin & Hair — Preview Branch Handoff

**Branch:** `preview/niagen-skin-hair-jun2026`  
**Status:** Live on `main` under `/preview/` as **Coming Soon**. Not linked from live nav. `noindex` on preview pages.  
**Repo:** `extremesportlocks-netizen/clyr-marketing`

## Live preview URLs

| Asset | Path |
|-------|------|
| Niagen + Skin & Hair coming soon | `/preview/niagen-skin-hair/` |
| Antiparasitic hero v2 (dosing + real pill photos) | `/preview/antiparasitic-hero-v2.html` |
| This handoff | `/preview/niagen-skin-hair/HANDOFF.md` |

## Revert (if needed)

Before deploy, `main` was tagged **`revert-point/before-coming-soon-jun2026`**.

**Option A — revert the merge (safest, keeps history):**
```bash
git checkout main
git revert -m 1 <merge-commit-sha>
git push origin main
```

**Option B — reset to the tag (only if no other commits landed on main since):**
```bash
git checkout main
git reset --hard revert-point/before-coming-soon-jun2026
git push origin main --force-with-lease
```

The preview branch `preview/niagen-skin-hair-jun2026` stays on GitHub either way.

## Niagen (Daily Wellness)

**Exists:** `niagen.html` (~70% done)  
**Missing:** intake catalog entry, backend SKUs, megamenu + catalog cards

### Wire-up checklist

- [ ] `intake-wellness.html` — add `niagen` to frontend `CATALOG`
- [ ] `clyr-backend/services/product-catalog.js` — `niagen_monthly` / `niagen_3month` + Stripe
- [ ] `daily-wellness.html`, `wellness.html`, `index.html` — product cards
- [ ] Megamenu — Niagen under Daily Wellness (sync ~30 HTML files)
- [ ] Cross-link `nad.html` ↔ `niagen.html`

**Template:** clone `nad.html` tier pricing pattern.

## Skin & Hair (new vertical)

**Exists:** stale `hair.html` only (old nav, waitlist)  
**New products:** Mindoxifil, Cabtreo

### New files

| File | Based on |
|------|----------|
| `skin-hair.html` | `daily-wellness.html` |
| `mindoxifil.html` | `tadalafil.html` or `nad.html` |
| `cabtreo.html` | same |
| `/img/cardv2/mindoxifil.webp`, `cabtreo.webp` | new assets |

### Nav (new megamenu item)

```
Skin & Hair ▼
  Mindoxifil
  Cabtreo
```

### Backend

- [ ] `type: 'skin_hair'` in `product-catalog.js`
- [ ] `SKIN_HAIR_INTAKE_QUESTIONS`
- [ ] Populate `VERTICALS.HAIR` in `product-catalog-portal.js`
- [ ] Stripe + MDI offering IDs

## Antiparasitic hero v2

Approved mockup style with dosing from live pages:

- **Ivermectin:** 18mg capsules · dosed to your body weight · $139/mo
- **Combo:** 25mg ivermectin + 250mg mebendazole per capsule · $169/mo
- Real pill images from `/img/card/ivermectin.png` + `mebendazole.png`

See `preview/antiparasitic-hero-v2.html`.

## Build order

1. Niagen backend + intake wiring  
2. Niagen nav + catalog cards  
3. `skin-hair.html` hub + nav tab  
4. `mindoxifil.html` + `cabtreo.html`  
5. Backend SKUs + intake  
6. Megamenu sync pass  

## Open questions (Orlando)

1. Mindoxifil + Cabtreo pricing tiers?
2. Cabtreo — compounded or branded?
3. Launch mode: full checkout or `COMING_SOON` waitlist?
4. Stripe + MDI offering IDs ready?