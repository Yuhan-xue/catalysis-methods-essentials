# -*- coding: utf-8 -*-
"""Compare the first text page of each chapter in both volumes.

If UP's chapter-first-text-page starts flush-left although its preceding page is a
*blank* (present in the scan), then 'flush-left' is the chapter's paragraph style
and DOWN's missing verso pages were blank too.
"""
import os, re
import pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDFS = {
 "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
 "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
PAGES = {
 "up":   [20, 21, 22, 23, 104, 105, 106, 188, 189, 190, 238, 239, 240, 322, 362, 363, 364, 434],
 "down": [18, 19, 59, 60, 224, 225, 226, 227, 296, 297, 298, 371, 372, 373, 374],
}
out = []
for vol, pages in PAGES.items():
    doc = pymupdf.open(PDFS[vol])
    for p in pages:
        pg = doc[p - 1]
        bl = [b for b in pg.get_text("blocks") if b[6] == 0 and b[4].strip()]
        bl.sort(key=lambda b: (b[1], b[0]))
        out.append(f"--- {vol} pdf {p} ---")
        for b in bl[:6]:
            first = b[4].strip().splitlines()[0][:46]
            out.append(f"    x0={b[0]:6.1f} y0={b[1]:6.1f}  {first!r}")
        # first line's x0 histogram of all blocks (indent detection)
        xs = sorted({round(b[0]) for b in bl})
        out.append(f"    distinct block x0 values: {xs}")
open(os.path.join(ROOT, "tools/out/firstpage_cmp.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
