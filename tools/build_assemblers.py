# -*- coding: utf-8 -*-
"""Build the parts-based assembly layer.

  chapters/chNN.tex        assembles parts a..e (missing parts are skipped)
  chapters/parts/chNN-x.tex   one independently written slice

Also moves the existing monolithic ch01 into parts/ch01-a.tex (once).
"""
import os, shutil

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
CH = os.path.join(ROOT, "chapters")
PARTS = os.path.join(CH, "parts")
os.makedirs(PARTS, exist_ok=True)

TITLES = {
    1: "物理吸附和催化剂的宏观物性测定",
    2: "透射电子显微镜",
    3: "热分析方法",
    4: "多晶X射线衍射分析",
    5: "化学吸附和程序升温技术",
    6: "催化过程的拉曼光谱方法",
    7: "原位红外光谱方法",
    8: "核磁共振方法",
    9: "表面分析技术基础",
    10: "多相催化反应动力学",
    11: "电化学催化研究方法",
    12: "扫描探针显微镜与纳米光谱技术",
}

# 1) 把现有 ch01.tex 迁移为 part a（只做一次）
src01 = os.path.join(CH, "ch01.tex")
dst01a = os.path.join(PARTS, "ch01-a.tex")
if os.path.exists(src01) and not os.path.exists(dst01a):
    txt = open(src01, encoding="utf-8").read()
    if "\\chapterstart" in txt:          # 确认是内容文件，不是装配层
        open(dst01a, "w", encoding="utf-8").write(txt)
        print("moved ch01.tex -> parts/ch01-a.tex")

# 2) 生成装配层
for n in range(1, 13):
    nn = f"{n:02d}"
    lines = [f"% chapters/ch{nn}.tex —— 第 {n} 章 {TITLES[n]}",
             "% 装配层：只负责按顺序引入各分片。分片缺失时跳过，便于增量成书。",
             f"% 分片文件：chapters/parts/ch{nn}-{{a..e}}.tex", ""]
    for tag in "abcde":
        lines.append(
            f"\\IfFileExists{{chapters/parts/ch{nn}-{tag}.tex}}"
            f"{{\\input{{chapters/parts/ch{nn}-{tag}}}}}{{}}")
    open(os.path.join(CH, f"ch{nn}.tex"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

print("assemblers written: chapters/ch01.tex .. ch12.tex")
print("parts dir:", PARTS)
print("existing parts:", sorted(os.listdir(PARTS)))
