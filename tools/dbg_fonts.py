# -*- coding: utf-8 -*-
"""调试：列出 PDF 中出现的全部字体名，以及哪些没有对应的系统字体文件。"""
import os
import sys
import collections
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))
seen = collections.Counter()
for pno in range(doc.page_count):
    for s in doc[pno].get_texttrace():
        seen[s["font"]] += 1

lines = []
for f, n in seen.most_common():
    lines.append("%7d  %-34r path=%s" % (n, f, inkbox.font_path(f)))

# 逐字体统计「unicode 在字体 cmap 里找不到」的字符
miss = collections.defaultdict(collections.Counter)
for pno in range(doc.page_count):
    for s in doc[pno].get_texttrace():
        f = s["font"]
        if inkbox.font_path(f) is None:
            continue
        for uni, gid, org, mbox in s["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            if inkbox.ink_bbox(f, c) is None:
                miss[f][c] += 1
lines.append("")
for f, cnt in miss.items():
    lines.append("## %s 缺字形 %d 种：%s" % (f, len(cnt), "".join(sorted(cnt))))
txt = "\n".join(lines)
print(txt)
with open(os.path.join(ROOT, "tools", "_dbg_fonts.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
