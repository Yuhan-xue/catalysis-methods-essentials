# -*- coding: utf-8 -*-
"""Split source text per chapter with dual page markers.

Output: sources/text/chNN_<vol>.txt
Each page is preceded by a marker line:
    [[<VOL> PDF p.<n> | 书内 p.<book>]]
so that chapter authors can cite precisely and cannot silently drift.

Page-mapping basis (verified by chapter page-count arithmetic, see sources/page_map.md):
  UP   : book = pdf - 19                     (constant, no missing pages)
  DOWN : piecewise, offsets by chapter start:
         ch8 pdf>=18 -> 507 ; ch9 pdf>=59 -> 508 ; ch10 pdf>=225 -> 510 ;
         ch11 pdf>=296 -> 511 ; ch12 pdf>=372 -> 513
"""
import os, re

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
TXT = os.path.join(ROOT, "sources", "text")

UP_RANGES = {1: (20, 103), 2: (104, 187), 3: (188, 237), 4: (238, 319),
             5: (320, 361), 6: (362, 431), 7: (432, 543)}
DN_RANGES = {8: (18, 58), 9: (59, 224), 10: (225, 295), 11: (296, 371), 12: (372, 435)}
DN_OFFSET = [(18, 507), (59, 508), (225, 510), (296, 511), (372, 513)]

FW = str.maketrans("０１２３４５６７８９", "0123456789")


def load(name):
    t = open(os.path.join(TXT, name), encoding="utf-8").read()
    pgs = t.split("\f")
    if pgs and pgs[-1].strip() == "":
        pgs = pgs[:-1]
    return pgs


def dn_book(pdf):
    """书内 = PDF + off（原先把符号写反过，已在 sources/qa_layout.md 记录）"""
    off = DN_OFFSET[0][1]
    for start, o in DN_OFFSET:
        if pdf >= start:
            off = o
    return pdf + off


up = load("up_layout.txt")
dn = load("down_layout.txt")

summary = []
for ch, (a, b) in sorted(UP_RANGES.items()):
    parts = [f"# 上册 第{ch}章  源文本（PDF p.{a}-{b}；书内 p.{a-19}-{b-19}）\n"
             f"# 每页以 [[UP PDF p.n | 书内 p.m]] 起头。上册为 OCR 文本层，公式与符号必然失真，\n"
             f"# 公式必须以原页面图像（tools/vpage.py）为核对依据。\n"]
    for p in range(a, min(b, len(up)) + 1):
        parts.append(f"\n[[UP PDF p.{p} | 书内 p.{p-19}]]\n")
        parts.append(up[p - 1])
    out = os.path.join(TXT, f"ch{ch:02d}_up.txt")
    open(out, "w", encoding="utf-8").write("".join(parts))
    summary.append((f"ch{ch:02d}_up.txt", a, b, len("".join(parts))))

for ch, (a, b) in sorted(DN_RANGES.items()):
    parts = [f"# 下册 第{ch}章  源文本（PDF p.{a}-{b}；书内 p.{dn_book(a)}-{dn_book(b)}）\n"
             f"# 每页以 [[DOWN PDF p.n | 书内 p.m]] 起头。下册 OCR 质量较好，仍须以页面图像核对公式。\n"]
    for p in range(a, min(b, len(dn)) + 1):
        parts.append(f"\n[[DOWN PDF p.{p} | 书内 p.{dn_book(p)}]]\n")
        parts.append(dn[p - 1])
    out = os.path.join(TXT, f"ch{ch:02d}_down.txt")
    open(out, "w", encoding="utf-8").write("".join(parts))
    summary.append((f"ch{ch:02d}_down.txt", a, b, len("".join(parts))))

lines = [f"{n:<18} PDF {a:>4}-{b:<4}  {sz/1024:8.1f} KB" for n, a, b, sz in summary]
open(os.path.join(ROOT, "tools/split_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
