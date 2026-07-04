#!/usr/bin/env python3
"""Render infographic HTML cover to PNG (1600x900) via headless Chrome."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COVERS = Path(__file__).resolve().parent / "covers"
DEFAULT_HTML = COVERS / "infographic-ivermectin-safety.html"


def chrome_bin() -> str | None:
    for p in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
    ):
        if p and Path(p).exists():
            return p
    return None


def render(html: Path, out: Path, w: int = 1600, h: int = 900) -> None:
    chrome = chrome_bin()
    if not chrome:
        raise SystemExit("Google Chrome not found — install Chrome to render infographic covers")
    html = html.resolve()
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={w},{h}",
        f"--screenshot={out}",
        f"file://{html}",
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✓ {out}")


def main():
    slug = sys.argv[1] if len(sys.argv) > 1 else "how-to-buy-ivermectin-safely-online"
    html = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HTML
    out = COVERS / f"{slug}.png"
    render(html, out)
    dl = Path.home() / "Downloads" / f"ivermectin-infographic-cover-1600x900.png"
    shutil.copy2(out, dl)
    print(f"✓ Downloads → {dl}")


if __name__ == "__main__":
    main()