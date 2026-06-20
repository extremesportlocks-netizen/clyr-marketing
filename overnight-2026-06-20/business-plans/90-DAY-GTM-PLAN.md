# CLYR Health — 90-Day GTM Plan (Jun–Sep 2026)

## Executive summary

CLYR is a multi-vertical telehealth pharmacy brand (weight loss, wellness, sexual health, antiparasitic protocols). The site is live with 52+ journal articles, GTM `GTM-T4FVQ87G`, PostHog, LegitScript seal, and GBP entity `/g/11z94cc8v_`. The **#1 blocker** is GBP website URL alignment with Search Console (see `gbp/GBP-VERIFICATION-PLAYBOOK.md`). Everything else is execution.

---

## Phase 1 — Days 1–14: Fix discovery plumbing

| Priority | Action | Owner | Done when |
|----------|--------|-------|-----------|
| P0 | GBP website = `https://clyr.health` OR add `www` GSC property | Orlando | GBP shows website linked |
| P0 | Resubmit `sitemap.xml` in Search Console | Orlando | Last read < 7 days |
| P1 | Confirm GTM fires on all intake funnels | Dev | GTM preview passes |
| P1 | PostHog funnel: landing → intake start → submit | Dev | Dashboard live |
| P2 | 5 new geo journals (TX, FL, PA, CA, NY) | Content | Published + indexed |

**KPI week 2:** 50+ GSC impressions/day, GBP website visible on Maps.

---

## Phase 2 — Days 15–45: Acquisition

### Paid (X Ads — skill ready)
- Campaign 1: Semaglutide cost comparison (`/journal/compounded-semaglutide-cost/`)
- Campaign 2: Ivermectin protocol (`/antiparasitic.html`)
- Campaign 3: Retarget journal readers (PostHog audience export)
- Budget start: $50–100/day, optimize on intake starts

### Organic
- 2 journal articles/week (product-adjacent, educational)
- Internal links: every product page → 2+ journal articles (script: `link-products-to-journals.py`)
- Journal hub featured rotation weekly

### Email/SMS (if ESP connected)
- Abandoned intake sequence (24h, 72h)
- Post-approval onboarding (dosing, side effects journal links)

**KPI day 45:** CAC baseline established, 3+ intake starts/day from organic+paid.

---

## Phase 3 — Days 46–90: Scale + trust

| Channel | Tactic |
|---------|--------|
| SEO | Target "semaglutide near me" variants — 10 state pages |
| GBP | Request 5 reviews from early patients (compliant, no incentives) |
| Content | Launch "CLYR Protocol" series for ivermectin + NAD stacks |
| Partnerships | LegitScript badge on all paid landing pages |
| Product | Promote tier-1 tirzepatide + sema bundle in journal CTAs |

**KPI day 90:** 200+ daily GSC impressions, 10+ intake starts/day, GBP 4.5+ stars (10+ reviews).

---

## Budget envelope (recommended)

| Line | Monthly |
|------|---------|
| X/Twitter ads | $3,000 |
| Content (freelance/editorial) | $1,500 |
| OG/creative (Canva Pro) | $100 |
| PostHog | $0–50 |
| **Total** | **~$4,650/mo** |

---

## Daily operator checklist (15 min)

1. GSC → Performance → top queries (note 3 winners)
2. GBP → views, calls, website clicks
3. PostHog → intake funnel drop-off step
4. Git push any content from overnight queue
5. Respond to GBP Q&A within 24h

---

## Files & tooling reference

- Site repo: `clyr-marketing` → `www.clyr.health`
- Journal publish: `scripts/publish-journal-local.py` + git push
- Overnight loop: `scripts/overnight-sprint.py`
- X Ads: `~/.grok/skills/x-ads-manager/SKILL.md`
- Canva: `~/.grok/skills/ivermectin-canva/SKILL.md`