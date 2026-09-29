# -*- coding: utf-8 -*-
r"""查「同一串文字被画了两遍」：文本相同的 span，其包围盒互相重叠。

若存在，说明图上某个标签被重复绘制（TikZ 里同一 node 出现在两处、或
pgfplots 的 legend 与 node 重叠），会看到加粗/错位的双重字。
"""
import os
import sys
import collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))

rows = []
for pno in range(doc.page_count):
    spans = []
    for s in doc[pno].get_texttrace():
        t = "".join(chr(c[0]) for c in s["chars"])
        if not t.strip():
            continue
        spans.append((s["bbox"], t, s["font"], s["size"], s["seqno"]))
    for i in range(len(spans)):
        for j in range(i + 1, len(spans)):
            a, b = spans[i], spans[j]
            if a[1] != b[1]:
                continue
            ox = min(a[0][2], b[0][2]) - max(a[0][0], b[0][0])
            oy = min(a[0][3], b[0][3]) - max(a[0][1], b[0][1])
            if ox <= 0.5 or oy <= 0.5:
                continue
            dx = a[0][0] - b[0][0]
            dy = a[0][1] - b[0][1]
            rows.append((pno + 1, a[1], a[2], a[3], ox, oy, dx, dy, a[4], b[4],
                         a[0], b[0]))

out = ["同一串文字、包围盒互相重叠的 span 对：共 %d 对" % len(rows), ""]
for r in rows:
    out.append("  p.%-4d %r  sz=%.1f %s  重叠 %.1fx%.1f  位移(%.2f,%.2f) seqno=%s/%s"
               % (r[0], r[1], r[3], r[2], r[4], r[5], r[6], r[7], r[8], r[9]))
    out.append("        A=[%.2f,%.2f,%.2f,%.2f]  B=[%.2f,%.2f,%.2f,%.2f]"
               % (r[10][0], r[10][1], r[10][2], r[10][3],
                  r[11][0], r[11][1], r[11][2], r[11][3]))
txt = "\n".join(out)
print(txt[:800])
with open(os.path.join(ROOT, "tools", "_dupstrings.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
