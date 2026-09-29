# -*- coding: utf-8 -*-
"""量出版心的实际上边界：逐页取文字墨迹的最小/最大 y（排除页眉页脚）。"""
import os
import sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))

FOOT_SIZE = 8.97
rows = []
for pno in range(doc.page_count):
    page = doc[pno]
    ymin, ymax = 1e9, -1e9
    what_min = what_max = ""
    for s in page.get_texttrace():
        t = "".join(chr(c[0]) for c in s["chars"])
        if not t.strip():
            continue
        # 排除页眉（y<70）与页脚（页码：单行纯数字、字号 8.97）
        if abs(s["size"] - FOOT_SIZE) < 0.05 and t.strip().isdigit():
            continue
        for uni, gid, org, mbox in s["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            ink = inkbox.ink_bbox_gid(s["font"], gid, c)
            if ink is None:
                x0, y0, x1, y1 = mbox
            else:
                dx, dy = s["dir"]
                xs, ys = [], []
                for px, py in ((ink[0], ink[1]), (ink[0], ink[3]),
                               (ink[2], ink[1]), (ink[2], ink[3])):
                    xs.append(org[0] + px * s["size"] * dx - py * s["size"] * dy)
                    ys.append(org[1] + px * s["size"] * dy + py * s["size"] * dx)
                x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            if y0 < ymin:
                ymin, what_min = y0, t[:24]
            if y1 > ymax:
                ymax, what_max = y1, t[:24]
    rows.append((pno + 1, ymin, ymax, what_min, what_max))

print("页面上边界最小 y = %.2f；下边界最大 y = %.2f"
      % (min(r[1] for r in rows), max(r[2] for r in rows)))
rows.sort(key=lambda r: -r[2])
out = ["墨迹最低的 12 页："]
for r in rows[:12]:
    out.append("  p.%-4d 最低 y=%.2f  %r" % (r[0], r[2], r[4]))
out.append("")
out.append("墨迹最高的 6 页：")
for r in sorted(rows, key=lambda r: r[1])[:6]:
    out.append("  p.%-4d 最高 y=%.2f  %r" % (r[0], r[1], r[3]))
txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "tools", "_textblock.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
