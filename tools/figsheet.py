# -*- coding: utf-8 -*-
r"""Contact sheets of the book's figures, for visual overlap inspection.

Rendering and reading 26 figures one at a time is far too expensive. This crops the
region ABOVE each figure caption (located by searching the page text for "图 N-M")
and tiles several crops into a single sheet, so one image read covers many figures.

Usage:
    python tools/figsheet.py out.png 16 19 33 59 63 99     # 6 pages -> one 3x2 sheet
    python tools/figsheet.py out.png 16 --dpi 300 --cols 1 # single figure, large
"""
import argparse, os, sys

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf
from PIL import Image

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDF = os.path.join(ROOT, "build", "main.pdf")

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("pages", nargs="+", type=int)
ap.add_argument("--dpi", type=int, default=150)
ap.add_argument("--cols", type=int, default=3)
a = ap.parse_args()

doc = pymupdf.open(PDF)
tiles = []

for pno in a.pages:
    pg = doc[pno - 1]
    r = pg.rect
    # 用矢量图形（TikZ/PGFPlots 与表格线）的实际范围定位图区，再向四周留边。
    # 早先按「图 N-M」定位图题不可靠，按整页裁又浪费分辨率。
    boxes = []
    for d in pg.get_drawings():
        b = d["rect"]
        if b.width > 2 and b.height > 2:          # 忽略极小的记号
            boxes.append(b)
    if boxes:
        x0 = min(b.x0 for b in boxes); x1 = max(b.x1 for b in boxes)
        y0 = min(b.y0 for b in boxes); y1 = max(b.y1 for b in boxes)
    else:
        x0, y0, x1, y1 = r.x0, r.y0, r.x1, r.y1
    pad = 14
    clip = pymupdf.Rect(max(r.x0, x0 - pad), max(r.y0, y0 - pad),
                        min(r.x1, x1 + pad), min(r.y1, y1 + pad + 34))  # +34pt 含图题
    pix = pg.get_pixmap(clip=clip, dpi=a.dpi)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    tiles.append((pno, img))
    print(f"  p.{pno}: {pix.width}x{pix.height}  drawing-extent=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f})")

# 等宽缩放后拼接
W = max(t[1].width for t in tiles)
scaled = []
for pno, img in tiles:
    if img.width != W:
        img = img.resize((W, int(img.height * W / img.width)), Image.LANCZOS)
    scaled.append((pno, img))

cols = a.cols
rows = (len(scaled) + cols - 1) // cols
row_h = [max(scaled[i * cols + j][1].height for j in range(cols)
             if i * cols + j < len(scaled)) for i in range(rows)]
sheet = Image.new("RGB", (W * cols, sum(row_h)), "white")
y = 0
for i in range(rows):
    x = 0
    for j in range(cols):
        k = i * cols + j
        if k >= len(scaled):
            break
        sheet.paste(scaled[k][1], (x, y))
        x += W
    y += row_h[i]

out = os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out
os.makedirs(os.path.dirname(out), exist_ok=True)
sheet.save(out)
print(f"sheet {sheet.width}x{sheet.height} -> {out}  (pages {a.pages})")
