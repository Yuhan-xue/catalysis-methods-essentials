# -*- coding: utf-8 -*-
r"""打印 overlap_hits.json 的完整字形信息 + 命中处的上下文行。"""
import io
import os
import sys
import json
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
HITS = os.path.join(ROOT, "tools", "overlap_hits.json")

hits = json.load(io.open(HITS, encoding="utf-8"))
doc = pymupdf.open(PDF)
out = []
bypage = {}
for h in hits:
    bypage.setdefault(h["page"], []).append(h)

for pno in sorted(bypage):
    page = doc[pno - 1]
    out.append("===== p.%d =====" % pno)
    for h in bypage[pno]:
        out.append("  '%s' × '%s'  盒重叠 %.2fx%.2f" % (h["ca"], h["cb"], h["ox"], h["oy"]))
        for tag in ("ga", "gb"):
            g = h[tag]
            out.append("     %s font=%s gid=%d sz=%.2f org=(%.2f,%.2f) dir=%s box=%s"
                       % (tag, g["font"], g["gid"], g["size"], g["org"][0], g["org"][1],
                          g["dir"], h["boxa" if tag == "ga" else "boxb"]))
        # 上下文行
        for g in (h["ga"], h["gb"]):
            x, y = g["org"]
            r = pymupdf.Rect(x - 40, y - 12, x + 40, y + 12)
            for b in page.get_text("dict", clip=r)["blocks"]:
                if b.get("type") != 0:
                    continue
                for l in b["lines"]:
                    t = "".join(s["text"] for s in l["spans"])
                    out.append("       上下文 %r" % t)
    out.append("")

txt = "\n".join(out)
print(txt[:200])
io.open(os.path.join(ROOT, "tools", "_hitctx.txt"), "w", encoding="utf-8").write(txt)
