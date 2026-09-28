# -*- coding: utf-8 -*-
r"""Stage-4 terminology unification — apply the canonical form per group.

Only the clear-cut cases are applied here. Deliberate NON-changes (documented in
sources/terminology_decisions.md):
  * 转换数 (TON) vs 转换频率 (TOF)  — different quantities, both correct.
  * 透射电子显微镜 / 透射电镜       — full name then abbreviation is correct style.
  * 标定 vs 校准                    — both standard; kept where an ISO/standard title uses 校准.

Replacements use a negative lookahead so that e.g. 比表面 does not match inside 比表面积.
"""
import re, io, os, glob

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
RULES = [
    # (file glob, regex, replacement, canonical form)
    ("chapters/parts/ch04-a.tex", r"X射线", "X 射线", "X 射线（与 CJK 间加空格，与全书一致）"),
    ("chapters/parts/ch10-a.tex", r"比表面(?!积)", "比表面积", "比表面积"),
    ("chapters/parts/ch01-b.tex", r"孔径分布", "孔尺寸分布", "孔尺寸分布（与本章节标题一致）"),
    ("chapters/parts/ch01-b.tex", r"孔体积", "孔容", "孔容"),
    ("chapters/parts/ch05-a.tex", r"活性中心", "活性位", "活性位"),
    ("chapters/ch00-intro.tex", r"现场", "原位", "原位"),
    ("chapters/ch13-synthesis.tex", r"现场", "原位", "原位"),
    ("chapters/ch90-backmatter.tex", r"现场", "原位", "原位"),
]

report = []
for pattern, rx, repl, canon in RULES:
    path = os.path.join(ROOT, pattern.replace("/", os.sep))
    if not os.path.exists(path):
        report.append(f"SKIP (missing) {pattern}")
        continue
    raw = io.open(path, encoding="utf-8").read()
    new, n = re.subn(rx, repl, raw)
    if n:
        io.open(path, "w", encoding="utf-8").write(new)
    report.append(f"{'FIXED' if n else 'no-op'}  {pattern}  {rx} -> {repl}  ({n} 处)   [{canon}]")

io.open(os.path.join(ROOT, "tools", "term_fix_log.txt"), "w", encoding="utf-8").write("\n".join(report))
print("rules:", len(RULES), "files touched:", sum(1 for r in report if r.startswith("FIXED")))
