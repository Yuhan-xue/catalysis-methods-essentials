# -*- coding: utf-8 -*-
r"""试验 2：验证 glyph_bbox 的坐标约定，并给出「墨迹盒」算法。

对 Page 上的 span，从 PDF 里取出嵌入字体 → pymupdf.Font → glyph_bbox(chr, size=1)。
再按原点平移得到页面坐标下的墨迹盒，与 rawdict 度量盒并排打印。
"""
import sys, os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
pno = int(sys.argv[1]) - 1
rect = pymupdf.Rect(*(float(a) for a in sys.argv[2:6]))
doc = pymupdf.open(PDF)
page = doc[pno]

# 字体字典：xref -> pymupdf.Font
fcache = {}
for f in page.get_fonts(full=True):
    xref, ext, subtype, basefont = f[0], f[1], f[2], f[3]
    if ext == "n/a":
        continue
    try:
        name, ext2, st, buf = doc.extract_font(xref)
        if buf:
            fo = pymupdf.Font(fontbuffer=buf)
            for key in {basefont, basefont.split("+", 1)[-1],
                        basefont.split("+", 1)[-1].replace("-Identity-H", ""),
                        basefont.split("+", 1)[-1].split("-Identity")[0]}:
                fcache[key] = fo
    except Exception as e:
        print("font fail", basefont, e)

print("loaded fonts:", sorted(fcache))

for b in page.get_text("rawdict", clip=rect)["blocks"]:
    if b.get("type") != 0:
        continue
    for l in b["lines"]:
        for s in l["spans"]:
            font = fcache.get(s["font"])
            if font is None:
                print("  (no font)", s["font"], "".join(c["c"] for c in s["chars"])[:40])
                continue
            sz = s["size"]
            for ch in s["chars"]:
                c = ch["c"]
                if not c.strip():
                    continue
                x0, y0, x1, y1 = ch["bbox"]
                ox, oy = ch["origin"]
                try:
                    gb = font.glyph_bbox(ord(c))
                except Exception as e:
                    gb = None
                if gb is None:
                    print(f"  {c!r:>6} metric=[{x0:7.2f},{y0:7.2f},{x1:7.2f},{y1:7.2f}] "
                          f"w={x1-x0:5.2f} h={y1-y0:5.2f}  no-glyph")
                    continue
                gx0, gy0, gx1, gy1 = gb
                # 约定 A：y 向下为正（与页面一致）
                A = (ox + gx0 * sz, oy + gy0 * sz, ox + gx1 * sz, oy + gy1 * sz)
                # 约定 B：y 向上为正（PDF 文本空间）
                B = (ox + gx0 * sz, oy - gy1 * sz, ox + gx1 * sz, oy - gy0 * sz)
                print(f"  {c!r:>6} sz={sz:4.1f} metric=[{x0:7.2f},{y0:7.2f},{x1:7.2f},{y1:7.2f}] "
                      f"w={x1-x0:5.2f} h={y1-y0:5.2f}")
                print(f"          gb={tuple(round(v,4) for v in gb)}  "
                      f"A=[{A[0]:7.2f},{A[1]:7.2f},{A[2]:7.2f},{A[3]:7.2f}] w={A[2]-A[0]:5.2f} h={A[3]-A[1]:5.2f}")
                print(f"          {'':14}B=[{B[0]:7.2f},{B[1]:7.2f},{B[2]:7.2f},{B[3]:7.2f}] "
                      f"w={B[2]-B[0]:5.2f} h={B[3]-B[1]:5.2f}  org=({ox:.2f},{oy:.2f})")
