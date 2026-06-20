#!/usr/bin/env python3
"""Normalize journal URLs to trailing-slash form (avoids GSC 'Page with redirect')."""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# href="/journal/slug" or href='/journal/slug' (not already ending in / or index.html)
HREF_REL = re.compile(r'''(href=["'])/journal/([a-z0-9-]+)(?=["'])''')
# absolute journal URLs missing trailing slash before quote, #, or ?
ABS_JOURNAL = re.compile(
    r"(https://www\.clyr\.health/journal/[a-z0-9-]+)(?=[\"'#\?]|$)"
)
OG_URL = re.compile(
    r'(<meta property="og:url" content="https://www\.clyr\.health/journal/[a-z0-9-]+)(">)'
)


def fix_text(text: str) -> tuple[str, int]:
    n = 0

    def href_sub(m):
        nonlocal n
        n += 1
        return f'{m.group(1)}/journal/{m.group(2)}/'

    text = HREF_REL.sub(href_sub, text)

    def abs_sub(m):
        nonlocal n
        n += 1
        return m.group(1) + "/"

    text = ABS_JOURNAL.sub(abs_sub, text)

    def og_sub(m):
        nonlocal n
        if m.group(1).endswith("/"):
            return m.group(0)
        n += 1
        return m.group(1) + "/" + m.group(2)

    text = OG_URL.sub(og_sub, text)
    return text, n


def main():
    total = 0
    files = 0

    patterns = [
        "journal/**/*.html",
        "journal/index.html",
        "scripts/journal-content/*.json",
        "*.html",
        "preview/**/*.html",
    ]
    seen = set()
    paths = []
    for pat in patterns:
        for p in glob.glob(str(ROOT / pat), recursive="**" in pat):
            if p not in seen:
                seen.add(p)
                paths.append(p)

    for path in sorted(paths):
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        fixed, n = fix_text(text)
        if n:
            p.write_text(fixed, encoding="utf-8")
            print(f"✓ {n:3d} fixes  {p.relative_to(ROOT)}")
            total += n
            files += 1

    print(f"\nDone: {total} URL fixes across {files} files")


if __name__ == "__main__":
    main()