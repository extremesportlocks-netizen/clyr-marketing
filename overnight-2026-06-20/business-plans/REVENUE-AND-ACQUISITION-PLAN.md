# Revenue & Acquisition Plan — CLYR Health

## Unit economics (current pricing)

| Product | Price | Gross margin est. |
|---------|-------|-------------------|
| Sema monthly | $229/mo | ~55–65% after pharmacy + provider |
| Sema 3-mo | $189/mo ($567) | Higher retention LTV |
| Tirz T1 monthly | $249/mo | ~50–60% |
| Tirz T1 3-mo | $199/mo ($597) | Best LTV/cohort |
| Tirz T2 monthly | $399/mo | Higher dose margin |
| Wellness SKUs | $74–$199/mo | Volume add-ons |

**Target blended CAC:** < $180 (3:1 LTV:CAC at 6-month retention)

---

## Funnel stages

```
Awareness → Landing (journal/ads) → Intake start → Provider review → Pay → Ship → Refill
```

### Conversion benchmarks (telehealth weight loss)

| Stage | Target |
|-------|--------|
| Landing → intake start | 8–12% |
| Intake start → complete | 45–60% |
| Complete → approved + paid | 70–85% |
| Month-2 refill | 65–75% |

---

## Channel mix (90-day target)

| Channel | % of intake starts | CAC |
|---------|-------------------|-----|
| Organic SEO (journal) | 35% | ~$0 marginal |
| X/Twitter paid | 40% | $120–200 |
| Direct/brand | 15% | ~$0 |
| Referral/partner | 10% | $50 incentive cap |

---

## Campaign priorities

### 1. Weight loss core (60% budget)
- Keywords: compounded semaglutide, tirzepatide online, GLP-1 telehealth
- Landing: `/weight-loss.html` + journal cost article
- Retarget: 7-day journal readers

### 2. Ivermectin vertical (25% budget)
- Keywords: ivermectin protocol, antiparasitic wellness
- Landing: `/antiparasitic.html` + `/ivermectin.html`
- Creative: Canva protocol cards

### 3. Sexual health + hair (15% budget)
- Long-tail: tadalafil troches, finasteride telehealth
- Landing: product pages + matching journals

---

## Retention levers

1. **Auto-refill default** on 3-month plans (already positioned as "Most Popular")
2. **SMS check-in** day 7 post-ship (side effects journal link)
3. **Portal nudge** at day 25 for refill
4. **Journal email** monthly "CLYR Protocol" newsletter

---

## Metrics dashboard (PostHog)

Events to track (via `clyr-tracking.js`):
- `PricingToggled`
- `article_view` (GTM dataLayer)
- Intake form steps (add if not present)
- `purchase` / `subscription_started` (Stripe webhook → GTM)

**North star:** Monthly active subscribers (MAS) with 60-day retention > 70%.