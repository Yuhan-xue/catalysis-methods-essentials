# -*- coding: utf-8 -*-
r"""诊断器：把字符级重叠命中按 **span（字符串）** 归类。

判据（span 级）：
  两个**不同 span** 的字形盒互相侵入 —— 即小盒有大比例落进大盒内，
  且两方向重叠都 > MIN_PT。同一 span 内的字符重叠一律不计（度量问题）。

输出每处命中的完整上下文：页、两个 span 的文本、bbox、字体、字号、
重叠量、包含率，便于逐条人工判定真伪。
"""
import io, os, sys, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "overlap_spans.txt")

MIN_PT = 1.2


def spans_of(page):
    out = []
    for bi, b in enumerate(page.get_text("dict")["blocks"]):
        if b.get("type") != 0:
            continue
        for li, l in enumerate(b["lines"]):
            for si, s in enumerate(l["spans"]):
                t = s["text"]
                if not t.strip():
                    continue
                x0, y0, x1, y1 = s["bbox"]
                if x1 - x0 <= 0 or y1 - y0 <= 0:
                    continue
                out.append(dict(bi=bi, li=li, si=si, text=t, bbox=(x0, y0, x1, y1),
                                font=s["font"], size=s["size"], asc=s.get("ascender"),
                                desc=s.get("descender"), origin=s["origin"], n=len(t)))
    return out


def rects_overlap(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return ox, oy


rows = []
doc = pymupdf.open(PDF)
for pno in range(doc.page_count):
    page = doc[pno]
    sp = spans_of(page)
    hits = []
    for i in range(len(sp)):
        for j in range(i + 1, len(sp)):
            A, B = sp[i], sp[j]
            ox, oy = rects_overlap(A["bbox"], B["bbox"])
            if ox <= MIN_PT or oy <= MIN_PT:
                continue
            aa = (A["bbox"][2] - A["bbox"][0]) * (A["bbox"][3] - A["bbox"][1])
            ab = (B["bbox"][2] - B["bbox"][0]) * (B["bbox"][3] - B["bbox"][1])
            inter = ox * oy
            small = min(aa, ab)
            cont = inter / small if small else 0
            hits.append((cont, ox, oy, inter, A, B))
    if hits:
        hits.sort(reverse=True, key=lambda t: t[0])
        rows.append((pno + 1, hits))

lines = [f"file={PDF}  pages={doc.page_count}",
         "span 级：跨 span 的字形盒互相侵入（两方向 >1.2pt）；按包含率降序", ""]
n = 0
for pno, hits in rows:
    lines.append(f"===== p.{pno} =====")
    for cont, ox, oy, inter, A, B in hits:
        n += 1
        lines.append(f"  [{cont*100:5.1f}% 含] {ox:.1f}x{oy:.1f}pt  inter={inter:.0f}")
        for tag, S in (("A", A), ("B", B)):
            x0, y0, x1, y1 = S["bbox"]
            lines.append(f"      {tag} bbox=[{x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}] "
                         f"w={x1-x0:.1f} h={y1-y0:.1f} font={S['font']} sz={S['size']:.1f} "
                         f"org=({S['origin'][0]:.1f},{S['origin'][1]:.1f}) "
                         f"txt={S['text']!r}")
    lines.append("")
lines.append(f"合计：跨 span 命中 {n} 处，涉及 {len(rows)} 页")
io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"跨 span 命中 {n} 处，涉及 {len(rows)} 页 -> {OUT}")
