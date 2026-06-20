# CLYR Journal — Posting Runbook (for the Grok agent)

How to publish a new article to **www.clyr.health/journal/** in the standard CLYR
format, via the GitHub Contents API. No clone, no server — just Python 3 (stdlib),
a content JSON, and a GitHub token.

## 1. What you produce
A single **content JSON** (the "standard form") — see `journal-content.example.json`.
Required fields: `slug`, `title`, `category`, `deck`, `date`, `readTime`,
`metaDescription`, `bodyHtml`. Optional: `titleHtml` (title with a `<span class="serif">`
accent), `categoryKey`, `author` (default "CLYR Editorial"), `ogTitle`, `ogImage`
(defaults to `/img/journal-og/<slug>.png`), `sources[]`, `related[]`.

- `slug` is kebab-case and becomes the URL: `/journal/<slug>/`.
- `bodyHtml` is the article body as plain HTML (`<p>`, `<h2>`, `<h3>`, `<ul>/<ol>/<li>`,
  `<strong>`, `<em>`, `<a href>`). Do NOT include `<html>/<head>/<nav>/<footer>` — the
  script wraps your body in the live CLYR chrome automatically.

## 2. How to publish
```bash
export CLYR_GH_TOKEN=ghp_xxx          # GitHub PAT with contents:write on clyr-marketing
python3 scripts/post-journal.py my-article.json
# or pipe:  cat my-article.json | CLYR_GH_TOKEN=ghp_xxx python3 scripts/post-journal.py -
# preview without committing:  python3 scripts/post-journal.py my-article.json --dry-run
```
The script:
1. Fetches a reference Journal post for the current on-brand chrome (head/styles/nav/footer).
2. Builds `journal/<slug>/index.html` (hero + your body + sources + related).
3. Prepends a listing card to `journal/index.html`.
4. Commits both via the GitHub Contents API. GitHub Pages deploys in ~1-2 minutes.

Re-running with the same slug **updates** the post (and skips duplicate listing cards).

## 3. Auth — never hardcode the token
The token is read from `CLYR_GH_TOKEN` (or `GITHUB_TOKEN`) in the environment only.
It needs `Contents: read/write` on `extremesportlocks-netizen/clyr-marketing`.
Optional env overrides: `CLYR_GH_OWNER`, `CLYR_GH_REPO`, `CLYR_GH_BRANCH` (default `main`).
Do not write the token into the JSON, the script, or any committed file.

## 4. Content rules (house style)
- Journals are **editorial and educational**, not product ads. You MAY cite and discuss
  clinical trials/research with sources (that is the format). Do **not** make efficacy
  or "cure"/"guaranteed" claims about CLYR's own products.
- Keep brand-name competitor drugs in proper editorial context (comparisons/explainers
  are fine in a journal; they are not allowed on product marketing pages).
- Typography is automatic (DM Sans + Instrument Serif, teal #00B4C5). Use `titleHtml`
  to italicize the tail of the headline in serif, matching existing posts.
- Provide 4-8 real `sources` with working links for any science-heavy piece.
- `metaDescription` ≤ ~160 chars.

## 5. Verify after posting
- The script prints the live URL. After ~1-2 min, load `https://www.clyr.health/journal/<slug>/`
  (hard-refresh) and confirm it renders, and that the new card shows on `/journal/`.
- An OG image at `/img/journal-og/<slug>.png` makes social shares look right; if it does
  not exist yet, the page still works — add the image to the repo later.

## 6. Files
- `scripts/post-journal.py` — the publisher (stdlib only).
- `scripts/journal-content.example.json` — the standard form to copy.
- Reference post (chrome source): `journal/niagen-nicotinamide-riboside-explained/index.html`.
