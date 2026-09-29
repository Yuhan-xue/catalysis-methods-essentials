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
    # --- 第 11 章（2026-09-29 补）-------------------------------------------
    # 原缺 ch11 规则：37(实测 39) 处 `现场` -> `原位` 是人工改的，
    # 台账声称的「用 fix_terms.py 复现」当时不成立。此处补齐三片规则。
    # 实测口径（`git show HEAD:<file> | Select-String 现场`）：
    #   ch11-a 1 处 / ch11-b 2 处 / ch11-c 36 处 = 39 处；改后三片零残留。
    # 已逐条核对：这 39 处的 `现场` 全部是 in situ 旧译（含小节标题、表题、
    # 表格列名与分片头注释里的「现场谱学」），**没有** ch01-c 那种
    # 「工业装置现场」的义项，故机械替换安全（理由见 terminology_decisions.md §二.4）。
    # 注：ch11-d 与本规则无关——它是 2026-09-29 新建的分片，写稿时即用「原位」，
    # 不含 `现场`；ch11-e 尚未建立。两片规则仍列出，使规则集对分片全集闭合
    # （缺失文件按 SKIP 记入 term_fix_log.txt，不报错）。
    ("chapters/parts/ch11-a.tex", r"现场", "原位", "原位（in situ 旧译）"),
    ("chapters/parts/ch11-b.tex", r"现场", "原位", "原位（in situ 旧译）"),
    ("chapters/parts/ch11-c.tex", r"现场", "原位", "原位（in situ 旧译）"),
    ("chapters/parts/ch11-d.tex", r"现场", "原位", "原位（in situ 旧译）"),
    ("chapters/parts/ch11-e.tex", r"现场", "原位", "原位（in situ 旧译）"),
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
n_ch11 = sum(int(m.group(1)) for r in report if "ch11-" in r
             for m in [re.search(r"\((\d+) 处\)", r)] if m)
print("ch11 现场->原位 命中:", n_ch11)  # 幂等：已统一后应为 0；对 HEAD 版本为 39
