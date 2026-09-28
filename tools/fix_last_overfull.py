# -*- coding: utf-8 -*-
r"""修最后 2 处 overfull（ch02-a 表、ch06-a 图内注释节点）。按行号定位。"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "chapters", "parts")

JOBS = [
    # ch02-a：表格最小宽度超过版心。改用显式 p{} 列，总宽约 148 mm，
    # 加两组列间距（4×\tabcolsep≈8.4 mm）后约 156 mm < 版心 165 mm。
    ("ch02-a.tex", 343,
     r"\begin{tabularx}{\columnwidth}{@{}>{\raggedright\arraybackslash}p{24mm}XX@{}}",
     "% tabularx 无法把 X 列压到其最小内容宽度以下；实测该表最小宽度超版心 29.8 pt。\n"
     "% 改为显式 p{} 列：24+36+88 = 148 mm，加列间距约 156 mm，小于版心 165 mm。\n"
     r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{24mm}"
     r">{\raggedright\arraybackslash}p{36mm}"
     r">{\raggedright\arraybackslash}p{88mm}@{}}"),
    ("ch02-a.tex", 356,
     r"\end{tabularx}}",
     r"\end{tabular}}"),
    # ch06-a：图内注释节点原按 88 mm 栏宽设计（text width=74 mm），
    # 单栏后可用 165 mm，但节点宽度没跟着放大，最长说明行撑出 36 pt。
    ("ch06-a.tex", 234,
     r"        text width=74mm, inner sep=0pt] at (5,-11)",
     "        text width=118mm, inner sep=0pt] at (5,-11)"),
]

for fname, lineno, old, new in JOBS:
    path = os.path.join(P, fname)
    lines = io.open(path, encoding="utf-8").read().split("\n")
    idx = lineno - 1
    cur = lines[idx].strip()
    if cur != old.strip():
        print(f"SKIP {fname}:{lineno}\n     期望: {old.strip()[:70]}\n     实际: {cur[:70]}")
        continue
    lines[idx] = new
    io.open(path, "w", encoding="utf-8").write("\n".join(lines))
    print(f"FIXED {fname}:{lineno}")
