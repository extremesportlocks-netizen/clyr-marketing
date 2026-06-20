#!/usr/bin/env python3
"""Sweep em dashes (and stray en dashes) out of the journal to match house style.
- numeric ranges  5–15 / 5—15  -> 5-15  (hyphen)
- clause em dash   word — word  -> word, word  (comma)
- stray en dash    word – word  -> word, word
Operates on journal/index.html, journal/*/index.html, scripts/journal-content/*.json.
Idempotent. Run from repo root.
"""
import re, glob, pathlib

def sweep(text):
    text = re.sub(r'(\d)\s*[–—]\s*(\d)', r'\1-\2', text)   # numeric range -> hyphen
    text = re.sub(r'\s*—\s*', ', ', text)                   # em dash -> comma
    text = re.sub(r'\s*–\s*', ', ', text)                   # remaining en dash -> comma
    text = re.sub(r',\s*,', ', ', text)                     # collapse double commas
    text = re.sub(r'\s+,', ',', text)                       # no space before comma
    return text

def main():
    targets = ["journal/index.html"] + sorted(glob.glob("journal/*/index.html")) + sorted(glob.glob("scripts/journal-content/*.json"))
    changed = 0
    for t in targets:
        p = pathlib.Path(t)
        s = p.read_text(encoding="utf-8")
        n = s.count("—") + s.count("–")
        if n:
            p.write_text(sweep(s), encoding="utf-8")
            changed += 1
    print(f"files swept: {changed}")

if __name__ == "__main__":
    main()
