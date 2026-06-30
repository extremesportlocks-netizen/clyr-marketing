#!/usr/bin/env python3
"""
CLYR Journal → X Articles syndication agent.

Indexes clyr.health/journal articles, converts HTML to DraftJS, creates X Article
drafts via xurl, tracks publish state, and pairs with @ClyrHealth distribution.

Usage:
  python3 scripts/x-journal-syndicate.py index
  python3 scripts/x-journal-syndicate.py list [--tier ashersoil]
  python3 scripts/x-journal-syndicate.py prepare parasite-cleanse-vs-antiparasitic-medicine
  python3 scripts/x-journal-syndicate.py draft parasite-cleanse-vs-antiparasitic-medicine
  python3 scripts/x-journal-syndicate.py draft-batch --tier ashersoil --limit 3
  python3 scripts/x-journal-syndicate.py publish 2071778280886165504
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "scripts" / "journal-content"
JOURNAL_DIR = ROOT / "journal"
STATE_DIR = ROOT / "scripts" / "x-articles"
QUEUE_PATH = STATE_DIR / "queue.json"
SITE = "https://www.clyr.health"
ASHERSOIL_UTM = "?utm_source=twitter&utm_medium=organic&utm_campaign=journal-article&utm_content={slug}"

DISCLAIMER = (
    "Compounded medications are not FDA-approved. This article is educational only "
    "and not medical advice. Licensed providers evaluate each patient individually. "
    "CLYR Health · LegitScript certified."
)

TIER_KEYWORDS = {
    "ashersoil": (
        "parasite", "ivermectin", "mebendazole", "antiparasitic", "cleanse", "gut",
    ),
    "glp1": ("semaglutide", "tirzepatide", "glp", "wegovy", "zepbound", "weight-loss", "weight_loss"),
    "longevity": ("nad", "niagen", "peptide", "sermorelin", "glutathione", "longevity", "bpc-157"),
    "sexual": ("tadalafil", "sildenafil", "trimix", "pt141", "ed", "sexual", "libido"),
    "skin": ("tretinoin", "acne", "hair", "foundayo", "ghk", "hydroquinone"),
    "hormone": ("testosterone", "estradiol", "progesterone", "hrt", "hcg", "enclomiphene"),
}


class _HTMLToBlocks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.blocks: list[dict[str, Any]] = []
        self._key = 0
        self._buf: list[str] = []
        self._list_type: str | None = None
        self._in_li = False

    def _flush(self, btype: str = "unstyled") -> None:
        text = html_lib.unescape("".join(self._buf)).strip()
        self._buf = []
        if not text:
            return
        self._key += 1
        self.blocks.append({
            "key": f"b{self._key}",
            "type": btype,
            "text": text,
            "entity_ranges": [],
            "inline_style_ranges": [],
        })

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("p", "div"):
            self._flush()
        elif tag == "h2":
            self._flush()
            self._list_type = None
        elif tag == "h3":
            self._flush()
            self._list_type = None
        elif tag == "blockquote":
            self._flush()
            self._list_type = None
        elif tag == "ul":
            self._flush()
            self._list_type = "unordered-list-item"
        elif tag == "ol":
            self._flush()
            self._list_type = "ordered-list-item"
        elif tag == "li":
            self._flush()
            self._in_li = True
        elif tag == "br":
            self._buf.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("p", "div"):
            self._flush()
        elif tag == "h2":
            self._flush("header-two")
        elif tag == "h3":
            self._flush("header-three")
        elif tag == "blockquote":
            self._flush("blockquote")
        elif tag in ("ul", "ol"):
            self._list_type = None
        elif tag == "li":
            self._flush(self._list_type or "unordered-list-item")
            self._in_li = False

    def handle_data(self, data: str) -> None:
        self._buf.append(data)

    def close(self) -> None:
        super().close()
        self._flush()


def strip_html(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def html_to_blocks(html: str) -> list[dict[str, Any]]:
    parser = _HTMLToBlocks()
    parser.feed(html)
    parser.close()
    return parser.blocks


def classify_tiers(slug: str, title: str, category: str) -> list[str]:
    hay = f"{slug} {title} {category}".lower()
    tiers = [t for t, keys in TIER_KEYWORDS.items() if any(k in hay for k in keys)]
    return tiers or ["general"]


def journal_url(slug: str) -> str:
    return f"{SITE}/journal/{slug.strip('/')}/"


def partner_cta_url(slug: str) -> str:
    if any(k in slug for k in ("parasite", "ivermectin", "mebendazole", "antiparasitic")):
        return (
            "https://verde-cleanse-site.vercel.app/protocol"
            + ASHERSOIL_UTM.format(slug=slug)
        )
    return journal_url(slug)


@dataclass
class ArticleRecord:
    slug: str
    title: str
    deck: str
    category: str
    tiers: list[str]
    source: str
    journal_url: str
    status: str = "queued"
    x_draft_id: str | None = None
    x_published_at: str | None = None
    companion_tweet: str | None = None


def load_json_article(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_html_article(path: Path) -> dict[str, Any] | None:
    html = path.read_text(encoding="utf-8", errors="replace")
    title_m = re.search(r"<title>([^<|]+)", html)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', html)
    slug = path.parent.name
    title = strip_html(title_m.group(1)) if title_m else slug.replace("-", " ").title()
    title = re.sub(r"\s*\|.*$", "", title).strip()
    deck = desc_m.group(1).strip() if desc_m else ""
    body_m = re.search(r'<div class="article-body">([\s\S]*?)</div>\s*<div class="article-sources"', html)
    if not body_m:
        body_m = re.search(r'<article[^>]*>([\s\S]*?)</article>', html)
    body_html = body_m.group(1) if body_m else ""
    cat_m = re.search(r"article_category:'([^']+)'", html)
    category = cat_m.group(1) if cat_m else "journal"
    return {
        "slug": slug,
        "title": title,
        "deck": deck,
        "category": category,
        "bodyHtml": body_html,
    }


def collect_articles() -> list[ArticleRecord]:
    seen: set[str] = set()
    records: list[ArticleRecord] = []

    for path in sorted(CONTENT_DIR.glob("*.json")):
        data = load_json_article(path)
        if not data or not data.get("slug"):
            continue
        slug = data["slug"].strip("/")
        if slug in seen:
            continue
        seen.add(slug)
        title = strip_html(data.get("title", slug))
        deck = data.get("deck", data.get("metaDescription", ""))
        category = data.get("category", "Journal")
        records.append(ArticleRecord(
            slug=slug,
            title=title,
            deck=deck,
            category=category,
            tiers=classify_tiers(slug, title, category),
            source="json",
            journal_url=journal_url(slug),
        ))

    for path in sorted(JOURNAL_DIR.glob("*/index.html")):
        slug = path.parent.name
        if slug in seen:
            continue
        data = load_html_article(path)
        if not data:
            continue
        seen.add(slug)
        title = data["title"]
        deck = data["deck"]
        category = data.get("category", "journal")
        records.append(ArticleRecord(
            slug=slug,
            title=title,
            deck=deck,
            category=category,
            tiers=classify_tiers(slug, title, category),
            source="html",
            journal_url=journal_url(slug),
        ))

    records.sort(key=lambda r: (0 if "ashersoil" in r.tiers else 1, r.slug))
    return records


def load_queue() -> dict[str, Any]:
    if QUEUE_PATH.exists():
        return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    return {"version": 1, "updated_at": None, "articles": {}}


def save_queue(data: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    articles = data.get("articles", {})
    data["stats"] = {
        "total": len(articles),
        "queued": sum(1 for a in articles.values() if a.get("status") == "queued"),
        "drafted": sum(1 for a in articles.values() if a.get("status") == "drafted"),
        "published": sum(1 for a in articles.values() if a.get("status") == "published"),
        "ashersoil": sum(1 for a in articles.values() if "ashersoil" in a.get("tiers", [])),
    }
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    QUEUE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cmd_index(_: argparse.Namespace) -> int:
    queue = load_queue()
    existing = queue.get("articles", {})
    articles = collect_articles()
    for rec in articles:
        prev = existing.get(rec.slug, {})
        merged = asdict(rec)
        merged["status"] = prev.get("status", "queued")
        merged["x_draft_id"] = prev.get("x_draft_id")
        merged["x_published_at"] = prev.get("x_published_at")
        merged["companion_tweet"] = prev.get("companion_tweet")
        queue.setdefault("articles", {})[rec.slug] = merged
    queue["stats"] = {
        "total": len(articles),
        "queued": sum(1 for a in queue["articles"].values() if a.get("status") == "queued"),
        "drafted": sum(1 for a in queue["articles"].values() if a.get("status") == "drafted"),
        "published": sum(1 for a in queue["articles"].values() if a.get("status") == "published"),
        "ashersoil": sum(1 for a in queue["articles"].values() if "ashersoil" in a.get("tiers", [])),
    }
    save_queue(queue)
    print(f"✓ Indexed {len(articles)} journal articles → {QUEUE_PATH}")
    print(json.dumps(queue["stats"], indent=2))
    return 0


def get_body_html(slug: str) -> tuple[dict[str, Any], str]:
    json_path = CONTENT_DIR / f"{slug}.json"
    if json_path.exists():
        data = load_json_article(json_path) or {}
        return data, data.get("bodyHtml", "")
    html_path = JOURNAL_DIR / slug / "index.html"
    if html_path.exists():
        data = load_html_article(html_path) or {}
        return data, data.get("bodyHtml", "")
    raise SystemExit(f"Article not found: {slug}")


MAX_ARTICLE_CHARS = 5500
MAX_BODY_BLOCKS = 14
DRAFT_PAUSE_SEC = 30
XURL_RETRY_ATTEMPTS = 6
XURL_RETRY_BASE_SEC = 60


def trim_blocks(blocks: list[dict[str, Any]], max_chars: int = MAX_ARTICLE_CHARS) -> list[dict[str, Any]]:
    """X Articles API rejects very large DraftJS payloads (503). Teaser + journal link."""
    out: list[dict[str, Any]] = []
    total = 0
    for block in blocks:
        if len(out) >= MAX_BODY_BLOCKS:
            break
        text = block.get("text", "")
        if total + len(text) > max_chars and out:
            break
        out.append(block)
        total += len(text)
    if len(out) < len(blocks):
        out.append({
            "key": "trim",
            "type": "unstyled",
            "text": "Read the full article on CLYR Journal (link below).",
            "entity_ranges": [],
            "inline_style_ranges": [],
        })
    return out


def build_draft_payload(slug: str) -> dict[str, Any]:
    data, body_html = get_body_html(slug)
    title = strip_html(data.get("title", slug))
    deck = data.get("deck", data.get("metaDescription", ""))
    url = journal_url(slug)
    partner = partner_cta_url(slug)

    blocks: list[dict[str, Any]] = [
        {"key": "h0", "type": "header-one", "text": title, "entity_ranges": [], "inline_style_ranges": []},
    ]
    if deck:
        blocks.append({
            "key": "deck", "type": "blockquote", "text": deck,
            "entity_ranges": [], "inline_style_ranges": [],
        })

    body_blocks = html_to_blocks(body_html)
    blocks.extend(trim_blocks(body_blocks))

    blocks.append({"key": "sp1", "type": "unstyled", "text": "—", "entity_ranges": [], "inline_style_ranges": []})
    blocks.append({
        "key": "cta", "type": "header-three", "text": "Continue on CLYR Health",
        "entity_ranges": [], "inline_style_ranges": [],
    })

    blocks.append({
        "key": "link1", "type": "unstyled", "text": f"Full article: {url}",
        "entity_ranges": [], "inline_style_ranges": [],
    })

    if "ashersoil" in classify_tiers(slug, title, data.get("category", "")):
        blocks.append({
            "key": "link2", "type": "unstyled", "text": f"Asher's Soil 30-day guide: {partner}",
            "entity_ranges": [], "inline_style_ranges": [],
        })

    blocks.append({
        "key": "disc", "type": "unstyled", "text": DISCLAIMER,
        "entity_ranges": [], "inline_style_ranges": [],
    })

    return {
        "title": title[:280],
        "content_state": {"blocks": blocks, "entities": []},
        "_meta": {"slug": slug, "journal_url": url, "block_count": len(blocks)},
    }


def companion_tweet(slug: str, title: str) -> str:
    url = journal_url(slug)
    if "ashersoil" in classify_tiers(slug, title, ""):
        return (
            f"New on CLYR Journal: {title}\n\n"
            f"Provider-guided 30-day cleanse tiers from $99 → {partner_cta_url(slug)}\n\n"
            f"Full read: {url}\n\n"
            "*Compounded not FDA-approved. Licensed providers only."
        )
    return (
        f"New on CLYR Journal: {title}\n\n"
        f"Read: {url}\n\n"
        "*Compounded not FDA-approved. Licensed providers only."
    )


def _xurl_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    max_attempts: int = XURL_RETRY_ATTEMPTS,
) -> dict[str, Any]:
    cmd = ["xurl", "-X", method, path]
    if payload is not None:
        cmd.extend(["-d", json.dumps(payload)])
    detail = "xurl failed"
    for attempt in range(max_attempts):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        detail = proc.stdout.strip() or proc.stderr.strip() or "xurl failed"
        if proc.returncode == 0:
            return json.loads(proc.stdout)
        if '"status":429' in detail or "Too Many Requests" in detail:
            if attempt + 1 >= max_attempts:
                raise RuntimeError(detail)
            wait = XURL_RETRY_BASE_SEC * (2 ** attempt)
            print(f"  rate limited — retry in {wait}s ({attempt + 1}/{max_attempts})", file=sys.stderr)
            time.sleep(wait)
            continue
        raise RuntimeError(detail)
    raise RuntimeError(detail)


def xurl_post(path: str, payload: dict[str, Any], *, max_attempts: int = XURL_RETRY_ATTEMPTS) -> dict[str, Any]:
    return _xurl_request("POST", path, payload, max_attempts=max_attempts)


def cmd_prepare(args: argparse.Namespace) -> int:
    payload = build_draft_payload(args.slug)
    meta = payload.pop("_meta")
    print(json.dumps({"meta": meta, "title": payload["title"], "blocks": len(payload["content_state"]["blocks"])}, indent=2))
    preview = STATE_DIR / f"preview-{args.slug}.json"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    preview.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"✓ Draft payload → {preview}")
    return 0


def cmd_draft(args: argparse.Namespace) -> int:
    payload = build_draft_payload(args.slug)
    meta = payload.pop("_meta")
    if args.dry_run:
        print(json.dumps(meta, indent=2))
        return 0
    attempts = 1 if getattr(args, "fast_fail", False) else XURL_RETRY_ATTEMPTS
    resp = xurl_post("/2/articles/draft", payload, max_attempts=attempts)
    time.sleep(DRAFT_PAUSE_SEC)
    draft_id = resp["data"]["id"]
    tweet = companion_tweet(args.slug, payload["title"])
    queue = load_queue()
    rec = queue.setdefault("articles", {}).get(args.slug, {"slug": args.slug})
    rec.update({
        "slug": args.slug,
        "title": payload["title"],
        "status": "drafted",
        "x_draft_id": draft_id,
        "companion_tweet": tweet,
        "journal_url": meta["journal_url"],
    })
    save_queue(queue)
    print(f"✓ X Article draft created: {draft_id}")
    print(f"  Title: {payload['title']}")
    print(f"  Blocks: {meta['block_count']}")
    print(f"  Publish: python3 scripts/x-journal-syndicate.py publish {draft_id}")
    print("\nCompanion tweet:\n" + tweet)
    return 0


def cmd_draft_batch(args: argparse.Namespace) -> int:
    queue = load_queue()
    articles = list(queue.get("articles", {}).values())
    if args.tier:
        articles = [a for a in articles if args.tier in a.get("tiers", [])]
    articles = [a for a in articles if a.get("status") == "queued"]
    articles = articles[: args.limit]
    if not articles:
        print("No queued articles for this tier.")
        return 0
    ok = 0
    for i, rec in enumerate(articles):
        slug = rec["slug"]
        if i:
            print(f"  pausing {DRAFT_PAUSE_SEC}s before next draft…", file=sys.stderr)
            time.sleep(DRAFT_PAUSE_SEC)
        try:
            ns = argparse.Namespace(slug=slug, dry_run=False)
            cmd_draft(ns)
            ok += 1
        except Exception as exc:
            print(f"✗ {slug}: {exc}", file=sys.stderr)
    print(f"\n✓ Drafted {ok}/{len(articles)}")
    return 0


def post_companion_tweet(text: str) -> dict[str, Any]:
    return xurl_post("/2/tweets", {"text": text})


def cmd_publish(args: argparse.Namespace) -> int:
    path = f"/2/articles/{args.article_id}/publish"
    resp = xurl_post(path, {})
    print(json.dumps(resp, indent=2))
    queue = load_queue()
    matched: dict[str, Any] | None = None
    for rec in queue.get("articles", {}).values():
        if rec.get("x_draft_id") == args.article_id:
            rec["status"] = "published"
            rec["x_published_at"] = datetime.now(timezone.utc).isoformat()
            rec["x_post_id"] = resp.get("data", {}).get("post_id")
            matched = rec
    save_queue(queue)
    if args.tweet and matched and matched.get("companion_tweet"):
        try:
            tweet_resp = post_companion_tweet(matched["companion_tweet"])
            print("\n✓ Companion tweet posted:")
            print(json.dumps(tweet_resp, indent=2))
        except Exception as exc:
            print(f"\n✗ Companion tweet failed: {exc}", file=sys.stderr)
            print("Post manually:\n" + matched["companion_tweet"])
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    """Draft the next queued article (priority: ashersoil tier first)."""
    queue = load_queue()
    articles = [a for a in queue.get("articles", {}).values() if a.get("status") == "queued"]
    if args.tier:
        articles = [a for a in articles if args.tier in a.get("tiers", [])]
    elif not getattr(args, "any_tier", False):
        ashersoil = [a for a in articles if "ashersoil" in a.get("tiers", [])]
        articles = ashersoil or articles
    if not articles:
        print("Queue empty for this filter.")
        return 0
    slug = articles[0]["slug"]
    print(f"→ Next: {slug}")
    return cmd_draft(argparse.Namespace(
        slug=slug,
        dry_run=args.dry_run,
        fast_fail=getattr(args, "fast_fail", False),
    ))


def cmd_drip(args: argparse.Namespace) -> int:
    """One fast-fail draft attempt for cron/launchd. Exit 2 = rate limited."""
    try:
        return cmd_next(argparse.Namespace(
            tier=args.tier,
            any_tier=args.any_tier,
            dry_run=False,
            fast_fail=True,
        ))
    except RuntimeError as exc:
        if "429" in str(exc) or "Too Many Requests" in str(exc):
            print("X API rate limited — try again later.", file=sys.stderr)
            return 2
        raise


def cmd_stats(_args: argparse.Namespace) -> int:
    queue = load_queue()
    articles = list(queue.get("articles", {}).values())
    by_status: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    for a in articles:
        st = a.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        for t in a.get("tiers", []):
            by_tier[t] = by_tier.get(t, 0) + 1
    print(f"Total articles: {len(articles)}")
    for st in ("queued", "drafted", "published"):
        print(f"  {st}: {by_status.get(st, 0)}")
    print("\nBy tier:")
    for tier, n in sorted(by_tier.items(), key=lambda x: -x[1]):
        print(f"  {tier}: {n}")
    published = [a for a in articles if a.get("status") == "published"]
    if published:
        print("\nLive on X:")
        for a in published:
            print(f"  {a['slug']}")
            if a.get("x_post_id"):
                print(f"    https://x.com/ClyrHealth/status/{a['x_post_id']}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    queue = load_queue()
    articles = list(queue.get("articles", {}).values())
    if args.tier:
        articles = [a for a in articles if args.tier in a.get("tiers", [])]
    if args.status:
        articles = [a for a in articles if a.get("status") == args.status]
    for a in articles[: args.limit]:
        tiers = ",".join(a.get("tiers", []))
        print(f"{a.get('status','?'):9} {tiers:12} {a['slug']}")
        if a.get("x_draft_id"):
            print(f"           draft_id={a['x_draft_id']}")
    print(f"\nShowing {min(len(articles), args.limit)} of {len(articles)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CLYR Journal → X Articles agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="Scan journal and build queue")
    p_index.set_defaults(func=cmd_index)

    p_list = sub.add_parser("list", help="List queue")
    p_list.add_argument("--tier")
    p_list.add_argument("--status")
    p_list.add_argument("--limit", type=int, default=30)
    p_list.set_defaults(func=cmd_list)

    p_prep = sub.add_parser("prepare", help="Build draft JSON without posting")
    p_prep.add_argument("slug")
    p_prep.set_defaults(func=cmd_prepare)

    p_draft = sub.add_parser("draft", help="Create X Article draft")
    p_draft.add_argument("slug")
    p_draft.add_argument("--dry-run", action="store_true")
    p_draft.set_defaults(func=cmd_draft)

    p_batch = sub.add_parser("draft-batch", help="Draft N queued articles")
    p_batch.add_argument("--tier")
    p_batch.add_argument("--limit", type=int, default=3)
    p_batch.set_defaults(func=cmd_draft_batch)

    p_pub = sub.add_parser("publish", help="Publish X Article draft")
    p_pub.add_argument("article_id")
    p_pub.add_argument("--no-tweet", dest="tweet", action="store_false", help="Skip companion tweet")
    p_pub.set_defaults(func=cmd_publish, tweet=True)

    p_next = sub.add_parser("next", help="Draft next queued article (ashersoil first)")
    p_next.add_argument("--tier")
    p_next.add_argument("--any-tier", action="store_true", help="Ignore ashersoil priority")
    p_next.add_argument("--dry-run", action="store_true")
    p_next.add_argument("--fast-fail", action="store_true", help="No 429 retries")
    p_next.set_defaults(func=cmd_next, fast_fail=False)

    p_drip = sub.add_parser("drip", help="Cron-friendly: one draft, fast-fail on 429")
    p_drip.add_argument("--tier", default="ashersoil")
    p_drip.add_argument("--any-tier", action="store_true")
    p_drip.set_defaults(func=cmd_drip)

    p_stats = sub.add_parser("stats", help="Pipeline counts")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())