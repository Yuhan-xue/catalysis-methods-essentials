# -*- coding: utf-8 -*-
"""Independent per-page folio reader.

Builds a digit template bank from the DOWN volume (whose running-head numbers are
known from the text layer AND ink-verified), then reads the folio of EVERY page of
BOTH volumes purely from the rendered bitmap.  That gives a per-page measurement of
the printed page number, independent of the OCR text layer and of the TOC.

Output: tools/out/folio_read.csv   (vol,pdf_page,folio_slot_ink,read_number,ntemplates)
        tools/out/folio_templates.txt (diagnostics)
"""
import os, re, json, collections
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
H, W = 28, 20          # normalised template grid

# folio slot rectangles in PDF points, per volume (from the layout analysis)
SLOT = {
 "up":   pymupdf.Rect(388, 28, 448, 54),
 "down": pymupdf.Rect(386, 36, 434, 60),
}


def render(pg):
    pix = pg.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)


def crop(a, rect):
    x0 = max(0, int(rect.x0 * S)); x1 = min(a.shape[1], int(rect.x1 * S))
    y0 = max(0, int(rect.y0 * S)); y1 = min(a.shape[0], int(rect.y1 * S))
    return a[y0:y1, x0:x1], (x0, y0)


def norm_patch(sub, thr=170):
    """Binarise, crop to ink bbox, resize to HxW float in [0,1]."""
    b = (sub < thr).astype(np.uint8)
    ys, xs = np.nonzero(b)
    if ys.size == 0:
        return None, 0
    b = b[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = np.array(pymupdf.Pixmap(pymupdf.csGRAY, pymupdf.IRect(0, 0, b.shape[1], b.shape[0]),
                                 False), copy=False) if False else None
    # nearest-neighbour resize with numpy
    yi = (np.arange(H) * b.shape[0] / H).astype(int).clip(0, b.shape[0] - 1)
    xi = (np.arange(W) * b.shape[1] / W).astype(int).clip(0, b.shape[1] - 1)
    r = b[np.ix_(yi, xi)].astype(np.float32)
    return r, int(b.sum())


def segment(sub, thr=170, min_area=40):
    b = sub < thr
    lab, n = ndimage.label(b, structure=np.ones((3, 3), int))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if ys.size < min_area:
            continue
        out.append((xs.min(), xs.max(), ys.min(), ys.max(), ys.size, i))
    out.sort()
    return b, lab, out


# ---------------------------------------------------------------- DOWN templates
doc_dn = pymupdf.open(PDFS["down"])
templates = []      # (label, normalised bitmap)
tmpl_info = []
for p in range(1, doc_dn.page_count + 1):
    pg = doc_dn[p - 1]
    raw = pg.get_text("rawdict")
    chars = []
    for blk in raw["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            for sp in ln["spans"]:
                for ch in sp["chars"]:
                    c = ch["c"]
                    if c.isdigit() and ch["bbox"][1] < 60 and ch["bbox"][0] > 380:
                        chars.append((c, pymupdf.Rect(ch["bbox"])))
    if not chars:
        continue
    a = render(pg)
    for c, r in chars:
        pad = pymupdf.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
        sub, _ = crop(a, pad)
        t, area = norm_patch(sub)
        if t is None or area < 25:
            continue
        templates.append((c, t, p, area))
doc_dn.close()

per_digit = collections.Counter(l for l, _, _, _ in templates)
print("DOWN digit templates:", len(templates), dict(sorted(per_digit.items())))
# prune: keep at most 12 exemplars per digit, preferring larger area (cleaner)
by_digit = collections.defaultdict(list)
for l, t, p, area in templates:
    by_digit[l].append((area, t, p))
bank = []
for d, lst in by_digit.items():
    lst.sort(key=lambda x: -x[0])
    for area, t, p in lst[:12]:
        bank.append((d, t))
print("template bank:", len(bank))
tmpl_info.append(f"template bank size {len(bank)}: " + str(collections.Counter(d for d, _ in bank)))


def classify(t):
    best = None
    for d, tt in bank:
        err = float(np.abs(t - tt).mean())
        if best is None or err < best[0]:
            best = (err, d)
    return best[1], best[0]


def read_folio(vol, p):
    doc = DOCS[vol]
    pg = doc[p - 1]
    a = render(pg)
    sub, _ = crop(a, SLOT[vol])
    b, lab, comps = segment(sub)
    slot_ink = int(b.sum())
    if not comps:
        return slot_ink, "", 0, []
    heights = [c[3] - c[2] for c in comps]
    hmax = max(heights)
    digits = []
    for x0, x1, y0, y1, area, i in comps:
        h = y1 - y0
        if h < 0.55 * hmax:            # the · separators and specks
            continue
        patch = (lab[y0:y1 + 1, x0:x1 + 1] == i).astype(np.uint8)
        t, _ = norm_patch(patch, thr=0.5)
        if t is None:
            continue
        d, err = classify(t)
        digits.append((x0, d, err, h, area))
    digits.sort()
    return slot_ink, "".join(d for _, d, _, _, _ in digits), len(comps), digits


DOCS = {v: pymupdf.open(PDFS[v]) for v in PDFS}
rows = []
for vol in ["up", "down"]:
    doc = DOCS[vol]
    for p in range(1, doc.page_count + 1):
        try:
            ink, num, ncomp, det = read_folio(vol, p)
        except Exception as e:
            ink, num, ncomp, det = -1, "ERR:" + str(e)[:40], 0, []
        rows.append((vol, p, ink, num, ncomp,
                     " ".join(f"{d}@{x}(e{e:.2f})" for x, d, e, h, ar in det)))
DOCS["up"].close(); DOCS["down"].close()

with open(os.path.join(ROOT, "tools/out/folio_read.csv"), "w", encoding="utf-8") as f:
    f.write("vol,pdf_page,slot_ink,read_number,ncomp,detail\n")
    for r in rows:
        f.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},\"{r[5]}\"\n")
open(os.path.join(ROOT, "tools/out/folio_templates.txt"), "w", encoding="utf-8").write("\n".join(tmpl_info))
print("rows:", len(rows))
