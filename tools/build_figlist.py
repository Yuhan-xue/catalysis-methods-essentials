# -*- coding: utf-8 -*-
r"""Rebuild sources/figure_table_list.csv —— 全书图表来源台账（企划 §5.3）。

为什么重写
----------
旧版只枚举 ``\caption{}``，而编号、正文引用与回查都以 **浮动体** 为单位；
旧版生成 39 条，而全书真实浮动体是 143 个。它还有两个致命缺陷：

1. ``\label`` 只在 ``\caption`` 之后 160 字符内找，长图题一律漏标；
2. ``caption_head`` 走的是 OCR 文本，含 ``$_K$`` ``$$`` 之类损坏 —— 而
   **成品 PDF 里这些错误早已修好**，于是台账与成品互相矛盾，谁照台账核对
   都会得出错误结论。

本版的事实来源
--------------
* **编号**：``build/main.aux`` 的 ``\newlabel``，取 LaTeX 实际写出的编号。
  绝不由 ``\label`` 计数推断：图、表计数器彼此独立，且
  ``\numberwithin{figure}{section}`` 使 ``\thefigure = \thesection-\arabic{figure}``，
  而 ``\chapterstart`` 把 ``\thesection`` 做成章号 —— 故形如 ``8-3``。
  aux 的 1142 条 ``\newlabel`` 里有 571 条是 cleveref 的 ``@cref`` 派生记录
  （首字段形如 ``[figure][1][0]8-3``，会让浮动体计数翻倍），必须滤掉。
* **图题**：直接取源码 ``\caption{}`` 的平衡括号内容并纯文本化。
  不读 PDF、不读 OCR，因而不可能引入 OCR 损坏。
* **来源标注**：从浮动体环境体内取 ``\figsrc{}`` / ``\src{}`` 的内容，
  以及 ``\modelmark`` ``\schemamark`` ``\redrawmark`` ``\pedset`` 标记。

诚实纪律
--------
* ``review_status`` 一律「未核对页面图像」—— 本脚本看不到页面图像，
  不声称核对过。措辞与 ``\tocheck`` 的既有「待核对」口径一致。
* ``source_location`` 取不到就留空、``source_class`` 记「未标注」，不猜。
* ``source_location`` 只从**浮动体环境体内**取。正文散文里的 ``\src{}``
  不属于该浮动体，混进来会造出假来源（例：ch09-a 图前的 ``\src``）。
* 无 ``\label`` 的浮动体照样列出（``label`` 记 ``(无 \label)``），
  这是真实的可追溯性缺口，不隐藏。

用法
----
    python tools/build_figlist.py            # 重建 CSV + 打印统计
    python tools/build_figlist.py --check    # 只统计，不写文件
"""
import os
import re
import csv
import glob
import sys
import argparse
from collections import OrderedDict, Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUX = os.path.join(ROOT, "build", "main.aux")
OUT_CSV = os.path.join(ROOT, "sources", "figure_table_list.csv")

REVIEW_DEFAULT = "未核对页面图像"
NO_LABEL = r"(无 \label)"
NO_MARK = "未标注"

FLOAT_ENVS = ("figure", "table", "longtable")
BEGIN_RE = re.compile(r"\\begin\{(" + "|".join(FLOAT_ENVS) + r")\}")
CAPTION_RE = re.compile(r"\\caption\*?\s*(?=\{)")
LABEL_RE = re.compile(r"\\label\{([^}]*)\}")
ANY_LABEL_RE = re.compile(r"\\label\{([^}]*)\}")

# 图源「性质」标记（style/macros.tex 第 77—85 行）
CLASS_MACROS = OrderedDict((
    ("\\modelmark", "模型计算"),
    ("\\schemamark", "示意"),
    ("\\redrawmark", "据原书改绘"),
    ("\\pedset", "教学设定"),
))
LOC_MACROS = ("\\figsrc", "\\src")          # 承载来源出处
NOTE_MACROS = ("\\tocheck", "\\supp")       # 核验状态 / 补充说明
INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}")
WIDTH_MACROS = (("\\twocolwidth", "跨栏或全宽"), ("\\onecolwidth", "单栏"))


# --------------------------------------------------------------------------
def brace_arg(s, start):
    r"""返回 ``s[start] == '{'`` 起的平衡括号内容。

    正则做不到：``\caption{...}`` 常含嵌套花括号（``\textbf{}``、``\qty{}``、
    ``\figsrc{}``），非贪婪匹配会停在第一个 ``}``，静默截断图题，并让嵌套组
    之后的标记看起来「不存在」—— 旧版正是这样误报「14 张图缺来源标记」。
    反斜杠转义按「跳过下一字符」处理，避免把 ``\{`` 当成组起始。
    """
    if start >= len(s) or s[start] != "{":
        return "", start
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


# 希腊字母与常用数学控制序列 -> Unicode。**不能简单删掉**：$\\theta$ 删成空串
# 会得到「$ $」，那和旧版 OCR 损坏看起来一样，却是我自己造的 artifact。
GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "θ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ",
    "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYMBOLS = {
    "times": "×", "cdot": "·", "pm": "±", "mp": "∓", "le": "≤", "leq": "≤",
    "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠", "approx": "≈", "propto": "∝",
    "infty": "∞", "rightarrow": "→", "to": "→", "leftarrow": "←",
    "circ": "°", "degree": "°", "ang": "Å", "AA": "Å", "sum": "Σ",
    "partial": "∂", "nabla": "∇", "sqrt": "√", "ell": "ℓ", "hbar": "ℏ",
    "perp": "⊥", "parallel": "∥", "in": "∈", "subset": "⊂",
    "prime": "′", "langle": "⟨", "rangle": "⟩",
}
MACRO_TEXT = {
    "sloppy": "", "centering": "", "small": "", "footnotesize": "", "tiny": "",
    "textbf": "", "textit": "", "emph": "", "textrm": "", "texttt": "",
    "mathrm": "", "mathit": "", "mathbf": "", "text": "", "mbox": "",
    "left": "", "right": "", "big": "", "Big": "", "bigl": "", "bigr": "",
    "quad": " ", "qquad": " ", "\\,": " ", "\\;": " ", "\\!": "",
    "%": "%", "&": "＆", "#": "#", "_": "_", "$": "$", "{": "{", "}": "}",
}
MATH_MAP = dict(GREEK)
MATH_MAP.update(SYMBOLS)


def latex_plain(s):
    r"""LaTeX 片段 -> 可读纯文本；保留数学内容，绝不制造新损坏。

    处理次序要紧：先映射数学宏（``\theta`` -> ``θ``），再丢弃排版类宏。
    旧版把 ``$..$`` 之间的内容一起丢掉，才出现「$$ 是入射束…」这种
    既像 OCR 损坏、又不可复原的字符串。
    """
    def repl(m):
        tok = m.group(1)
        if tok in MACRO_TEXT:
            return MACRO_TEXT[tok]
        if tok in MATH_MAP:
            return MATH_MAP[tok]
        # 未知控制序列：丢弃（它多半是纯排版宏），但已知数学符号已在上面映射
        return ""
    s = re.sub(r"\$+", "$", s)                       # $$..$$ -> $..$
    s = re.sub(r"\\([a-zA-Z]+|[,;!%&#_${}])", repl, s)
    s = s.replace("\\", "").replace("~", " ")
    s = re.sub(r"\^\{?([23])\}?", r"\1", s)          # ^{2} -> 2，与 PDF 文字层一致
    s = re.sub(r"\^\{([^{}]*)\}", r"\1", s)          # ^{abc} -> abc
    s = re.sub(r"_\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"[{}]", "", s)
    # 其余上下标标记去掉，避免留下 $λK$ 这类不可读残留
    s = re.sub(r"(?<=[\w)\]])[\^_](?=\S)", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def heading(s, limit=56):
    """截到 limit 字；优先在标点处收口，避免留半句。"""
    s = s.strip()
    if len(s) <= limit:
        return s
    cut = s[:limit]
    for i in range(len(cut) - 1, max(0, limit - 16), -1):
        if cut[i] in "。；！？":
            return cut[:i + 1]
    return cut.rstrip() + "…"


def markers(text):
    return [name for macro, name in CLASS_MACROS.items() if macro in text]


def locs(body):
    r"""按出现次序取环境体内的 ``\figsrc{}`` / ``\src{}`` 非空内容。"""
    hits = []
    for macro in LOC_MACROS:
        for m in re.finditer(re.escape(macro) + r"\s*(?=\{)", body):
            txt = latex_plain(brace_arg(body, m.end())[0])
            if txt:
                hits.append((m.start(), macro, txt))
    hits.sort(key=lambda t: t[0])
    return hits


def notes(body):
    out = []
    for macro in NOTE_MACROS:
        for m in re.finditer(re.escape(macro) + r"\s*(?=\{)", body):
            txt = latex_plain(brace_arg(body, m.end())[0])
            if txt:
                out.append(txt)
    return out


# --------------------------------------------------------------------------
# 1. 编号权威源
# --------------------------------------------------------------------------
def load_aux(path):
    r"""``{label: {number, page, caption}}``，只保留浮动体标签。

    ``<label>@cref`` 是 cleveref 的派生记录，必须滤掉，否则计数翻倍。
    """
    if not os.path.exists(path):
        raise SystemExit(
            f"缺少 {os.path.relpath(path, ROOT)}：编号必须以 aux 为准。"
            "请先编译全书（本脚本自己不跑 build.ps1）。")
    labels = OrderedDict()
    n_all = n_cref = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"\\newlabel\{(.+?)\}\{(.*)\}\s*$", line)
            if not m:
                continue
            lab, body = m.group(1), m.group(2)
            n_all += 1
            if "@cref" in lab:
                n_cref += 1
                continue
            if not lab.startswith(("fig:", "tab:")):
                continue
            f = re.findall(r"\{([^{}]*)\}", body)
            labels[lab] = {
                "number": f[0] if f else "",
                "page": f[1] if len(f) > 1 else "",
                "caption": f[2] if len(f) > 2 else "",
                "anchor": f[3] if len(f) > 3 else "",
            }
    return labels, n_all, n_cref


# --------------------------------------------------------------------------
# 2. 源码侧提取
# --------------------------------------------------------------------------
def source_files():
    files = sorted(glob.glob(os.path.join(ROOT, "chapters", "parts", "*.tex")))
    files += sorted(glob.glob(os.path.join(ROOT, "chapters", "ch*.tex")))
    files += [os.path.join(ROOT, "main.tex")]
    return [f for f in files if os.path.exists(f)]


def chapter_of_path(rel):
    b = os.path.basename(rel)
    m = re.match(r"ch(\d{2})-([a-e])", b)
    if m:
        return int(m.group(1)), m.group(2)
    m = re.match(r"ch(\d{2})", b)
    if m:
        return int(m.group(1)), "-"
    return -1, "-"


def scan(files):
    r"""按文件顺序枚举浮动体。

    用「先 ``\begin`` 再找 ``\end``」而非回溯正则：长浮动体（含大 tikzpicture）
    会让 ``.*?\\end`` 回溯变慢，且嵌套同名环境时不可靠。
    """
    floats, counters = [], defaultdict(int)
    for f in files:
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        ch, part = chapter_of_path(rel)
        text = open(f, encoding="utf-8", errors="replace").read()
        for m in BEGIN_RE.finditer(text):
            env = m.group(1)
            kind = "figure" if env == "figure" else "table"
            e = text.find("\\end{%s}" % env, m.end())
            body = text[m.end():e if e > 0 else len(text)]
            counters[kind] += 1

            lm = LABEL_RE.search(body)
            label = lm.group(1) if lm else ""
            if not label:
                lm2 = ANY_LABEL_RE.search(body)
                label = (lm2.group(1) if lm2 and
                         lm2.group(1).startswith(("fig:", "tab:")) else "")

            cm = CAPTION_RE.search(body)
            cap_raw, cap_pos = "", -1
            if cm:
                cap_raw, cap_pos = brace_arg(body, body.index("{", cm.start()))
            # 图题之后的正文段落不应算进「图题内标记」
            tail = body[(cap_pos + len(cap_raw)):] if cap_pos >= 0 else body

            srcs = locs(body)
            if kind == "figure" and INCLUDE_RE.search(body):
                cls_pdf = "原书实测图（裁切）"
            else:
                cls_pdf = ""

            floats.append({
                "env": env,
                "kind": kind,
                "label": label,
                "file": rel,
                "line": text.count("\n", 0, m.start()) + 1,
                "caption_raw": cap_raw,
                "caption_head": heading(latex_plain(cap_raw)),
                "mark_in_caption": markers(cap_raw),
                "mark_in_tail": markers(tail),
                "class_pdf": cls_pdf,
                "srcs": srcs,
                "src_location": " ｜ ".join(t[2] for t in srcs),
                "src_macro": "、".join(sorted({t[1].lstrip("\\") for t in srcs})),
                "check_note": "；".join(notes(body)),
                "seq": counters[kind],
                "src_chapter": ch,
                "part": part,
                "width": next((n for mac, n in WIDTH_MACROS if mac in body), ""),
                "has_caption": bool(cap_raw),
            })
    return floats


# --------------------------------------------------------------------------
# 3. 合并
# --------------------------------------------------------------------------
def merge(floats, aux):
    rows, unlabeled, unmatched = [], [], []
    for flt in floats:
        a = aux.get(flt["label"]) if flt["label"] else None
        if flt["label"] and not a:
            unmatched.append(flt)
        number = a["number"] if a else ""

        # section：编号前缀 = \thesection。ch13/ch90 是**不编号**区块，
        # \thesection 不递增，故它们的浮动体沿用上一章号（12-4、12-5）。
        # 这一点与「chapter」列不同，必须分开记，否则会把 ch13 的表误报成第 12 章的。
        sm = re.match(r"(\d+)-\d+$", number)
        section = int(sm.group(1)) if sm else None
        chapter = flt["src_chapter"]          # 以**所在文件**判章（权威）

        # source_class 证据优先级：图题内标记 > 环境体内标记 > PDF 侧可判定
        if flt["mark_in_caption"]:
            cls, ev = "、".join(flt["mark_in_caption"]), "图题内标记"
        elif flt["mark_in_tail"]:
            cls, ev = "、".join(flt["mark_in_tail"]), "环境体内标记"
        elif flt["kind"] == "table":
            cls, ev = NO_MARK, ""
        elif flt["class_pdf"]:
            cls, ev = flt["class_pdf"], "按 \\includegraphics 判定"
        else:
            cls, ev = NO_MARK, ""

        row = OrderedDict()
        row["label"] = flt["label"] or NO_LABEL
        row["kind"] = flt["kind"]
        row["number"] = number
        row["chapter"] = chapter
        row["file"] = flt["file"]
        row["line"] = flt["line"]
        row["caption_head"] = flt["caption_head"]
        row["source_class"] = cls
        row["source_location"] = flt["src_location"]
        row["review_status"] = REVIEW_DEFAULT
        # 便于回查的附加列
        # id 用作稳定主键：ch<章><分片>-图/表<号>，如 ch01a-图1、ch13-表4
        suffix = number.split("-")[-1] if number else "X" + str(flt["seq"])
        row["id"] = (f"ch{chapter:02d}{flt['part'] if flt['part'] != '-' else ''}"
                     f"-{'图' if flt['kind'] == 'figure' else '表'}{suffix}")
        row["part"] = flt["part"]
        row["env"] = flt["env"]
        row["section"] = section if section is not None else ""
        row["caption_source"] = "源码 \\caption{}" if flt["has_caption"] else "（无 \\caption）"
        row["class_evidence"] = ev
        row["source_macro"] = flt["src_macro"]
        row["check_note"] = flt["check_note"]
        row["width"] = flt["width"]
        rows.append(row)
        if not flt["label"]:
            unlabeled.append(row)
    return rows, unlabeled, unmatched


FIELDS = ["label", "kind", "number", "chapter", "file", "line", "caption_head",
          "source_class", "source_location", "review_status",
          "id", "part", "env", "section", "caption_source", "class_evidence",
          "source_macro", "check_note", "width"]


def sort_key(r):
    m = re.match(r"(\d+)-(\d+)$", r["number"] or "")
    return (int(r["chapter"]), int(m.group(1)) if m else 9999,
            int(m.group(2)) if m else 9999,
            0 if r["kind"] == "figure" else 1, r["line"])


# --------------------------------------------------------------------------
# 4. 统计
# --------------------------------------------------------------------------
def report(rows, unlabeled, unmatched, aux, n_all, n_cref, floats):
    figs = [r for r in rows if r["kind"] == "figure"]
    tabs = [r for r in rows if r["kind"] == "table"]
    has_loc = [r for r in rows if r["source_location"]]
    has_cls = [r for r in rows if r["source_class"] != NO_MARK]
    has_any = [r for r in rows if r["source_location"] or r["source_class"] != NO_MARK]
    gaps = [r for r in rows if not r["source_location"] and r["source_class"] == NO_MARK]

    W = 78
    print("=" * W)
    print("全书图表来源台账 —— 统计")
    print("=" * W)
    print(f"aux \\newlabel 共 {n_all} 条，其中 @cref 派生记录 {n_cref} 条（已滤掉）")
    print(f"→ 浮动体标签 {len(aux)} 个；源码浮动体环境 {len(floats)} 个")
    print()
    print(f"台账总条数: {len(rows)}   （图 {len(figs)} / 表 {len(tabs)}）")
    print(f"  有 source_class 标记        : {len(has_cls)}")
    print(f"  有 source_location 来源定位 : {len(has_loc)}")
    print(f"  两者至少有一                : {len(has_any)}")
    print(f"  两者都没有（真实缺口）      : {len(gaps)}")
    print()
    print("按章分布（chapter 以所在文件判；section 为编号前缀）:")
    print(f"  {'章':<5}{'图':>4}{'表':>4}{'小计':>6}   有来源定位/有标记/两者都无")
    agg = defaultdict(lambda: [0, 0, 0, 0, 0])
    for r in rows:
        b = agg[r["chapter"]]
        b[0 if r["kind"] == "figure" else 1] += 1
        if r["source_location"]:
            b[2] += 1
        if r["source_class"] != NO_MARK:
            b[3] += 1
        if not r["source_location"] and r["source_class"] == NO_MARK:
            b[4] += 1
    for ch in sorted(agg):
        f, t, loc, cls, gap = agg[ch]
        print(f"  ch{ch:<3}{f:>4}{t:>4}{f + t:>6}   {loc:>5} /{cls:>4} /{gap:>4}")
    f, t, loc, cls, gap = (sum(v[i] for v in agg.values()) for i in range(5))
    print(f"  {'合计':<4}{f:>4}{t:>4}{f + t:>6}   {loc:>5} /{cls:>4} /{gap:>4}")
    print()
    print("source_class 取值分布:")
    for k, v in Counter(r["source_class"] for r in rows).most_common():
        print(f"   {v:>4}  {k}")
    print()
    print("class_evidence 取值分布（标记来自哪里）:")
    for k, v in Counter(r["class_evidence"] or "（无标记）"
                        for r in rows).most_common():
        print(f"   {v:>4}  {k}")
    print()
    print(f"无来源标注 {len(gaps)} 条 —— 真实可追溯性缺口，逐条列出：")
    for r in sorted(gaps, key=sort_key):
        print(f"   {r['file']}:{r['line']:<5} {r['number'] or '(无编号)':<8} "
              f"{r['label']:<26} {r['caption_head'][:28]}")
    print()
    print(f"缺 \\label 的浮动体 {len(unlabeled)} 个：")
    for r in unlabeled:
        print(f"   {r['file']}:{r['line']:<5} {r['env']:<9} {r['caption_head'][:34]}")
    if not unlabeled:
        print("   （无）")
    print()
    print(f"review_status: {dict(Counter(r['review_status'] for r in rows))}")
    print("   本脚本看不到页面图像，故一律不声称已核对；"
          "check_note 列保留源码 \\tocheck/\\supp 原话。")
    if unmatched:
        print(f"\n⚠ 源码有 \\label 但 aux 中无（可能是失效条目）: "
              f"{[f['label'] for f in unmatched]}")
    used = {f["label"] for f in floats if f["label"]}
    unused = [l for l in aux if l not in used]
    if unused:
        print(f"\n⚠ aux 有编号但源码未匹配到浮动体（{len(unused)}）：")
        for l in unused:
            print(f"   {l}  {aux[l]['number']}  {aux[l]['caption'][:50]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只统计，不写文件")
    args = ap.parse_args()

    aux, n_all, n_cref = load_aux(AUX)
    floats = scan(source_files())
    rows, unlabeled, unmatched = merge(floats, aux)
    rows.sort(key=sort_key)
    # 无 \label 者拿不到编号，如实留空（aux 里没有它的记录，不猜）
    for r in unlabeled:
        r["number"] = ""

    report(rows, unlabeled, unmatched, aux, n_all, n_cref, floats)
    if args.check:
        print("\n--check：未写文件。")
        return 0

    with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"\n-> {os.path.relpath(OUT_CSV, ROOT)}  ({len(rows)} 行)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
