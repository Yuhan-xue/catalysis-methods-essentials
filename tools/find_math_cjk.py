# -*- coding: utf-8 -*-
r"""Find CJK characters sitting inside math mode.

They route to the MATH font (TeXGyreTermesMath), which has no CJK glyphs, so they
vanish silently. Must scan $...$ and $$...$$ spans rather than whole lines, since a
line usually contains prose between two math spans.
"""
import re, glob, os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, "chapters", "parts", "*.tex"))) + \
        sorted(glob.glob(os.path.join(ROOT, "chapters", "*.tex")))

CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")
# 去掉转义的美元符与注释后再找数学段
MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)

hits = []
for f in FILES:
    txt = open(f, encoding="utf-8").read()
    txt = re.sub(r"(?m)(?<!\\)%.*$", "", txt)          # 注释
    txt = txt.replace(r"\$", "")                        # 转义美元符
    for m in MATH.finditer(txt):
        body = m.group(1) or m.group(2) or ""
        found = CJK.findall(body)
        if found:
            line = txt[:m.start()].count("\n") + 1
            hits.append((os.path.relpath(f, ROOT), line, "".join(sorted(set(found))), body.strip()[:70]))

print(f"CJK-inside-math occurrences: {len(hits)}")
seen = set()
for f, line, chars, body in hits:
    key = (f, chars)
    if key in seen:
        continue
    seen.add(key)
    print(f"  {f}:{line}  chars={chars}")
    print(f"      {body}")
