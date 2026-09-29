# -*- coding: utf-8 -*-
r"""复核判据 B 有没有「过滤过头」或「漏掉整类」。

把**旧判据**（取所有 drawing 的 `rect` 两两求交 + 只排嵌套/擦边/尺寸悬殊）的
每一条命中逐条重算，并给出它的真实身份，再看新判据 B 会怎么处理。

同时统计全书被新判据认定为「近似矩形」的图元数量与最小间距，
以验证判据不是「什么都没认出来」。
"""
import os
import sys
import collections
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlap_check as oc                                  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "_rectaudit.txt")

doc = pymupdf.open(PDF)
stat = collections.Counter()
rows = []

for pno in range(doc.page_count):
    page = doc[pno]
    cands = []
    for dr in page.get_drawings():
        r = dr["rect"]
        w, h = r.width, r.height
        if w < 15 or h < 15:
            continue
        ratio = w / h if h else 99
        if not (0.25 <= ratio <= 4):
            continue
        cands.append((r, dr))
    cands.sort(key=lambda t: (t[0].x0, t[0].y0))
    for i in range(len(cands)):
        ra, da = cands[i]
        for j in range(i + 1, len(cands)):
            rb, db = cands[j]
            if rb.x0 >= ra.x1 - oc.B_MIN_PT:
                break
            ox = min(ra.x1, rb.x1) - max(ra.x0, rb.x0)
            oy = min(ra.y1, rb.y1) - max(ra.y0, rb.y0)
            if ox <= oc.B_MIN_PT or oy <= oc.B_MIN_PT:
                continue
            area_a, area_b = ra.width * ra.height, rb.width * rb.height
            inter = ox * oy
            if inter >= 0.95 * min(area_a, area_b):
                stat["旧判据本就排除：嵌套"] += 1
                continue
            if inter <= 0.02 * max(area_a, area_b):
                stat["旧判据本就排除：擦边"] += 1
                continue
            if not (0.34 <= area_a / area_b <= 2.9):
                stat["旧判据本就排除：尺寸悬殊"] += 1
                continue
            stat["旧判据命中"] += 1
            qa = oc._quasi_rect_of_items(da.get("items") or [])
            qb = oc._quasi_rect_of_items(db.get("items") or [])
            reason = []
            if qa is None or qb is None:
                reason.append("非近似矩形(面积比<0.92)")
            if qa is not None and qb is not None:
                if ((qb.x0 >= qa.x0 - oc.B_NEST_TOL and qb.x1 <= qa.x1 + oc.B_NEST_TOL and
                     qb.y0 >= qa.y0 - oc.B_NEST_TOL and qb.y1 <= qa.y1 + oc.B_NEST_TOL) or
                    (qa.x0 >= qb.x0 - oc.B_NEST_TOL and qa.x1 <= qb.x1 + oc.B_NEST_TOL and
                     qa.y0 >= qb.y0 - oc.B_NEST_TOL and qa.y1 <= qb.y1 + oc.B_NEST_TOL)):
                    reason.append("嵌套")
                if not (da.get("color") is not None and (da.get("width") or 0) > 0 and
                        db.get("color") is not None and (db.get("width") or 0) > 0):
                    reason.append("含无描边项")
                if (min(qa.width, qa.height) < oc.B_SLIVER or
                        min(qb.width, qb.height) < oc.B_SLIVER):
                    reason.append("长细条")
            cls = "+".join(reason) if reason else "**近似矩形相撞（判据 B 会报告）**"
            stat[cls] += 1
            kinds_a = dict(collections.Counter(it[0] for it in (da.get("items") or [])))
            kinds_b = dict(collections.Counter(it[0] for it in (db.get("items") or [])))
            rows.append((pno + 1, ra, rb, ox, oy, cls, kinds_a, kinds_b))

# 全书被认定为近似矩形的图元
nquasi = 0
for pno in range(doc.page_count):
    for dr in doc[pno].get_drawings():
        if oc._quasi_rect_of_items(dr.get("items") or []) is not None:
            nquasi += 1

out = ["判据 B 复核", ""]
out.append("全书被认定为「近似矩形」的图元：%d 个" % nquasi)
out.append("")
for k in sorted(stat):
    out.append("  %-46s %d" % (k, stat[k]))
out.append("")
cur = None
for r in rows:
    if r[0] != cur:
        cur = r[0]
        out.append("===== p.%d =====" % cur)
    out.append("   [%s] 框[%.1f,%.1f,%.1f,%.1f]×[%.1f,%.1f,%.1f,%.1f] 重叠 %.1fx%.1f  "
               "路径项A=%s 路径项B=%s"
               % (r[5], r[1].x0, r[1].y0, r[1].x1, r[1].y1,
                  r[2].x0, r[2].y0, r[2].x1, r[2].y1, r[3], r[4], r[6], r[7]))
txt = "\n".join(out)
print(txt[:2000])
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(txt)
