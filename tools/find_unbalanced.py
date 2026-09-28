# -*- coding: utf-8 -*-
"""Find the region where brace nesting fails to return to zero.

TeX strips % comments (and the newline) before brace matching, so we must do the
same: a } sitting on a commented line is invisible to TeX.
"""
import sys, io, re

path = sys.argv[1]
src = io.open(path, encoding="utf-8").read()

depth = 0
line = 1
col = 0
last_zero = (1, 0)
opens = []          # stack of (line, col)
i = 0
n = len(src)
while i < n:
    c = src[i]
    if c == "\n":
        line += 1
        col = 0
        i += 1
        continue
    if c == "\\":
        # escaped char: skip it (handles \{ \} \%)
        nxt = src[i + 1] if i + 1 < n else ""
        if nxt == "\n":
            line += 1
            col = 0
        i += 2
        col += 2
        continue
    if c == "%":
        # comment: skip to end of line
        while i < n and src[i] != "\n":
            i += 1
        continue
    if c == "{":
        depth += 1
        opens.append((line, col))
    elif c == "}":
        depth -= 1
        if opens:
            opens.pop()
        if depth == 0:
            last_zero = (line, col)
        if depth < 0:
            print(f"UNBALANCED: extra }} at line {line} col {col}")
            break
    i += 1
    col += 1

print(f"final depth = {depth}")
if depth > 0:
    print(f"last point where depth returned to 0: line {last_zero[0]}")
    print(f"{depth} unclosed '{{' remain; innermost openings (line, col):")
    for ln, cl in opens[-12:]:
        print(f"   line {ln}, col {cl}")
    print("\n--- text around the first still-open brace ---")
    ln = opens[0][0] if opens else 1
    lines = src.splitlines()
    for k in range(max(0, ln - 4), min(len(lines), ln + 8)):
        print(f"{k+1:>5}: {lines[k]}")
