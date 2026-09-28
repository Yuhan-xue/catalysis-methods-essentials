# -*- coding: utf-8 -*-
r"""检测页面上的「黑块」——大面积实心暗区。

用户报告「公式 1-8 有黑块」。目视读渲染图在本项目已被证明不可靠（曾把有字的裁切看成空白），
所以改用程序判据：**文字是细笔画，黑块是实心区**。

判据：在 150 dpi 下，找**连续水平暗像素游程 ≥ 12 px**（约 6 pt）且**垂直方向也成片**的区域。
再要求该区域的「填充率」（暗像素数 / 包围盒面积）足够高，以排除密集但仍有空隙的文字行。
"""
import sys
import pymupdf
from PIL import Image
import numpy as np
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "blackblock_report.txt")

DPI = 150
RUN = 12          # 水平游程阈值（px）
FILL = 0.55       # 包围盒填充率阈值
MIN_AREA = 120    # 最小暗像素数

pages = [int(a) for a in sys.argv[1:]] or list(range(1, 16))

doc = pymupdf.open(PDF)
lines = [f"file={PDF}", f"criterion: horizontal dark run >= {RUN}px @ {DPI}dpi, fill >= {FILL}", ""]

for pno in pages:
    if not (1 <= pno <= doc.page_count):
        continue
    pix = doc[pno - 1].get_pixmap(dpi=DPI)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    gray = img[:, :, :3].mean(axis=2)
    dark = gray < 96

    # 用「水平长游程」定位候选行
    hits = []
    for y in range(dark.shape[0]):
        row = dark[y]
        if not row.any():
            continue
        # 找最长连续 True
        best = cur = 0
        for v in row:
            cur = cur + 1 if v else 0
            if cur > best:
                best = cur
        if best >= RUN:
            hits.append((y, best))
    if not hits:
        continue

    # 把相邻候选行聚成块
    blocks = []
    cur = [hits[0]]
    for h in hits[1:]:
        if h[0] - cur[-1][0] <= 3:
            cur.append(h)
        else:
            blocks.append(cur); cur = [h]
    blocks.append(cur)

    for blk in blocks:
        y0, y1 = blk[0][0], blk[-1][0]
        sub = dark[y0:y1 + 1]
        xs = np.where(sub.any(axis=0))[0]
        if len(xs) == 0:
            continue
        x0, x1 = int(xs[0]), int(xs[-1])
        area = int(sub.sum())
        bbox = (y1 - y0 + 1) * (x1 - x0 + 1)
        if area < MIN_AREA or bbox == 0:
            continue
        fill = area / bbox
        if fill >= FILL and (y1 - y0 + 1) >= 5:
            lines.append(f"p.{pno}: 黑块 y={y0}-{y1} x={x0}-{x1} "
                         f"尺寸={(x1-x0+1)}x{(y1-y0+1)}px  填充率={fill:.2f}  暗像素={area}")

if len(lines) <= 3:
    lines.append("未检出符合判据的黑块")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines[:12]))
