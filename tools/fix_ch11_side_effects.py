# -*- coding: utf-8 -*-
r"""修三处由「调序」与「注释过度承诺」引入的副作用（Lead 自己造成的）。

1. ch11-a.tex:562 —— 本稿图 11-2（fig:series）自己的 \figsrc 里写「与图 11-2 改绘」，
   调序外加「原书」口径后，裸写会被读成**自指**。属于 4 处撞本稿图号的图号之一。
2. ch11-c.tex:5 —— 调序后前一节的实际编号是 \subsection（§11.5），
   而原文写「前一节（§11.5.1…）」，把层级指高了一级。
3. chapters/ch11.tex —— 我写的注释称「指代方向与编号顺序同时恢复正确」，只对了一半：
   顺序恢复了，但编号与原书不再一一对应。
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 1) ch11-a 的 4 处撞号图号 ----
p = os.path.join(ROOT, "chapters", "parts", "ch11-a.tex")
s = io.open(p, encoding="utf-8").read()
# 只处理图号，不动式号；这 4 处落在本稿图号空间 11-1..11-5 内
n_fig = 0
for num in ("11-2", "11-3", "11-4", "11-5"):
    # 把「图 11-N」且尚未带「原书/源书」前缀的，改为「原书图 11-N」
    pat = re.compile(r"(?<!原书)(?<!源书)(?<!书中)图\s*" + re.escape(num) + r"(?![\d\-])")
    s, k = pat.subn("原书图 " + num, s)
    n_fig += k
io.open(p, "w", encoding="utf-8").write(s)
print(f"1) ch11-a 图号加「原书」: {n_fig} 处")

# ---- 2) ch11-c:5 的节号层级 ----
p = os.path.join(ROOT, "chapters", "parts", "ch11-c.tex")
s = io.open(p, encoding="utf-8").read()
before = s
s = s.replace("前一节（§11.5.1", "前一节（§11.5 阻抗谱基本原理")
if s == before:
    # 兜底：换一种写法
    s = re.sub(r"前一节（\s*§\s*11\.5\.1", "前一节（§11.5 阻抗谱基本原理", s)
io.open(p, "w", encoding="utf-8").write(s)
print(f"2) ch11-c 节号层级: {'已改' if s != before else '未匹配到（需人工看）'}")

# ---- 3) ch11.tex 的注释过度承诺 ----
p = os.path.join(ROOT, "chapters", "ch11.tex")
s = io.open(p, encoding="utf-8").read()
old = "指代方向与编号顺序同时恢复正确"
new = ("指代方向与前后顺序恢复正确。**注意：编号与原书不再一一对应**——"
       "成书为 §11.5 阻抗谱基本原理、§11.6 电化学阻抗谱（原书 §11.5，仅其应用部分）、"
       "§11.7 电化学原位谱学（原书 §11.6）。要完全对齐须把分片 d 的标题降为 "
       "\\subsubsection 并入分片 c 的 §11.5。")
if old in s:
    s = s.replace(old, new)
    io.open(p, "w", encoding="utf-8").write(s)
    print("3) ch11.tex 注释: 已改为准确表述")
else:
    print("3) ch11.tex 注释: 未匹配到原句（可能已被改过）")
