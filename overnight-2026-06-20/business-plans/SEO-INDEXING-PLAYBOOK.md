# SEO & Indexing Playbook — CLYR Health

## Current state (2026-06-20)

- **135 URLs** in sitemap.xml (52 journal + product + legal)
- **GTM** GTM-T4FVQ87G site-wide
- **Search Console** property `clyr.health` — verified, receiving clicks
- **Fixed:** journal trailing-slash redirects, robots/canonical/JSON-LD on indexable pages
- **GBP:** entity live, website link pending URL alignment

---

## Weekly Search Console routine

### Monday — Coverage
1. Indexing → Pages → check "Not indexed" count
2. For each URL: URL Inspection → Request indexing (max 10/day priority pages)
3. Priority order: homepage, `/weight-loss.html`, `/semaglutide.html`, `/tirzepatide.html`, top 5 journals by impressions

### Wednesday — Performance
1. Export last 28 days queries
2. Identify queries with impressions > 50 and position > 8 → target with new journal or on-page H2
3. Update `metaDescription` on matching product pages

### Friday — Sitemap
1. Confirm `https://www.clyr.health/sitemap.xml` last read < 7 days
2. Run `python3 scripts/update-sitemap-journals.py`
3. Push if `lastmod` changed

---

## Issue → fix matrix

| GSC issue | Fix |
|-----------|-----|
| Page with redirect | Run `scripts/fix-journal-urls.py` — use trailing-slash canonicals |
| Discovered – not indexed | Add robots canonical JSON-LD via `polish-indexable-pages.py` |
| Crawled – not indexed | Improve internal links from homepage + journal hub |
| Soft 404 | Check page has unique content > 300 words |
| Duplicate without canonical | Ensure `<link rel="canonical">` present |

---

## Internal linking rules

1. Every product page links to **2 journal articles** minimum (`link-products-to-journals.py`)
2. Every journal links to **1 product** + **2 related journals**
3. Homepage footer → all treatment hubs
4. Journal hub featured grid rotates new posts to top

---

## Schema checklist (homepage)

- [x] MedicalBusiness with phone, email, address
- [x] sameAs: Instagram + Google Maps
- [x] hasMap
- [x] FAQPage
- [ ] Add `aggregateRating` only when real GBP reviews exist (never fake)

---

## Geo expansion queue (state journals)

Priority states (telehealth-friendly, high search volume):
1. California — `semaglutide-california`
2. New York — `semaglutide-new-york`
3. Ohio — `compounded-tirzepatide-ohio`
4. Georgia — `weight-loss-telehealth-georgia`
5. North Carolina — `glp1-weight-loss-north-carolina`

Template: copy `semaglutide-florida` structure, swap state-specific regulations and provider network notes.