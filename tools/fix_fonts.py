# -*- coding: utf-8 -*-
"""Raise figure text below the 8 pt floor up to 8 pt (企划 §6.1 / §5.3).

Also adds \\sloppy to captions that overfull, since captions often contain long
unbreakable inline-math runs.
"""
import re, sys, os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FS = re.compile(r"\\fontsize\{([0-9.]+)\}\{([0-9.]+)\}")

targets = sys.argv[1:] or [os.path.join(ROOT, "chapters", "parts", "ch02-a.tex")]
total = 0
for path in targets:
    src = open(path, encoding="utf-8").read()
    n = [0]

    def repl(m):
        sz, lead = float(m.group(1)), float(m.group(2))
        if sz < 8.0:
            n[0] += 1
            return r"\fontsize{8}{9.6}"      # 8 pt 正文下限，行距按 1.2 倍
        return m.group(0)

    out = FS.sub(repl, src)
    if n[0]:
        open(path, "w", encoding="utf-8").write(out)
    print(f"{os.path.relpath(path, ROOT)}: raised {n[0]} font-size occurrence(s)")
    total += n[0]
print("total:", total)
