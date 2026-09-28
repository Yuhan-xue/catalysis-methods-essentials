# -*- coding: utf-8 -*-
"""1:1 ASCII art of the UP front-matter folio slot (to see whether it is roman)."""
import os
import numpy as np, pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
RAMP = " .:-=+*#%@"
doc = pymupdf.open(P)
out = []
for p in [8, 9, 10, 12, 13, 14, 15, 17, 19]:
    pg = doc[p - 1]
    pix = pg.get_pixmap(dpi=300, clip=pymupdf.Rect(20, 26, 90, 54), colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
    ys, xs = np.nonzero(a < 170)
    out.append(f"===== up p{p} left slot x=20..90pt y=26..54pt  ink={ys.size}")
    if ys.size == 0:
        out.append("   NO INK")
        continue
    a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    for row in a:
        out.append("".join(RAMP[min(9, int((255 - v) / 25.6))] for v in row))
open(ROOT + r"\tools\out\up_front_folio.txt", "w", encoding="utf-8").write("\n".join(out))
print("lines", len(out))
