#!/usr/bin/env python3
"""
post-journal.py  —  Publish a CLYR Journal article via the GitHub Contents API.

For the Grok agent (or any automation). Self-contained: standard library only
(urllib + json + base64), no pip install. It:
  1. Reads a journal content JSON (the "standard form" — see journal-content.example.json).
  2. Fetches a reference Journal post from the repo for the on-brand chrome
     (head styles, nav, footer, scripts) so output always matches the live design.
  3. Builds the new post (hero + article body + sources + related) and writes
     journal/<slug>/index.html.
  4. Prepends a card to journal/index.html so the post appears in the listing.
  Both files are committed to the clyr-marketing repo via the GitHub Contents API;
  GitHub Pages then deploys to www.clyr.health (~1-2 min).

AUTH (never hardcode a token):
  export CLYR_GH_TOKEN=<github PAT with repo contents:write on clyr-marketing>
Optional overrides:
  CLYR_GH_OWNER (default extremesportlocks-netizen)
  CLYR_GH_REPO  (default clyr-marketing)
  CLYR_GH_BRANCH(default main)

USAGE:
  CLYR_GH_TOKEN=ghp_xxx python3 scripts/post-journal.py path/to/content.json
  cat content.json | CLYR_GH_TOKEN=ghp_xxx python3 scripts/post-journal.py -
  Add --dry-run to render + validate locally and print the post WITHOUT committing.
"""
import sys, os, re, json, base64, html as _html, urllib.request, urllib.error

OWNER  = os.environ.get("CLYR_GH_OWNER", "extremesportlocks-netizen")
REPO   = os.environ.get("CLYR_GH_REPO", "clyr-marketing")
BRANCH = os.environ.get("CLYR_GH_BRANCH", "main")
TOKEN  = os.environ.get("CLYR_GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
REFERENCE = "journal/niagen-nicotinamide-riboside-explained/index.html"  # on-brand chrome source
API = "https://api.github.com"

def die(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr); sys.exit(code)

# ── GitHub Contents API (stdlib) ─────────────────────────────────────────────
def _req(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "Bearer " + (TOKEN or ""))
    r.add_header("Accept", "application/vnd.github+json")
    r.add_header("User-Agent", "clyr-post-journal")
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def gh_get(path):
    """Return (text, sha) for a repo file, or (None, None) if it does not exist."""
    code, body = _req("GET", f"{API}/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}")
    if code == 404:
        return None, None
    if code != 200:
        die(f"GET {path} failed ({code}): {body.get('message')}")
    return base64.b64decode(body["content"]).decode("utf-8"), body["sha"]

def gh_put(path, text, message, sha=None):
    payload = {"message": message, "branch": BRANCH,
               "content": base64.b64encode(text.encode("utf-8")).decode("ascii")}
    if sha:
        payload["sha"] = sha
    code, body = _req("PUT", f"{API}/repos/{OWNER}/{REPO}/contents/{path}", payload)
    if code not in (200, 201):
        die(f"PUT {path} failed ({code}): {body.get('message')}")
    return body

# ── Rendering ────────────────────────────────────────────────────────────────
CLOCK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>'
CAL   = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
PEN   = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>'
NEUTRAL_COVER = 'background:linear-gradient(135deg,#0d1b2e 0%,#1a3045 100%)'

def esc(s): return _html.escape(s or "", quote=True)

MONTHS = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
          "july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
IMG_KEYS = {"metabolic","cost","nad","research","longevity","peptides",
            "pennsylvania","florida","texas"}

def parse_date_iso(date_str):
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", (date_str or "").strip())
    if not m:
        return "2026-06-20"
    mo = MONTHS.get(m.group(1).lower(), 6)
    return f"{m.group(3)}-{mo:02d}-{int(m.group(2)):02d}"

def img_data_key(c):
    k = (c.get("categoryKey") or "research").strip().lower()
    return k if k in IMG_KEYS else "research"

def build_article_img(c):
    key = img_data_key(c)
    cat = esc(c["category"])
    return (f'<div class="article-img" data-img="{key}">\n'
            f'  <div class="article-img-inner">\n'
            f'    <div class="article-img-decoration" style="opacity:0.22">\n'
            f'      <svg viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" width="100%" style="max-width:720px;height:auto">\n'
            f'        <text x="320" y="72" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="13" font-weight="700" fill="#00B4C5" letter-spacing="4">CLYR JOURNAL</text>\n'
            f'        <text x="320" y="108" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="11" font-weight="600" fill="#6B7C8A" letter-spacing="2">{cat.upper()}</text>\n'
            f'        <line x1="120" y1="128" x2="520" y2="128" stroke="#00B4C5" stroke-width="1" opacity="0.35"/>\n'
            f'      </svg>\n'
            f'    </div>\n'
            f'  </div>\n'
            f'</div>')

def build_json_ld(c, url, ogimg):
    slug = c["slug"].strip("/")
    iso = parse_date_iso(c.get("date"))
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": url + "#article",
                "headline": c["title"],
                "description": c["metaDescription"],
                "image": ogimg,
                "datePublished": iso,
                "dateModified": iso,
                "author": {"@type": "Organization", "name": c.get("author", "CLYR Editorial")},
                "publisher": {
                    "@type": "Organization",
                    "name": "CLYR Health",
                    "url": "https://www.clyr.health/",
                    "logo": {"@type": "ImageObject", "url": "https://www.clyr.health/ogimageclyrfinal.png"},
                },
                "mainEntityOfPage": {"@type": "WebPage", "@id": url},
                "articleSection": c["category"],
                "inLanguage": "en-US",
                "isAccessibleForFree": True,
            },
            {
                "@type": "BreadcrumbList",
                "@id": url + "#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "CLYR Health", "item": "https://www.clyr.health/"},
                    {"@type": "ListItem", "position": 2, "name": "Journal", "item": "https://www.clyr.health/journal/"},
                    {"@type": "ListItem", "position": 3, "name": c["title"], "item": url},
                ],
            },
        ],
    }
    payload = json.dumps(data, ensure_ascii=False)
    return f'<script type="application/ld+json">{payload}</script>'

def build_article(c):
    cat = esc(c["category"])
    title_html = c.get("titleHtml") or esc(c["title"])
    meta = (f'    <div class="article-meta">\n'
            f'      <div class="article-meta-item">{CLOCK}{esc(c["readTime"])}</div>\n'
            f'      <div class="article-meta-divider"></div>\n'
            f'      <div class="article-meta-item">{CAL}Published {esc(c["date"])}</div>\n'
            f'      <div class="article-meta-divider"></div>\n'
            f'      <div class="article-meta-item">{PEN}{esc(c.get("author","CLYR Editorial"))}</div>\n'
            f'    </div>')
    hero = (f'<section class="article-hero">\n  <div class="article-hero-inner">\n'
            f'    <div class="breadcrumb"><a href="/">CLYR</a><span class="sep">/</span>'
            f'<a href="/journal/">Journal</a><span class="sep">/</span>{cat}</div>\n'
            f'    <div class="article-cat">{cat}</div>\n'
            f'    <h1 class="article-title">{title_html}</h1>\n'
            f'    <p class="article-deck">{esc(c["deck"])}</p>\n{meta}\n  </div>\n</section>')
    body = f'<article class="article-body">\n{c["bodyHtml"]}\n</article>'
    sources = ""
    if c.get("sources"):
        items = "\n".join(
            f'    <li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{s.get("label","").strip() or esc(s["url"])}</a></li>'
            for s in c["sources"])
        sources = f'\n<div class="article-sources">\n  <h3>Sources</h3>\n  <ol>\n{items}\n  </ol>\n</div>'
    related = ""
    if c.get("related"):
        cards = "\n".join(
            f'    <a href="/journal/{esc(r["slug"]).strip("/")}/" class="related-card">'
            f'<div class="related-card-img" style="{NEUTRAL_COVER}"></div>'
            f'<div class="related-card-body"><div class="related-card-cat">{esc(r.get("category",""))}</div>'
            f'<h3 class="related-card-title">{esc(r["title"])}</h3></div></a>'
            for r in c["related"])
        related = ('\n<section class="article-related">\n  <div class="related-header">'
                   '<div class="related-title">More from <span class="serif">the Journal</span></div>'
                   '<a href="/journal/" class="related-back">All articles &rarr;</a></div>\n'
                   f'  <div class="related-grid">\n{cards}\n  </div>\n</section>')
    return f"{hero}\n\n{build_article_img(c)}\n\n{body}{sources}{related}"

def replace_head(pre, c, url, ogimg):
    slug = c["slug"].strip("/")
    cat_key = esc(c.get("categoryKey", "research"))
    iso = parse_date_iso(c.get("date"))
    t = esc(c["title"]); d = esc(c["metaDescription"]); ot = esc(c.get("ogTitle", c["title"]))
    auth = esc(c.get("author", "CLYR Editorial"))
    subs = [
        (r"<title>.*?</title>", f"<title>{t} | CLYR Health</title>"),
        (r'(<meta name="description" content=")[^"]*(">)', rf"\g<1>{d}\g<2>"),
        (r'(<meta property="og:title" content=")[^"]*(">)', rf"\g<1>{ot}\g<2>"),
        (r'(<meta property="og:description" content=")[^"]*(">)', rf"\g<1>{d}\g<2>"),
        (r'(<meta property="og:url" content=")[^"]*(">)', rf"\g<1>{url}\g<2>"),
        (r'(<meta property="og:image" content=")[^"]*(">)', rf"\g<1>{ogimg}\g<2>"),
        (r'(<meta name="twitter:title" content=")[^"]*(">)', rf"\g<1>{ot}\g<2>"),
        (r'(<meta name="twitter:description" content=")[^"]*(">)', rf"\g<1>{d}\g<2>"),
        (r'(<meta name="twitter:image" content=")[^"]*(">)', rf"\g<1>{ogimg}\g<2>"),
        (r'(<link rel="canonical" href=")[^"]*(">)', rf"\g<1>{url}\g<2>"),
        (r"posthog\.register\(\{[^}]+\}\);",
         f"posthog.register({{article_slug:'{slug}',article_category:'{cat_key}'}});"),
    ]
    for pat, rep in subs:
        pre = re.sub(pat, rep, pre, count=1, flags=re.S)
    seo_block = (
        f'<meta name="robots" content="index, follow, max-image-preview:large">\n'
        f'<meta name="author" content="{auth}">\n'
        f'<meta property="og:site_name" content="CLYR Health">\n'
        f'<meta property="og:locale" content="en_US">\n'
        f'<meta property="article:published_time" content="{iso}">\n'
        f'<meta property="article:modified_time" content="{iso}">\n'
        f'<meta property="article:author" content="{auth}">\n'
        f'<meta property="article:section" content="{esc(c["category"])}">\n'
        f'<meta name="twitter:site" content="@ClyrHealth">\n'
        f'{build_json_ld(c, url, ogimg)}\n'
        f'<script>window.dataLayer=window.dataLayer||[];dataLayer.push({{event:"article_view",'
        f'article_slug:"{slug}",article_category:"{cat_key}",article_title:{json.dumps(c["title"])}}});</script>\n'
    )
    dlayer = (
        f'<script>window.dataLayer=window.dataLayer||[];dataLayer.push({{event:"article_view",'
        f'article_slug:"{slug}",article_category:"{cat_key}",article_title:{json.dumps(c["title"])}}});</script>\n'
    )
    if '<meta name="robots"' not in pre:
        pre = pre.replace("</head>", seo_block + "</head>", 1)
    else:
        pre = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", pre, flags=re.S)
        pre = pre.replace("</head>", build_json_ld(c, url, ogimg) + "\n</head>", 1)
        if 'event:"article_view"' not in pre:
            pre = pre.replace("</head>", dlayer + "</head>", 1)
    return pre

def render_page(ref_html, c):
    slug = c["slug"].strip("/")
    url = f"https://www.clyr.health/journal/{slug}/"
    ogimg = c.get("ogImage") or f"https://www.clyr.health/img/journal-og/{slug}.png"
    if not ogimg.startswith("http"):
        ogimg = "https://www.clyr.health" + ogimg
    pre = ref_html[: ref_html.index("</nav>") + len("</nav>")]
    post = ref_html[ref_html.index("<footer"):]
    pre = replace_head(pre, c, url, ogimg)
    page = f"{pre}\n\n{build_article(c)}\n\n{post}"
    if 'src="/js/clyr-tracking.js"' not in page:
        page = page.replace("</body>", '<script src="/js/clyr-tracking.js"></script>\n</body>', 1)
    return page

def index_card(c):
    slug = c["slug"].strip("/")
    key = img_data_key(c)
    title = c["title"].rstrip(".")
    return (f'    <a href="/journal/{slug}/" class="feature-card" data-category="{esc(c.get("categoryKey","new"))}" data-img="{key}">\n'
            f'      <div class="feature-card-img" style="{NEUTRAL_COVER}"></div>\n'
            f'      <div class="feature-card-body">\n'
            f'        <div class="feature-card-cat">{esc(c["category"])}</div>\n'
            f'        <h3 class="feature-card-title">{esc(title)}</h3>\n'
            f'        <p class="feature-card-dek">{esc(c["deck"])}</p>\n'
            f'        <div class="feature-card-meta"><span class="new">NEW</span><span class="dot"></span><span>{esc(c["readTime"])}</span></div>\n'
            f'      </div>\n    </a>\n')

REQUIRED = ["slug", "title", "category", "deck", "date", "readTime", "metaDescription", "bodyHtml"]

def main():
    if len(sys.argv) < 2:
        die("usage: post-journal.py <content.json | -> [--dry-run]")
    dry = "--dry-run" in sys.argv
    src = sys.argv[1]
    raw = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    c = json.loads(raw)
    missing = [k for k in REQUIRED if not c.get(k)]
    if missing:
        die("missing required fields: " + ", ".join(missing))
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]+", c["slug"].strip("/")):
        die("slug must be kebab-case (a-z, 0-9, hyphens)")
    if len(c["metaDescription"]) > 165:
        print("WARN: metaDescription >165 chars (Google truncates ~155-160).", file=sys.stderr)
    # light editorial lint (journals may cite trials; just flag product-style overreach)
    low = c["bodyHtml"].lower()
    for bad in ["clyr cures", "guaranteed results", "miracle"]:
        if bad in low:
            print(f"WARN: body contains '{bad}' — keep journals educational, not promotional.", file=sys.stderr)

    if not TOKEN and not dry:
        die("CLYR_GH_TOKEN (or GITHUB_TOKEN) not set. Export a GitHub PAT with contents:write.")

    slug = c["slug"].strip("/")
    if dry:
        # render using the local reference if available, else note it
        ref_path = os.path.join(os.path.dirname(__file__), "..", REFERENCE)
        if os.path.exists(ref_path):
            ref = open(ref_path, encoding="utf-8").read()
        elif TOKEN:
            ref, _ = gh_get(REFERENCE)
        else:
            die("dry-run needs the reference post locally or CLYR_GH_TOKEN to fetch it")
        page = render_page(ref, c)
        print(page)
        print(f"\n--- DRY RUN: would write journal/{slug}/index.html ({len(page.splitlines())} lines) and prepend its index card ---", file=sys.stderr)
        return

    ref, _ = gh_get(REFERENCE)
    if ref is None:
        die("reference post not found in repo: " + REFERENCE)
    page = render_page(ref, c)
    post_path = f"journal/{slug}/index.html"
    _, post_sha = gh_get(post_path)
    gh_put(post_path, page, f"journal: {'update' if post_sha else 'publish'} {slug}", post_sha)
    print(f"✓ {'updated' if post_sha else 'published'} {post_path}")

    idx, idx_sha = gh_get("journal/index.html")
    if idx is None:
        die("journal/index.html not found")
    anchor = '<div class="featured-grid">'
    if anchor not in idx:
        die("could not find featured-grid anchor in journal/index.html")
    already = f'href="/journal/{slug}/"'
    if already in idx:
        print("• index already lists this post; leaving listing unchanged")
    else:
        idx = idx.replace(anchor, anchor + "\n" + index_card(c), 1)
        gh_put("journal/index.html", idx, f"journal: list {slug}", idx_sha)
        print("✓ added card to journal/index.html")
    print(f"\nLive in ~1-2 min: https://www.clyr.health/journal/{slug}/")

if __name__ == "__main__":
    main()
