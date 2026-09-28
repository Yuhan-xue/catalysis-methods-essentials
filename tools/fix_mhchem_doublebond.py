# -*- coding: utf-8 -*-
r"""修 mhchem 的双键缺陷：\ce{Mo=O} 在本项目渲染成两个 en-dash（U+2013），不是等号。

由 ch06-c 作者实测确证：`\ce{Mo=O}` → `––`；`\ce{Mo\bond{2}O}` → `––`；
只有 `\ce{Mo{=}O}` 给出真正的 U+003D。原因应是 mhchem 画双键所用的字形在本项目的
字体组合下缺失，回退成了破折号——**而且是静默的**，编译不报错、也不计入 Missing character。

做法：只把 `\ce{...}` **内部未被花括号包裹的 `=`** 改成 `{=}`。
已经是 `{=}` 的不动（避免变成 `{{=}}`）。
"""
import io, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "chapters")

# 匹配 \ce{...}，允许内部有一层花括号
CE = re.compile(r'\\ce\{((?:[^{}]|\{[^{}]*\})*)\}')


def fix_arg(arg):
    out = []
    i = 0
    changed = 0
    while i < len(arg):
        c = arg[i]
        if c == '{':
            # 跳过整个 {..} 组，组内不动
            j = arg.index('}', i)
            out.append(arg[i:j + 1])
            i = j + 1
        elif c == '=':
            # 箭头 <=> / <-> 里的等号不能动
            prev = out[-1] if out else ''
            nxt = arg[i + 1] if i + 1 < len(arg) else ''
            if prev == '<' or nxt == '>':
                out.append(c)
            else:
                out.append('{=}')
                changed += 1
            i += 1
        else:
            out.append(c)
            i += 1
    return ''.join(out), changed


total = 0
touched = []
files = sorted(glob.glob(os.path.join(CH, "*.tex")) +
               glob.glob(os.path.join(CH, "parts", "*.tex")))
for p in files:
    txt = io.open(p, encoding="utf-8").read()
    n = [0]

    def repl(m):
        new, c = fix_arg(m.group(1))
        n[0] += c
        return '\\ce{' + new + '}'

    new = CE.sub(repl, txt)
    if n[0]:
        io.open(p, "w", encoding="utf-8").write(new)
        touched.append(f"  {os.path.relpath(p, ROOT)}: {n[0]} 处")
        total += n[0]

print(f"共修 {total} 处裸等号（改为 {{=}}）：")
print("\n".join(touched) if touched else "  （无）")

# 复核：是否还有裸 =
left = []
for p in files:
    txt = io.open(p, encoding="utf-8").read()
    for m in CE.finditer(txt):
        if '=' in m.group(1) and not re.search(r'\{=\}', m.group(1)):
            left.append(f"  {os.path.relpath(p, ROOT)}: {m.group(0)[:40]}")
print("\n仍含裸等号：")
print("\n".join(left) if left else "  （无）")
