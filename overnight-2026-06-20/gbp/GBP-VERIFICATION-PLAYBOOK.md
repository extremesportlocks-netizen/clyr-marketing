# GBP Website Verification — CLYR Health (definitive playbook)

**You are NOT failing.** Business Manager "Connection to CLYR Health" is **already done**.  
That is account ownership — not website verification.

| ID | Value |
|----|-------|
| Business Profile ID | `10576517044753504409` |
| Business Manager org | `om-2650970875912821456` |
| Knowledge Graph / GBP entity | `/g/11z94cc8v_` |
| Verified GSC property (yours) | `clyr.health` |
| Live canonical website | `https://www.clyr.health` |
| HTML verification tag | `9h7apy74gKqUxepuj34VgZ5-7Ie9JXNGqWTuwQ-xL6I` (live on homepage) |

---

## The actual bug (URL mismatch)

Google instant-verification via Search Console requires the **GBP website URL** to match a **verified GSC property URL prefix exactly**.

- Your Search Console shows **`clyr.health`** (likely domain or non-www prefix).
- Your GBP website is probably **`https://www.clyr.health`**.
- Google treats those as **different properties** unless you verified a **Domain property** via DNS.

**Site-side is done.** The tag is live. This is a URL-alignment issue in Google's UI.

---

## Fix A — 2 minutes (try first)

1. [business.google.com](https://business.google.com) → **CLYR Health** → **Edit profile**
2. **Business information** → **Website**
3. Change to: **`https://clyr.health`** (no `www`)
4. Save → Verify → **Search Console**
5. Wait 24–48h for Maps to show website link

`clyr.health` 301-redirects to `www.clyr.health` — patients still land correctly.

---

## Fix B — 5 minutes (permanent www alignment)

1. [search.google.com/search-console](https://search.google.com/search-console)
2. **+ Add property** → **URL prefix** → `https://www.clyr.health`
3. Verification: **HTML tag** (already on homepage — click Verify immediately)
4. GBP website → `https://www.clyr.health` → Verify via Search Console

---

## Fix C — GBP support (if A and B fail)

Contact GBP support with:

```
Business Profile ID: 10576517044753504409
Organization: om-2650970875912821456
Website: https://www.clyr.health
Search Console: clyr.health verified, HTML tag live
Issue: Website verification fails despite Search Console ownership
Request: Link verified Search Console property to GBP website field
```

---

## What NOT to do

- **Do not** delete Business Manager connection — that removes profile access
- **Do not** re-verify Search Console on Overview — there is no button there (already verified)
- **Do not** add a second conflicting website URL in GBP

---

## Site-side checklist (complete ✓)

- [x] `google-site-verification` meta on `index.html`
- [x] GBP Maps URL in `sameAs` + `hasMap` JSON-LD
- [x] Footer "Google Business Profile" link (85 pages)
- [x] Contact page "Find Us on Google" card
- [x] Full NAP in schema (5020 Clark Rd #159, Sarasota FL)