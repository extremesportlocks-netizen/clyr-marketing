#!/usr/bin/env python3
"""Render X ad HTML creative to PNG/JPG via headless Chrome."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def render(html: Path, out: Path, w: int, h: int) -> None:
    chrome = chrome_bin()
    if not chrome:
        raise SystemExit("Google Chrome not found")
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
    print(f"✓ {out} ({out.stat().st_size // 1024} KB)")


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: render-x-ad-creative.py <slug> [width] [height]")
    slug = sys.argv[1]
    w = int(sys.argv[2]) if len(sys.argv) > 2 else 1080
    h = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
    html = ROOT / "ads" / "x" / "creatives" / f"{slug}.html"
    if not html.exists():
        sys.exit(f"missing {html}")
    png = ROOT / "ads" / "x" / "creatives" / f"{slug}.png"
    render(html, png, w, h)
    jpg = ROOT / "ads" / "x" / "creatives" / f"{slug}.jpg"
    try:
        from PIL import Image

        Image.open(png).convert("RGB").save(jpg, "JPEG", quality=92, optimize=True)
        print(f"✓ {jpg} ({jpg.stat().st_size // 1024} KB)")
    except ImportError:
        shutil.copy2(png, jpg.with_suffix(".png"))
        print("• Pillow not installed — PNG only")
    dl = Path.home() / "Downloads" / f"{slug}-x-ad.jpg"
    if jpg.exists():
        shutil.copy2(jpg, dl)
        print(f"✓ Downloads → {dl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())