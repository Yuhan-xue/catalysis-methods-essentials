# -*- coding: utf-8 -*-
"""Measure ink in the UP running-head folio slot (top-right corner) for every page.

UP page 455.8 x 696 pt.  Running head line sits at y=36..48 pt.
  - title (第N章… / 现代催化研究方法新编（上册）) is centred around x=150..310
  - the folio (if printed) sits at the right edge, x approx 396..440
Also report the text-layer tokens found in that slot.
"""
import os, re
import numpy as np, pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDF_UP = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(PDF_UP)
DPI = 200
S = DPI / 72.0

FOLIO = pymupdf.Rect(392, 30, 445, 52)     # right edge of running-head line
TITLE = pymupdf.Rect(120, 30, 330, 52)     # running-head title
LEFTSLOT = pymupdf.Rect(16, 30, 70, 52)    # left edge of running-head line


def darkcount(a, r):
    x0 = max(0, int(r.x0 * S)); x1 = min(a.shape[1], int(r.x1 * S))
    y0 = max(0, int(r.y0 * S)); y1 = min(a.shape[0], int(r.y1 * S))
    if x1 <= x0 or y1 <= y0:
        return -1
    return int((a[y0:y1, x0:x1] < 170).sum())


lines = []
folioless = []
for p in range(1, doc.page_count + 1):
    pg = doc[p - 1]
    pix = pg.get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    f = darkcount(a, FOLIO)
    t = darkcount(a, TITLE)
    l = darkcount(a, LEFTSLOT)
    # text-layer tokens in the folio slot
    toks = [w[4] for w in pg.get_text("words") if w[0] > 380 and w[3] < 60]
    # whole-page ink to spot blank pages
    whole = int((a < 170).sum())
    lines.append(f"p{p:>4} folio_ink={f:>6} title_ink={t:>6} left_ink={l:>6} page_ink={whole:>7} tok={toks}")
    if f < 25:
        folioless.append(p)
open(os.path.join(ROOT, "tools/out/up_folio.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("pages:", doc.page_count, "pages with (almost) no ink in folio slot:", len(folioless))
print(folioless[:80])
