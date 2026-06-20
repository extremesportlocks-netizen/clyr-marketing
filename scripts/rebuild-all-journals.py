#!/usr/bin/env python3
"""Rebuild all journal HTML pages from scripts/journal-content/*.json."""
import glob
import importlib.util
import json
import os
import subprocess
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
spec = importlib.util.spec_from_file_location(
    "post_journal", os.path.join(os.path.dirname(__file__), "post-journal.py")
)
pj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pj)

def main():
    ref_path = os.path.join(ROOT, pj.REFERENCE)
    with open(ref_path, encoding="utf-8") as f:
        ref = f.read()

    json_files = sorted(glob.glob(os.path.join(ROOT, "scripts/journal-content/*.json")))
    if not json_files:
        sys.exit("no JSON files")

    # OG images first
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts/generate-journal-og.py")] + json_files, check=True)

    ok = 0
    for path in json_files:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
        slug = c["slug"].strip("/")
        page = pj.render_page(ref, c)
        out_dir = os.path.join(ROOT, "journal", slug)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page)
        ok += 1
        print(f"✓ rebuilt journal/{slug}/index.html")

    print(f"\nDone: {ok} articles rebuilt with SEO polish + OG images")

if __name__ == "__main__":
    main()