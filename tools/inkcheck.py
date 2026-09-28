# -*- coding: utf-8 -*-
"""Verify that text-layer tokens correspond to real ink in the rendered bitmap.

For each requested (vol, page, needle): find words whose text matches needle in the
text layer, render the page, and measure ink (dark pixel) statistics inside the
word bbox.  Also reports ink in the running-head row outside the matched word.
"""
import os, sys, json
import numpy as np
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}

DOCS = {}


def doc(v):
    if v not in DOCS:
        DOCS[v] = pymupdf.open(PDF[v])
    return DOCS[v]


def gray(pg, dpi=200):
    pix = pg.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a


def ink_in(a, rect, dpi, thr=160):
    sx = dpi / 72.0
    x0 = max(0, int(rect.x0 * sx)); x1 = min(a.shape[1], int(rect.x1 * sx) + 1)
    y0 = max(0, int(rect.y0 * sx)); y1 = min(a.shape[0], int(rect.y1 * sx) + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    sub = a[y0:y1, x0:x1]
    dark = int((sub < thr).sum())
    return {"box": [x0, y0, x1, y1], "px": int(sub.size), "dark": dark,
            "dark_frac": round(dark / max(1, sub.size), 4), "min": int(sub.min())}


def probe(vol, page, needle, dpi=200, whole_row=False):
    pg = doc(vol)[page - 1]
    a = gray(pg, dpi)
    words = pg.get_text("words")
    out = {"vol": vol, "page": page, "needle": needle, "page_wh": [round(pg.rect.width, 1), round(pg.rect.height, 1)],
           "matches": []}
    for w in words:
        t = w[4]
        if needle and needle in t:
            r = pymupdf.Rect(w[:4])
            out["matches"].append({"text": t, "rect": [round(v, 1) for v in w[:4]],
                                   "ink": ink_in(a, r, dpi)})
    if whole_row:
        # all words in the top 12% of the page, with ink stats
        h = pg.rect.height
        row = [w for w in words if w[1] < 0.12 * h]
        row.sort(key=lambda w: w[0])
        out["top_row"] = [{"text": w[4], "x0": round(w[0], 1), "x1": round(w[2], 1),
                           "ink": ink_in(a, pymupdf.Rect(w[:4]), dpi)} for w in row]
    return out


if __name__ == "__main__":
    tasks = json.load(open(sys.argv[1], encoding="utf-8"))
    res = [probe(t["vol"], t["page"], t.get("needle", ""), t.get("dpi", 200), t.get("row", False))
           for t in tasks]
    json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", sys.argv[2], len(res))
