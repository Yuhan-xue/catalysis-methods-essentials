"""PDF 结构探针：书签目标页 vs 标题实际落页、后置区块页眉串章检查。

只读，不改任何源文件。用法：

    python tools/pdf_probe.py                       # 默认查 build/main.pdf
    python tools/pdf_probe.py --pdf <文件> --out <报告路径>
    python tools/pdf_probe.py --require <清单>      # 换必要书签清单
    python tools/pdf_probe.py --no-require          # 显式跳过 C 项（报告记 SKIP）

检查三项（R2-U01 / R2-U02 对应 reviews/2026-09-30-round2，R3-W03 对应 round3）：

  A. 书签目标页：每条书签的目标页（或其后一页、前一页）必须真的出现该标题。
     **匹配规则（务必与实现一致，否则会误报）**：标题在 PDF 文本层里会被断行、
     插空格，且章级标题印刷为「第 1 章物理吸附…」而书签写作「1 物理吸附…」，
     故不能直接做子串比较。这里把书签标题去掉空白后，再剥掉开头的章节号
     （`第?N章?` / `N.` 等），取剩余正文的前 10 个字符作键，在该页的
     「去空白文本」里找。候选键依次尝试，任一命中即算落页正确。

  B. 后置区块页眉：最后一个**编号章**之后的页面，页眉带（块 y0 < 70pt）里
     不得再出现该章标题或「第 N 章」字样——非编号标题没有更新 mark 时就会串章。
     只认「块首即章标题」的窗格（页眉是独立文本块），避免把正文首行误判成页眉。
     注意：后置区块自身的标题（如「符号、缩写与索引」）出现在页眉带里是**正确**的，
     不算命中——本项只针对串章。

  C. 必要书签覆盖：tools/pdf_required_bookmarks.txt 列出「章级 + 后置区块」必要
     书签，逐项与 PDF 实际书签比对，缺一即 FAIL。清单是**外部期望**，不是从
     当前 PDF 反推——否则删掉书签只会让检查项一起消失，等于没查。

前置不足（书签数为 0、全部书签标题过短、无编号章、清单缺失）一律记 UNUSABLE 并
把跳过原因写进 JSON，**不许静默通过**：拿空集当「无不符」正是本项要堵的假通过。

退出码：0 = 全部检查项 PASS（C 项被 --no-require 显式跳过也算）；
        1 = 有 FAIL（发现问题）；2 = 有 UNUSABLE（前置不足，检查根本没建立）。
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HEADER_BAND = 70.0   # pt：页眉带高度阈值
BODY_KEY_LEN = 10    # 去空白、剥章号后用于比对的正文前缀长度
MIN_KEY_LEN = 4      # 太短的键没有区分度，直接跳过
CHAPTER_RE = re.compile(r"第\s*\d+\s*章")
LEAD_NUM_RE = re.compile(r"^\s*第?\s*\d+\s*[章.、]?\s*")
NUMBERED_L1_RE = re.compile(r"^\s*\d+\s")

# 检查项状态：PASS 通过 / FAIL 有发现 / UNUSABLE 前置不足（检查没建立）/ SKIP 显式跳过
PASS, FAIL, UNUSABLE, SKIP = "PASS", "FAIL", "UNUSABLE", "SKIP"
REQUIRED_FILE = Path(__file__).with_name("pdf_required_bookmarks.txt")


def norm(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def title_keys(title: str) -> list[str]:
    """书签标题 → 候选匹配键（去空白后剥章号的正文前缀，再回退到原串前缀）。"""
    t = norm(title)
    body = LEAD_NUM_RE.sub("", t)
    keys = []
    if len(body) >= MIN_KEY_LEN:
        keys.append(body[:BODY_KEY_LEN])
    m = re.match(r"^\s*(\d+)", title or "")
    if m and len(body) >= MIN_KEY_LEN:
        keys.append("第%s章%s" % (m.group(1), body[:BODY_KEY_LEN]))
        keys.append("%s章%s" % (m.group(1), body[:BODY_KEY_LEN]))
    if len(t) >= MIN_KEY_LEN and t[:BODY_KEY_LEN] not in keys:
        keys.append(t[:BODY_KEY_LEN])
    return keys


def load_required(path: Path) -> list[dict]:
    """读必要书签清单：`组名<TAB>标题`；`#` 注释；标题尾部 `*` 表示前缀匹配。"""
    rows: list[dict] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        group, _, title = line.partition("\t")
        if not title:
            group, title = "required", group
        title = title.strip()
        if not title:
            continue
        prefix = title.endswith("*")
        rows.append({"group": group.strip() or "required", "title": title,
                     "prefix": prefix,
                     "key": norm(title[:-1] if prefix else title)})
    return rows


def coverage_facts(toc: list, required: list[dict], require_coverage: bool,
                   source: Path) -> dict:
    """C 项：必要书签覆盖。返回带 status / 明细的事实块（不做任何静默通过）。"""
    facts = {"require_coverage": require_coverage, "source": str(source),
             "required_total": len(required), "present_total": 0,
             "missing_total": 0, "missing": [],
             "status": UNUSABLE, "skip_reason": ""}
    if not require_coverage:
        facts["status"] = SKIP
        facts["skip_reason"] = "--no-require 显式跳过必要书签覆盖检查"
        facts["missing_total"] = len(required)
        return facts
    if not required:
        facts["status"] = UNUSABLE
        facts["skip_reason"] = f"必要书签清单缺失或为空：{source}"
        return facts
    if not toc:
        facts["status"] = FAIL
        facts["skip_reason"] = "PDF 书签数为 0，必要书签全部缺失"
        facts["missing"] = [{"group": r["group"], "title": r["title"]}
                            for r in required]
        facts["missing_total"] = len(required)
        return facts
    got = [norm(t) for _lv, t, _p in toc]
    for r in required:
        hit = (any(g.startswith(r["key"]) for g in got) if r["prefix"]
               else r["key"] in got)
        if hit:
            facts["present_total"] += 1
        else:
            facts["missing"].append({"group": r["group"], "title": r["title"]})
    facts["missing_total"] = len(facts["missing"])
    facts["status"] = FAIL if facts["missing"] else PASS
    return facts


def probe(pdf_path: Path, required: list[dict] | None = None,
          require_coverage: bool = True,
          required_source: Path = REQUIRED_FILE) -> dict:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    facts: dict = {"pdf": str(pdf_path), "pages": doc.page_count}
    toc = doc.get_toc()
    facts["bookmarks_total"] = len(toc)

    # --- A. 书签目标页是否真的是标题所在页 -------------------------------
    pages_norm = [norm(doc[i].get_text()) for i in range(doc.page_count)]
    targets = []
    skipped = []
    for _level, title, page in toc:
        keys = title_keys(title)
        if not keys:
            skipped.append({"title": title, "bookmark_page": page,
                            "why": f"标题过短，构不出有区分度的匹配键（MIN_KEY_LEN="
                                   f"{MIN_KEY_LEN}）"})
            continue
        hit = None
        matched_key = None
        for cand in (page, page + 1, page - 1):
            if not (1 <= cand <= doc.page_count):
                continue
            for key in keys:
                if key in pages_norm[cand - 1]:
                    hit, matched_key = cand, key
                    break
            if hit:
                break
        targets.append({"title": title, "bookmark_page": page,
                        "first_page_with_title": hit, "matched_key": matched_key,
                        "ok": hit == page})
    facts["bookmark_targets"] = targets
    facts["bookmark_targets_skipped"] = skipped
    facts["bookmark_mismatches"] = [t for t in targets if not t["ok"]]

    # --- B. 后置区块页眉串章 ---------------------------------------------
    level1 = [(t, p) for lv, t, p in toc if lv == 1]
    facts["level1_chapters"] = [{"title": t, "page": p} for t, p in level1]
    numbered = [(t, p) for t, p in level1 if NUMBERED_L1_RE.match(t or "")]
    last_chapter, last_chapter_page = (numbered[-1] if numbered else ("", 0))
    facts["last_numbered_chapter"] = {"title": last_chapter, "page": last_chapter_page}
    # 扫描起点：最后一个编号章之后的第一个一级条目（后置区块的首条）
    after = [(t, p) for t, p in level1 if p > last_chapter_page]
    scan_from = after[0][1] if after else last_chapter_page + 1
    facts["backmatter_scan_from"] = scan_from
    ch_key = title_keys(last_chapter)[0] if last_chapter else ""
    hits = []
    for i in range(max(0, scan_from - 1), doc.page_count):
        for block in doc[i].get_text("blocks"):
            y0, text = block[1], block[4]
            if y0 >= HEADER_BAND:
                continue
            n = norm(text)
            if not n:
                continue
            # 只认「块首即章标题」的块：页眉是独立窗格，正文首行不会以章题开头
            if ch_key and n.startswith(ch_key):
                hits.append({"page": i + 1, "y0": round(y0, 1),
                             "why": "后置页面页眉仍印最后一个编号章标题",
                             "text": re.sub(r"\s+", " ", text).strip()[:80]})
            elif CHAPTER_RE.match(n):
                hits.append({"page": i + 1, "y0": round(y0, 1),
                             "why": "后置页面页眉出现「第 N 章」字样",
                             "text": re.sub(r"\s+", " ", text).strip()[:80]})
    facts["backmatter_header_hits"] = hits

    # --- C. 必要书签覆盖（外部清单，非自指）--------------------------------
    if required is None:
        required = (load_required(required_source)
                    if Path(required_source).exists() else [])
    facts["required_coverage"] = coverage_facts(toc, required, require_coverage,
                                                Path(required_source))

    # --- 状态汇总：空集一律记 UNUSABLE，绝不静默通过 ------------------------
    if not toc:
        u01 = u02 = UNUSABLE
        facts["U01_skip_reason"] = "PDF 书签数为 0，书签落页检查无输入"
        facts["U02_skip_reason"] = "PDF 书签数为 0，取不到编号章，后置区块起点无法确定"
    else:
        if targets:
            u01 = PASS if not facts["bookmark_mismatches"] else FAIL
            facts["U01_skip_reason"] = ""
        else:
            u01 = UNUSABLE
            facts["U01_skip_reason"] = "全部书签标题都过短，未构造出任何可检查项"
        if numbered:
            u02 = PASS if not hits else FAIL
            facts["U02_skip_reason"] = ""
        else:
            u02 = UNUSABLE
            facts["U02_skip_reason"] = ("未发现编号章（形如「N 标题」的一级书签），"
                                        "无法确定后置区块起点")
    facts["U01_status"], facts["U02_status"] = u01, u02
    facts["W03_status"] = facts["required_coverage"]["status"]
    facts["U01_ok"] = u01 == PASS          # 兼容旧字段：UNUSABLE 不再算 ok
    facts["U02_ok"] = u02 == PASS
    facts["W03_ok"] = facts["W03_status"] == PASS
    doc.close()
    return facts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PDF 书签与页眉结构探针（只读）")
    ap.add_argument("--pdf", default="build/main.pdf")
    ap.add_argument("--out", default="build/pdf_probe.txt")
    ap.add_argument("--json", default="build/pdf_probe.json")
    ap.add_argument("--require", default=str(REQUIRED_FILE),
                    help="必要书签清单路径（默认 tools/pdf_required_bookmarks.txt）")
    ap.add_argument("--no-require", action="store_true",
                    help="显式跳过必要书签覆盖检查（报告记 SKIP，非静默）")
    args = ap.parse_args(argv)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 1
    req_path = Path(args.require)
    required = load_required(req_path) if req_path.exists() else []
    facts = probe(pdf_path, required=required,
                  require_coverage=not args.no_require,
                  required_source=req_path)

    def st(key: str) -> str:
        return facts[key]

    cov = facts["required_coverage"]
    lines = [f"PDF            : {facts['pdf']}",
             f"页数 / 书签数  : {facts['pages']} / {facts['bookmarks_total']}",
             f"R2-U01 书签落页 : {st('U01_status')}"
             f"（检查 {len(facts['bookmark_targets'])} 条，跳过 "
             f"{len(facts['bookmark_targets_skipped'])} 条，不符 "
             f"{len(facts['bookmark_mismatches'])} 条）"
             + (f"［{facts['U01_skip_reason']}］" if facts["U01_skip_reason"] else "")]
    for row in facts["bookmark_mismatches"]:
        lines.append(f"    - 书签「{row['title']}」目标页 {row['bookmark_page']}，"
                     f"标题实际首见于 {row['first_page_with_title']}"
                     f"（键 {row['matched_key']}）")
    for row in facts["bookmark_targets_skipped"]:
        lines.append(f"    - 跳过书签「{row['title']}」（p.{row['bookmark_page']}）："
                     f"{row['why']}")
    lines.append(f"R2-U02 后置页眉 : {st('U02_status')}"
                 f"（命中 {len(facts['backmatter_header_hits'])} 处；扫描自 p."
                 f"{facts['backmatter_scan_from']}，最后一个编号章「"
                 f"{facts['last_numbered_chapter']['title']}」在 p."
                 f"{facts['last_numbered_chapter']['page']}）"
                 + (f"［{facts['U02_skip_reason']}］" if facts["U02_skip_reason"] else ""))
    for row in facts["backmatter_header_hits"]:
        lines.append(f"    - p.{row['page']}  页眉带 y0={row['y0']}：{row['text']}"
                     f" ［{row['why']}］")
    lines.append(f"R3-W03 必要书签 : {cov['status']}"
                 f"（清单 {cov['source']}；必要 {cov['required_total']} 项，命中 "
                 f"{cov['present_total']}，缺失 {cov['missing_total']}，跳过 "
                 f"{cov['required_total'] - cov['present_total'] if cov['status'] == 'SKIP' else 0}）"
                 + (f"［{cov['skip_reason']}］" if cov["skip_reason"] else ""))
    for row in cov["missing"]:
        lines.append(f"    - 必要书签缺失［{row['group']}］：{row['title']}")
    lines.append("")
    tail = facts["backmatter_scan_from"]
    lines.append("后置区块书签目标页：" + "、".join(
        f"{r['title']}={r['bookmark_page']}" for r in facts["bookmark_targets"]
        if r["bookmark_page"] >= tail))
    report = "\n".join(lines) + "\n"

    statuses = [facts["U01_status"], facts["U02_status"], facts["W03_status"]]
    exit_code = 2 if UNUSABLE in statuses else (1 if FAIL in statuses else 0)
    facts["exit_code"] = exit_code
    facts["statuses"] = {"R2-U01": facts["U01_status"], "R2-U02": facts["U02_status"],
                         "R3-W03": facts["W03_status"]}

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")
    Path(args.json).write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
