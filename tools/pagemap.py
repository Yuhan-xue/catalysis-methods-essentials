# -*- coding: utf-8 -*-
"""Tiny lookup helper for the page maps.

  python tools/pagemap.py up 268            -> printed page for PDF page 268
  python tools/pagemap.py up --book 249     -> PDF page(s) for printed page 249
  python tools/pagemap.py down 373 --note   -> also print the Chinese note

Default output is ASCII only (safe on a GBK console).  Use `| Out-File -Encoding utf8`
if you need the Chinese notes.
"""
import csv, os, sys

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FILES = {"up": "sources/page_map_up.csv", "down": "sources/page_map_down.csv"}


def load(vol):
    return list(csv.DictReader(open(os.path.join(ROOT, FILES[vol]), encoding="utf-8-sig")))


def main():
    vol = sys.argv[1].lower()
    rows = load(vol)
    show_note = "--note" in sys.argv
    if "--book" in sys.argv:
        want = sys.argv[sys.argv.index("--book") + 1]
        hits = [r for r in rows if r["book_page"] == want]
        if not hits:
            print(f"{vol}: printed page {want} not present in the PDF")
            return
        for r in hits:
            print(f"{vol}: printed {want} -> pdf {r['pdf_page']}  ({r['method']}/{r['confidence']})")
    else:
        p = sys.argv[2]
        hits = [r for r in rows if r["pdf_page"] == p]
        if not hits:
            print(f"{vol}: pdf page {p} out of range")
            return
        r = hits[0]
        print(f"{vol}: pdf {p} -> printed {r['book_page'] or '(none)'}  ({r['method']}/{r['confidence']})")
    if show_note:
        for r in rows:
            if r["pdf_page"] == sys.argv[2]:
                print("note:", r["note"])


if __name__ == "__main__":
    main()
