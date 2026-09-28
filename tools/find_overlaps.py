# -*- coding: utf-8 -*-
r"""Detect genuinely overlapping glyphs in the built book.

Why character level: a first attempt used *span* bounding boxes and reported 211 hits
on 67 pages, but spot-checking a 100%-overlap hit against a 260-dpi render showed the
text was cleanly separated. XeLaTeX positions each glyph explicitly, and PyMuPDF's
span box is the union of advances, which inflates for CJK/Latin mixed runs — so
adjacent table cells read as "overlapping". Per-character boxes come straight from the
glyph positions and do not suffer that inflation.

A real collision means two glyphs actually printed on top of each other, so we require
a large fraction of the smaller glyph box to be covered, and we only compare glyphs
that are near each other (spatial grid) to keep it O(n).
"""
import argparse, os, sys
from collections import defaultdict

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDF = os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "overlap_report.txt")

ap = argparse.ArgumentParser()
ap.add_argument("--min-frac", type=float, default=0.45,
                help="intersection as a fraction of the smaller glyph box")
ap.add_argument("--cell", type=float, default=12.0, help="spatial grid cell, pt")
a = ap.parse_args()

# 关键：xeCJK 会把 CJK 标点压缩到半宽（标点挤压），而 PyMuPDF 按 1 em 给框，
# 于是相邻的 。，、（）： 之间必然「重叠」——首版报出的 1342 处几乎全是这个假象。
# 因此凡涉及 CJK 标点的比较一律跳过；我们只关心**文字压在文字上**。
CJK_PUNCT = set("。，、；：？！（）〔〕【】《》〈〉「」『』“”‘’—…·～［］％　"
                "．－／＋＝＜＞＃＆＊＠｜＼＾＿｛｝［］")


def inter(r1, r2):
    x0, y0 = max(r1[0], r2[0]), max(r1[1], r2[1])
    x1, y1 = min(r1[2], r2[2]), min(r1[3], r2[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def area(r):
    return max(0.0, r[2] - r[0]) * max(0.0, r[3] - r[1])


doc = pymupdf.open(PDF)
findings = []

for pno in range(1, doc.page_count + 1):
    pg = doc[pno - 1]
    glyphs = []
    for blk in pg.get_text("rawdict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            for sp in ln["spans"]:
                for ch in sp["chars"]:
                    c = ch["c"]
                    if not c.strip():
                        continue
                    b = ch["bbox"]
                    if area(b) <= 0.2:
                        continue
                    glyphs.append((b, c, round(sp["size"], 1)))

    # 空间网格：只在同一格或相邻格之间比较
    grid = defaultdict(list)
    for i, (b, c, s) in enumerate(glyphs):
        gx, gy = int(b[0] // a.cell), int(b[1] // a.cell)
        grid[(gx, gy)].append(i)

    seen = set()
    for (gx, gy), idxs in grid.items():
        near = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near.extend(grid.get((gx + dx, gy + dy), ()))
        for i in idxs:
            for j in near:
                if i >= j:
                    continue
                key = (i, j) if i < j else (j, i)
                if key in seen:
                    continue
                seen.add(key)
                b1, c1, s1 = glyphs[i]
                b2, c2, s2 = glyphs[j]
                if c1 in CJK_PUNCT or c2 in CJK_PUNCT:
                    continue
                # 同为 ASCII 标点/空白也跳过
                if not c1.isalnum() and not c2.isalnum():
                    continue
                ov = inter(b1, b2)
                if ov <= 0:
                    continue
                small = min(area(b1), area(b2))
                if small <= 0 or ov / small < a.min_frac:
                    continue
                findings.append((pno, c1, c2, ov / small, s1, s2,
                                 tuple(round(v, 1) for v in b1),
                                 tuple(round(v, 1) for v in b2)))

by_page = defaultdict(list)
for f in findings:
    by_page[f[0]].append(f)

lines = [f"file={PDF}  pages={doc.page_count}",
         f"overlapping GLYPH pairs: {len(findings)}  on {len(by_page)} pages",
         f"criterion: intersection >= {a.min_frac:.0%} of the smaller glyph box", ""]
for pno in sorted(by_page):
    lines.append(f"--- p.{pno}  ({len(by_page[pno])} pairs) ---")
    for pno_, c1, c2, frac, s1, s2, b1, b2 in sorted(by_page[pno], key=lambda x: -x[3])[:12]:
        lines.append(f"   {frac:5.0%}  {c1!r} [{s1}pt] @{b1}")
        lines.append(f"          {c2!r} [{s2}pt] @{b2}")
    lines.append("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"overlapping glyph pairs: {len(findings)} on {len(by_page)} pages -> tools/overlap_report.txt")
