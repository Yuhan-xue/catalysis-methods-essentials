# -*- coding: utf-8 -*-
r"""按文本片段查 span（跨页），打印其 bbox / 字体 / 字号 / seqno / type，用于核查重复绘制。"""
import os
import sys
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))
needle = sys.argv[1]
pages = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else range(1, doc.page_count + 1)

out = []
for pno in pages:
    page = doc[pno - 1]
    for s in page.get_texttrace():
        t = "".join(chr(c[0]) for c in s["chars"])
        if needle not in t:
            continue
        out.append("p.%-4d %-28r bbox=[%.2f,%.2f,%.2f,%.2f] sz=%.2f %s seqno=%s type=%s wmode=%s"
                   % (pno, t, s["bbox"][0], s["bbox"][1], s["bbox"][2], s["bbox"][3],
                      s["size"], s["font"], s["seqno"], s["type"], s.get("wmode")))
        for uni, gid, org, mbox in s["chars"]:
            out.append("        %r gid=%d org=(%.2f,%.2f) metric=[%.2f,%.2f,%.2f,%.2f]"
                       % (chr(uni), gid, org[0], org[1],
                          mbox[0], mbox[1], mbox[2], mbox[3]))
    # rawdict 对照
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                t = "".join(c["c"] for c in s["chars"])
                if needle in t:
                    out.append("  [rawdict] p.%-4d %-28r bbox=[%.2f,%.2f,%.2f,%.2f] sz=%.2f %s"
                               % (pno, t, s["bbox"][0], s["bbox"][1], s["bbox"][2],
                                  s["bbox"][3], s["size"], s["font"]))
txt = "\n".join(out)
print(txt[:6000])
with open(os.path.join(ROOT, "tools", "_findspan.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
