# -*- coding: utf-8 -*-
"""Check where numbered headings actually sit on the disputed UP pages."""
import re, pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
d = pymupdf.open(P)
FW = str.maketrans("０１２３４５６７８９．", "0123456789.")
out = []
for p in [226, 240, 241, 242, 257, 297, 339, 462]:
    out.append(f"=== up pdf {p}  (book {p-19}) ===")
    lines = []
    for blk in d[p - 1].get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            t = "".join(s["text"] for s in ln["spans"]).strip().translate(FW)
            if t:
                lines.append((round(ln["bbox"][1], 1), round(ln["bbox"][0], 1),
                              round(ln["spans"][0]["size"], 1), t[:64]))
    lines.sort()
    for y, x, size, t in lines:
        mark = "  <<<" if re.match(r"^\d{1,2}(\.\d{1,2}){1,2}[ 　]", t) else ""
        out.append(f"   y={y:6.1f} x0={x:6.1f} size={size:4.1f}  {t}{mark}")
open(ROOT + r"\tools\out\heading_check.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
