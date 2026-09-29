# -*- coding: utf-8 -*-
r"""验证：用**系统原字体**（非 PDF 子集）取字形墨迹盒 glyph_bbox 是否可用。

子集字体没有 unicode cmap，glyph_bbox 会退化成 FontBBox（所有字相同）。
系统 OTF 有完整 cmap，应能给出每个字的真实墨迹范围（以 em 为单位）。
"""
import pymupdf

FONTS = {
    "FandolSong": r"c:/texlive/2026/texmf-dist/fonts/opentype/public/fandol/FandolSong-Regular.otf",
    "FandolHei": r"c:/texlive/2026/texmf-dist/fonts/opentype/public/fandol/FandolHei-Regular.otf",
    "TermesMath": r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre-math/texgyretermes-math.otf",
    "Termes": r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre/texgyretermes-regular.otf",
    "TermesItalic": r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre/texgyretermes-italic.otf",
}

TESTS = {
    "FandolSong": "面像［］，。（）入失桥移位模",
    "FandolHei": "面像［］，。",
    "TermesMath": "−→↽⇀λ2",
    "Termes": "R10–kfEm",
    "TermesItalic": "Eλ",
}

for key, path in FONTS.items():
    try:
        f = pymupdf.Font(fontfile=path)
    except Exception as e:
        print(f"## {key}: LOAD FAIL {e}")
        continue
    print(f"## {key}  name={f.name}  asc={f.ascender} desc={f.descender}")
    em = 1.0
    for c in TESTS.get(key, ""):
        o = ord(c)
        has = f.has_glyph(o)
        try:
            gb = f.glyph_bbox(o)
        except Exception as e:
            gb = f"ERR {e}"
        try:
            ga = f.glyph_advance(o, 1.0)
        except Exception as e:
            ga = f"ERR {e}"
        if isinstance(gb, tuple):
            w = gb[2] - gb[0]
            h = gb[3] - gb[1]
            print(f"   {c!r} U+{o:04X} has={has} adv={ga:.4f} "
                  f"bbox=({gb[0]:+.4f},{gb[1]:+.4f},{gb[2]:+.4f},{gb[3]:+.4f}) w={w:.4f} h={h:.4f}")
        else:
            print(f"   {c!r} U+{o:04X} has={has} adv={ga} {gb}")
