# -*- coding: utf-8 -*-
r"""字形**墨迹盒**（ink bbox）提供者。

为什么需要它：PDF 文本层里，rawdict 给出的字符盒是**度量盒**——
CJK 一律按 1 em 计，西文按字体盒计。`−`（细横条）、`］`（挤压到半宽）、
上下标这类字形的度量盒与其真实墨迹相差极大，会造成大量假重叠。

做法：用系统原字体（TeX Live 里的 OTF，与 PDF 内嵌子集同一套轮廓）+
fontTools 取 charstring 的真实边界，换算成「相对原点的 em 单位、y 向下为正」，
与页面坐标同向，可直接平移到页面上。

坐标约定：返回 (x0, y0, x1, y1)，单位为 em（乘字号得 pt）；
原点为基线起点，y 向下（即 y0 < y1，且基线在 y=0）。
"""
import os
import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

# 页面 span 里的字体名 -> 系统字体文件
# 注意：PyMuPDF 报出的 span 字体名**可能被截断**（实测 TeXGyreTermesMath-Regular
# 被报成 'TeXGyreTermesMath-Regula'，26 字 -> 22 字），所以下面用前缀匹配解析。
FONT_FILES = {
    "FandolSong-Regular": "FandolSong-Regular.otf",
    "FandolSong-Bold": "FandolSong-Bold.otf",
    "FandolHei-Regular": "FandolHei-Regular.otf",
    "FandolHei-Bold": "FandolHei-Bold.otf",
    "FandolKai-Regular": "FandolKai-Regular.otf",
    "FandolFang-Regular": "FandolFang-Regular.otf",
    "TeXGyreTermes-Regular": "texgyretermes-regular.otf",
    "TeXGyreTermes-Bold": "texgyretermes-bold.otf",
    "TeXGyreTermes-Italic": "texgyretermes-italic.otf",
    "TeXGyreTermes-BoldItalic": "texgyretermes-bolditalic.otf",
    "TeXGyreTermesMath-Regular": "texgyretermes-math.otf",
    "TeXGyreCursor-Regular": "texgyrecursor-regular.otf",
    "TeXGyreHeros-Regular": "texgyreheros-regular.otf",
    "LatinModernMath-Regular": "latinmodern-math.otf",
}

SEARCH_DIRS = [
    r"c:/texlive/2026/texmf-dist/fonts/opentype/public/fandol",
    r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre",
    r"c:/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre-math",
    r"c:/texlive/2026/texmf-dist/fonts/opentype/public/lm-math",
]

_fontcache = {}
_inkcache = {}


_resolved = {}


def font_key(name):
    """把页面报出的（可能被截断的）字体名解析成 FONT_FILES 的键。"""
    if name in _resolved:
        return _resolved[name]
    key = None
    if name in FONT_FILES:
        key = name
    else:
        cands = [k for k in FONT_FILES
                 if k.startswith(name) or name.startswith(k)]
        if cands:
            key = max(cands, key=len)     # 取最长匹配，避免前缀歧义
    _resolved[name] = key
    return key


def font_path(name):
    key = font_key(name)
    if not key:
        return None
    fn = FONT_FILES[key]
    for d in SEARCH_DIRS:
        p = os.path.join(d, fn)
        if os.path.exists(p):
            return p
    return None


def _load(name):
    if name in _fontcache:
        return _fontcache[name]
    p = font_path(name)
    if p is None:
        _fontcache[name] = None
        return None
    f = TTFont(p, fontNumber=0, lazy=True)
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    upem = f["head"].unitsPerEm
    order = f.getGlyphOrder()
    # CID-keyed CFF（Fandol 系列）的字形名是 cidNNNNN，PDF 里的 gid 是 **CID**，
    # 不是字形序号。实测 FandolSong：U+2013 的 cmap 名是 cid09910（序号 8900），
    # 而 PDF 报 gid=9910 —— 差的正是 CID 与序号。若不区分，会取到完全不相干的
    # 字形（9910 号是 cid29760），墨迹盒就错了。
    cidmap = {}
    for i, gn in enumerate(order):
        if gn.startswith("cid") and gn[3:].isdigit():
            cidmap[int(gn[3:])] = i
    _fontcache[name] = (f, cmap, gs, upem, order, cidmap)
    return _fontcache[name]


def gid_index(ent, gid):
    """把 PDF 的 gid 换成字形序号；CID 键字体走 cidmap。"""
    f, cmap, gs, upem, order, cidmap = ent
    if cidmap:
        if gid in cidmap:
            return cidmap[gid]
        return None
    if 0 <= gid < len(order):
        return gid
    return None


def _bbox_of_glyph(gs, upem, gname):
    pen = BoundsPen(gs)
    try:
        gs[gname].draw(pen)
    except Exception:
        return None
    if pen.bounds is None:          # 空白字形（如空格）
        return None
    x0, y0, x1, y1 = pen.bounds
    # fontTools: y 向上；页面: y 向下 -> 取负并换序
    return (x0 / upem, -y1 / upem, x1 / upem, -y0 / upem)


def ink_bbox(name, ch):
    """按 unicode 取墨迹盒。返回 (x0, y0, x1, y1)，em 单位、y 向下。"""
    key = ("u", name, ch)
    if key in _inkcache:
        return _inkcache[key]
    ent = _load(name)
    if ent is None:
        _inkcache[key] = None
        return None
    f, cmap, gs, upem, order, cidmap = ent
    gname = cmap.get(ord(ch))
    box = _bbox_of_glyph(gs, upem, gname) if gname else None
    _inkcache[key] = box
    return box


def ink_bbox_gid(name, gid, ch=None):
    r"""按**字形序号 / CID** 取墨迹盒——这是精确做法。

    为什么必须用 gid：PDF 的 ToUnicode 会把多个不同字形映射到同一个 unicode。
    实测（Termes 系）11320/11538 个字符的 gid 与原字体字形序号一致，216 个不一致
    的全部是**字形变体**（数字的 two.st / six.st）或 GlyphAssembly **拼装件**
    （uni20D7.lft/.ex/.rt、minus.ex 等，根本不在 cmap 里）。按 unicode 取盒会取到
    基准字形，盒就错了。CID 键字体（Fandol）另需 CID→序号换算，见 _load()。
    """
    key = ("g", name, gid)
    if key in _inkcache:
        return _inkcache[key]
    ent = _load(name)
    if ent is None:
        _inkcache[key] = None
        return None
    f, cmap, gs, upem, order, cidmap = ent
    box = None
    idx = gid_index(ent, gid)
    if idx is not None:
        box = _bbox_of_glyph(gs, upem, order[idx])
    if box is None and ch is not None:
        box = ink_bbox(name, ch)
    _inkcache[key] = box
    return box


def glyph_name_of(name, gid, ch=None):
    """给定了 gid，返回真正被绘制的字形名（供轮廓相交计算用）。"""
    ent = _load(name)
    if ent is None:
        return None
    f, cmap, gs, upem, order, cidmap = ent
    idx = gid_index(ent, gid)
    if idx is not None:
        return order[idx]
    return cmap.get(ord(ch)) if ch else None


if __name__ == "__main__":
    import sys
    tests = {
        "FandolSong-Regular": "面像［］，。（）入失桥移位模顶",
        "TeXGyreTermesMath-Regular": "−→↽⇀λ2kf",
        "TeXGyreTermes-Regular": "R10–kfEm",
        "TeXGyreTermes-Italic": "Eλ",
        "TeXGyreTermes-Bold": "R",
    }
    out = []
    for fname, chars in tests.items():
        out.append(f"## {fname}  ({font_path(fname)})")
        for c in chars:
            b = ink_bbox(fname, c)
            if b is None:
                out.append(f"   {c!r} U+{ord(c):04X}  <无墨迹/无字形>")
            else:
                out.append(f"   {c!r} U+{ord(c):04X} ink=({b[0]:+.4f},{b[1]:+.4f},{b[2]:+.4f},{b[3]:+.4f}) "
                           f"w={b[2]-b[0]:.4f} h={b[3]-b[1]:.4f}")
    txt = "\n".join(out)
    print(txt)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_inkbox.txt"),
              "w", encoding="utf-8") as fh:
        fh.write(txt)
