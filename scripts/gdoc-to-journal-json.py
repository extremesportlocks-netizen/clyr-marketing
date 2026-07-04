#!/usr/bin/env python3
"""Convert exported Google Doc text to journal-content JSON."""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "scripts" / "journal-content"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def inline_markup(text: str) -> str:
    parts: list[str] = []
    pos = 0
    for m in LINK_RE.finditer(text):
        if m.start() > pos:
            parts.append(html.escape(text[pos : m.start()]))
        parts.append(
            f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'
        )
        pos = m.end()
    parts.append(html.escape(text[pos:]))
    out = "".join(parts)
    return BOLD_RE.sub(r"<strong>\1</strong>", out)


def parse_doc(text: str) -> tuple[dict[str, str], list[tuple[str, str | list[str]]]]:
    lines = text.splitlines()
    meta: dict[str, str] = {}
    body_lines: list[str] = []
    in_body = False
    for line in lines:
        if line.strip() == "---" and not in_body:
            in_body = True
            continue
        if not in_body:
            upper = line.strip().upper()
            for key in ("TITLE", "SLUG", "CATEGORY", "READING TIME", "DECK", "PRODUCT LINK"):
                if upper.startswith(key + ":"):
                    meta[key] = line.split(":", 1)[1].strip()
            continue
        body_lines.append(line)

    blocks: list[tuple[str, str | list[str]]] = []
    para: list[str] = []
    list_items: list[str] = []
    list_type: str | None = None

    def flush_para() -> None:
        nonlocal para
        if para:
            blocks.append(("p", " ".join(para).strip()))
            para = []

    def flush_list() -> None:
        nonlocal list_items, list_type
        if list_items:
            blocks.append((list_type or "ul", list_items[:]))
            list_items = []
            list_type = None

    for raw in body_lines:
        line = raw.strip()
        if not line:
            flush_para()
            flush_list()
            continue
        if line.startswith("## "):
            flush_para()
            flush_list()
            blocks.append(("h2", line[3:].strip()))
            continue
        if line.startswith("**") and line.endswith("**") and line.count("**") == 2:
            flush_para()
            flush_list()
            blocks.append(("h3", line.strip("* ").strip()))
            continue
        if line.startswith("- "):
            flush_para()
            if list_type != "ul":
                flush_list()
                list_type = "ul"
            list_items.append(line[2:].strip())
            continue
        flush_list()
        para.append(line)
    flush_para()
    flush_list()
    return meta, blocks


def blocks_to_html(blocks: list[tuple[str, str | list[str]]]) -> str:
    out: list[str] = []
    for kind, value in blocks:
        if kind == "h2":
            out.append(f"<h2>{inline_markup(str(value))}</h2>")
        elif kind == "h3":
            out.append(f"<h3>{inline_markup(str(value))}</h3>")
        elif kind == "p":
            out.append(f"<p>{inline_markup(str(value))}</p>")
        elif kind == "ul":
            items = "".join(f"<li>{inline_markup(i)}</li>" for i in value)  # type: ignore
            out.append(f"<ul>{items}</ul>")
    return "\n\n".join(out)


def main() -> int:
    doc_id = sys.argv[1] if len(sys.argv) > 1 else "1077tQQnzb0rrzfGY6rZf3s_DuAs3gHzhadw7OMtg-dw"
    text = subprocess.check_output(
        ["curl", "-fsSL", f"https://docs.google.com/document/d/{doc_id}/export?format=txt"],
        text=True,
    )
    meta, blocks = parse_doc(text)
    slug = meta.get("SLUG", "article")
    title = meta.get("TITLE", slug.replace("-", " ").title())
    deck = meta.get("DECK", "")
    category = meta.get("CATEGORY", "Journal")
    read_time = meta.get("READING TIME", "10 min read")
    body_html = blocks_to_html(blocks)

    payload = {
        "slug": slug,
        "title": title,
        "category": category,
        "categoryKey": "longevity",
        "deck": deck,
        "date": "July 1, 2026",
        "readTime": read_time,
        "metaDescription": deck,
        "bodyHtml": body_html,
        "related": [
            {"slug": "parasite-cleanse-vs-antiparasitic-medicine", "title": "Parasite Cleanses vs. Real Antiparasitic Medicine", "category": "Longevity"},
            {"slug": "ivermectin-wellness-protocol-overview", "title": "Ivermectin Wellness Protocol Overview", "category": "Recovery"},
        ],
    }
    out = CONTENT_DIR / f"{slug}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"✓ Wrote {out} ({len(body_html)} chars bodyHtml)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())