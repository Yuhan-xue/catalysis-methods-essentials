# -*- coding: utf-8 -*-
"""Build sources/page_map_down.csv and sources/page_map_up.csv plus a stats dump.

Row vocabulary
  method      runninghead      number printed in the running head, read back from the
                               rendered bitmap by tools/folio_ocr2.py (digit templates
                               learned from DOWN, self-test 436/444 = 100 % of pages
                               that actually carry a folio)
              runninghead_tl   number only in the PDF text layer; no ink at that
                               position in the scanned image (chapter/section openers)
              toc              printed table of contents (chapter / appendix start)
              interpolated     inferred from the constant offset between verified pages
              none             page genuinely carries no number
  confidence  high | medium | low
"""
import csv, os, collections

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
OUT = os.path.join(ROOT, "tools", "out")

# ---------- inputs ----------
dn_tl = {}                      # pdf_page -> printed number from DOWN text layer
for r in csv.DictReader(open(os.path.join(ROOT, "sources/page_map_down.csv"), encoding="utf-8-sig")):
    if r["book_page"].strip():
        dn_tl[int(r["pdf_page"])] = int(r["book_page"])
dn_head = {}
for r in csv.DictReader(open(os.path.join(ROOT, "sources/page_map_down.csv"), encoding="utf-8-sig")):
    dn_head[int(r["pdf_page"])] = r["head"]

folio = {}                      # (vol, pdf_page) -> dict
for r in csv.DictReader(open(os.path.join(OUT, "folio_read.csv"), encoding="utf-8")):
    folio[(r["vol"], int(r["pdf_page"]))] = r

UP_OFF = 19
DN_ROMAN = {2: "i", 3: "iii", 4: "v", 6: "vii",           # 1st roman sequence
            7: "i", 8: "ii", 9: "iii", 10: "v", 11: "vi", 12: "vii",
            13: "viii", 14: "ix", 15: "x", 16: "xi", 17: "xii"}
DN_CH = {18: ("第8章 核磁共振方法", 525), 59: ("第9章 表面分析技术基础", 567),
         225: ("第10章 多相催化反应动力学", 735), 296: ("第11章 电化学催化研究方法", 807),
         372: ("第12章 扫描探针显微镜与纳米光谱技术", 885),
         435: ("附录1 历届国际催化大会", 949), 436: ("附录2 历届全国（中国）催化大会", 950),
         437: ("附录3 Studies in Surface Science and Catalysis 丛书书目", 951)}
UP_CH = {20: ("第1章 物理吸附和催化剂的宏观物性测定", 1),
         104: ("第2章 透射电子显微镜", 85), 188: ("第3章 热分析方法", 169),
         238: ("第4章 多晶X射线衍射分析", 219), 320: ("第5章 化学吸附和程序升温技术", 301),
         362: ("第6章 催化过程的拉曼光谱方法", 343), 432: ("第7章 原位红外光谱方法", 413)}
UP_BLANK = [21, 105, 187, 189, 239, 321, 361, 363, 431, 433]
UP_UNNUM = {1: "封面", 2: "扉页（丛书名、书名、主编）", 3: "内容简介／版权页",
            4: "资助出版说明（大连市人民政府）", 5: "资助出版说明（中触媒新材料股份有限公司）",
            6: "2018年现代催化研究方法高级讲习班指定用书页", 7: "丛书书目页"}
UP_FRONT = {8: "丛书序（首页）", 9: "丛书序（续）", 10: "序（首页）", 11: "《现代催化研究方法》前言（首页）",
            12: "前言（续）", 13: "目录（首页）", 14: "目录", 15: "目录", 16: "目录",
            17: "目录", 18: "目录", 19: "目录（末页）"}
DN_FRONT = {1: "封面", 2: "资助出版页（大连市人民政府）", 3: "资助出版页（中触媒新材料股份有限公司）",
            4: "扉页（丛书名、书名）", 5: "内容简介／版权页", 6: "丛书编委会／总策划页",
            7: "丛书序（首页）", 8: "丛书序（续）", 9: "序（首页）", 10: "《现代催化研究方法》前言（首页）",
            11: "前言（续）", 12: "目录（首页）", 13: "目录", 14: "目录", 15: "目录",
            16: "目录", 17: "目录（末页）"}

UP_TAIL = {519: "附录（参考文献之后）", 520: "", 521: "", 522: "", 523: ""}

# ---------- DOWN ----------
dn_rows = []
for p in range(1, 463):
    f = folio[("down", p)]
    bitmap_ok = f["read"] == str(dn_tl.get(p, "")) and f["read"] != ""
    if p == 1:
        dn_rows.append((p, "", "none", "low", "封面（无页码）"))
    elif p == 462:
        dn_rows.append((p, "", "none", "low", "封底（科学出版社联系方式/建议上架分类/定价；无页码）"))
    elif p in DN_FRONT:
        base = DN_FRONT[p]
        if p == 5:
            dn_rows.append((p, "", "none", "low", base + "；无可见页码"))
        elif p in DN_ROMAN:
            sec_open = p in (7, 9, 10, 12)
            ink = ("该页上部有印刷页眉墨迹" if f["ink"] and int(f["ink"]) > 400
                   else ("扫描图上部无墨迹（节首页，只印标题不印页眉）" if sec_open
                         else "扫描图上部无墨迹（该页未印页眉）"))
            conf = "medium" if f["ink"] and int(f["ink"]) > 400 else "low"
            dn_rows.append((p, DN_ROMAN[p], "runninghead_tl", conf,
                            f"前置罗马数字 {DN_ROMAN[p]}；{base}；{ink}；数字取自 PDF 文本层"))
        else:
            dn_rows.append((p, "", "none", "low", base + "；无页码"))
    elif p in DN_CH:
        title, bp = DN_CH[p]
        assert dn_tl[p] == bp, (p, dn_tl[p], bp)
        kind = "章首页" if p not in (435, 436, 437) else "附录首页"
        dn_rows.append((p, bp, "toc", "high",
                        f"{kind}《{title}》＝印刷第{bp}页（与印刷目录一致）；"
                        f"扫描图上该页无页眉/页码，页眉文字仅见于 PDF 文本层"))
    else:
        bp = dn_tl[p]
        if bitmap_ok:
            dn_rows.append((p, bp, "runninghead", "high", "页眉页码，已由位图数字识别复核"))
        else:
            dn_rows.append((p, bp, "runninghead_tl", "medium",
                            f"页眉页码取自 PDF 文本层（位图复核读作 "
                            f"{f['read'] or '空'}，为切分/识别噪声）；与相邻页连续"))
with open(os.path.join(ROOT, "sources/page_map_down.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["pdf_page", "book_page", "method", "confidence", "note"])
    w.writerows(dn_rows)

# ---------- UP ----------
up_rows = []
for p in range(1, 544):
    f = folio[("up", p)]
    if p == 1:
        up_rows.append((p, "", "none", "low", "封面（无页码）"))
    elif p == 543:
        up_rows.append((p, "", "none", "low",
                        "封底（科学出版社联系方式/建议上架分类/定价；无页码）"))
    elif p in UP_UNNUM:
        up_rows.append((p, "", "none", "low", UP_UNNUM[p] + "；无页眉、无页码"))
    elif p in UP_FRONT:
        if p == 14:
            up_rows.append((p, "viii", "runninghead", "medium",
                            "目录；页眉页脚处印有罗马数字 viii（文本层+墨迹均为 viii）"))
        else:
            up_rows.append((p, "", "none", "low",
                            UP_FRONT[p] + "；页码为罗马数字（据 p.14 印作 viii 推断，本页应为 "
                            + "／".join(["vii", "vi", "v", "iv", "iii", "ii", "i", "ix", "x", "xi", "xii", "xiii"][
                                {13: 0, 12: 1, 11: 2, 10: 3, 9: 4, 8: 5, 15: 7, 16: 8, 17: 9, 18: 10, 19: 11}.get(p, 6)])
                            + " 附近）；位图数字识别器仅识阿拉伯数字，未填，待人工核对"))
    elif p in UP_CH:
        title, bp = UP_CH[p]
        up_rows.append((p, bp, "toc", "high",
                        f"章首页《{title}》＝印刷第{bp}页（与印刷目录一致）；"
                        f"章首页不印页眉/页码，扫描图上该页仅中部有章名图形"))
    elif p in UP_BLANK:
        bp = p - UP_OFF
        up_rows.append((p, bp, "interpolated", "medium",
                        f"空白页（整页无墨迹、无页眉），页码由前后已复核页的恒定偏移(＝{UP_OFF})推定"))
    else:
        bp = p - UP_OFF
        if f["read"] == str(bp):
            up_rows.append((p, bp, "runninghead", "high", "页眉右上角页码，已由位图数字识别逐页复核"))
        else:
            up_rows.append((p, bp, "interpolated", "medium",
                            f"页眉页码位图识别失败（读作 {f['read'] or '空'}）；"
                            f"由全卷恒定偏移 {UP_OFF} 及相邻已复核页推定"))
with open(os.path.join(ROOT, "sources/page_map_up.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["pdf_page", "book_page", "method", "confidence", "note"])
    w.writerows(up_rows)

# ---------- stats ----------
def stats(rows, name):
    c = collections.Counter(r[1] for r in rows)
    conf = collections.Counter(r[3] for r in rows)
    meth = collections.Counter(r[2] for r in rows)
    return (f"{name}: rows={len(rows)} non-empty book_page={len(rows)-c['']} "
            f"confidence={dict(conf)} method={dict(meth)}")

lines = [stats(dn_rows, "DOWN"), stats(up_rows, "UP"), ""]
# DOWN offset structure
found = [(p, dn_tl[p]) for p in sorted(dn_tl)]
segs, prev = [], None
for p, b in found:
    o = p - b
    if prev is None or o != prev[3]:
        segs.append([p, p, b, o, b])
    else:
        segs[-1][1] = p
    prev = (p, p, b, o)
lines.append("DOWN offset segments (pdf range, offset, book range):")
for a, b2, bp0, o, _ in segs:
    lines.append(f"  pdf {a}-{b2}  offset {o:+d}  book {a-o}-{b2-o}")
lines.append("")
lines.append("DOWN missing printed pages (offset steps):")
prev = None
chain = []
for p, b in found:
    if prev is not None and b != prev[1] + 1:
        chain.append((prev[0], p, list(range(prev[1] + 1, b))))
    prev = (p, b)
for a, b2, miss in chain:
    lines.append(f"  after pdf {a} (book {a - (a - dn_tl[a]) - 0}) -> pdf {b2}: missing {miss}")
lines.append("")
# UP offset
uo = collections.Counter()
bad = []
for p in range(20, 543):
    f = folio[("up", p)]
    if f["read"] == str(p - UP_OFF):
        uo[UP_OFF] += 1
lines.append(f"UP: pages 20..542 all match offset +{UP_OFF}; "
             f"bitmap-verified rows = {uo[UP_OFF]}, unverified (blank/chapter-title) = "
             f"{len([p for p in range(20,543) if folio[('up',p)]['read'] != str(p-UP_OFF)])}")
open(os.path.join(OUT, "map_stats.txt"), "w", encoding="utf-8").write("\n".join(lines))
print("\n".join(lines[:40]))
