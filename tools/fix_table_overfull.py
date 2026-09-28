# -*- coding: utf-8 -*-
r"""修 3 处表格 overfull —— 按**行号**定位，避免同名模式误替换。

根因各不相同：
  ch02-a L343 / ch04-a L75  {@{}lXX@{}}：首列用 l 吃掉自然宽度，两个 X 列被挤到
                            低于最小内容宽度 → 29.8 / 36.0 pt overfull。
                            改为定宽 p{24mm}，首列可折行。
  ch08-b L309               五列定宽合计仅 80 mm（版心 165 mm），却有单元格溢出 9 pt；
                            说明最窄的 p{8mm}、p{19mm} 装不下内容。加宽即可，宽度富余。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "chapters", "parts")

JOBS = [
    ("ch02-a.tex", 343,
     r"\begin{tabularx}{\columnwidth}{@{}lXX@{}}",
     "% 原为 @{}lXX@{}：首列 l 吃掉自然宽度，两个 X 列被挤到低于最小内容宽度（29.8 pt overfull）。\n"
     "% 改为定宽 p{24mm}，首列可折行，宽度留给 X 列。\n"
     r"\begin{tabularx}{\columnwidth}{@{}>{\raggedright\arraybackslash}p{24mm}XX@{}}"),
    ("ch04-a.tex", 75,
     r"\begin{tabularx}{\columnwidth}{@{}lXX@{}}",
     "% 原为 @{}lXX@{}：首列 l 吃掉自然宽度，两个 X 列被挤到低于最小内容宽度（36.0 pt overfull）。\n"
     "% 改为定宽 p{24mm}，首列可折行，宽度留给 X 列。\n"
     r"\begin{tabularx}{\columnwidth}{@{}>{\raggedright\arraybackslash}p{24mm}XX@{}}"),
    ("ch08-b.tex", 309,
     r"\begin{tabular}{@{}p{12mm}p{8mm}p{19mm}p{22mm}p{19mm}@{}}",
     "% 原五列合计仅 80 mm（版心 165 mm），最窄列装不下内容，单元格溢出 9.05 pt。\n"
     "% 版心宽度富余，加宽各列；加宽后合计约 108 mm，含列间距仍远小于版心。\n"
     r"\begin{tabular}{@{}p{16mm}p{10mm}p{26mm}p{30mm}p{26mm}@{}}"),
]

for fname, lineno, old, new in JOBS:
    path = os.path.join(P, fname)
    lines = io.open(path, encoding="utf-8").read().split("\n")
    idx = lineno - 1
    cur = lines[idx].strip()
    if cur != old.strip():
        print(f"SKIP {fname}:{lineno} 实际内容不符：{cur[:70]}")
        continue
    lines[idx] = new
    io.open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"FIXED {fname}:{lineno}")
    print(f"      {old[:64]}")
    print(f"   -> {new.splitlines()[-1][:64]}")
