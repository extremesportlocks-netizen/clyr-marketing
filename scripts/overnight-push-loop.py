#!/usr/bin/env python3
"""12-hour maintenance loop: audit live site, run polish scripts, push if changed."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "overnight-push-loop.log"
STATE_FILE = LOG_DIR / "overnight-push-loop-state.json"

DURATION_HOURS = 12
INTERVAL_MINUTES = 20
SITE = "https://www.clyr.health"
GBP_MAPS_FRAGMENT = "16s%2Fg%2F11z94cc8v_"

POLISH_SCRIPTS = [
    "wire-gbp.py",
    "polish-indexable-pages.py",
    "fix-journal-urls.py",
    "link-products-to-journals.py",
    "update-sitemap-journals.py",
]

CHECK_URLS = [
    SITE + "/",
    SITE + "/niagen",
    SITE + "/contact.html",
    SITE + "/sitemap.xml",
    SITE + "/journal/",
    SITE + "/weight-loss.html",
]


def log(msg: str) -> None:
    line = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}] {msg}"
    print(line, flush=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "CLYR-overnight-loop/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body


def audit_live() -> dict:
    report: dict = {"ok": True, "checks": {}}
    status, home = fetch(SITE + "/")
    report["checks"]["homepage_status"] = status
    report["checks"]["gbp_schema"] = GBP_MAPS_FRAGMENT in home
    report["checks"]["gbp_footer"] = "Google Business Profile" in home
    report["checks"]["google_verification"] = "google-site-verification" in home

    status, sitemap = fetch(SITE + "/sitemap.xml")
    report["checks"]["sitemap_status"] = status
    report["checks"]["sitemap_urls"] = sitemap.count("<loc>")

    broken = []
    for url in CHECK_URLS:
        code, _ = fetch(url)
        if code != 200:
            broken.append({"url": url, "status": code})
    report["checks"]["broken_pages"] = broken
    if broken or status != 200:
        report["ok"] = False
    return report


def run_script(name: str) -> str:
    path = ROOT / "scripts" / name
    if not path.exists():
        return "skip"
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return out.strip()[-500:] if out else ("ok" if proc.returncode == 0 else f"exit {proc.returncode}")


def git_push_if_dirty(cycle: int) -> bool:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        capture_output=True,
    )
    if diff.returncode == 0:
        return False

    msg = f"chore(overnight): cycle {cycle} maintenance auto-push"
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=False)
    push = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, capture_output=True, text=True)
    if push.returncode != 0:
        log(f"PUSH FAILED: {push.stderr or push.stdout}")
        return False
    log(f"PUSHED cycle {cycle}")
    return True


def save_state(data: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=DURATION_HOURS)
    cycle = 0

    log(f"START 12h loop — until {end.isoformat()} (every {INTERVAL_MINUTES}m)")

    while datetime.now(timezone.utc) < end:
        cycle += 1
        remaining = end - datetime.now(timezone.utc)
        log(f"=== CYCLE {cycle} — {remaining} remaining ===")

        try:
            report = audit_live()
            log(
                "LIVE: "
                f"home={report['checks']['homepage_status']} "
                f"gbp_schema={report['checks']['gbp_schema']} "
                f"gbp_footer={report['checks']['gbp_footer']} "
                f"verify_tag={report['checks']['google_verification']} "
                f"sitemap_urls={report['checks']['sitemap_urls']}"
            )
            if report["checks"]["broken_pages"]:
                log(f"BROKEN: {report['checks']['broken_pages']}")

            for script in POLISH_SCRIPTS:
                result = run_script(script)
                if result != "skip":
                    log(f"SCRIPT {script}: {result[:200]}")

            pushed = git_push_if_dirty(cycle)
            save_state(
                {
                    "started": start.isoformat(),
                    "ends": end.isoformat(),
                    "last_cycle": cycle,
                    "last_run": datetime.now(timezone.utc).isoformat(),
                    "last_report": report,
                    "last_pushed": pushed,
                }
            )
        except Exception as exc:
            log(f"CYCLE ERROR: {exc}")

        if datetime.now(timezone.utc) >= end:
            break
        time.sleep(INTERVAL_MINUTES * 60)

    log(f"DONE — completed {cycle} cycles")


if __name__ == "__main__":
    main()