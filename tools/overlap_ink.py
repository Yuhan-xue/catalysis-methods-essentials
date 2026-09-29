# -*- coding: utf-8 -*-
r"""把「包围盒相交」升级为「**轮廓墨迹真实相交**」。

包围盒相交只是必要条件：斜体 f 的横杠、积分号的尾巴、连字符的端点都可能
让两个盒相交而笔画并不相碰。本脚本用字体的真实轮廓（fontTools）+ 扫描采样，
算出两个字形**填充区域的实际交叠面积**（pt²），从而把
「盒相交但笔画不碰」与「笔画真压在一起」分开。

做法：在两者墨迹盒的公共区域上按 0.05 pt 网格采样，对每个采样点分别做
「点在字形轮廓内」（nonzero winding）判定，统计两侧同时为内的格数 × 格面积。
字形局部坐标由 origin + dir 反变换得到，旋转文本同样适用。

输入：tools/overlap_hits.json（由 overlap_check.py 生成）
输出：tools/overlap_ink.txt
"""
import io
import os
import sys
import json
import math

from fontTools.ttLib import TTFont
from fontTools.pens.pointInsidePen import PointInsidePen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HITS = os.path.join(ROOT, "tools", "overlap_hits.json")
OUT = os.path.join(ROOT, "tools", "overlap_ink.txt")
STEP = 0.05          # pt，采样步长

_fonts = {}


def font(key):
    if key not in _fonts:
        p = inkbox.font_path(key)
        _fonts[key] = TTFont(p, fontNumber=0, lazy=True) if p else None
    return _fonts[key]


def glyph_of(fontname, gid, ch):
    f = font(fontname)
    if f is None:
        return None
    order = f.getGlyphOrder()
    if 0 <= gid < len(order):
        return order[gid]
    return f.getBestCmap().get(ord(ch))


def inside_fn(fontname, gid, ch, size, org, dirv):
    r"""返回 page(x,y) -> bool 的判定函数（是否落在该字形墨迹内）。"""
    f = font(fontname)
    if f is None:
        return None
    gname = glyph_of(fontname, gid, ch)
    if gname is None:
        return None
    gs = f.getGlyphSet()
    upem = f["head"].unitsPerEm
    dx, dy = dirv
    ox, oy = org

    def inside(px, py):
        # 页面 -> 字形局部（先减原点，再反向旋转）
        rx, ry = px - ox, py - oy
        lx = rx * dx + ry * dy
        ly = -rx * dy + ry * dx
        # 局部 pt -> 字体单位（y 向上）
        ux = lx / size * upem
        uy = -ly / size * upem
        pen = PointInsidePen(gs, (ux, uy))
        try:
            gs[gname].draw(pen)
        except Exception:
            return False
        return bool(pen.getResult())

    return inside


def main():
    hits = json.load(io.open(HITS, encoding="utf-8"))
    rows = []
    for h in hits:
        ba, bb = h["boxa"], h["boxb"]
        if not ba or not bb:
            continue
        x0 = max(ba[0], bb[0]); x1 = min(ba[2], bb[2])
        y0 = max(ba[1], bb[1]); y1 = min(ba[3], bb[3])
        if x1 <= x0 or y1 <= y0:
            continue
        fa = inside_fn(h["ga"]["font"], h["ga"]["gid"], h["ca"],
                       h["ga"]["size"], h["ga"]["org"], h["ga"]["dir"])
        fb = inside_fn(h["gb"]["font"], h["gb"]["gid"], h["cb"],
                       h["gb"]["size"], h["gb"]["org"], h["gb"]["dir"])
        if fa is None or fb is None:
            rows.append((None, h, 0))
            continue
        nx = max(1, int(math.ceil((x1 - x0) / STEP)))
        ny = max(1, int(math.ceil((y1 - y0) / STEP)))
        cell = ((x1 - x0) / nx) * ((y1 - y0) / ny)
        n = 0
        for ix in range(nx):
            px = x0 + (ix + 0.5) * (x1 - x0) / nx
            for iy in range(ny):
                py = y0 + (iy + 0.5) * (y1 - y0) / ny
                if fa(px, py) and fb(py=py, px=px):
                    n += 1
        rows.append((n * cell, h, nx * ny))

    rows.sort(key=lambda r: (-1 if r[0] is None else r[0]), reverse=True)
    out = ["轮廓墨迹真实交叠面积（采样步长 %.2f pt）" % STEP,
           "包围盒相交只是必要条件；这里算的是**笔画填充区域**的真实公共面积。", ""]
    for area, h, ns in rows:
        if area is None:
            out.append("  [无法取样] p.%d '%s'×'%s'" % (h["page"], h["ca"], h["cb"]))
            continue
        out.append("  %8.3f pt²  p.%-4d '%s' × '%s'  盒重叠 %.1fx%.1f  %r × %r"
                   % (area, h["page"], h["ca"], h["cb"], h["ox"], h["oy"], h["ta"], h["tb"]))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(out))
    nz = sum(1 for a, _, _ in rows if a and a > 0.001)
    print("命中 %d 处；轮廓真实相交(>0.001pt²) %d 处 -> %s" % (len(rows), nz, OUT))


main()
