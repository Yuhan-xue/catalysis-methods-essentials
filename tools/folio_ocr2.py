# -*- coding: utf-8 -*-
"""Independent per-page folio reader (v2).

Digit templates are learned from the DOWN volume, whose running-head numbers are
known from the text layer.  Every page of both volumes is then read straight from
the rendered bitmap, giving a per-page measurement of the printed folio that is
independent of the OCR text layer and of the printed TOC.

Output: tools/out/folio_read.csv
"""
import os, csv, collections
import numpy as np
import pymupdf
from scipy import ndimage

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDFS = {
 "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
 "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
DPI = 300
S = DPI / 72.0
H, W = 28, 20
THR = 170

# rectangles (PDF pt) that may hold the folio
SLOTS = {
 "up":   [pymupdf.Rect(386, 26, 450, 56), pymupdf.Rect(12, 26, 76, 56)],
 "down": [pymupdf.Rect(384, 34, 436, 62), pymupdf.Rect(46, 34, 98, 62)],
}


def render(pg):
    pix = pg.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def crop(a, rect):
    x0 = max(0, int(rect.x0 * S)); x1 = min(a.shape[1], int(rect.x1 * S))
    y0 = max(0, int(rect.y0 * S)); y1 = min(a.shape[0], int(rect.y1 * S))
    return a[y0:y1, x0:x1]


def binar(a, thr=THR):
    if a.dtype == bool:
        return a.astype(np.uint8)
    return (a < thr).astype(np.uint8)


def norm_patch(b):
    """b: uint8 0/1 ink mask -> (28,20) float, or None."""
    ys, xs = np.nonzero(b)
    if ys.size == 0:
        return None, 0
    sub = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    yi = (np.arange(H) * sub.shape[0] / H).astype(int).clip(0, sub.shape[0] - 1)
    xi = (np.arange(W) * sub.shape[1] / W).astype(int).clip(0, sub.shape[1] - 1)
    return sub[np.ix_(yi, xi)].astype(np.float32), int(sub.sum())


# ---------------------------------------------------------------- learn templates
doc_dn = pymupdf.open(PDFS["down"])
tmpl = []
for p in range(1, doc_dn.page_count + 1):
    pg = doc_dn[p - 1]
    chars = []
    for blk in pg.get_text("rawdict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            for sp in ln["spans"]:
                for ch in sp["chars"]:
                    if ch["c"].isdigit() and ch["bbox"][1] < 60:
                        chars.append((ch["c"], pymupdf.Rect(ch["bbox"])))
    if not chars:
        continue
    a = render(pg)
    for c, r in chars:
        b = binar(crop(a, pymupdf.Rect(r.x0 - 0.6, r.y0 - 0.6, r.x1 + 0.6, r.y1 + 0.6)))
        t, area = norm_patch(b)
        if t is None or area < 25 or area > 0.8 * t.size:
            continue
        tmpl.append((c, t))
doc_dn.close()

labels = [c for c, _ in tmpl]
BANK = np.stack([t.ravel() for _, t in tmpl])          # (N,560)
LAB = np.array(labels)
print("templates:", BANK.shape, dict(sorted(collections.Counter(labels).items())))


def classify(t):
    d = np.abs(BANK - t.ravel()).mean(axis=1)
    i = int(d.argmin())
    return LAB[i], float(d[i])


def read_slot(a, rect):
    sub = crop(a, rect)
    b = binar(sub)
    lab, n = ndimage.label(b, structure=np.ones((3, 3), int))
    comps = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if ys.size < 30:
            continue
        comps.append((int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()), int(ys.size), i))
    if not comps:
        return None
    comps.sort()
    hmax = max(c[3] - c[2] for c in comps)
    digits, errs = [], []
    for x0, x1, y0, y1, area, i in comps:
        if (y1 - y0) < 0.6 * hmax:
            continue
        m = (lab[y0:y1 + 1, x0:x1 + 1] == i).astype(np.uint8)
        t, ar = norm_patch(m)
        if t is None:
            continue
        d, e = classify(t)
        digits.append((x0, d)); errs.append(e)
    if not digits:
        return None
    digits.sort()
    return {"num": "".join(d for _, d in digits),
            "maxerr": round(max(errs), 4), "ndig": len(digits),
            "ink": int(b.sum())}


DOCS = {v: pymupdf.open(PDFS[v]) for v in PDFS}
rows = []
for vol in ["up", "down"]:
    doc = DOCS[vol]
    for p in range(1, doc.page_count + 1):
        a = render(doc[p - 1])
        best = None
        for si, rect in enumerate(SLOTS[vol]):
            got = read_slot(a, rect)
            if got:
                got["slot"] = si
                if best is None or (1 <= got["ndig"] <= 4 and got["ink"] > best["ink"]):
                    best = got
        rows.append({"vol": vol, "pdf_page": p,
                     "read": best["num"] if best else "",
                     "ndig": best["ndig"] if best else 0,
                     "slot": best["slot"] if best else "",
                     "maxerr": best["maxerr"] if best else "",
                     "ink": best["ink"] if best else 0})
    print(vol, "done")
for v in DOCS:
    DOCS[v].close()

with open(os.path.join(ROOT, "tools/out/folio_read.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["vol", "pdf_page", "read", "ndig", "slot", "maxerr", "ink"])
    w.writeheader(); w.writerows(rows)
print("rows", len(rows))
