# -*- coding: utf-8 -*-
"""Report folio-reader output for specific UP pages + tight 1:1 art of a few folios."""
import csv, os
import numpy as np, pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
rows = list(csv.DictReader(open(ROOT + r"\tools\out\folio_read.csv", encoding="utf-8")))
want = list(range(20, 33)) + [93, 163, 263, 460, 464, 465, 475, 537, 543]
out = ["== folio reader output =="]
for r in rows:
    if r["vol"] != "up":
        continue
    p = int(r["pdf_page"])
    if p in want:
        out.append(f"  up p{p:>4} -> book {p-19:>4} | read={r['read']!r:>7} ndig={r['ndig']} slot={r['slot']} ink={r['ink']} err={r['maxerr']}")

RAMP = " .:-=+*#%@"
doc = pymupdf.open(P)
for p in [22, 23, 93]:
    pg = doc[p - 1]
    pix = pg.get_pixmap(dpi=300, clip=pymupdf.Rect(386, 30, 442, 52), colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
    ys, xs = np.nonzero(a < 170)
    out.append(f"\n== up p{p} tight 1:1 art of x=386..442pt y=30..52pt (expect folio {p-19}) ink={ys.size} ==")
    if ys.size == 0:
        out.append("   NO INK")
        continue
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    for row in a:
        out.append("".join(RAMP[min(9, int((255 - v) / 25.6))] for v in row))
open(ROOT + r"\tools\out\folio_specific.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
