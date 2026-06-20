#!/usr/bin/env python3
"""8-hour autonomous sprint: publish articles, maintain site, push, log status."""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "overnight-2026-06-20"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "overnight-sprint.log"
STATE_FILE = LOG_DIR / "overnight-sprint-state.json"
STATUS_FILE = SPRINT_DIR / "STATUS.md"
PUBLISHED_LOG = SPRINT_DIR / "articles-published.log"
CONTENT_DIR = ROOT / "scripts" / "journal-content"

DURATION_HOURS = 8
INTERVAL_MINUTES = 15
SITE = "https://www.clyr.health"
GBP_FRAGMENT = "16s%2Fg%2F11z94cc8v_"
VERIFY_TOKEN = "9h7apy74gKqUxepuj34VgZ5-7Ie9JXNGqWTuwQ-xL6I"

MAINTENANCE = [
    "wire-gbp.py",
    "fix-journal-urls.py",
    "link-products-to-journals.py",
    "update-sitemap-journals.py",
]


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}] {msg}"
    print(line, flush=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "CLYR-overnight-sprint/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace") if e.fp else ""


def audit() -> dict:
    code, home = fetch(SITE + "/")
    code2, sm = fetch(SITE + "/sitemap.xml")
    return {
        "homepage": code,
        "sitemap": code2,
        "sitemap_urls": sm.count("<loc>"),
        "gbp_schema": GBP_FRAGMENT in home,
        "gbp_footer": "Google Business Profile" in home,
        "verify_tag": VERIFY_TOKEN in home,
        "ok": code == 200 and code2 == 200,
    }


def published_slugs() -> set[str]:
    if not PUBLISHED_LOG.exists():
        return set()
    return {ln.strip() for ln in PUBLISHED_LOG.read_text().splitlines() if ln.strip()}


def journal_html_exists(slug: str) -> bool:
    return (ROOT / "journal" / slug / "index.html").exists()


def next_article() -> Path | None:
    done = published_slugs()
    for path in sorted(CONTENT_DIR.glob("*.json")):
        slug = json.loads(path.read_text())["slug"]
        if slug not in done and not journal_html_exists(slug):
            return path
    return None


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    out = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return out[-400:] if out else f"exit {proc.returncode}"


def publish_one(json_path: Path) -> str | None:
    slug = json.loads(json_path.read_text())["slug"]
    out = run([sys.executable, "scripts/publish-journal-local.py", str(json_path)])
    if "wrote" not in out:
        log(f"PUBLISH FAIL {slug}: {out}")
        return None
    run([sys.executable, "scripts/generate-journal-og.py", slug])
    PUBLISHED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with PUBLISHED_LOG.open("a") as f:
        f.write(slug + "\n")
    log(f"PUBLISHED {slug}")
    return slug


def git_push(cycle: int) -> bool:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if diff.returncode == 0:
        return False
    msg = f"overnight-sprint: cycle {cycle} articles+maintenance"
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=False)
    push = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, text=True)
    if push.returncode:
        log(f"PUSH FAIL: {push.stderr or push.stdout}")
        return False
    log(f"PUSHED cycle {cycle}")
    return True


def write_status(cycle: int, report: dict, ends: datetime, pushed: bool) -> None:
    SPRINT_DIR.mkdir(parents=True, exist_ok=True)
    pending = sum(
        1
        for p in CONTENT_DIR.glob("*.json")
        if not journal_html_exists(json.loads(p.read_text())["slug"])
    )
    STATUS_FILE.write_text(
        f"""# Overnight Sprint Status

**Updated:** {datetime.now(timezone.utc).isoformat()}  
**Cycle:** {cycle}  
**Ends:** {ends.isoformat()}  
**Last push:** {"yes" if pushed else "no"}

## Live checks
- Homepage: {report.get("homepage")}
- Sitemap URLs: {report.get("sitemap_urls")}
- GBP schema/footer: {report.get("gbp_schema")} / {report.get("gbp_footer")}
- Google verify tag: {report.get("verify_tag")}

## Articles
- Pending JSON not yet on site: {pending}
- Published this sprint: see `articles-published.log`

## When you return
1. `overnight-2026-06-20/gbp/GBP-VERIFICATION-PLAYBOOK.md` — fix GBP website (use `https://clyr.health` in GBP)
2. `overnight-2026-06-20/business-plans/90-DAY-GTM-PLAN.md` — execute GTM
3. Search Console → Sitemaps → resubmit if needed
4. GBP → website → verify via Search Console
""",
        encoding="utf-8",
    )


def main() -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=DURATION_HOURS)
    cycle = 0
    log(f"SPRINT START — 8h until {end.isoformat()} (every {INTERVAL_MINUTES}m)")

    while datetime.now(timezone.utc) < end:
        cycle += 1
        remaining = end - datetime.now(timezone.utc)
        log(f"=== CYCLE {cycle} — {remaining} left ===")
        pushed = False
        try:
            report = audit()
            log(f"LIVE {report}")

            article = next_article()
            if article:
                publish_one(article)
                run([sys.executable, "scripts/update-sitemap-journals.py"])
                run([sys.executable, "scripts/link-products-to-journals.py"])
            else:
                log("No pending articles this cycle")

            for script in MAINTENANCE:
                run([sys.executable, f"scripts/{script}"])

            pushed = git_push(cycle)
            write_status(cycle, report, end, pushed)
            STATE_FILE.write_text(
                json.dumps(
                    {
                        "cycle": cycle,
                        "ends": end.isoformat(),
                        "report": report,
                        "pushed": pushed,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception as exc:
            log(f"ERROR cycle {cycle}: {exc}")

        if datetime.now(timezone.utc) >= end:
            break
        time.sleep(INTERVAL_MINUTES * 60)

    log(f"SPRINT DONE — {cycle} cycles")


if __name__ == "__main__":
    main()