# -*- coding: utf-8 -*-
r"""Single-column migration: `figure*`/`table*` are illegal outside twocolumn.

LaTeX's starred float environments only exist in two-column mode; after switching the
book to single column they must become the unstarred forms, otherwise:
    ! LaTeX Error: \begin{table} on input line 305 ended by \end{table*}.
Also rewrites the float-placement hint, since wide floats no longer need `t` only.
"""
import io, os, glob, re

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, "chapters", "**", "*.tex"), recursive=True))

log = []
total = 0
for p in FILES:
    raw = io.open(p, encoding="utf-8").read()
    new = raw.replace(r"\begin{figure*}", r"\begin{figure}")
    new = new.replace(r"\end{figure*}", r"\end{figure}")
    new = new.replace(r"\begin{table*}", r"\begin{table}")
    new = new.replace(r"\end{table*}", r"\end{table}")
    if new != raw:
        n = len(re.findall(r"\\begin\{(figure|table)\*\}", raw))
        io.open(p, "w", encoding="utf-8").write(new)
        total += n
        log.append(f"{os.path.relpath(p, ROOT).replace(chr(92),'/')}: {n} 处 starred float -> unstarred")

io.open(os.path.join(ROOT, "tools", "unstar_log.txt"), "w", encoding="utf-8").write("\n".join(log))
print(f"files changed: {len(log)}   starred floats converted: {total}")
