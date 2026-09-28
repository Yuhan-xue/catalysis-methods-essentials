# -*- coding: utf-8 -*-
r"""Build the figure/table inventory required by the plan (企划 §5.3).

Required columns: 图表 ID、所属章节、学习目的、来源定位、图源类别、加工方式、
可编辑文件、计划宽度、校核状态.

Most are derivable mechanically from the LaTeX sources:
  * ID / label        <- \label{fig:..} / \label{tab:..}
  * chapter           <- which chNN-*.tex the item lives in
  * caption head      <- first clause of \caption{...}
  * source class      <- \modelmark / \schemamark / \redrawmark, or a
                         cropped source image (includegraphics)
  * source location   <- \figsrc{...} / \src{...} content
  * editable source   <- the .tex file itself (TikZ/PGFPlots are inline)
  * width             <- \onecolwidth / \twocolwidth / figure* / columnwidth
  * review status     <- 待逐页渲染核查 by default

Output: sources/figure_table_list.csv  (+ a Markdown summary)
"""
import os, re, glob, csv

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PARTS = os.path.join(ROOT, "chapters", "parts")

FILES = sorted(glob.glob(os.path.join(PARTS, "*.tex"))) + [
    os.path.join(ROOT, "chapters", n) for n in
    ("ch00-intro.tex", "ch13-synthesis.tex", "ch90-backmatter.tex")
]

CAP = re.compile(r"\\caption\{")
LABEL = re.compile(r"\\label\{(fig|tab):([^}]*)\}")
CLASS = [("\\modelmark", "模型计算"), ("\\schemamark", "示意"),
         ("\\redrawmark", "据原书改绘")]
SRC = re.compile(r"\\figsrc\{(.{0,200}?)\}", re.S)
SRC2 = re.compile(r"\\src\{(.{0,160}?)\}", re.S)


def brace_arg(s, start):
    r"""Return the balanced {...} argument beginning at s[start] == '{'.

    Regex cannot do this: `\caption{...}` routinely contains nested braces
    (\textbf{}, \qty{}, \figsrc{}), and a non-greedy match stops at the first
    closing brace — which silently truncates the caption and makes any marker
    appearing after a nested group look absent. That produced a false
    "14 figures lack a source-class marker" report.
    """
    assert s[start] == "{"
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1:i], i
        i += 1
    return s[start + 1:], len(s)


def chapter_of(path):
    b = os.path.basename(path)
    m = re.match(r"ch(\d{2})-([a-e])", b)
    if m:
        return int(m.group(1)), m.group(2)
    m = re.match(r"ch(\d{2})", b)
    if m:
        return int(m.group(1)), "-"
    return 0, "-"


def clean(s):
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("{", "").replace("}", "").replace("~", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def source_class(cap, whole):
    for macro, name in CLASS:
        if macro in cap:
            return name
    if "\\includegraphics" in whole:
        return "原书实测图（裁切）"
    if "tikzpicture" in whole or "axis" in whole:
        return "据原书改绘（判定需人工确认）"
    return "未标注（需补）"


rows = []
for f in FILES:
    if not os.path.exists(f):
        continue
    txt = open(f, encoding="utf-8").read()
    ch, part = chapter_of(f)
    for m in CAP.finditer(txt):
        cap, cap_end = brace_arg(txt, m.end() - 1)
        after = txt[cap_end:cap_end + 160]
        lm = LABEL.search(after)
        label = f"{lm.group(1)}:{lm.group(2)}" if lm else ""
        # 判定是 figure 还是 table：看 caption 之前最近的环境
        before = txt[max(0, m.start() - 3000):m.start()]
        kind = "table" if before.rfind("\\begin{table") > before.rfind("\\begin{figure") else "figure"
        # 图源定位
        s1 = SRC.search(cap)
        if not s1:
            s1 = SRC2.search(cap)
        loc = clean(s1.group(1))[:60] if s1 else ""
        # 宽度
        seg = before[-1200:]
        if kind == "figure":
            width = ("跨栏 176mm" if ("figure*" in seg or "\\twocolwidth" in seg)
                     else "单栏 84mm" if "\\onecolwidth" in seg else "未显式设定")
        else:
            width = "跨栏" if ("table*" in seg or "\\twocolwidth" in seg) else "单栏"
        cls = source_class(cap, before[-2500:])
        # 企划 §5.2 的「图源四类」是针对**图**的；表格不适用，不要误报为缺失。
        if kind == "table":
            cls = "表格（图源四类不适用）"
        if not label and cap:
            lm = LABEL.search(cap)
            label = f"{lm.group(1)}:{lm.group(2)}" if lm else ""
        rows.append({
            "id": f"ch{ch:02d}{part}-{'图' if kind=='figure' else '表'}{len([r for r in rows if r['chapter']==ch and r['kind']==kind])+1:02d}",
            "chapter": ch,
            "part": part,
            "kind": kind,
            "label": label,
            "caption_head": clean(cap)[:56],
            "source_class": cls,
            "source_location": loc,
            "editable_source": os.path.relpath(f, ROOT).replace("\\", "/"),
            "planned_width": width,
            "review_status": "待逐页渲染核查",
        })

out = os.path.join(ROOT, "sources", "figure_table_list.csv")
with open(out, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "chapter", "part", "kind", "label",
                                       "caption_head", "source_class", "source_location",
                                       "editable_source", "planned_width", "review_status"])
    w.writeheader()
    w.writerows(rows)

figs = [r for r in rows if r["kind"] == "figure"]
tabs = [r for r in rows if r["kind"] == "table"]
bycls = {}
for r in rows:
    bycls[r["source_class"]] = bycls.get(r["source_class"], 0) + 1

print(f"figures: {len(figs)}   tables: {len(tabs)}   total: {len(rows)}")
print("figures by source class:")
for k, v in sorted({r["source_class"]: 0 for r in figs}.items()):
    n = len([r for r in figs if r["source_class"] == k])
    print(f"   {n:>3}  {k}")

miss = [r for r in figs if "未标注" in r["source_class"] or "需人工确认" in r["source_class"]]
print(f"\nfigures lacking an explicit source-class marker (企划 §5.2 requires one): {len(miss)}")
for r in miss:
    print(f"   ch{r['chapter']:>2}{r['part']}  {r['label']:<22} {r['caption_head'][:44]}")

print(f"\n-> {os.path.relpath(out, ROOT)}")
print("plan target: 60–80 numbered figures, 30–40 tables")
print(f"current coverage: figures {len(figs)}/60  tables {len(tabs)}/30")
