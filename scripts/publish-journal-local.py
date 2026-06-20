#!/usr/bin/env python3
"""Render a journal JSON locally and update journal/index.html (no GitHub API)."""
import importlib.util
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
spec = importlib.util.spec_from_file_location(
    "post_journal", os.path.join(os.path.dirname(__file__), "post-journal.py")
)
pj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pj)


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: publish-journal-local.py <content.json>")
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    missing = [k for k in pj.REQUIRED if not c.get(k)]
    if missing:
        sys.exit("missing: " + ", ".join(missing))

    ref_path = os.path.join(ROOT, pj.REFERENCE)
    with open(ref_path, encoding="utf-8") as f:
        ref = f.read()

    slug = c["slug"].strip("/")
    page = pj.render_page(ref, c)
    out_dir = os.path.join(ROOT, "journal", slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"✓ wrote {out_path} ({len(page.splitlines())} lines)")

    idx_path = os.path.join(ROOT, "journal", "index.html")
    with open(idx_path, encoding="utf-8") as f:
        idx = f.read()
    anchor = '<div class="featured-grid">'
    needle = f'href="/journal/{slug}/"'
    if needle in idx:
        print("• index already lists this post")
    else:
        idx = idx.replace(anchor, anchor + "\n" + pj.index_card(c), 1)
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(idx)
        print("✓ prepended card to journal/index.html")

    print(f"Preview: file://{out_path}")
    print(f"Live after push: https://www.clyr.health/journal/{slug}/")


if __name__ == "__main__":
    main()