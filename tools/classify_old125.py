# -*- coding: utf-8 -*-
r"""把**旧判据**的 125 处字符级命中按类别归并（供交付说明用）。

数据来源：tools/_overlap_all_prev.txt（旧判据在修复前的输出，已存档）。
分类规则（只看字符本身，不依赖坐标）：
  1 CJK 标点邻居      —— 任一方是 CJK 标点/全角括号（字身盒全宽、推进半宽）
  2 定界符零件拼接    —— 任一方是 TeX 拼接大括号用的零件 U+239B—23AD / 23B0—B7
  3 数学箭头拼装      —— 双方都在 {− = → ← ↔ ⇀ ↽ ↼ ⇌}（amsmath/xymtex 用零件拼长箭头）
  4 数学上下标/极限   —— 涉及 ∫ √ ∑，或一方是纯数字且另一方是斜体字母
  5 连字展开          —— 同一字形被 ToUnicode 展开（旧判据里表现为同串的 ff/fi/fl）
  6 其余（须逐条核）
"""
import io
import os
import re
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "_overlap_all_prev.txt")
OUT = os.path.join(ROOT, "tools", "_class125.txt")

CJK_PUNCT = set("，。、；：？！（）【】《》〈〉「」『』〔〕—…·　"
                "“”‘’％＋－＝／＼｜［］")
STRETCHY = set(chr(c) for c in list(range(0x239B, 0x23AE)) + list(range(0x23B0, 0x23B8)))
ARROW = set("−=→←↔⇀↽↼⇌⇋")

raw = io.open(SRC, encoding="utf-8").read()
pat = re.compile(r"===== p\.(\d+) =====|\[字符\] 字符 '(.)' × '(.)'  重叠 ([\d.]+)x([\d.]+) pt")
page = None
cls = collections.Counter()
detail = collections.defaultdict(list)
for m in pat.finditer(raw):
    if m.group(1):
        page = int(m.group(1))
        continue
    a, b, ox, oy = m.group(2), m.group(3), float(m.group(4)), float(m.group(5))
    if a in CJK_PUNCT or b in CJK_PUNCT:
        k = "1 CJK 标点/全角括号邻居"
    elif a in STRETCHY or b in STRETCHY:
        k = "2 定界符零件拼接"
    elif a in ARROW and b in ARROW:
        k = "3 数学箭头零件拼装"
    elif (a in "∫√∑" or b in "∫√∑" or
          (a.isdigit() and b.isalpha()) or (b.isdigit() and a.isalpha()) or
          a.isdigit() or b.isdigit()):
        k = "4 数学上下标/积分极限"
    elif a == b:
        k = "5 连字展开（同一字形）"
    else:
        k = "6 其余（须逐条核）"
    cls[k] += 1
    detail[k].append((page, a, b, ox, oy))

total = sum(cls.values())
out = ["旧判据 125 处字符级命中的归并（源：_overlap_all_prev.txt，共 %d 处）" % total, ""]
for k in sorted(cls):
    out.append("  %-28s %d" % (k, cls[k]))
out.append("")
for k in sorted(detail):
    out.append("## %s" % k)
    for page, a, b, ox, oy in detail[k]:
        out.append("   p.%-4d '%s' × '%s'  %.1fx%.1f pt" % (page, a, b, ox, oy))
txt = "\n".join(out)
print("\n".join(out[:12]))
with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write(txt)
