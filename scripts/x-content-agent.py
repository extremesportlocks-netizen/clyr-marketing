#!/usr/bin/env python3
"""
CLYR X Organic Content Agent — @ClyrHealth

Intel (search, mentions, bookmarks) + Journal → X Articles syndication.
Uses xurl for all X API calls. Wraps x-journal-syndicate.py for articles.

  python3 scripts/x-content-agent.py status
  python3 scripts/x-content-agent.py intel
  python3 scripts/x-content-agent.py tick
  python3 scripts/x-content-agent.py overnight --interval 3600
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
STATE_DIR = SCRIPTS / "x-articles"
STATE_PATH = STATE_DIR / "agent-state.json"
LOG_PATH = STATE_DIR / "agent.log"
SYNDICATE = SCRIPTS / "x-journal-syndicate.py"

SEARCH_QUERIES = [
    "parasite cleanse OR antiparasitic -is:retweet",
    "ivermectin wellness protocol -is:retweet",
    "gut health telehealth -is:retweet lang:en",
    "semaglutide telehealth -is:retweet lang:en",
]

MENTION_ALERT_KEYWORDS = (
    "parasite", "ivermectin", "cleanse", "gut", "enclomiphene",
    "semaglutide", "nad", "trimix", "intake", "price",
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utcnow()}] {msg}"
    print(line)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {
        "version": 1,
        "started_at": utcnow(),
        "last_tick": None,
        "ticks": 0,
        "intel": {"searches": [], "mentions": [], "angles": []},
        "syndication": {"last_draft": None, "last_publish": None, "errors": []},
        "config": {
            "priority_tier": "ashersoil",
            "auto_draft": True,
            "auto_publish": False,
        },
    }


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def xurl_json(args: list[str]) -> dict[str, Any] | list[Any] | None:
    proc = subprocess.run(["xurl", *args], capture_output=True, text=True)
    raw = proc.stdout.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw, "_rc": proc.returncode}


def run_syndicate(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SYNDICATE), *cmd],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = (proc.stdout + proc.stderr).strip()
    return proc.returncode, out


def extract_angles(posts: list[dict[str, Any]]) -> list[dict[str, str]]:
    angles: list[dict[str, str]] = []
    for p in posts[:15]:
        text = p.get("text", "")
        if not text or text.startswith("RT @"):
            continue
        metrics = p.get("public_metrics", {})
        impressions = metrics.get("impression_count", 0)
        likes = metrics.get("like_count", 0)
        if impressions < 50 and likes < 2:
            continue
        angles.append({
            "id": p.get("id", ""),
            "text": text[:220],
            "impressions": str(impressions),
            "likes": str(likes),
        })
    return angles[:8]


def cmd_intel(args: argparse.Namespace) -> int:
    state = load_state()
    intel: dict[str, Any] = {"at": utcnow(), "searches": [], "mentions": [], "angles": []}

    for query in SEARCH_QUERIES:
        resp = xurl_json(["search", query, "-n", "10"])
        posts = []
        if isinstance(resp, dict):
            posts = resp.get("data", []) or []
        hits = [{"id": p.get("id"), "text": (p.get("text") or "")[:180]} for p in posts[:5]]
        intel["searches"].append({"query": query, "hits": hits})
        log(f"search: {query!r} → {len(posts)} posts")

    mentions_resp = xurl_json(["mentions", "-n", "15"])
    mentions = []
    if isinstance(mentions_resp, dict):
        mentions = mentions_resp.get("data", []) or []
    for m in mentions:
        text = (m.get("text") or "").lower()
        flagged = [kw for kw in MENTION_ALERT_KEYWORDS if kw in text]
        intel["mentions"].append({
            "id": m.get("id"),
            "text": (m.get("text") or "")[:200],
            "flagged": flagged,
            "needs_reply": bool(flagged),
        })
    log(f"mentions: {len(mentions)} ({sum(1 for m in intel['mentions'] if m['needs_reply'])} flagged)")

    all_posts: list[dict[str, Any]] = []
    for s in intel["searches"]:
        for h in s["hits"]:
            all_posts.append({"text": h["text"], "id": h["id"], "public_metrics": {}})
    intel["angles"] = extract_angles(all_posts)

    state["intel"] = intel
    save_state(state)

    report_path = STATE_DIR / "intel-report.md"
    lines = [f"# X Intel — {intel['at']}\n"]
    lines.append("## Search angles\n")
    for a in intel["angles"]:
        lines.append(f"- [{a['impressions']} imp] {a['text']}\n")
    lines.append("\n## Mentions needing attention\n")
    flagged = [m for m in intel["mentions"] if m["needs_reply"]]
    if flagged:
        for m in flagged:
            lines.append(f"- `{m['id']}` {m['text']} _(keywords: {', '.join(m['flagged'])})_\n")
    else:
        lines.append("_None flagged._\n")
    report_path.write_text("".join(lines), encoding="utf-8")
    print(f"✓ Intel → {report_path}")
    if args.json:
        print(json.dumps(intel, indent=2))
    return 0


def cmd_syndicate_tick(state: dict[str, Any]) -> int:
    cfg = state["config"]
    tier = cfg.get("priority_tier", "ashersoil")

    _, stats_out = run_syndicate(["stats"])
    print(stats_out)

    if not cfg.get("auto_draft", True):
        log("syndicate: auto_draft disabled")
        return 0

    ec, out = run_syndicate(["drip", "--tier", tier])
    log(f"syndicate drip: exit={ec}")
    print(out)
    state["syndication"]["last_draft_attempt"] = utcnow()
    if ec == 0 and "draft created" in out.lower():
        state["syndication"]["last_draft"] = utcnow()
    elif ec == 2:
        state["syndication"]["errors"].append({"at": utcnow(), "error": "rate_limited"})
    elif ec != 0:
        state["syndication"]["errors"] = state["syndication"]["errors"][-9:] + [
            {"at": utcnow(), "error": out[:300]}
        ]

    if cfg.get("auto_publish"):
        queue_path = STATE_DIR / "queue.json"
        if queue_path.exists():
            queue = json.loads(queue_path.read_text(encoding="utf-8"))
            for rec in queue.get("articles", {}).values():
                if rec.get("status") == "drafted" and rec.get("x_draft_id"):
                    draft_id = rec["x_draft_id"]
                    log(f"auto_publish: {rec['slug']} ({draft_id})")
                    pec, pout = run_syndicate(["publish", draft_id])
                    print(pout)
                    if pec == 0:
                        state["syndication"]["last_publish"] = utcnow()
                    break
    return 0


def cmd_tick(_args: argparse.Namespace) -> int:
    state = load_state()
    log("── tick start ──")
    cmd_intel(argparse.Namespace(json=False))
    state = load_state()
    cmd_syndicate_tick(state)
    state["last_tick"] = utcnow()
    state["ticks"] = state.get("ticks", 0) + 1
    save_state(state)
    log("── tick end ──")
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    state = load_state()
    who = xurl_json(["whoami"])
    username = "?"
    if isinstance(who, dict):
        username = who.get("data", {}).get("username", "?")

    print("\n── CLYR X Organic Content Agent ──\n")
    print(f"Account:     @{username}")
    print(f"Ticks:       {state.get('ticks', 0)}")
    print(f"Last tick:   {state.get('last_tick', 'never')}")
    print(f"Priority:    {state['config'].get('priority_tier', 'ashersoil')}")
    print(f"Auto draft:  {state['config'].get('auto_draft', True)}")
    print(f"Auto publish:{state['config'].get('auto_publish', False)}")

    _, stats_out = run_syndicate(["stats"])
    print("\n" + stats_out)

    intel = state.get("intel", {})
    if intel.get("angles"):
        print("\nLatest angles:")
        for a in intel["angles"][:3]:
            print(f"  · {a['text'][:100]}…")

    flagged = [m for m in intel.get("mentions", []) if m.get("needs_reply")]
    if flagged:
        print(f"\n⚠ {len(flagged)} mention(s) flagged for reply")

    print(f"\nState: {STATE_PATH}")
    print(f"Log:   {LOG_PATH}")
    return 0


def cmd_overnight(args: argparse.Namespace) -> int:
    log(f"overnight start — interval={args.interval}s duration={args.duration}s")
    deadline = time.time() + args.duration
    while time.time() < deadline:
        cmd_tick(argparse.Namespace())
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        sleep = min(args.interval, remaining)
        log(f"sleeping {int(sleep)}s")
        time.sleep(sleep)
    log("overnight end")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="CLYR X Organic Content Agent")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Agent + queue status")
    p_status.set_defaults(func=cmd_status)

    p_intel = sub.add_parser("intel", help="Search + mentions intel pass")
    p_intel.add_argument("--json", action="store_true")
    p_intel.set_defaults(func=cmd_intel)

    p_tick = sub.add_parser("tick", help="One agent cycle: intel + syndicate")
    p_tick.set_defaults(func=cmd_tick)

    p_on = sub.add_parser("overnight", help="Run tick loop")
    p_on.add_argument("--interval", type=int, default=3600, help="Seconds between ticks")
    p_on.add_argument("--duration", type=int, default=28800, help="Total seconds (default 8h)")
    p_on.set_defaults(func=cmd_overnight)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())