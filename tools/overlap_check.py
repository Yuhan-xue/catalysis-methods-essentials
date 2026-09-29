# -*- coding: utf-8 -*-
r"""全书叠印检查器 v3（结构判据，不依赖看图）。

三套判据
--------
A. **文字层：跨字形「墨迹盒」求交**（核心改进）
   旧判据用 PDF 文本层的**度量盒**：CJK 一律按 1 em 给盒、西文按字体盒给盒，
   于是 `−`（细横条，墨迹只有 0.052 em 高）、`］`（挤压到半宽但盒仍是 1 em）、
   上下标（盒子天然搭在底数上）这类会大量假报。实测旧判据 125 处里
   114 处属此类（只有 11 处是真叠印）。
   v3 改用**字形轮廓的真实墨迹盒**：从 TeX Live 的系统 OTF（与 PDF 内嵌子集
   同一套轮廓）用 fontTools 取 charstring 边界。字形必须按 **gid** 取——
   PDF 的 ToUnicode 会把多个字形映射到同一 unicode（数字的 `two.st` 变体、
   GlyphAssembly 拼装件 `minus.ex`/`uni20D7.lft`），Fandol 系还是 **CID 键**字体
   （PDF 的 gid 是 CID 不是序号）；按 unicode 取会取到别的字形，盒就错了。
   取到后按 span 的 dir 旋转、平移到页面，于是「盒相交」直接等于「墨迹相交」。

   两条判据：
     - **跨串**（两个不同字符串）：两方向重叠 > 1.2 pt 且交叠面积 ≥ 1 pt²
       → 报为叠印候选。用**绝对**面积而不是「占较小盒 x%」：实测相对判据会漏掉
       「两行字只压 2–3 pt」的部分压叠（p.143 `桥`×`移` 18.1 pt² 只占 42%）。
     - **同串**（一个字符串内部）：只作附注统计。这是字体自身的字距/斜体倾斜，
       任何用该字体的 LaTeX 文档都一样，靠移动图元改不掉。
   另排除：连字（各字符共用同一原点 = 同一个字形）、定界符零件拼接
   （OpenType MATH 的 GlyphAssembly 规定零件必须重叠）。

   最后一步：对每条候选用**轮廓真实相交面积**复核（tools/overlap_ink.py），
   把「盒相交但笔画不碰」的（积分号与积分限、斜体 f 与上下标）剔除。

B. **图形层：近似矩形相撞**
   只认**近似矩形**路径：取面积最大的闭合子路径，要求
   **面积 / 包围盒面积 ≥ 0.92**。旧判据取所有 drawing 的 `rect`，而那是
   非矩形路径（菱形、圆、箭头、括号、网格线）的**包围盒**——菱形 0.50、
   正六边形 0.75、圆 0.785，必然假报（图 0-1 的教训：99 处里 0 处是真矩形）。
   不能只认**精确**矩形：TikZ `node[draw, rounded corners=1pt]` 画出来是四段
   圆弧（比值 0.998），而图 0-1 那类缺陷正是圆角节点框，只认精确矩形会整类漏掉。
   三类判定：
     1) 嵌套：一个框的四条边都落在另一个内部（容差 3 pt）→ **正常**，排除；
     2) 相撞：两个框**都描边可见**且两方向重叠 > 2 pt 且非嵌套 → **缺陷**，报告；
     3) 装饰/背景：至少一方只有填充（无描边，如 pgfplots 背景块）→ 排除；
        一方是长细条（宽或高 < 6 pt，如坐标轴刻度带）→ 排除。

C. **粗线**：全书 > 2 pt 的粗横线 / 粗竖线。
   `\underbrace` 在 TeX Gyre Termes Math 下缺 U+23DF 字形时会**静默**退化成
   一条 4.48 pt 粗横条——文字层完全正常，只有矢量描边能查出来。
   判据：描边宽 > 2 pt 且包围盒高 < 1 pt 且宽 > 8 pt（横）；
         描边宽 > 2 pt 且包围盒宽 < 1 pt 且高 > 8 pt（竖）。
   另查**填充型粗条**：`re` 项厚度在 (2, 8) pt 之间且长度 > 8 pt
   （用于区分「图形里的实心条」与「字形退化成实心块」；实测 12 处全是前者）。

输出：tools/overlap_all.txt（明细）、tools/overlap_hits.json（供轮廓复核）
用法：python tools/overlap_check.py [pdf]

门禁模式（v4 新增，R2-W05）
============================

扫描模式只**报告**，恒返回 0；它不能当门禁用（命中相交矩形也照样 0）。门禁模式
把结果按**类别**分开，只对「确认应阻断」的一类设失败退出码：

    阻断（BLOCK）  graphics-collision              图形相撞：两个都描边、非嵌套、
                                                   两方向重叠 > 2 pt 的近似矩形。
                                                   —— 本项目已确认的缺陷形态
                                                   （图 0-1 圆角节点框互侵）。
    （--block-text 时另含 text-cross-unclassified，见下）

    候选（候选不阻断，分开报数）
                   text-cross-unclassified         跨串墨迹盒相交但**未归类**的候选。
                                                   真实本书有大量此类（文字轮廓、
                                                   斜体与箭头标注擦边），按总数一刀切
                                                   会把好稿子判死，故只报数。
                   text-script-sup / -sub          数学上下标：字号比 ≤ 0.85 且基线
                                                   错位 0.12–1.00 em（TeX 上下标
                                                   约 0.35 em）。分类可审计。
                   thick-hline / -vline / filled-bar  粗线/填充粗条（`\underbrace`
                                                   字形退化的监测项；实测本书 12 处
                                                   全是图形里的合法实心条）。
    豁免（记数，不入候选）
                   text-same-string                同一字符串内部（字体字距/斜体倾斜，
                                                   任何用该字体的文档都一样）。
                   nested-box                      合法嵌套：一个框的四条边都在另一个
                                                   内部（容差 3 pt）。
                   delimiter-piece                 MATH 定界符零件拼接（判据内已排除）。

**例外台账**（可审计）：`--exceptions tools/overlap_gate_exceptions.json`，JSON 数组，
每条 `{kind, page, boxes:[[x0,y0,x1,y1],[x0,y0,x1,y1]], reason, date, reviewer}`
（`kind ∈ {graphics-collision, text-cross-unclassified}`；box 匹配容差 0.5 pt，与顺序无关）。
缺 `reason`/`date`/`reviewer` 的条目**一律作废**（计入 invalid，不产生豁免）；
台帐里没有被命中的条目计入 unused（过期）并打印告警——不阻断，但必须可见。

退出码（**区分「没问题」与「没检查」**）：
    0 = PASS      没有阻断类命中（候选数照常分别报告）
    1 = BLOCK     有阻断类命中（扣掉例外台账里有效的条目后仍 > 0）
    2 = UNUSABLE  跑不起来：PDF 缺失/损坏、pymupdf 或 fontTools 缺失、参数错误、
                  或**有页面检查异常**（那意味着没检查，不是通过）
扫描模式：0 = 报告完成；2 = 有页面未能检查；**永不返回 1**（它只报告，不阻断）。

用法：
    python tools/overlap_check.py [pdf]                     # 扫描模式（只报告，退出码恒 0）
    python tools/overlap_check.py --gate [--pdf PDF] [--json OUT] [--exceptions FILE]
    python tools/overlap_check.py --gate --block-text       # 把未归类文字候选也计入阻断
    python tools/overlap_check.py --gate --status-file F    # 另写一行 ASCII 状态供脚本判读
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import sys
import traceback

_IMPORT_ERROR = None
try:
    import pymupdf
except Exception as _e:                           # pragma: no cover - 依赖缺失路径
    pymupdf = None
    _IMPORT_ERROR = "pymupdf 不可用：%s" % _e

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import inkbox                                    # noqa: E402
except Exception as _e:                           # pragma: no cover - 依赖缺失路径
    inkbox = None
    _IMPORT_ERROR = ((_IMPORT_ERROR + "；") if _IMPORT_ERROR else "") + \
                    "inkbox/fontTools 不可用：%s" % _e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "overlap_all.txt")

# ---- A 判据参数 ----
A_MIN_PT = 1.2        # 两方向都要超过（pt）
A_MIN_AREA = 1.0      # 交叠面积下限（pt²）。正文排版中相邻字形墨迹从不叠加，
                      # 1 pt² 已是肉眼可见的压叠（约 1×1 pt 的墨迹公共区）。
                      # v3 早期用过「占较小盒 45%」的**相对**判据，实测会漏掉
                      # 「两行字只压 2-3 pt」的部分压叠（如 p.143 桥×移 18.1pt²
                      # 只占 42% 而被漏掉）。改为绝对面积后不再漏。

# ---- B 判据参数 ----
B_MIN_PT = 2.0        # 两方向都要超过
B_NEST_TOL = 3.0      # 嵌套容差：四边都在对方内侧 3 pt 内即算嵌套
B_SLIVER = 6.0        # 长细条（刻度带 / 分隔条）最小边长

# ---- stretchy 定界符零件（TeX 用它们拼接高括号，零件之间**必须**重叠）----
DELIM_PIECES = set(range(0x239B, 0x23AE)) | set(range(0x23B0, 0x23B8))


def _rot(px, py, dx, dy):
    r"""字形局部坐标 (px,py)（x 沿基线、y 向下）-> 页面偏移。"""
    return (px * dx - py * dy, px * dy + py * dx)


def page_glyphs(page, unmapped):
    """返回所有字形的墨迹盒。"""
    out = []
    for sid, span in enumerate(page.get_texttrace()):
        font = span["font"]
        size = span["size"]
        dx, dy = span["dir"]
        txt = "".join(chr(c[0]) for c in span["chars"])
        is_delim = any(ord(c) in DELIM_PIECES for c in txt)
        for uni, gid, org, mbox in span["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            ink = inkbox.ink_bbox_gid(font, gid, c)
            ox, oy = org[0], org[1]
            if ink is None:
                # 取不到轮廓（字体未映射 / 空白字形）：退化为度量盒，并登记，不静默跳过
                if inkbox.font_path(font) is None:
                    unmapped.add((font, c))
                x0, y0, x1, y1 = mbox
            else:
                xs, ys = [], []
                for px, py in ((ink[0], ink[1]), (ink[0], ink[3]),
                               (ink[2], ink[1]), (ink[2], ink[3])):
                    rx, ry = _rot(px * size, py * size, dx, dy)
                    xs.append(ox + rx)
                    ys.append(oy + ry)
                x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
            if x1 - x0 <= 0 or y1 - y0 <= 0:
                continue
            out.append((x0, y0, x1, y1, c, font, txt, is_delim, uni,
                        (round(ox, 2), round(oy, 2)), gid, size, (dx, dy), sid))
    return out


def check_text(page, unmapped):
    r"""返回 (跨串命中, 同串命中)。

    **跨串**才算「叠印」：两个**不同的字符串**（不同的文字运行）互相侵入，
    这正是本项目已确认的缺陷形态（图 2-1：箭头标注 `衍射模式` 落进箱体标签
    `像平面：样品的放大像（实空间）`；图 0-1：同一父节点的多个子节点铺开互侵）。

    **同串**内的字形墨迹相碰不算：那是 TeX 在**一个字符串内部**的间距/字距
    （斜体倾斜、成对字距 kern）造成的，任何用该字体的 LaTeX 文档都一样，
    也无法靠移动图元修掉。这类单列一节如实报告，不静默丢弃。
    """
    gs = page_glyphs(page, unmapped)
    gs.sort(key=lambda g: g[0])
    cross, same = [], []
    for i in range(len(gs)):
        (ax0, ay0, ax1, ay1, ac, afont, atxt, adel, _,
         aorg, agid, asz, adir, asid) = gs[i]
        for j in range(i + 1, len(gs)):
            (bx0, by0, bx1, by1, bc, bfont, btxt, bdel, _,
             borg, bgid, bsz, bdir, bsid) = gs[j]
            if bx0 >= ax1 - A_MIN_PT:
                break
            # 连字：一个字形被 ToUnicode 展开成多个字符时，各字符**共用同一个原点**。
            # 它们不是叠印，是同一个字形（实测 Wulff / Teflon / Broekhoff 的 ff、fl、fi）。
            if aorg == borg:
                continue
            ox = min(ax1, bx1) - max(ax0, bx0)
            if ox <= A_MIN_PT:
                continue
            oy = min(ay1, by1) - max(ay0, by0)
            if oy <= A_MIN_PT:
                continue
            inter = ox * oy
            if inter < A_MIN_AREA:
                continue
            if adel and bdel:
                continue          # 定界符零件拼接：MATH 表规定零件必须重叠
            rec = (ac, bc, ox, oy, inter, atxt, btxt,
                   (ax0, ay0, ax1, ay1), (bx0, by0, bx1, by1),
                   (afont, agid, aorg, asz, adir), (bfont, bgid, borg, bsz, bdir))
            (same if asid == bsid else cross).append(rec)
    return cross, same


def _flatten(items):
    r"""把路径项摊平成子路径的点序列。

    'l' 直线取两端点；'re' 取四角；'qu' 取四角；'c' 三次贝塞尔按 t=0.25/0.5/0.75/1 采样
    （只为估面积，采样足够）。每遇「上一项终点 ≠ 本项起点」即断开为新子路径。
    """
    subs = []
    cur = []

    def push(p, q):
        nonlocal cur
        if cur and (abs(cur[-1][0] - p[0]) > 0.05 or abs(cur[-1][1] - p[1]) > 0.05):
            subs.append(cur)
            cur = []
        if not cur:
            cur.append(p)
        cur.append(q)

    for it in items:
        k = it[0]
        if k == "l":
            push((it[1].x, it[1].y), (it[2].x, it[2].y))
        elif k == "re":
            r = pymupdf.Rect(it[1])
            push((r.x0, r.y0), (r.x1, r.y0))
            push((r.x1, r.y0), (r.x1, r.y1))
            push((r.x1, r.y1), (r.x0, r.y1))
            push((r.x0, r.y1), (r.x0, r.y0))
        elif k == "qu":
            q = it[1]
            pts = [q.ul, q.ur, q.lr, q.ll]
            for a in range(4):
                p0, p1 = pts[a], pts[(a + 1) % 4]
                push((p0.x, p0.y), (p1.x, p1.y))
        elif k == "c":
            p0, p1, p2, p3 = it[1], it[2], it[3], it[4]
            prev = (p0.x, p0.y)
            for t in (0.25, 0.5, 0.75, 1.0):
                mt = 1 - t
                x = (mt ** 3 * p0.x + 3 * mt ** 2 * t * p1.x +
                     3 * mt * t ** 2 * p2.x + t ** 3 * p3.x)
                y = (mt ** 3 * p0.y + 3 * mt ** 2 * t * p1.y +
                     3 * mt * t ** 2 * p2.y + t ** 3 * p3.y)
                push(prev, (x, y))
                prev = (x, y)
    if cur:
        subs.append(cur)
    return subs


def _quasi_rect_of_items(items):
    r"""路径是否「近似矩形」；是则返回**面积最大的那条闭合子路径**的包围盒。

    为什么不能只认**精确**矩形：TikZ 的 `node[draw, rounded corners=1pt]` 画出来是
    四段圆弧，路径里全是 `c` 项。本项目已确认的缺陷形态之一——图 0-1 的
    `below left=<v> and <h> of <父节点>` 让同一父节点的多个子节点铺开互侵——
    正是**圆角节点框**；只认精确矩形会把这一类整个漏掉（本轮复核时发现并补上）。

    判据：面积最大的闭合子路径满足
      - 闭合（首末点重合），包围盒两边都 ≥ 6 pt；
      - **面积 / 包围盒面积 ≥ 0.92**。圆角矩形的比值 = 1 − (4−π)r²/(WH)：
        r = 1 pt、框 40×12 pt 时为 0.998。而菱形 0.50、圆/椭圆 0.785、
        正六边形 0.75、三角形 0.50 —— 旧判据的误报正是这些，全部被这一条挡掉。
    """
    best = None
    for pts in _flatten(items):
        if len(pts) < 4:
            continue
        x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts)
        y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)
        if x1 - x0 < 6 or y1 - y0 < 6:
            continue
        if abs(pts[0][0] - pts[-1][0]) > 0.5 or abs(pts[0][1] - pts[-1][1]) > 0.5:
            continue
        area = 0.0
        for i in range(len(pts) - 1):
            area += pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
        area = abs(area) / 2.0
        bbox_area = (x1 - x0) * (y1 - y0)
        if bbox_area <= 0 or area / bbox_area < 0.92:
            continue
        if best is None or area > best[1]:
            best = (pymupdf.Rect(x0, y0, x1, y1), area)
    return best[0] if best else None


def check_graphics(page):
    rects = []
    for dr in page.get_drawings():
        r = _quasi_rect_of_items(dr.get("items") or [])
        if r is None:
            continue
        w, h = r.width, r.height
        if w < 6 or h < 6:
            continue
        stroked = dr.get("color") is not None and (dr.get("width") or 0) > 0
        filled = dr.get("fill") is not None
        if not (stroked or filled):
            continue
        rects.append((r, stroked, filled))
    rects.sort(key=lambda t: (t[0].x0, t[0].y0))
    hits = []
    nested = 0
    for i in range(len(rects)):
        ra, sa, fa = rects[i]
        for j in range(i + 1, len(rects)):
            rb, sb, fb = rects[j]
            if rb.x0 >= ra.x1 - B_MIN_PT:
                break
            ox = min(ra.x1, rb.x1) - max(ra.x0, rb.x0)
            oy = min(ra.y1, rb.y1) - max(ra.y0, rb.y0)
            if ox <= B_MIN_PT or oy <= B_MIN_PT:
                continue
            # 1) 嵌套（任一方向被完整包含）
            if (rb.x0 >= ra.x0 - B_NEST_TOL and rb.x1 <= ra.x1 + B_NEST_TOL and
                    rb.y0 >= ra.y0 - B_NEST_TOL and rb.y1 <= ra.y1 + B_NEST_TOL) or \
               (ra.x0 >= rb.x0 - B_NEST_TOL and ra.x1 <= rb.x1 + B_NEST_TOL and
                    ra.y0 >= rb.y0 - B_NEST_TOL and ra.y1 <= rb.y1 + B_NEST_TOL):
                nested += 1
                continue
            # 3) 装饰/背景：有一方无描边（纯填充块）
            if not (sa and sb):
                continue
            # 3) 长细条（刻度带、分隔条）不算框
            if min(ra.width, ra.height) < B_SLIVER or min(rb.width, rb.height) < B_SLIVER:
                continue
            hits.append((ra, rb, ox, oy))
    return hits, nested


def check_thick(page):
    hz, vt, bar = [], [], []
    for dr in page.get_drawings():
        r = dr["rect"]
        wdt = dr.get("width") or 0
        if wdt > 2 and r.height < 1 and r.width > 8:
            hz.append((r, wdt))
        if wdt > 2 and r.width < 1 and r.height > 8:
            vt.append((r, wdt))
        for it in (dr.get("items") or []):
            if it[0] != "re":
                continue
            rr = pymupdf.Rect(it[1])
            if rr.width > 8 and 2 < rr.height < 8:
                bar.append((rr, rr.height))
            if rr.height > 8 and 2 < rr.width < 8:
                bar.append((rr, rr.width))
    return hz, vt, bar


# ---- 门禁模式参数（R2-W05）----
_SCRIPT_SIZE_RATIO = 0.85     # 上下标：小/大字号比上限（TeX \scriptstyle ≈ 0.7 em）
_SCRIPT_RAISE = (0.12, 1.00)  # 上下标：基线错位 / 大字号（em）。TeX 上下标 ≈ 0.35 em
_EXC_TOL = 0.5                # 例外台账 box 匹配容差（pt）
GATE_MAX_HITS = 500           # 结构化输出里每类最多收录多少条（防病态膨胀）
BLOCKING_KINDS = ("graphics-collision", "text-cross-unclassified")


class GateUnusable(Exception):
    """跑不起来（**不是**「没问题」）：PDF 缺失/损坏、依赖缺失、页面检查异常等。"""


def parse_args(argv):
    p = argparse.ArgumentParser(prog="overlap_check.py", add_help=True,
                                description="全书叠印检查器（扫描模式 / 门禁模式）")
    p.add_argument("pdf", nargs="?", default=None,
                   help="目标 PDF（扫描模式的位置参数，兼容旧的 `overlap_check.py <pdf>` 用法）")
    p.add_argument("--pdf", dest="pdf_opt", default=None, help="目标 PDF（显式选项，优先于位置参数）")
    p.add_argument("--gate", action="store_true", help="门禁模式：按类别判定并设失败退出码")
    p.add_argument("--block-text", dest="block_text", action="store_true",
                   help="把「未归类的跨串文字候选」也计入阻断（默认只阻断图形相撞）")
    p.add_argument("--out", default=None, help="明细报告路径（默认 tools/overlap_all.txt）")
    p.add_argument("--json", dest="json_path", default=None,
                   help="结构化结果路径（扫描模式默认 tools/overlap_hits.json；门禁模式 tools/overlap_gate.json）")
    p.add_argument("--exceptions", default=None, help="例外台账 JSON（默认 tools/overlap_gate_exceptions.json）")
    p.add_argument("--status-file", dest="status_file", default=None,
                   help="另写一行 ASCII 状态（overlap gate: PASS|BLOCK|UNUSABLE）供发布脚本判读")
    return p.parse_args(argv if argv is not None else [])


def classify_cross(ga, gb):
    r"""跨串墨迹命中是否属于「数学上下标」。

    两条都要满足：
      1) 两侧字号不同且 小/大 ≤ 0.85（TeX 上下标用 \scriptstyle，约 0.7 em）；
      2) 小字号基线相对大字号基线**竖直错位** 0.12–1.00 em（按大字号计）——
         TeX 上标抬升、下标下沉都在 0.35 em 量级，0.12 em 是肉眼可辨的下限。
    只对横排文字（span 的 dir 竖直分量 ≈ 0）作此判定，旋转文字一律归为未归类。

    **这只是分类，不是免罪**：未归类候选默认也不阻断（真实本书这类候选很多），
    只有 --block-text 才把未归类候选计入阻断；上下标单独成类是为了让候选数
    可审计、不混成一锅。
    """
    if not ga or not gb:
        return "cross-other"
    _fa, _gida, aorg, asz, adir = ga
    _fb, _gidb, borg, bsz, bdir = gb
    if abs(adir[1]) > 0.05 or abs(bdir[1]) > 0.05:
        return "cross-other"
    big = asz if asz >= bsz else bsz
    small = bsz if asz >= bsz else asz
    if big <= 0 or abs(asz - bsz) < 1e-6 or small / big > _SCRIPT_SIZE_RATIO:
        return "cross-other"
    dy = aorg[1] - borg[1]                     # y 轴向下：dy < 0 表示 A 更靠上
    if not (_SCRIPT_RAISE[0] * big <= abs(dy) <= _SCRIPT_RAISE[1] * big):
        return "cross-other"
    sup = (asz < bsz and dy < 0) or (bsz < asz and dy > 0)
    return "script-sup" if sup else "script-sub"


def _exc_box(v):
    return tuple(round(float(x), 3) for x in v)


def load_exceptions(path):
    r"""读例外台账，返回 (有效条目, 作废条目)。

    作废 = 结构或字段不合格（**绝不产生豁免**）：kind 不在 BLOCKING_KINDS、
    page 不是 ≥1 的整数、boxes 不是两条 4 数字数组、缺 reason / date / reviewer。
    例外必须写明「为什么可接受、哪天、谁确认的」——否则它就不是审计记录。
    """
    valid, invalid = [], []
    if not path or not os.path.exists(path):
        return valid, invalid
    try:
        raw = json.loads(io.open(path, encoding="utf-8").read())
    except Exception as e:
        return [], [{"index": None, "error": "台账无法解析：%s" % e, "record": None}]
    if not isinstance(raw, list):
        return [], [{"index": None, "error": "台账必须是 JSON 数组", "record": None}]
    for i, rec in enumerate(raw):
        err = None
        if not isinstance(rec, dict):
            err = "条目不是对象"
        elif rec.get("kind") not in BLOCKING_KINDS:
            err = "kind 必须是 %s 之一" % " / ".join(BLOCKING_KINDS)
        elif not isinstance(rec.get("page"), int) or rec.get("page") < 1:
            err = "page 必须是 ≥1 的整数"
        elif not isinstance(rec.get("boxes"), list) or len(rec["boxes"]) != 2:
            err = "boxes 必须是两条 [x0,y0,x1,y1]"
        else:
            try:
                rec["boxes"] = [_exc_box(b) for b in rec["boxes"]]
            except Exception as e:
                err = "boxes 不是数字：%s" % e
        if err is None and not str(rec.get("reason") or "").strip():
            err = "缺 reason（例外必须写明理由）"
        if err is None and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(rec.get("date") or "")):
            err = "缺 date（YYYY-MM-DD）"
        if err is None and not str(rec.get("reviewer") or "").strip():
            err = "缺 reviewer（谁确认的）"
        if err:
            invalid.append({"index": i, "error": err, "record": rec})
        else:
            valid.append(rec)
    return valid, invalid


def _match_exception(exceptions, kind, page, boxes):
    r"""命中是否有台账例外（同 kind、同页、两条 box 与顺序无关、容差 _EXC_TOL）。"""
    want = sorted(tuple(b) for b in boxes)
    if len(want) != 2:
        return None
    for rec in exceptions:
        if rec.get("_used"):
            continue
        if rec["kind"] != kind or rec["page"] != page:
            continue
        got = sorted(tuple(b) for b in rec["boxes"])
        if all(all(abs(a - b) <= _EXC_TOL for a, b in zip(g, w)) for g, w in zip(got, want)):
            return rec
    return None


def _status_line(mode, status, blocking, candidates):
    return "overlap %s: %s blocking=%d candidates=%d" % (mode, status, blocking, candidates)


def _ensure_parent(path):
    """输出目录不存在就建出来（探针/CI 常把输出重定向到全新目录）。"""
    if not path:
        return
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        os.makedirs(parent)


def write_status_file(path, line, blocking, candidates, exit_code, reason=""):
    r"""给发布脚本（build.ps1）判读的 ASCII 状态文件——绕开控制台编码。"""
    if not path:
        return
    _ensure_parent(path)
    io.open(path, "w", encoding="utf-8").write(
        "%s\nblocking=%d\ncandidates=%d\nexit_code=%d\n%s"
        % (line, blocking, candidates, exit_code,
           ("reason=%s\n" % reason) if reason else ""))


def _cap(items):
    return {"n": len(items), "truncated": len(items) > GATE_MAX_HITS,
            "items": items[:GATE_MAX_HITS]}


def main(argv=None):
    args = parse_args(argv)
    gate = bool(args.gate)
    mode = "gate" if gate else "scan"
    out_path = args.out or OUT
    json_path = args.json_path or os.path.join(
        ROOT, "tools", "overlap_gate.json" if gate else "overlap_hits.json")
    result = {
        "tool": "tools/overlap_check.py",
        "mode": mode,
        "gate": gate,
        "block_text": bool(args.block_text),
        "pdf": None,
        "pages": None,
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "UNUSABLE",
        "exit_code": 2,
        "blocking": {},
        "blocking_total": 0,
        "candidates": {},
        "candidate_total": 0,
        "exempt": {},
        "exceptions": {"path": None, "provided": False, "valid": 0, "used": [],
                       "unused": [], "invalid": []},
        "page_errors": [],
        "errors": [],
        "hits": {},
        "out": out_path,
        "json": json_path,
    }
    try:
        return _run(args, gate, out_path, json_path, result)
    except GateUnusable as exc:
        result["errors"].append(str(exc))
    except Exception:
        result["errors"].append(traceback.format_exc())
        sys.stderr.write(result["errors"][-1])
    result["status"] = "UNUSABLE"
    result["exit_code"] = 2
    first = result["errors"][0].strip().splitlines()[-1] if result["errors"] else "未知原因"
    line = _status_line(mode, "UNUSABLE", 0, 0)
    print(line)
    print("  原因：%s" % first)
    if gate:
        _ensure_parent(json_path)
        io.open(json_path, "w", encoding="utf-8").write(
            json.dumps(result, ensure_ascii=False, indent=1))
    write_status_file(args.status_file, line, 0, 0, 2, first)
    return result


def _run(args, gate, out_path, json_path, result):
    if _IMPORT_ERROR:
        raise GateUnusable("依赖缺失：%s" % _IMPORT_ERROR)
    pdf_path = os.path.abspath(args.pdf_opt or args.pdf or PDF)
    result["pdf"] = pdf_path
    if not os.path.exists(pdf_path):
        raise GateUnusable("PDF 不存在：%s" % pdf_path)
    st = os.stat(pdf_path)
    result["pdf_bytes"] = st.st_size
    result["pdf_mtime"] = datetime.datetime.fromtimestamp(
        st.st_mtime).astimezone().isoformat(timespec="seconds")
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        raise GateUnusable("PDF 打不开：%s" % e)
    if doc.page_count <= 0:
        raise GateUnusable("PDF 页数为 0：%s" % pdf_path)
    result["pages"] = doc.page_count
    lines = [f"file={pdf_path}  pages={doc.page_count}", ""]
    lines.append("判据 A（文字/墨迹盒级）：**跨串**（两个不同字符串）、两方向重叠 > %.1f pt、"
                 "交叠面积 ≥ %.1f pt²" % (A_MIN_PT, A_MIN_AREA))
    lines.append("判据 B（图形/真矩形）：两侧均描边、非嵌套（容差 %.0f pt）、两方向重叠 > %.1f pt、"
                 "最短边 ≥ %.0f pt" % (B_NEST_TOL, B_MIN_PT, B_SLIVER))
    lines.append("判据 C（粗线）：描边宽 > 2 pt 且包围盒 < 1 pt 厚、长 > 8 pt；另含填充型粗条")
    lines.append("")

    unmapped = set()
    nA = nA2 = nB = nHZ = nVT = nBAR = 0
    tot_nested = 0
    page_hits = []
    same_rows = []
    same_hits = []
    cat = collections.Counter()          # 跨串候选的分类计数
    block_hits = []                      # 阻断类命中（结构化）
    cand_text_other = []                 # 未归类跨串候选（默认不阻断）
    cand_text_script = []                # 数学上下标候选（单独成类）
    thick_hits = []                      # 粗线 / 填充粗条（候选）
    page_errors = []                     # 页面检查异常（= 没检查，不是通过）

    for pno in range(doc.page_count):
        page = doc[pno]
        try:
            ha, hs = check_text(page, unmapped)
        except Exception as e:
            ha, hs = [], []
            page_errors.append({"page": pno + 1, "check": "text",
                                "error": "%s: %s" % (type(e).__name__, e)})
        try:
            hb, nested = check_graphics(page)
        except Exception as e:
            hb, nested = [], 0
            page_errors.append({"page": pno + 1, "check": "graphics",
                                "error": "%s: %s" % (type(e).__name__, e)})
        try:
            hz, vt, bar = check_thick(page)
        except Exception as e:
            hz, vt, bar = [], [], []
            page_errors.append({"page": pno + 1, "check": "thick",
                                "error": "%s: %s" % (type(e).__name__, e)})
        tot_nested += nested
        if not (ha or hs or hb or hz or vt or bar):
            continue
        lines.append("===== p.%d =====" % (pno + 1))
        for ac, bc, ox, oy, inter, atxt, btxt, abox, bbox, ga, gb in ha:
            nA += 1
            page_hits.append(dict(page=pno + 1, ca=ac, cb=bc, ox=ox, oy=oy, inter=inter,
                                  ta=atxt, tb=btxt,
                                  boxa=list(abox) if abox else None,
                                  boxb=list(bbox) if bbox else None,
                                  ga=dict(font=ga[0], gid=ga[1], org=list(ga[2]),
                                          size=ga[3], dir=list(ga[4])),
                                  gb=dict(font=gb[0], gid=gb[1], org=list(gb[2]),
                                          size=gb[3], dir=list(gb[4]))))
            lines.append("  [A/跨串] %r × %r  盒重叠 %.1fx%.1f pt  面积 %.2f pt²"
                         % (ac, bc, ox, oy, inter))
            lines.append("        串A=%r 墨迹盒=[%.1f,%.1f,%.1f,%.1f]" % (atxt, *abox))
            lines.append("        串B=%r 墨迹盒=[%.1f,%.1f,%.1f,%.1f]" % (btxt, *bbox))
            kind = classify_cross(ga, gb)
            cat[kind] += 1
            rec_a = dict(page=pno + 1, kind=kind, ca=ac, cb=bc, ox=round(ox, 2),
                         oy=round(oy, 2), inter=round(inter, 2), ta=atxt, tb=btxt,
                         boxa=list(abox) if abox else None,
                         boxb=list(bbox) if bbox else None,
                         size_a=ga[3], size_b=gb[3],
                         dorg_y=round(ga[2][1] - gb[2][1], 2))
            if kind == "cross-other":
                cand_text_other.append(rec_a)
                lines.append("        分类：未归类跨串候选（默认不阻断；--block-text 时计入阻断）")
            else:
                cand_text_script.append(rec_a)
                lines.append("        分类：数学%s（字号 %.2f ↔ %.2f，基线错位 %.2f pt，免阻断）"
                             % ("上标" if kind == "script-sup" else "下标",
                                ga[3], gb[3], abs(ga[2][1] - gb[2][1])))
        for ac, bc, ox, oy, inter, atxt, btxt, abox, bbox, ga, gb in hs:
            nA2 += 1
            same_rows.append((pno + 1, ac, bc, ox, oy, inter, atxt))
            same_hits.append(dict(page=pno + 1, ca=ac, cb=bc, ox=ox, oy=oy, inter=inter,
                                  ta=atxt, tb=btxt, kind="same",
                                  boxa=list(abox) if abox else None,
                                  boxb=list(bbox) if bbox else None,
                                  ga=dict(font=ga[0], gid=ga[1], org=list(ga[2]),
                                          size=ga[3], dir=list(ga[4])),
                                  gb=dict(font=gb[0], gid=gb[1], org=list(gb[2]),
                                          size=gb[3], dir=list(gb[4]))))
        for ra, rb, ox, oy in hb:
            nB += 1
            lines.append("  [B/相撞] 框[%.1f,%.1f,%.1f,%.1f] 与 [%.1f,%.1f,%.1f,%.1f] 重叠 %.1fx%.1f pt"
                         % (ra.x0, ra.y0, ra.x1, ra.y1, rb.x0, rb.y0, rb.x1, rb.y1, ox, oy))
            block_hits.append(dict(
                page=pno + 1, kind="graphics-collision",
                boxa=[round(ra.x0, 2), round(ra.y0, 2), round(ra.x1, 2), round(ra.y1, 2)],
                boxb=[round(rb.x0, 2), round(rb.y0, 2), round(rb.x1, 2), round(rb.y1, 2)],
                ox=round(ox, 2), oy=round(oy, 2), inter=round(ox * oy, 2)))
        for r, w in hz:
            nHZ += 1
            lines.append("  [C/粗横线] %.2f pt  [%.1f,%.1f]→[%.1f,%.1f]" % (w, r.x0, r.y0, r.x1, r.y1))
            thick_hits.append(dict(page=pno + 1, kind="thick-hline", width=round(w, 2),
                                   box=[round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]))
        for r, w in vt:
            nVT += 1
            lines.append("  [C/粗竖线] %.2f pt  [%.1f,%.1f]→[%.1f,%.1f]" % (w, r.x0, r.y0, r.x1, r.y1))
            thick_hits.append(dict(page=pno + 1, kind="thick-vline", width=round(w, 2),
                                   box=[round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]))
        for r, t in bar:
            nBAR += 1
            lines.append("  [C/填充粗条] 厚 %.2f pt  [%.1f,%.1f,%.1f,%.1f]" % (t, r.x0, r.y0, r.x1, r.y1))
            thick_hits.append(dict(page=pno + 1, kind="filled-bar", width=round(t, 2),
                                   box=[round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]))

    lines.append("")
    if same_rows:
        lines.append("附：**同串内**字形墨迹相碰 %d 处（不算叠印：是一个字符串内部由字体"
                     "字距/斜体倾斜造成，任何用该字体的 LaTeX 文档都一样，无法靠移动图元修掉）"
                     % len(same_rows))
        agg = collections.Counter((r[1], r[2], r[6]) for r in same_rows)
        for (ca, cb, t), n in agg.most_common():
            lines.append("    %r × %r  出现在 %r  共 %d 处" % (ca, cb, t, n))
        lines.append("")
    if unmapped:
        lines.append("未能取到字形轮廓（退化为度量盒）的字体/字符 %d 种：" % len(unmapped))
        for f, c in sorted(unmapped)[:40]:
            lines.append("    %s  %r U+%04X" % (f, c, ord(c)))
        lines.append("")
    lines.append("合计：文字级（跨串）%d 处，同串内墨迹相碰 %d 处，图形级 %d 处，"
                 "粗横线 %d 处，粗竖线 %d 处，填充粗条 %d 处"
                 % (nA, nA2, nB, nHZ, nVT, nBAR))
    lines.append("（图形级另排除「嵌套」%d 对）" % tot_nested)
    if page_errors:
        lines.append("")
        lines.append("**检查异常 %d 处（未能检查 ≠ 通过）**：" % len(page_errors))
        for pe in page_errors:
            lines.append("    p.%s 的 %s 检查异常：%s" % (pe["page"], pe["check"], pe["error"]))

    # ---- 例外台账：只有写明理由+日期+确认人的例外才能免阻断（可审计）----
    exc_path = args.exceptions or os.path.join(ROOT, "tools", "overlap_gate_exceptions.json")
    exc_valid, exc_invalid = load_exceptions(exc_path)
    raw_blocking = list(block_hits)
    if gate and args.block_text:
        raw_blocking += cand_text_other
    effective = []
    exc_used = []
    for rec in raw_blocking:
        m = _match_exception(exc_valid, rec["kind"], rec["page"], (rec["boxa"], rec["boxb"]))
        if m is None:
            effective.append(dict(rec))
        else:
            m["_used"] = True
            exc_used.append(dict(rec, exception=m.get("reason", "")))
    exc_unused = [m for m in exc_valid if not m.get("_used")]

    # ---- 判定与退出码：区分「没问题」与「没检查」----
    blocking_by_kind = collections.Counter(r["kind"] for r in effective)
    candidate_total = len(cand_text_other) + len(cand_text_script) + len(thick_hits)
    if page_errors:
        status, exit_code = "UNUSABLE", 2
    elif gate and effective:
        status, exit_code = "BLOCK", 1
    else:
        status, exit_code = "PASS", 0
    if gate:
        lines.append("")
        lines.append("===== 门禁（--gate）=====")
        lines.append("  阻断（扣掉有效例外后）%d 处%s" % (
            len(effective),
            "：" + "、".join("%s %d" % kv for kv in sorted(blocking_by_kind.items()))
            if effective else "（无）"))
        lines.append("  候选（默认不阻断，分类报告）%d 处：未归类跨串 %d、数学上标 %d、数学下标 %d、"
                     "粗横线 %d、粗竖线 %d、填充粗条 %d"
                     % (candidate_total, len(cand_text_other), cat["script-sup"], cat["script-sub"],
                        nHZ, nVT, nBAR))
        lines.append("  豁免（记数不阻断）%d 处：同串内墨迹相碰 %d、合法嵌套框 %d"
                     % (nA2 + tot_nested, nA2, tot_nested))
        lines.append("  例外台账：%s（有效 %d、本次命中 %d、过期 %d、作废 %d）"
                     % (exc_path if os.path.exists(exc_path) else "未提供（" + exc_path + " 不存在）",
                        len(exc_valid), len(exc_used), len(exc_unused), len(exc_invalid)))
        for m in exc_unused:
            lines.append("    ! 过期例外（台账里有、本次没命中）：p.%s %s" % (m.get("page"), m.get("kind")))
        for m in exc_invalid:
            lines.append("    x 作废例外（字段不合格，不产生豁免）：#%s %s" % (m.get("index"), m.get("error")))
        lines.append("  结论：%s（退出码 %d）—— %s" % (
            status, exit_code,
            {"PASS": "没有确认缺陷类命中（候选数照常报告，见上）",
             "BLOCK": "命中确认缺陷类，必须处理或登记可审计的例外",
             "UNUSABLE": "有页面未能检查，不可当作通过"}[status]))
    _ensure_parent(out_path)
    io.open(out_path, "w", encoding="utf-8").write("\n".join(lines))
    if gate:
        result.update(
            status=status, exit_code=exit_code,
            blocking=dict(blocking_by_kind), blocking_total=len(effective),
            candidates={"text-cross-unclassified": len(cand_text_other),
                        "text-script-sup": cat["script-sup"], "text-script-sub": cat["script-sub"],
                        "thick-hline": nHZ, "thick-vline": nVT, "filled-bar": nBAR},
            candidate_total=candidate_total,
            exempt={"text-same-string": nA2, "nested-box": tot_nested},
            exceptions={"path": exc_path, "provided": os.path.exists(exc_path),
                        "valid": len(exc_valid), "used": _cap(exc_used),
                        "unused": _cap(exc_unused), "invalid": _cap(exc_invalid)},
            page_errors=_cap(page_errors),
            hits={"graphics-collision": _cap(block_hits),
                  "text-cross-unclassified": _cap(cand_text_other),
                  "text-script": _cap(cand_text_script),
                  "thick": _cap(thick_hits)})
        _ensure_parent(json_path)
        io.open(json_path, "w", encoding="utf-8").write(
            json.dumps(result, ensure_ascii=False, indent=1))
    else:
        result.update(
            status=status, exit_code=exit_code,
            candidates={"text-cross-unclassified": len(cand_text_other),
                        "text-script-sup": cat["script-sup"], "text-script-sub": cat["script-sub"],
                        "thick-hline": nHZ, "thick-vline": nVT, "filled-bar": nBAR},
            candidate_total=candidate_total,
            exempt={"text-same-string": nA2, "nested-box": tot_nested},
            page_errors=_cap(page_errors))
        _ensure_parent(json_path)
        io.open(json_path, "w", encoding="utf-8").write(
            json.dumps(page_hits + same_hits, ensure_ascii=False, indent=1))
    print("文字级(跨串) %d  同串 %d  图形级 %d  粗横线 %d  粗竖线 %d  填充粗条 %d  嵌套已排除 %d"
          % (nA, nA2, nB, nHZ, nVT, nBAR, tot_nested))
    print("->", out_path)
    line = _status_line("gate" if gate else "scan", status,
                        len(effective) if gate else 0, candidate_total)
    print(line)
    write_status_file(args.status_file, line, len(effective) if gate else 0, candidate_total,
                      exit_code, "；".join(str(e) for e in result.get("errors", []))[:200])
    return result


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]).get("exit_code", 2))
