# CLYR Overnight Sprint — 2026-06-20

**User returns in ~10 hours.** Everything produced during the 8-hour autonomous run lives here and in git commits tagged `overnight-sprint`.

## Quick start when you return

1. Read **`STATUS.md`** (auto-updated each cycle)
2. Read **`gbp/GBP-VERIFICATION-PLAYBOOK.md`** — exact fix for Profile ID `10576517044753504409`
3. Read **`business-plans/90-DAY-GTM-PLAN.md`** — ready-to-execute GTM
4. New journal articles listed in **`articles-published.log`**
5. Live site: https://www.clyr.health — loop keeps pushing fixes

## Logs

| File | Purpose |
|------|---------|
| `../logs/overnight-sprint.log` | Master 8h loop log |
| `../logs/overnight-sprint-state.json` | Last cycle JSON state |
| `articles-published.log` | New articles shipped this sprint |

## Commands to resume manually

```bash
cd /Users/orlandosmith/clyr-code/clyr-marketing
python3 scripts/overnight-sprint.py          # restart 8h loop
python3 scripts/rebuild-all-journals.py      # rebuild all JSON → HTML
python3 scripts/update-sitemap-journals.py
git log --oneline -20 | grep overnight
```