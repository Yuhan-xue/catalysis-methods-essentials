# -*- coding: utf-8 -*-
r"""查 MATH 表的 GlyphAssembly：确认「重叠拼接」是不是字体规定的设计行为。

对横向拉伸的重音（如 U+20D7 右箭头）与定界符，OpenType MATH 用 GlyphAssembly
把若干零件拼起来，零件之间按 **connector 长度重叠**——重叠是设计要求，
不是缺陷。本脚本打印零件清单与各自的 advance / connector，用数据说话。
"""
import os
import sys
import pymupdf
from fontTools.ttLib import TTFont

FONTS = [
    (r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre-math/texgyretermes-math.otf",
     ["uni20D7", "uni2192", "uni2190"]),
]

for path, names in FONTS:
    f = TTFont(path, fontNumber=0)
    math = f["MATH"].table
    cmap = f.getBestCmap()
    gorder = f.getGlyphOrder()
    print("## %s" % path)
    # 反向：glyph name -> codepoint
    inv = {}
    for cp, gn in cmap.items():
        inv.setdefault(gn, cp)
    for gn in names:
        cp = inv.get(gn)
        print("   glyph %s (U+%04X)" % (gn, cp if cp else 0))
    # 打印所有 GlyphAssembly
    va = math.MathVariants
    if va is None:
        print("   no MathVariants")
        continue
    print("   MinConnectorOverlap =", va.MinConnectorOverlap)
    for label, cover, cons in (("vert", va.VertGlyphCoverage, va.VertGlyphConstruction),
                               ("horiz", va.HorizGlyphCoverage, va.HorizGlyphConstruction)):
        if cover is None:
            continue
        for i, g in enumerate(cover.glyphs):
            c = cons[i]
            if getattr(c, "GlyphAssembly", None) is None:
                continue
            cp = inv.get(g)
            if cp is None:
                continue
            asm = c.GlyphAssembly
            print("   [%s] %s U+%04X  ItalicCorrection=%s  parts=%d"
                  % (label, g, cp, asm.ItalicsCorrection.Value, len(asm.PartRecords)))
            for p in asm.PartRecords:
                print("        part %-10s flags=%d startConn=%d endConn=%d fullAdv=%d"
                      % (p.glyph, p.PartFlags, p.StartConnectorLength,
                         p.EndConnectorLength, p.FullAdvance))
