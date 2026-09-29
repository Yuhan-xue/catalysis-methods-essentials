# -*- coding: utf-8 -*-
r"""打印某页某区域内所有字形的墨迹盒（按 span 分组），用于看清命中处的真实布局。"""
import os
import sys
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))
pno = int(sys.argv[1]) - 1
X0, Y0, X1, Y1 = (float(a) for a in sys.argv[2:6])
page = doc[pno]
out = []
for s in page.get_texttrace():
    dx, dy = s["dir"]
    txt = "".join(chr(c[0]) for c in s["chars"])
    rows = []
    for uni, gid, org, mbox in s["chars"]:
        c = chr(uni)
        if not c.strip():
            continue
        ink = inkbox.ink_bbox_gid(s["font"], gid, c)
        if ink is None:
            box = tuple(mbox)
            tag = "METRIC"
        else:
            xs, ys = [], []
            for px, py in ((ink[0], ink[1]), (ink[0], ink[3]),
                           (ink[2], ink[1]), (ink[2], ink[3])):
                xs.append(org[0] + px * s["size"] * dx - py * s["size"] * dy)
                ys.append(org[1] + px * s["size"] * dy + py * s["size"] * dx)
            box = (min(xs), min(ys), max(xs), max(ys))
            tag = "ink"
        if box[2] < X0 or box[0] > X1 or box[3] < Y0 or box[1] > Y1:
            continue
        rows.append((box[0], "%r %s box=[%.2f,%.2f,%.2f,%.2f] w=%.2f h=%.2f org=(%.2f,%.2f) gid=%d"
                     % (c, tag, box[0], box[1], box[2], box[3],
                        box[2] - box[0], box[3] - box[1], org[0], org[1], gid)))
    if rows:
        rows.sort()
        out.append("span %s sz=%.2f dir=(%.3f,%.3f) %r" % (s["font"], s["size"], dx, dy, txt))
        for _, r in rows:
            out.append("    " + r)
txt = "\n".join(out)
print(txt)
