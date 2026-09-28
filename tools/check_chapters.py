# -*- coding: utf-8 -*-
r"""Guard the chapter-numbering invariant.

Chapter numbers in this book come from assembly ORDER, not from the file name:
main.tex inputs chapters/ch01.tex .. ch12.tex in sequence, and each chapter's
`\chapterstart` does \refstepcounter{section}. So if any chapter is missing,
every later chapter silently shifts down by one and all \chapref cross-references
become WRONG while still resolving (no undefined-reference warning to catch it).

That is exactly the kind of failure that looks fine in the PDF. This script makes
it loud.
"""
import os, re, sys

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PARTS = os.path.join(ROOT, "chapters", "parts")

EXPECT = {
    1: "物理吸附和催化剂的宏观物性测定", 2: "透射电子显微镜", 3: "热分析方法",
    4: "多晶X射线衍射分析", 5: "化学吸附和程序升温技术", 6: "催化过程的拉曼光谱方法",
    7: "原位红外光谱方法", 8: "核磁共振方法", 9: "表面分析技术基础",
    10: "多相催化反应动力学", 11: "电化学催化研究方法",
    12: "扫描探针显微镜与纳米光谱技术",
}

rows = []
missing = []
for n in range(1, 13):
    nn = f"{n:02d}"
    a = os.path.join(PARTS, f"ch{nn}-a.tex")
    present = os.path.exists(a)
    has_head = False
    title = ""
    if present:
        t = open(a, encoding="utf-8").read()
        m = re.search(r"\\chapterstart\{([^}]*)\}", t)
        has_head = bool(m)
        title = m.group(1) if m else ""
    other = sorted(f for f in os.listdir(PARTS)
                   if f.startswith(f"ch{nn}-") and f.endswith(".tex"))
    status = "OK"
    if not present:
        status = "MISSING a-part"
        missing.append(n)
    elif not has_head:
        status = "a-part lacks \\chapterstart"
        missing.append(n)
    rows.append((n, EXPECT[n], len(other), title, status))

print(f"{'ch':>3}  {'expected title':<24} {'parts':>5}  {'title in a-part':<24} status")
for n, exp, nparts, title, status in rows:
    print(f"{n:>3}  {exp:<24} {nparts:>5}  {title:<24} {status}")

print()
if missing:
    print(f"!! {len(missing)} chapter(s) missing: {missing}")
    print("!! Chapter numbers are assigned by ASSEMBLY ORDER. While any chapter is missing,")
    print("!! every later chapter's number is wrong and all \\chapref cross-references are")
    print("!! silently incorrect. Do NOT treat the current PDF as final.")
    sys.exit(1)
print("all 12 chapters present with a valid \\chapterstart -> numbering invariant holds")
sys.exit(0)
