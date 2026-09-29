# -*- coding: utf-8 -*-
r"""并排比较 rawdict / texttrace 的字符盒，判断哪种更接近字形墨迹盒。

用法：python tools/probe_charbox.py <page1based> <x0> <y0> <x1> <y1>
"""
import sys, os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
pno = int(sys.argv[1]) - 1
rect = pymupdf.Rect(*(float(a) for a in sys.argv[2:6]))
doc = pymupdf.open(PDF)
page = doc[pno]

print("### rawdict")
for b in page.get_text("rawdict", clip=rect)["blocks"]:
    if b.get("type") != 0:
        continue
    for l in b["lines"]:
        for s in l["spans"]:
            for ch in s["chars"]:
                if not ch["c"].strip():
                    continue
                x0, y0, x1, y1 = ch["bbox"]
                print(f"  {ch['c']!r:>8} bbox=[{x0:7.2f},{y0:7.2f},{x1:7.2f},{y1:7.2f}] "
                      f"w={x1-x0:5.2f} h={y1-y0:5.2f} org=({ch['origin'][0]:7.2f},{ch['origin'][1]:7.2f})")

print("### texttrace")
for s in page.get_texttrace():
    if not (pymupdf.Rect(s["bbox"]) & rect):
        continue
    for ch in s["chars"]:
        c = chr(ch["c"]) if isinstance(ch["c"], int) else ch["c"]
        if not c.strip():
            continue
        x0, y0, x1, y1 = ch["bbox"]
        print(f"  {c!r:>8} gid={ch['g']:<5} bbox=[{x0:7.2f},{y0:7.2f},{x1:7.2f},{y1:7.2f}] "
              f"w={x1-x0:5.2f} h={y1-y0:5.2f} org=({ch['origin'][0]:7.2f},{ch['origin'][1]:7.2f}) "
              f"font={s['font']} sz={s['size']:.2f}")
