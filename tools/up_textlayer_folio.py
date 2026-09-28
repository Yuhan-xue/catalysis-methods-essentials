# -*- coding: utf-8 -*-
"""Extra cross-check: does the PDF text layer itself contain the expected folio
number for UP pages?  (Independent of the bitmap reader.)"""
import re, pymupdf
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
d = pymupdf.open(P)
hit = miss = 0
miss_pages = []
out = []
for p in range(20, 543):
    exp = str(p - 19)
    pg = d[p - 1]
    words = [w[4] for w in pg.get_text("words") if w[3] < 60 and w[0] > 380]
    if exp in words:
        hit += 1
    else:
        miss += 1
        miss_pages.append(p)
out.append(f"UP text-layer folio check: expected number found as a top-right token on {hit} pages, "
           f"not found on {miss} pages (of 20..542)")
out.append("pages without a text-layer folio token: " + str(miss_pages))
open(ROOT + r"\tools\out\up_textlayer_folio.txt", "w", encoding="utf-8").write("\n".join(out))
print(out[0][:120])
