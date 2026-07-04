#!/usr/bin/env python3
"""Generate X Article cover from journal-content JSON (matches site OG system)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OG_SCRIPT = ROOT / "scripts" / "generate-journal-og.py"
CONTENT = ROOT / "scripts" / "journal-content"
COVERS = Path(__file__).resolve().parent / "covers"
JOURNAL_OG = ROOT / "img" / "journal-og"


def _load_render():
    spec = importlib.util.spec_from_file_location("generate_journal_og", OG_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.render_card


def main():
    slug = sys.argv[1]
    json_path = CONTENT / f"{slug}.json"
    if not json_path.exists():
        title = sys.argv[2] if len(sys.argv) > 2 else slug.replace("-", " ").title()
        c = {"slug": slug, "title": title, "category": "Recovery", "categoryKey": "longevity", "deck": ""}
    else:
        c = json.loads(json_path.read_text(encoding="utf-8"))

    render = _load_render()
    x_out = COVERS / f"{slug}.png"
    og_out = JOURNAL_OG / f"{slug}.png"
    render(c, x_out, size=(1600, 900))
    render(c, og_out, size=(1200, 630))
    print(f"✓ X cover → {x_out}")
    print(f"✓ Journal OG → {og_out}")


if __name__ == "__main__":
    main()