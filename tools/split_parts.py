# -*- coding: utf-8 -*-
"""Emit per-part source slices: sources/parts/chNN-x.txt

Each slice carries dual page markers so chapter authors can cite precisely
and cannot silently drift.  Mapping comes from tools/pagemap_lib.py
(running-head table for DOWN; anchor-derived table for UP).
"""
import os, sys

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import pagemap_lib as pm

TXT = os.path.join(ROOT, "sources", "text")
OUT = os.path.join(ROOT, "sources", "parts")
os.makedirs(OUT, exist_ok=True)

# (chapter, vol, [(tag, book_start, book_end), ...])
PLAN = {
    1:  ("up",   [("a", 1, 42), ("b", 43, 60), ("c", 61, 84)]),
    2:  ("up",   [("a", 85, 109), ("b", 110, 146), ("c", 147, 168)]),
    3:  ("up",   [("a", 169, 180), ("b", 181, 218)]),
    4:  ("up",   [("a", 219, 243), ("b", 244, 269), ("c", 270, 300)]),
    5:  ("up",   [("a", 301, 319), ("b", 320, 342)]),
    6:  ("up",   [("a", 343, 372), ("b", 373, 412)]),
    7:  ("up",   [("a", 413, 447), ("b", 448, 488), ("c", 489, 524)]),
    8:  ("down", [("a", 525, 543), ("b", 544, 554), ("c", 555, 566)]),
    9:  ("down", [("a", 567, 614), ("b", 615, 661), ("c", 662, 693), ("d", 694, 734)]),
    10: ("down", [("a", 735, 768), ("b", 769, 792), ("c", 793, 806)]),
    11: ("down", [("a", 807, 832), ("b", 833, 865), ("c", 866, 884)]),
    12: ("down", [("a", 885, 912), ("b", 913, 925), ("c", 926, 948)]),
}

DN_NOTE = ("# 【下册页码说明】有 7 个印刷页未出现在 PDF 中（526, 568, 734, 736, 808, 884, 886），\n"
           "# 偏移量因此在下列 PDF 页处跳变：18, 19, 60, 225, 226, 297, 372, 373。\n"
           "# 所以“书内页码出现跳号”是原书扫描缺失，不是你的错误。\n"
           "# 一律以本文件给出的 [[DOWN PDF p.n | 书内 p.m]] 标记为准，不要自己套偏移量。\n")

UP_NOTE = ("# 【上册页码说明】book = PDF - 19，全书恒定（已在 150 个锚点上核验）。\n"
           "# 上册是 OCR 文本层，公式、上下标、希腊字母必然失真。\n"
           "# 公式必须以原页面图像为核对依据：\n"
           "#   python tools/vpage.py up <pdf_page> sources/pages/x.png --dpi 190\n")


def load(name):
    t = open(os.path.join(TXT, name), encoding="utf-8").read()
    pgs = t.split("\f")
    if pgs and pgs[-1].strip() == "":
        pgs = pgs[:-1]
    return pgs


ARR = {"up": load("up_layout.txt"), "down": load("down_layout.txt")}

rows = []
for ch, (vol, parts) in sorted(PLAN.items()):
    for tag, b0, b1 in parts:
        p0, p1 = pm.pdf(vol, b0), pm.pdf(vol, b1)
        arr = ARR[vol]
        head = (f"# {'上册' if vol=='up' else '下册'} 第{ch}章 分片 {tag}  "
                f"书内 p.{b0}-{b1} / PDF p.{p0}-{p1}\n" + (UP_NOTE if vol == "up" else DN_NOTE))
        buf = [head]
        for p in range(p0, min(p1, len(arr)) + 1):
            b = pm.book(vol, p)
            buf.append(f"\n[[{vol.upper()} PDF p.{p} | 书内 p.{b}]]\n")
            buf.append(arr[p - 1])
        name = f"ch{ch:02d}-{tag}.txt"
        open(os.path.join(OUT, name), "w", encoding="utf-8").write("".join(buf))
        rows.append((name, b0, b1, p0, p1, len("".join(buf))))

lines = [f"{n:<14} book {b0:>4}-{b1:<4} PDF {p0:>4}-{p1:<4}  {s/1024:7.1f} KB"
         for n, b0, b1, p0, p1, s in rows]
open(os.path.join(ROOT, "tools/parts_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines))
print(f"\n{len(rows)} part slices -> sources/parts/")
