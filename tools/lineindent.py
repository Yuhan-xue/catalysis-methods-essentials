# -*- coding: utf-8 -*-
"""Line-level first-line indent analysis (block bboxes hide the indent)."""
import os
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDFS = {
 "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
 "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
PAGES = {
 "up":   [22, 106, 190, 240, 322, 364, 434, 26, 28, 30],
 "down": [19, 60, 226, 227, 297, 298, 373, 374, 21, 23, 25],
}
out = []
for vol, pages in PAGES.items():
    doc = pymupdf.open(PDFS[vol])
    for p in pages:
        pg = doc[p - 1]
        out.append(f"--- {vol} pdf {p}  (lines: y0, x0, first-line indent) ---")
        d = pg.get_text("dict")
        lines = []
        for blk in d["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk["lines"]:
                txt = "".join(s["text"] for s in ln["spans"]).strip()
                if txt:
                    lines.append((round(ln["bbox"][1], 1), round(ln["bbox"][0], 1),
                                  round(ln["bbox"][2], 1), txt[:34]))
        lines.sort()
        for y, x, x1, t in lines[:9]:
            out.append(f"    y={y:6.1f} x0={x:6.1f} x1={x1:6.1f}  {t!r}")
open(os.path.join(ROOT, "tools/out/lineindent.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
