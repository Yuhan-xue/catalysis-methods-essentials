"""PDF 结构探针：书签目标页 vs 标题实际落页、后置区块页眉串章检查。

只读，不改任何源文件。用法：

    python tools/pdf_probe.py                       # 默认查 build/main.pdf
    python tools/pdf_probe.py --pdf <文件> --out <报告路径>

检查两项（对应 reviews/2026-09-30-round2 的 R2-U01 / R2-U02）：

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

退出码：0 = 两项均通过；1 = 有发现（明细写在报告里）。
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


def probe(pdf_path: Path) -> dict:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    facts: dict = {"pdf": str(pdf_path), "pages": doc.page_count}
    toc = doc.get_toc()
    facts["bookmarks_total"] = len(toc)

    # --- A. 书签目标页是否真的是标题所在页 -------------------------------
    pages_norm = [norm(doc[i].get_text()) for i in range(doc.page_count)]
    targets = []
    for _level, title, page in toc:
        keys = title_keys(title)
        if not keys:
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
    facts["bookmark_mismatches"] = [t for t in targets if not t["ok"]]

    # --- B. 后置区块页眉串章 ---------------------------------------------
    level1 = [(t, p) for lv, t, p in toc if lv == 1]
    facts["level1_chapters"] = [{"title": t, "page": p} for t, p in level1]
    numbered = [(t, p) for t, p in level1 if re.match(r"^\s*\d+\s", t or "")]
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

    facts["U01_ok"] = not facts["bookmark_mismatches"]
    facts["U02_ok"] = not hits
    doc.close()
    return facts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PDF 书签与页眉结构探针（只读）")
    ap.add_argument("--pdf", default="build/main.pdf")
    ap.add_argument("--out", default="build/pdf_probe.txt")
    ap.add_argument("--json", default="build/pdf_probe.json")
    args = ap.parse_args(argv)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 1
    facts = probe(pdf_path)

    lines = [f"PDF            : {facts['pdf']}",
             f"页数 / 书签数  : {facts['pages']} / {facts['bookmarks_total']}",
             f"R2-U01 书签落页 : {'PASS' if facts['U01_ok'] else 'FAIL'}"
             f"（检查 {len(facts['bookmark_targets'])} 条，不符 "
             f"{len(facts['bookmark_mismatches'])} 条）"]
    for row in facts["bookmark_mismatches"]:
        lines.append(f"    - 书签「{row['title']}」目标页 {row['bookmark_page']}，"
                     f"标题实际首见于 {row['first_page_with_title']}"
                     f"（键 {row['matched_key']}）")
    lines.append(f"R2-U02 后置页眉 : {'PASS' if facts['U02_ok'] else 'FAIL'}"
                 f"（命中 {len(facts['backmatter_header_hits'])} 处；扫描自 p."
                 f"{facts['backmatter_scan_from']}，最后一个编号章「"
                 f"{facts['last_numbered_chapter']['title']}」在 p."
                 f"{facts['last_numbered_chapter']['page']}）")
    for row in facts["backmatter_header_hits"]:
        lines.append(f"    - p.{row['page']}  页眉带 y0={row['y0']}：{row['text']}"
                     f" ［{row['why']}］")
    lines.append("")
    tail = facts["backmatter_scan_from"]
    lines.append("后置区块书签目标页：" + "、".join(
        f"{r['title']}={r['bookmark_page']}" for r in facts["bookmark_targets"]
        if r["bookmark_page"] >= tail))
    report = "\n".join(lines) + "\n"

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")
    Path(args.json).write_text(json.dumps(facts, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(report)
    return 0 if (facts["U01_ok"] and facts["U02_ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
