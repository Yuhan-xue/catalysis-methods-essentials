# -*- coding: utf-8 -*-
"""Shared PDF-page <-> printed-page mapping (library).

The CLI in tools/pagemap.py is for humans; this module is for scripts.

Authoritative sources:
  sources/page_map_down.csv  — per-page printed number read from running heads.
  sources/page_map_up.csv    — per-page mapping derived from section anchors.
Fallback only where the CSVs carry no numeric entry:
  UP  : book = pdf - 19                       (verified constant, all 7 chapters)
  DOWN: piecewise book = pdf + off            (off in {507..514}, 8 segments)
"""
import csv, os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
DN_SEG = [(18, 507), (19, 508), (60, 509), (225, 510),
          (226, 511), (297, 512), (372, 513), (373, 514)]
UP_OFF = 19
DN_FIRST, DN_LAST = 18, 462

_cache = {}


def _load(name):
    if name in _cache:
        return _cache[name]
    path = os.path.join(ROOT, "sources", name)
    m = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path, encoding="utf-8-sig")):
            v = (r.get("book_page") or "").strip()
            if v.isdigit():
                m[int(r["pdf_page"])] = int(v)
    _cache[name] = m
    return m


def dn_map():
    return _load("page_map_down.csv")


def up_map():
    return _load("page_map_up.csv")


def dn_book(pdf):
    m = dn_map()
    if pdf in m:
        return m[pdf]
    off = DN_SEG[0][1]
    for start, o in DN_SEG:
        if pdf >= start:
            off = o
    return pdf + off


def up_book(pdf):
    m = up_map()
    return m.get(pdf, pdf - UP_OFF)


def dn_pdf(book):
    """first DOWN pdf page whose printed page is >= book."""
    rev = {v: k for k, v in dn_map().items()}
    if book in rev:
        return rev[book]
    for p in range(DN_FIRST, DN_LAST + 1):
        if dn_book(p) >= book:
            return p
    return DN_LAST


def up_pdf(book):
    return book + UP_OFF


def book(vol, pdf_page):
    return up_book(pdf_page) if vol == "up" else dn_book(pdf_page)


def pdf(vol, book_page):
    return up_pdf(book_page) if vol == "up" else dn_pdf(book_page)


if __name__ == "__main__":
    # self-check against the known anchors
    anchors = [("down", 18, 525), ("down", 19, 527), ("down", 20, 528),
               ("down", 59, 567), ("down", 225, 735), ("down", 296, 807),
               ("down", 372, 885), ("down", 461, 975),
               ("up", 20, 1), ("up", 104, 85), ("up", 238, 219), ("up", 543, 524)]
    bad = 0
    for vol, p, b in anchors:
        got = book(vol, p)
        flag = "OK " if got == b else "BAD"
        if got != b:
            bad += 1
        print(f"{flag} {vol} pdf {p} -> book {got} (expect {b})")
    print("self-check:", "PASS" if bad == 0 else f"FAIL ({bad})")
