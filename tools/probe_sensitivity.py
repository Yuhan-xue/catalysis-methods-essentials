# -*- coding: utf-8 -*-
r"""灵敏度探测：把「面积占比」阈去掉，看墨迹盒相交的**全部**情形有多少、长什么样。

目的：确认 45% 占比判据是否把「部分压叠」（两行字压了 2-3 pt）漏掉了。
若正常正文在任何面积阈值下都不产生命中，就可以安全地改用绝对面积阈值，
从而更灵敏、又不引入误报。
"""
import os
import sys
import collections
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
MIN_PT = 1.2

DELIM = set(range(0x239B, 0x23AE)) | set(range(0x23B0, 0x23B8))


def glyphs(page):
    out = []
    for span in page.get_texttrace():
        font, size = span["font"], span["size"]
        dx, dy = span["dir"]
        txt = "".join(chr(c[0]) for c in span["chars"])
        isdel = any(ord(c) in DELIM for c in txt)
        for uni, gid, org, mbox in span["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            ink = inkbox.ink_bbox_gid(font, gid, c)
            if ink is None:
                x0, y0, x1, y1 = mbox
            else:
                xs, ys = [], []
                for px, py in ((ink[0], ink[1]), (ink[0], ink[3]),
                               (ink[2], ink[1]), (ink[2], ink[3])):
                    xs.append(org[0] + px * size * dx - py * size * dy)
                    ys.append(org[1] + px * size * dy + py * size * dx)
                x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            if x1 - x0 <= 0 or y1 - y0 <= 0:
                continue
            out.append((x0, y0, x1, y1, c, font, txt, isdel,
                        (round(org[0], 2), round(org[1], 2))))
    return out


doc = pymupdf.open(PDF)
buckets = collections.Counter()
rows = []
for pno in range(doc.page_count):
    gs = glyphs(doc[pno])
    gs.sort(key=lambda g: g[0])
    for i in range(len(gs)):
        ax0, ay0, ax1, ay1, ac, af, at, adel, ao = gs[i]
        aa = (ax1 - ax0) * (ay1 - ay0)
        for j in range(i + 1, len(gs)):
            bx0, by0, bx1, by1, bc, bf, bt, bdel, bo = gs[j]
            if bx0 >= ax1 - MIN_PT:
                break
            if ao == bo:
                continue
            ox = min(ax1, bx1) - max(ax0, bx0)
            if ox <= MIN_PT:
                continue
            oy = min(ay1, by1) - max(ay0, by0)
            if oy <= MIN_PT:
                continue
            ab = (bx1 - bx0) * (by1 - by0)
            inter = ox * oy
            frac = inter / min(aa, ab)
            # 面积分档
            if inter < 0.5:
                b = "a <0.5pt2"
            elif inter < 1:
                b = "b 0.5-1"
            elif inter < 2:
                b = "c 1-2"
            elif inter < 5:
                b = "d 2-5"
            elif inter < 10:
                b = "e 5-10"
            else:
                b = "f >=10"
            buckets[b] += 1
            buckets[b + (" delim" if (adel and bdel) else "")] += 1
            if frac >= 0.45:
                buckets["[45%判据命中]"] += 1
            else:
                buckets["[45%判据漏掉]"] += 1
                rows.append((inter, frac, pno + 1, ac, bc, at, bt, ox, oy, adel and bdel))

out = ["面积分档："]
for k in sorted(buckets):
    out.append("   %-14s %d" % (k, buckets[k]))
out.append("")
out.append("被判据漏掉的（面积 ≥2pt²，按面积降序，最多 120 条）：")
rows.sort(reverse=True)
for r in rows:
    if r[0] < 2:
        continue
    out.append("   %6.2fpt² 占%3.0f%%  p.%-4d '%s'×'%s'  %.1fx%.1f  %r × %r%s"
               % (r[0], r[1] * 100, r[2], r[3], r[4], r[7], r[8], r[5], r[6],
                  "  [delim]" if r[9] else ""))
    if len(out) > 200:
        break
txt = "\n".join(out)
print(txt[:1500])
with open(os.path.join(ROOT, "tools", "_sensitivity.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
