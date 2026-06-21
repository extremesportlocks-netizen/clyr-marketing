# P0 Action Guide — Do These Now (~10 min)

Site pre-flight: **PASS** (verify tag live, sitemap 100 URLs, 7 geo articles 200 OK)

---

## P0-1: GBP Website Verification (5 min)

**Go to:** https://business.google.com

1. Select **CLYR Health**
2. Click **Edit profile** (pencil icon)
3. **Business information** → find **Website**
4. Enter exactly: `https://clyr.health`  
   (no `www` — matches your Search Console property name)
5. Click **Save**
6. When prompted to verify:
   - Choose **Verify with Google Search Console** (if shown), OR
   - Choose **HTML tag** — already live on homepage, click Verify
7. Wait for green checkmark on website field

**If verification fails:** try alternate URL `https://www.clyr.health` only after adding that URL-prefix property in GSC (P0-2b below).

**Do NOT** delete Business Manager connection `om-2650970875912821456`.

Profile ID for support: `10576517044753504409`

---

## P0-2: Search Console — Resubmit Sitemap (2 min)

**Go to:** https://search.google.com/search-console  
Property: **clyr.health**

1. Left sidebar → **Indexing** → **Sitemaps**
2. In "Add a new sitemap", enter: `sitemap.xml`
3. Click **Submit**
4. Confirm status shows **Success** (may take a few hours for "Last read")

Full URL submitted: `https://www.clyr.health/sitemap.xml`  
(Already declared in `robots.txt`)

**Optional P0-2b** (if GBP www verification needed):
1. Property dropdown → **+ Add property**
2. **URL prefix:** `https://www.clyr.health`
3. Verification → **HTML tag** → **Verify** (tag already on homepage)

---

## P0-3: Request Indexing — 7 Geo Articles (5 min)

Left sidebar → **URL inspection** (top search bar)

Paste each URL → Enter → **Request indexing** (button appears if eligible)

```
https://www.clyr.health/journal/semaglutide-california/
https://www.clyr.health/journal/semaglutide-new-york/
https://www.clyr.health/journal/compounded-tirzepatide-ohio/
https://www.clyr.health/journal/weight-loss-telehealth-georgia/
https://www.clyr.health/journal/glp1-weight-loss-north-carolina/
https://www.clyr.health/journal/semaglutide-illinois/
https://www.clyr.health/journal/semaglutide-michigan/
```

Google limits ~10–12 indexing requests per day per property — 7 is within quota.

Also request (high value):
```
https://www.clyr.health/
https://www.clyr.health/weight-loss.html
```

---

## Done checklist

- [ ] GBP website shows verified + linked
- [ ] Sitemap submitted / last read updating
- [ ] 7 geo URLs requested (or "already indexed")
- [ ] Screenshot any error messages → send to agent