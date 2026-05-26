# CLYR Homepage v3 — Preview Handoff

**URL:** https://www.clyr.health/preview/v3/
**Status:** Mockup, not live. `noindex, nofollow`. Yellow PREVIEW banner pinned to top.
**Date:** Built in response to: "site should look more like goodlifemeds, but we have our own direction in Stitch/Canva and we've done a lot already."

---

## What v3 is

A category-first homepage that absorbs goodlifemeds' best structural moves while keeping the CLYR brand voice, Gut Tax differentiation, and real partner credibility. Built to support the catalog pivot from GLP-1-only to 5 verticals.

## What changed vs. v2 (the one with the fake press strip)

| v2 | v3 |
|---|---|
| Fake "As Featured In" press logos (Healthline/Yale/etc.) — LegitScript risk | Real credibility partners only: LegitScript, HIPAA, 503A, Licensed Providers, Fast & Discreet |
| Generic "12 products" wall with filter pills | Per-category product walls — Weight Loss, Wellness, Sexual Health, Protocols |
| 3-step How It Works (your original was 4) | 4-step How It Works restored |
| 4 emoji category cards | 5 pillars (added Hair as "Coming Soon" waitlist; elevated Ivermectin to its own pillar) |
| No differentiation block | Gut Tax block recreated in HTML/CSS (matches your infographic exactly) |
| No journal surfacing | Journal section with 3 cards linking to /journal/ |
| No real partner badges | "Our Network" bar: MD Integrations, The Pharmacy Hub, DispensePro, Stripe, Twilio |

## What v3 takes from goodlifemeds

1. **Category-first IA.** Their site is organized by Weight Loss / Daily Wellness / Sexual Health / Hair. Ours is Weight Loss / Daily Wellness / Sexual Health / Hair / Protocols.
2. **Mega-menu with product thumbnails on hover.** Implemented for Weight Loss, Daily Wellness, Sexual Health nav items. Uses your existing SVGs from `/img/`.
3. **Per-category product wall on homepage.** Each category has its own band with 4 product cards, category color tinting, and a "View all" link.
4. **Top trust strip.** 6 specific claims, real (LegitScript, HIPAA, 503A, 47 states, transparent pricing, board-certified providers).

## What v3 does NOT take from goodlifemeds (intentional)

- **"FDA-Regulated Pharmacies"** language → replaced with "State-Licensed Compounding" per Feb 2026 FDA guidance.
- **"100K subscribers" social proof** → not claimed because we don't have it. Replaced with concrete numbers: 5 verticals, 22+ Rx medications, 47 states.
- **3D product render photography on cream backgrounds** → using your existing SVG product graphics. (Real product photography would be a separate Brandon/Ethan task — keep the SVGs as canonical for now.)
- **"Most Popular" badge style and tagline cadence** → kept CLYR voice (DM Sans + Instrument Serif italic accents, "Find what's right for you", "made clear.").

## The 5 pillars

| # | Pillar | Color | Products | Status |
|---|---|---|---|---|
| 1 | Weight Loss | Teal `#00B4C5` | Tirz, Sema, Zepbound, Wegovy, Mounjaro, Ozempic, Foundayo, Wegovy Pill | Live, "Most Popular" badge |
| 2 | Daily Wellness | Purple `#9333EA` | NAD+, Sermorelin, Glutathione, Lipo-Mino | Live |
| 3 | Sexual Health | Rose `#E11D48` | Tadalafil, Sildenafil Gummy, Combo ODT, PT-141 | Live |
| 4 | Hair | Amber `#F59E0B` | Finasteride, Minoxidil (planned) | "Coming Soon" badge, waitlist CTA |
| 5 | Ivermectin / Protocols | Green `#10B981` | Ivermectin, Ivermectin+Mebendazole | "New" badge |

If you want to swap Hair → a "Longevity" pillar split (pulling NAD+/Sermorelin out of Daily Wellness), it's a one-section edit.

## Specific elements I want sign-off on

1. **Gut Tax block placement** — I put it after the 4 category product walls, before "How It Works". Reasoning: pillars + product walls hook discovery, Gut Tax converts on differentiation, How It Works closes objections. Move it earlier (before pillars) if you want it as the lead differentiation.

2. **Hair as 5th pillar** — alternative is keeping 4 pillars and putting Hair in nav only, or splitting Wellness into Daily Wellness + Longevity. Easy swap.

3. **Journal cards** — currently 3 hardcoded placeholder cards that all link to `/journal/`. If you want them to pull the 3 latest from the actual journal index, that's a 30-line static-gen script (build-time) or a fetch (client-side). Tell me which.

4. **Partner bar logos** — Currently text wordmarks (MD Integrations, The Pharmacy Hub, DispensePro, Stripe, Twilio). If you have real SVG logos from any of these partners, drop them and I'll swap in real marks.

5. **"Our Network" disclosure** — surfacing MDI / TPH / DispensePro publicly. Is that something MDI/TPH have approved for marketing use, or should the bar stay generic ("Certified network · Licensed compounding · Tracked shipping")? Quick answer needed before merging to main.

## What I still need from you

- **Stitch screenshots or share-to-public** so I can match the specific visual direction Brandon/Ethan have been working on. The current v3 is my best read of "category-first like goodlifemeds, but CLYR voice." It may diverge from what they have queued.
- **Canva exports** (PDF or PNG) of any mockups, same reason.
- **Real product photography** if/when ready. Today's product cards use the existing SVG graphics, which work but read more "diagrammatic" than goodlifemeds' polished 3D renders.

## Merge plan (when you sign off)

Per the rule from the last chat: nothing goes to live `/index.html` without your explicit "merge it." Proposed surgical merge order:

1. **Top trust strip** — drop-in addition above existing nav. Zero risk.
2. **5-pillar grid replaces the current 4-emoji-card section.** Direct swap.
3. **Per-category product walls** — 4 new sections inserted after pillars. Pushes the existing "Treatments" section down or replaces it.
4. **Gut Tax block** — new section inserted before How It Works.
5. **Journal section** — new section inserted before FAQ.
6. **Mega-menu nav** — replaces existing nav. Test mobile carefully.
7. **Partners section** — replaces or augments existing trust/credibility section.

Each step is its own commit. You sign off at each step. No surprises.
