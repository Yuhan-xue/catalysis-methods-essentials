# -*- coding: utf-8 -*-
r"""按区域打印页面的文字行（带坐标），用于判定命中处的上下文。

用法：python tools/ctx_region.py <page1based> <x0> <y0> <x1> <y1>
"""
import sys
import os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
pno = int(sys.argv[1]) - 1
rect = pymupdf.Rect(*(float(a) for a in sys.argv[2:6]))
doc = pymupdf.open(PDF)
page = doc[pno]
lines = []
for b in page.get_text("dict", clip=rect)["blocks"]:
    if b.get("type") != 0:
        continue
    for l in b["lines"]:
        txt = "".join(s["text"] for s in l["spans"])
        bb = l["bbox"]
        fonts = ",".join(sorted({s["font"] for s in l["spans"]}))
        sizes = ",".join("%.1f" % s["size"] for s in l["spans"])
        lines.append("[%7.2f,%7.2f,%7.2f,%7.2f] sz=%s %s  %r"
                     % (bb[0], bb[1], bb[2], bb[3], sizes, fonts, txt))
out = "\n".join(lines)
print(out)
with open(os.path.join(ROOT, "tools", "_ctx.txt"), "w", encoding="utf-8") as fh:
    fh.write(out)
