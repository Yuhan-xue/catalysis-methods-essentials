# -*- coding: utf-8 -*-
r"""判据 B 灵敏度 + 判据 C「填充粗条」归类。

B 灵敏度：全书所有「近似矩形」两两求交，按重叠量分档，看判据是否卡在边界上
（若最大被排除的重叠量远小于阈值，说明判据有余量；若紧贴阈值则要警惕）。
C 归类：把 12 处「填充粗条」按所在页面/尺寸列出，并给出同页的其它线索，
判断是**图形里的实心条**还是**字形退化**。
"""
import os
import sys
import collections
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlap_check as oc                                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "_sensB.txt")
doc = pymupdf.open(PDF)

out = []
# ---------- B 灵敏度 ----------
buckets = collections.Counter()
max_excl = 0.0
min_reported = 99.0
for pno in range(doc.page_count):
    page = doc[pno]
    rects = []
    for dr in page.get_drawings():
        r = oc._quasi_rect_of_items(dr.get("items") or [])
        if r is None or r.width < 6 or r.height < 6:
            continue
        stroked = dr.get("color") is not None and (dr.get("width") or 0) > 0
        filled = dr.get("fill") is not None
        if stroked or filled:
            rects.append((r, stroked, filled))
    rects.sort(key=lambda t: (t[0].x0, t[0].y0))
    for i in range(len(rects)):
        ra, sa, fa = rects[i]
        for j in range(i + 1, len(rects)):
            rb, sb, fb = rects[j]
            if rb.x0 >= ra.x1:
                break
            ox = min(ra.x1, rb.x1) - max(ra.x0, rb.x0)
            oy = min(ra.y1, rb.y1) - max(ra.y0, rb.y0)
            if ox <= 0 or oy <= 0:
                buckets["不重叠"] += 1
                continue
            m = min(ox, oy)
            nested = ((rb.x0 >= ra.x0 - oc.B_NEST_TOL and rb.x1 <= ra.x1 + oc.B_NEST_TOL and
                       rb.y0 >= ra.y0 - oc.B_NEST_TOL and rb.y1 <= ra.y1 + oc.B_NEST_TOL) or
                      (ra.x0 >= rb.x0 - oc.B_NEST_TOL and ra.x1 <= rb.x1 + oc.B_NEST_TOL and
                       ra.y0 >= rb.y0 - oc.B_NEST_TOL and ra.y1 <= rb.y1 + oc.B_NEST_TOL))
            if nested:
                buckets["嵌套(容差 3pt 内)"] += 1
                max_excl = max(max_excl, m)
                continue
            if not (sa and sb):
                buckets["一方无描边"] += 1
                max_excl = max(max_excl, m)
                continue
            if min(ra.width, ra.height) < oc.B_SLIVER or min(rb.width, rb.height) < oc.B_SLIVER:
                buckets["长细条"] += 1
                max_excl = max(max_excl, m)
                continue
            if m <= oc.B_MIN_PT:
                buckets["部分重叠但较小边 ≤ %.1fpt（阈值下）" % oc.B_MIN_PT] += 1
                max_excl = max(max_excl, m)
                continue
            buckets["**报告**"] += 1
            min_reported = min(min_reported, m)

out.append("判据 B 灵敏度（全书近似矩形两两求交）")
for k in sorted(buckets):
    out.append("  %-38s %d" % (k, buckets[k]))
out.append("  被排除项的最大重叠量：%.2f pt；被报告项的最小重叠量：%s"
           % (max_excl, ("%.2f pt" % min_reported) if min_reported < 99 else "（无报告项）"))
out.append("")

# ---------- C 填充粗条 ----------
out.append("判据 C：填充粗条逐条")
for pno in range(doc.page_count):
    hz, vt, bar = oc.check_thick(doc[pno])
    for r, t in bar:
        ctx = []
        rr = pymupdf.Rect(r.x0 - 6, r.y0 - 6, r.x1 + 6, r.y1 + 6)
        for b in doc[pno].get_text("dict", clip=rr)["blocks"]:
            if b.get("type") != 0:
                continue
            for l in b["lines"]:
                ctx.append("".join(s["text"] for s in l["spans"]))
        out.append("  p.%-4d 厚 %.2f pt  [%.1f,%.1f,%.1f,%.1f]  周边文字=%r"
                   % (pno + 1, t, r.x0, r.y0, r.x1, r.y1, " / ".join(ctx)[:70]))
out.append("")
out.append("判据 C：粗横线 / 粗竖线")
n = 0
for pno in range(doc.page_count):
    hz, vt, _ = oc.check_thick(doc[pno])
    for r, w in hz:
        out.append("  [横] p.%-4d %.2f pt [%.1f,%.1f]→[%.1f,%.1f]" % (pno + 1, w, r.x0, r.y0, r.x1, r.y1))
        n += 1
    for r, w in vt:
        out.append("  [竖] p.%-4d %.2f pt [%.1f,%.1f]→[%.1f,%.1f]" % (pno + 1, w, r.x0, r.y0, r.x1, r.y1))
        n += 1
if n == 0:
    out.append("  （无）")

txt = "\n".join(out)
print(txt)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(txt)
