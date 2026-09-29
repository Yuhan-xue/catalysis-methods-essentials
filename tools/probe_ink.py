# -*- coding: utf-8 -*-
r"""试验：用字体轮廓（glyph_bbox）算**墨迹盒**，替代 rawdict 的「度量盒」。

rawdict 的字符盒 = 推进宽度 × (ascender..descender)，对 `−`（细横条）这类字形
虚胖严重，会产生大量假重叠。字体程序里的 glyph bbox 才是真墨迹范围。

用法：python tools/probe_ink.py <page1based> <x0> <y0> <x1> <y1>
"""
import sys, os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
pno = int(sys.argv[1]) - 1
rect = pymupdf.Rect(*(float(a) for a in sys.argv[2:6]))
doc = pymupdf.open(PDF)
page = doc[pno]

print("### get_fonts")
for f in page.get_fonts(full=True):
    print("   ", f)

print("### texttrace raw shape")
tt = page.get_texttrace()
if tt:
    s0 = tt[0]
    print("   span keys:", sorted(s0.keys()))
    print("   chars type:", type(s0["chars"]), "len", len(s0["chars"]))
    print("   chars[0]:", s0["chars"][0], type(s0["chars"][0]))
