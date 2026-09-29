# -*- coding: utf-8 -*-
r"""诊断：给出**每一处字符级命中的完整上下文**，供逐条判定真伪。

对 rawdict 里的每个字形，记录：字符、度量盒、原点、字号、字体、所属
block/line/span 序号、span 文本。命中按「同 span / 跨 span」「是否标点」
自动分档，并打印可判定的特征（字号比、基线差、包含率）。

用法：python tools/overlap_ctx.py [pdf] > out.txt
"""
import io, os, sys, collections
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "main.pdf")
OUT = os.path.join(ROOT, "tools", "overlap_ctx.txt")

MIN_OVERLAP = 1.2
FRAC = 0.45

CJK_PUNCT = set(
    "，。、；：？！（）【】《》〈〉「」『』〔〕—…·　"
    "“”‘’％＋－＝／＼｜"
)

ROLE = {}

NONPUNCT_ONLY = len(sys.argv) > 2 and sys.argv[2] == "nonpunct"


def build(page):
    """返回字形列表：dict(c, bbox, org, size, font, bi, li, si, stext)"""
    glyphs = []
    d = page.get_text("rawdict")
    for bi, b in enumerate(d["blocks"]):
        if b.get("type") != 0:
            continue
        for li, l in enumerate(b["lines"]):
            for si, s in enumerate(l["spans"]):
                stext = "".join(c["c"] for c in s["chars"])
                for ch in s["chars"]:
                    c = ch["c"]
                    if not c.strip():
                        continue
                    x0, y0, x1, y1 = ch["bbox"]
                    if x1 - x0 <= 0 or y1 - y0 <= 0:
                        continue
                    glyphs.append(dict(c=c, bbox=(x0, y0, x1, y1), org=ch["origin"],
                                       size=s["size"], font=s["font"], bi=bi, li=li,
                                       si=si, stext=stext))
    return glyphs


doc = pymupdf.open(PDF)
out = [f"file={PDF} pages={doc.page_count}",
       f"判据：面积重叠 >= {FRAC} × 较小盒，两方向 > {MIN_OVERLAP} pt", ""]
stat = collections.Counter()
per_page = []

for pno in range(doc.page_count):
    page = doc[pno]
    gs = build(page)
    gs.sort(key=lambda g: g["bbox"][0])
    hits = []
    for i in range(len(gs)):
        a = gs[i]
        ax0, ay0, ax1, ay1 = a["bbox"]
        aa = (ax1 - ax0) * (ay1 - ay0)
        for j in range(i + 1, len(gs)):
            b = gs[j]
            bx0, by0, bx1, by1 = b["bbox"]
            if bx0 >= ax1 - MIN_OVERLAP:
                break
            ox = min(ax1, bx1) - max(ax0, bx0)
            if ox <= MIN_OVERLAP:
                continue
            oy = min(ay1, by1) - max(ay0, by0)
            if oy <= MIN_OVERLAP:
                continue
            ab = (bx1 - bx0) * (by1 - by0)
            inter = ox * oy
            small = min(aa, ab)
            if inter < FRAC * small:
                continue
            same_span = (a["bi"], a["li"], a["si"]) == (b["bi"], b["li"], b["si"])
            punct = a["c"] in CJK_PUNCT or b["c"] in CJK_PUNCT
            if punct:
                kind = "含标点"
            elif same_span:
                kind = "同span"
            elif a["li"] == b["li"] and a["bi"] == b["bi"]:
                kind = "跨span同行"
            else:
                kind = "跨span跨行"
            stat[kind] += 1
            hits.append((kind, a, b, ox, oy, inter, small))
    if hits:
        if NONPUNCT_ONLY:
            hits = [h for h in hits if h[0] != "含标点"]
        if hits:
            per_page.append((pno + 1, hits))

for pno, hits in per_page:
    out.append(f"===== p.{pno} =====")
    for kind, a, b, ox, oy, inter, small in hits:
        aw = a["bbox"][2] - a["bbox"][0]
        bw = b["bbox"][2] - b["bbox"][0]
        cont = inter / small
        out.append(f"  <{kind}> {ox:.1f}x{oy:.1f}pt inter={inter:.0f} 含={cont*100:.0f}%")
        for tag, g in (("A", a), ("B", b)):
            x0, y0, x1, y1 = g["bbox"]
            out.append(f"     {tag} {g['c']!r} bbox=[{x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}] "
                       f"w={x1-x0:.1f} h={y1-y0:.1f} sz={g['size']:.1f} {g['font']} "
                       f"org=({g['org'][0]:.1f},{g['org'][1]:.1f}) "
                       f"blk/lin/spn={g['bi']}/{g['li']}/{g['si']} span={g['stext']!r}")
    out.append("")
out.append(f"分档统计：{dict(stat)}  合计 {sum(stat.values())}")
io.open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("kind stats:", dict(stat), "total", sum(stat.values()))
print("->", OUT)
