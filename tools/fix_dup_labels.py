# -*- coding: utf-8 -*-
r"""G-01: 消除重复标签，避免跨章误引用。

问题（评审已证实）：源码里有 4 组同名标签，LaTeX 只保留最后一个定义，
于是引用会静默跳到**别的章**：
    eq:bragg      ch02-a / ch04-a / ch09-a   → 全部解析到 9-5
    eq:iss        ch09-c / ch11-a            → 解析到 11-27
    eq:langmuir   ch01-a / ch10-a            → 解析到 10-16
    tab:extinction ch02-a / ch04-a           → 解析到 4-3
重复标签 LaTeX 只给 warning，编译不报错，所以一直没被发现。

做法：**按文件**重命名。每个分片对同名标签的引用几乎都是引用自己那一份，
因此把标签和**同文件内**的引用一起改成 <原名>-chNN；跨文件的引用单独报告，人工判断。
"""
import io, os, re, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "chapters")

LABEL = re.compile(r"\\label\{([^}]+)\}")
REF = re.compile(r"\\(?:eqref|ref|pageref|autoref|cref|Cref)\{([^}]+)\}")


def chap_of(path):
    b = os.path.basename(path)
    m = re.match(r"ch(\d{2})", b)
    return m.group(1) if m else "00"


files = sorted(glob.glob(os.path.join(CH, "**", "*.tex"), recursive=True))

# 1) 找出重复标签
owner = collections.defaultdict(list)
for p in files:
    txt = io.open(p, encoding="utf-8").read()
    for m in LABEL.finditer(txt):
        owner[m.group(1)].append(p)

dups = {k: v for k, v in owner.items() if len(v) > 1}
print(f"重复标签 {len(dups)} 组")

# 2) 逐文件重命名
renamed = []
for name, paths in dups.items():
    for p in paths:
        nn = chap_of(p)
        new = f"{name}-ch{nn}"
        txt = io.open(p, encoding="utf-8").read()
        # 标签本身
        txt2 = txt.replace(f"\\label{{{name}}}", f"\\label{{{new}}}")
        # 同文件内的引用（含语义宏 \equref/\figref/\tabref/\chapref 都走 \ref）
        txt2 = re.sub(r"(\\[A-Za-z]*ref\*?\{)" + re.escape(name) + r"(\})",
                      lambda m: m.group(1) + new + m.group(2), txt2)
        if txt2 != txt:
            io.open(p, "w", encoding="utf-8").write(txt2)
            n_label = txt.count(f"\\label{{{name}}}")
            n_ref = len(re.findall(r"\\[A-Za-z]*ref\*?\{" + re.escape(name) + r"\}", txt))
            renamed.append(f"  {os.path.relpath(p, ROOT)}: {name} -> {new}  (标签 {n_label}，同文件引用 {n_ref})")

print(f"改了 {len(renamed)} 个文件：")
print("\n".join(renamed))

# 3) 检查是否还有跨文件引用残留旧名
print("\n残留旧名引用（需人工判断指向哪一章）：")
left = 0
for p in files:
    txt = io.open(p, encoding="utf-8").read()
    for m in REF.finditer(txt):
        base = m.group(1)
        # 去掉可能的 -chNN 后缀看是否命中旧名
        if base in dups:
            print(f"  {os.path.relpath(p, ROOT)}: \\ref{{{base}}}")
            left += 1
if not left:
    print("  （无）")
