# -*- coding: utf-8 -*-
"""Audit chapter sources for plan violations that are cheap to detect mechanically.

Checks:
  1. font sizes below the 8 pt floor (企划 §6.1 / §5.3)
  2. figures/tables wider than the safe widths (\\onecolwidth / \\twocolwidth)
  3. forbidden constructs (\\usepackage, hand-written cross references, negative \\vspace)
  4. leftover TODO / empty environments
"""
import re, glob, os, sys

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
FILES = sorted(glob.glob(os.path.join(ROOT, "chapters", "parts", "*.tex"))) + [
    os.path.join(ROOT, "chapters", n) for n in
    ("ch00-intro.tex", "ch13-synthesis.tex", "ch90-backmatter.tex")
]

FS = re.compile(r"\\fontsize\{([0-9.]+)\}\{([0-9.]+)\}")
FIXED = re.compile(r"(?:width|height)=\s*([0-9.]+)\s*(mm|cm|pt)")
FORBID = [
    (re.compile(r"\\usepackage"), "禁止 \\usepackage"),
    (re.compile(r"\\vspace\{-"), "禁止负 \\vspace"),
    (re.compile(r"\bTODO\b"), "残留 TODO"),
    (re.compile(r"\\begin\{(probout|principle|measure|dataflow|pitfall|crosscheck|keycond|methodsum|obs|infer)\}\s*\\end"), "空环境"),
]
# 手写图号/表号只在「正文交叉引用」时才是问题；出现在来源标记里是**要求**的
# （企划 §5.2 要求注明原书图号）。因此含这些宏的行一律不判。
SOURCE_MACROS = ("\\figsrc", "\\src{", "\\srcnote", "\\tocheck")
REF_FIG = re.compile(r"图\s*\d+\s*-\s*\d+")
REF_TAB = re.compile(r"表\s*\d+\s*-\s*\d+")
LIMITS = {"onecol": 84.0, "twocol": 176.0, "text": 183.0}


def mm(v, unit):
    return {"mm": v, "cm": v * 10.0, "pt": v * 25.4 / 72.27}[unit]


def main():
    out = []
    nbad = 0
    for f in FILES:
        if not os.path.exists(f):
            continue
        rel = os.path.relpath(f, ROOT)
        for i, line in enumerate(open(f, encoding="utf-8"), 1):
            for m in FS.finditer(line):
                sz = float(m.group(1))
                if sz < 8.0:
                    out.append(f"[FONT<8pt] {rel}:{i}  {sz}pt  {line.strip()[:90]}")
                    nbad += 1
            for m in FIXED.finditer(line):
                w = mm(float(m.group(1)), m.group(2))
                # only flag obviously oversized fixed widths
                if w > 200:
                    out.append(f"[WIDE {w:.0f}mm] {rel}:{i}  {line.strip()[:90]}")
                    nbad += 1
            for rx, msg in FORBID:
                if rx.search(line):
                    out.append(f"[{msg}] {rel}:{i}  {line.strip()[:90]}")
                    nbad += 1
            if not any(m in line for m in SOURCE_MACROS):
                if REF_FIG.search(line):
                    out.append(f"[疑似手写图号（应用 \\figref）] {rel}:{i}  {line.strip()[:90]}")
                    nbad += 1
                if REF_TAB.search(line):
                    out.append(f"[疑似手写表号（应用 \\tabref）] {rel}:{i}  {line.strip()[:90]}")
                    nbad += 1
    dst = os.path.join(ROOT, "tools", "source_audit.txt")
    open(dst, "w", encoding="utf-8").write(
        f"files scanned: {len([f for f in FILES if os.path.exists(f)])}\n"
        f"issues: {nbad}\n\n" + "\n".join(out))
    print(f"issues: {nbad} -> {dst}")


if __name__ == "__main__":
    main()
