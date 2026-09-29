# -*- coding: utf-8 -*-
r"""全书重叠检查器：找出「真的会被看出来的重叠」。

前几代检测器的教训（本项目实测）：
  1. 用 **span/行级包围盒** 会把相邻单元格、相邻文字误判为重叠（211 处误报）。
  2. 用 **包围盒** 判断**非矩形节点**（菱形、圆）会误报——菱形包围盒含大片空白角。
     图 0-1 修好后仍有 3 对「重叠」，排除菱形后其实为 0。
  3. CJK 标点的字身盒是**全宽**而推进宽度是**半宽**，会被误判成与邻居重叠。

因此本检查器用两套判据，各自只看**确实会叠印**的情形：

  A. 字符级：两个**字形包围盒**重叠面积同时超过「双方各自面积的 45%」且两个方向都 >1.2pt。
     正常排版中相邻字形的盒子不会这样重叠；只有真正叠印才会。
     排除 CJK 标点（全宽盒 / 半宽推进）。
  B. 图形级：只取**类矩形**路径（宽高都 >15pt 且长宽比在 0.25—4 之间，
     以排除长横线、箭头、菱形），两两求交，两个方向重叠都 >2pt。
"""
import io, os, sys, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "overlap_all.txt")

# CJK 标点与全角符号：字身盒全宽、推进半宽，必然与邻居「重叠」，须排除
CJK_PUNCT = set(
    "，。、；：？！（）【】《》〈〉「」『』〔〕—…·　"
    "“”‘’％＋－＝／＼｜"
)

MIN_OVERLAP = 1.2      # pt，两个方向都要超过
FRAC = 0.45            # 重叠面积 / 较小盒面积


def char_overlaps(page):
    hits = []
    chars = []
    for b in page.get_text("rawdict")["blocks"]:
        if b.get("type") != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                for ch in s["chars"]:
                    c = ch["c"]
                    if not c.strip() or c in CJK_PUNCT:
                        continue
                    o = ord(c)
                    # 拉伸定界符的「零件」（??? ??? ???? 等 U+239B-U+23AD）：
                    # 它们本来就是一节一节拼起来的，零件盒相邻甚至相接，属正常。
                    if 0x239B <= o <= 0x23AD or 0x23B0 <= o <= 0x23B7:
                        continue
                    x0, y0, x1, y1 = ch["bbox"]
                    if x1 - x0 <= 0 or y1 - y0 <= 0:
                        continue
                    chars.append((x0, y0, x1, y1, c))
    # 按 x 排序后只在邻域内比较，避免 O(n^2)
    chars.sort(key=lambda t: t[0])
    for i in range(len(chars)):
        ax0, ay0, ax1, ay1, ac = chars[i]
        for j in range(i + 1, len(chars)):
            bx0, by0, bx1, by1, bc = chars[j]
            if bx0 >= ax1 - MIN_OVERLAP:
                break
            ox = min(ax1, bx1) - max(ax0, bx0)
            if ox <= MIN_OVERLAP:
                continue
            oy = min(ay1, by1) - max(ay0, by0)
            if oy <= MIN_OVERLAP:
                continue
            area_o = ox * oy
            area_a = (ax1 - ax0) * (ay1 - ay0)
            area_b = (bx1 - bx0) * (by1 - by0)
            if area_o >= FRAC * min(area_a, area_b):
                hits.append((f"字符 '{ac}' × '{bc}'", ox, oy))
    return hits


def rect_overlaps(page):
    rects = []
    for dr in page.get_drawings():
        r = dr["rect"]
        w, h = r.width, r.height
        if w < 15 or h < 15:
            continue
        ratio = w / h if h else 99
        if not (0.25 <= ratio <= 4):
            continue          # 排除长横线/长竖线/极端扁长形
        rects.append((r.x0, r.y0, r.x1, r.y1))
    rects = sorted(set(rects))
    hits = []
    for i in range(len(rects)):
        ax0, ay0, ax1, ay1 = rects[i]
        area_a = (ax1 - ax0) * (ay1 - ay0)
        for j in range(i + 1, len(rects)):
            bx0, by0, bx1, by1 = rects[j]
            if bx0 >= ax1 - 2:
                break
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox <= 2 or oy <= 2:
                continue
            area_b = (bx1 - bx0) * (by1 - by0)
            inter = ox * oy
            # 【关键过滤】排除「包含关系」：一个框整个落在另一个框里面，
            # 这是**正常**的（如 pgfplots 的坐标轴外框 + 绘图区内框、背景矩形），
            # 不加这条会产出成百上千条误报（实测 p.8 单页 21 条全是这类）。
            if inter >= 0.95 * min(area_a, area_b):
                continue
            if inter <= 0.02 * max(area_a, area_b):
                continue      # 仅仅擦边
            # 尺寸必须相近：框与框相撞才是叠印；大框套小装饰件不是。
            if not (0.34 <= area_a / area_b <= 2.9):
                continue
            hits.append((f"框 [{ax0:.0f},{ay0:.0f},{ax1:.0f},{ay1:.0f}] 与 [{bx0:.0f},{by0:.0f},{bx1:.0f},{by1:.0f}]", ox, oy))
    return hits


doc = pymupdf.open(PDF)
lines = [f"file={PDF}  pages={doc.page_count}", ""]
nchar = nrect = 0
for pno in range(doc.page_count):
    page = doc[pno]
    try:
        ch = char_overlaps(page)
    except Exception as e:
        ch = [(f"<检查异常 {e}>", 0, 0)]
    rc = rect_overlaps(page)
    if ch or rc:
        lines.append(f"===== p.{pno + 1} =====")
        for d, ox, oy in ch:
            lines.append(f"  [字符] {d}  重叠 {ox:.1f}x{oy:.1f} pt")
            nchar += 1
        for d, ox, oy in rc:
            lines.append(f"  [图形] {d}  重叠 {ox:.1f}x{oy:.1f} pt")
            nrect += 1
lines.append("")
lines.append(f"合计：字符级 {nchar} 处，图形级 {nrect} 处")
io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"字符级 {nchar} 处，图形级 {nrect} 处 -> {OUT}")
