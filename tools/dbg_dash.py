# -*- coding: utf-8 -*-
"""核查 p.94 的 '–'×'ln' 命中：那个 '–' 到底是什么字形。"""
import os
import sys
import pymupdf
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))
page = doc[93]
out = []
for s in page.get_texttrace():
    if s["bbox"][1] < 730 or s["bbox"][1] > 750:
        continue
    out.append("span font=%s size=%.2f dir=%s" % (s["font"], s["size"], s["dir"]))
    for uni, gid, org, mbox in s["chars"]:
        c = chr(uni)
        out.append("   %r U+%04X gid=%d org=(%.2f,%.2f) metric=%s"
                   % (c, uni, gid, org[0], org[1],
                      [round(v, 2) for v in mbox]))

for fname in ("FandolSong-Regular", "TeXGyreTermes-Regular"):
    p = inkbox.font_path(fname)
    f = TTFont(p, fontNumber=0, lazy=True)
    order = f.getGlyphOrder()
    cmap = f.getBestCmap()
    out.append("## %s  glyphs=%d" % (fname, len(order)))
    for cp in (0x2013, 0x2014, 0x2212):
        gn = cmap.get(cp)
        out.append("   U+%04X -> %s (gid %s)" % (cp, gn, order.index(gn) if gn in order else "?"))
    for gid in (9910, 73, 106, 56, 69):
        if gid < len(order):
            out.append("   gid %d -> %s" % (gid, order[gid]))
    for gn in ("endash", "emdash", "uni2013", "uni2014"):
        if gn in order:
            gid = order.index(gn)
            out.append("   %s gid=%d ink=%s" % (gn, gid, inkbox.ink_bbox(fname, chr(
                0x2013 if "2013" in gn or gn == "endash" else 0x2014))))

txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "tools", "_dbg_dash.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
