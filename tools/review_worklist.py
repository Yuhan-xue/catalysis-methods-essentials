#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Build the machine-readable worklists for the three content-level acceptance
# items:
#   1. page-by-page content read   (artifact pages -> owning slice)
#   2. numbered-formula crosscheck (every \label{eq:...} -> printed number, page,
#                                   nearest source page hint)
#   3. T2 table cell verification  (59 tables -> file:line, artifact page,
#                                   source pages from the table's own \src)
#
# Inputs (read-only): build/main.aux, build/main.toc, build/main.pdf,
#                     chapters/parts/*.tex, chapters/*.tex, sources/table_status.md
# Outputs (gitignored): build/review_worklist.json,
#                       build/work_pages.tsv, build/work_formulas.tsv,
#                       build/work_tables.tsv,
#                       build/work_groups/<group>.tsv
#
# ASCII-only on purpose: the project's file tooling mangles non-ASCII in .py.
#
# Usage: python tools/review_worklist.py [--check]
#        --check  fail (exit 1) on page gaps/overlaps, unresolved eq numbers,
#                 unplaced slice files, or unresolved table pages.

import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
PARTS = os.path.join(ROOT, "chapters", "parts")
CHAPDIR = os.path.join(ROOT, "chapters")
AUX = os.path.join(BUILD, "main.aux")
TOC = os.path.join(BUILD, "main.toc")
PDF = os.path.join(BUILD, "main.pdf")
TABLE_STATUS = os.path.join(ROOT, "sources", "table_status.md")

# page groups for item 1 (artifact page numbers, inclusive)
PAGE_GROUPS = {
    "p1": (5, 88),
    "p2": (89, 176),
    "p3": (177, 264),
    "p4": (265, 339),
}

# slice groups for item 2 (every numbered equation of the slice must be judged)
FORMULA_GROUPS = {
    "f1": ["ch01-a", "ch01-b", "ch01-c", "ch02-a", "ch02-b", "ch02-c"],
    "f2": ["ch03-a", "ch03-b", "ch04-a", "ch04-b", "ch04-c"],
    "f3": ["ch05-a", "ch05-b", "ch06-a", "ch06-b", "ch06-c",
           "ch07-a", "ch07-b", "ch07-c", "ch08-a", "ch08-b", "ch08-c"],
    "f4": ["ch09-a", "ch09-b", "ch09-c", "ch09-d", "ch10-a", "ch10-b", "ch10-c"],
    "f5": ["ch11-a", "ch11-b", "ch11-c", "ch11-d", "ch12-a", "ch12-b", "ch12-c"],
}

# table groups for item 3: split the T2 list in source order
TABLE_GROUPS = {"t1": (0, 30), "t2": (30, 59)}

SRC_BOOK_RE = re.compile(r"\u4e66\u5185\s*p\.?\s*([0-9]+)")
SRC_PDF_RE = re.compile(r"PDF\s*p\.?\s*([0-9]+)")


def read(path, encoding="utf-8"):
    with open(path, encoding=encoding) as fh:
        return fh.read()


def brace_group(text, start):
    """Return (content, next_index) of the brace group starting at text[start]."""
    if start >= len(text) or text[start] != "{":
        return None, start
    depth = 0
    i = start
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
        i += 1
    return None, start


def norm_title(s):
    s = s or ""
    s = re.sub(r"\\numberline\s*\{[^{}]*\}", "", s)
    s = re.sub(r"\\texorpdfstring\s*\{([^{}]*)\}\s*\{[^{}]*\}", r"\1", s)
    s = re.sub(r"\\ce\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("$", "").replace("\\", "")
    s = re.sub(r"\s+", "", s)
    return s


def parse_aux(path):
    """label -> {num, page} from \\newlabel lines (brace-aware: captions nest)."""
    out = {}
    txt = read(path)
    for m in re.finditer(r"\\newlabel\{([^{}]+)\}\{", txt):
        label = m.group(1)
        body, _ = brace_group(txt, m.end() - 1)
        if body is None or not body.startswith("{"):
            continue
        num, i = brace_group(body, 0)
        page = None
        if i < len(body) and body[i] == "{":
            page_s, _ = brace_group(body, i)
            try:
                page = int(page_s)
            except (TypeError, ValueError):
                page = None
        if label.endswith("@cref"):
            continue
        out.setdefault(label, {"num": num, "page": page})
    return out


def parse_toc(path):
    entries = []
    txt = read(path)
    for m in re.finditer(r"\\contentsline\s*\{(section|subsection|subsubsection)\}", txt):
        level = m.group(1)
        tit, i = brace_group(txt, m.end())
        num, i2 = brace_group(txt, i) if i < len(txt) and txt[i] == "{" else (None, i)
        if tit is None:
            continue
        try:
            page = int(num)
        except (TypeError, ValueError):
            continue
        entries.append({"level": level, "title": tit, "norm": norm_title(tit), "page": page})
    return entries


def split_header(text):
    info = {"vol": "", "src_book": "", "src_pdf": ""}
    for line in text.splitlines()[:14]:
        if not line.startswith("%"):
            continue
        if "\u4e0a\u518c" in line:
            info["vol"] = "up"
        elif "\u4e0b\u518c" in line:
            info["vol"] = "down"
        m = re.search(r"\u4e66\u5185\s*p\.?\s*([0-9]+)\s*[\u2014\u2013-]+\s*([0-9]+)", line)
        if m:
            info["src_book"] = "%s-%s" % (m.group(1), m.group(2))
        m = re.search(r"PDF\s*p\.?\s*([0-9]+)\s*[\u2014\u2013-]+\s*([0-9]+)", line)
        if m:
            info["src_pdf"] = "%s-%s" % (m.group(1), m.group(2))
    return info


def first_heading(text):
    pat = re.compile(r"\\(chapterstart|chapter|section|subsection|subsubsection)\*?\{")
    for m in pat.finditer(text):
        arg, _ = brace_group(text, m.end() - 1)
        if arg is not None:
            return {"level": m.group(1), "title": arg, "norm": norm_title(arg)}
    return None


def nearest_src(lines, idx, window=45):
    """Nearest 'shu-nei / PDF p.N' mention around line idx (0-based)."""
    best = None
    for d in range(0, window + 1):
        for j in (idx - d, idx + d):
            if j < 0 or j >= len(lines) or (d == 0 and j != idx):
                continue
            line = lines[j]
            mb = SRC_BOOK_RE.search(line)
            mp = SRC_PDF_RE.search(line)
            if mb or mp:
                return (mb.group(1) if mb else "", mp.group(1) if mp else "", d)
    return best or ("", "", -1)


def units_from(paths):
    out = []
    for path in sorted(paths):
        text = read(path)
        name = os.path.splitext(os.path.basename(path))[0]
        head = first_heading(text)
        info = split_header(text)
        lines = text.splitlines()
        eqs = []
        for m in re.finditer(r"\\label\{(eq:[^{}]+)\}", text):
            idx = text.count("\n", 0, m.start())
            sb, sp, dist = nearest_src(lines, idx)
            eqs.append({"label": m.group(1), "line": idx + 1,
                        "hint_book": sb, "hint_pdf": sp, "hint_dist": dist})
        tabs = []
        for m in re.finditer(r"\\label\{(tab:[^{}]+)\}", text):
            idx = text.count("\n", 0, m.start())
            # source pages claimed by the table's own caption/\src: scan a window
            lo = max(0, idx - 30)
            hi = min(len(lines), idx + 12)
            blob = "\n".join(lines[lo:hi])
            mb = SRC_BOOK_RE.findall(blob)
            mp = SRC_PDF_RE.findall(blob)
            tabs.append({"label": m.group(1), "line": idx + 1,
                         "hint_book": mb[0] if mb else "", "hint_pdf": mp[0] if mp else ""})
        if not head and not eqs and not tabs:
            continue  # pure \input wrapper (chapters/chNN.tex)
        out.append({
            "slice": name,
            "file": os.path.relpath(path, ROOT).replace("\\", "/"),
            "heading": head,
            "vol": info["vol"],
            "src_book": info["src_book"],
            "src_pdf": info["src_pdf"],
            "eqs": eqs,
            "tables": tabs,
        })
    return out


def t2_tables():
    """Parse the 59 T2 rows out of sources/table_status.md (in-place section)."""
    txt = read(TABLE_STATUS)
    rows = []
    sec = False
    for line in txt.splitlines():
        if line.startswith("## "):
            sec = "\u5c31\u5730\u6838\u5bf9\u8bf4\u660e" in line
            continue
        if not sec or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        m = re.match(r"`([^`]+)`", cells[1])
        loc = re.match(r"`([^`:]+):(\d+)`", cells[2])
        if not m or not loc:
            continue
        src = re.sub(r"[^0-9\u2014\u2013-]", "", cells[3]) or cells[3]
        rows.append({
            "id": m.group(1),
            "slice": loc.group(1),
            "line": int(loc.group(2)),
            "src_book": src.strip("-\u2013\u2014 "),
        })
    return rows


def assign_groups(frows, trows):
    for r in frows:
        r["fgroup"] = ""
    for gname, slices in FORMULA_GROUPS.items():
        for r in frows:
            if r["slice"] in slices:
                r["fgroup"] = gname
    for i, t in enumerate(trows):
        t["tgroup"] = ""
        for gname, (lo, hi) in TABLE_GROUPS.items():
            if lo <= i < hi:
                t["tgroup"] = gname


def main():
    check = "--check" in sys.argv
    aux = parse_aux(AUX)
    toc = parse_toc(TOC)
    units = units_from(glob.glob(os.path.join(PARTS, "*.tex")))
    units += units_from(glob.glob(os.path.join(CHAPDIR, "*.tex")))
    tables = t2_tables()
    pages = len(__import__("pymupdf").open(PDF))
    problems = []

    # ---- resolve slice start page from the table of contents
    for u in units:
        h = u["heading"]
        if not h:
            problems.append("%s: no heading" % u["slice"])
            u["start_page"] = None
            u["start_toc"] = ""
            continue
        same = [e for e in toc if e["norm"] == h["norm"]]
        if not same:
            same = [e for e in toc
                    if e["norm"].startswith(h["norm"]) or h["norm"].startswith(e["norm"])]
        if not same:
            problems.append("%s: heading %r not in toc" % (u["slice"], h["title"]))
            pgs = [aux[x["label"]]["page"] for x in u["eqs"] + u["tables"]
                   if aux.get(x["label"], {}).get("page")]
            u["start_page"] = min(pgs) if pgs else None
        else:
            u["start_page"] = min(e["page"] for e in same)
        u["start_toc"] = same[0]["title"] if same else ""

    # front matter (cover, title, preface, how-to-read head) belongs to no slice
    front = {"slice": "front", "file": "", "heading": {"title": "front matter"},
             "vol": "", "src_book": "", "src_pdf": "", "eqs": [], "tables": [],
             "start_page": 1, "start_toc": ""}
    units.append(front)
    units.sort(key=lambda x: (x["start_page"] is None, x["start_page"] or 0, x["slice"]))
    unplaced = [u for u in units if u["start_page"] is None]
    units = [u for u in units if u["start_page"] is not None]
    for u in unplaced:
        problems.append("%s: unplaced (no toc page)" % u["slice"])
    for i, u in enumerate(units):
        u["end_page"] = (units[i + 1]["start_page"] - 1) if i + 1 < len(units) else pages

    # ---- formulas
    frows = []
    for u in units:
        for e in u["eqs"]:
            a = aux.get(e["label"], {})
            frows.append({
                "label": e["label"], "num": a.get("num", ""), "page": a.get("page", ""),
                "slice": u["slice"], "line": e["line"], "vol": u["vol"],
                "src_book": u["src_book"], "src_pdf": u["src_pdf"],
                "hint_book": e.get("hint_book", ""), "hint_pdf": e.get("hint_pdf", ""),
                "hint_dist": e.get("hint_dist", ""),
            })

    # ---- tables
    hint = {}
    for u in units:
        for t in u["tables"]:
            hint[t["label"]] = t
    trows = []
    for t in tables:
        a = aux.get(t["id"], {})
        h = hint.get(t["id"], {})
        t["num"] = a.get("num", "")
        t["page"] = a.get("page", "")
        t["hint_book"] = h.get("hint_book", "")
        t["hint_pdf"] = h.get("hint_pdf", "")
        trows.append(t)

    assign_groups(frows, trows)

    # ---- page owners
    prows = []
    for p in range(1, pages + 1):
        owner = ""
        pgroup = ""
        for u in units:
            if u["start_page"] <= p <= u["end_page"]:
                owner = u["slice"]
                break
        for gname, (lo, hi) in PAGE_GROUPS.items():
            if lo <= p <= hi:
                pgroup = gname
        prows.append({"page": p, "slice": owner, "pgroup": pgroup})

    # ---- write
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(os.path.join(BUILD, "work_groups"), exist_ok=True)
    data = {"pages": pages, "slices": units, "formulas": frows, "tables": trows,
            "page_groups": PAGE_GROUPS, "formula_groups": FORMULA_GROUPS,
            "table_groups": TABLE_GROUPS, "problems": problems}
    with open(os.path.join(BUILD, "review_worklist.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    def dump_tsv(path, header, rows):
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t", lineterminator="\n")
            w.writerow(header)
            for r in rows:
                w.writerow([r.get(k, "") for k in header])

    dump_tsv(os.path.join(BUILD, "work_pages.tsv"), ["page", "slice", "pgroup"], prows)
    dump_tsv(os.path.join(BUILD, "work_formulas.tsv"),
             ["label", "num", "page", "slice", "line", "vol", "src_book", "src_pdf",
              "hint_book", "hint_pdf", "hint_dist", "fgroup"], frows)
    dump_tsv(os.path.join(BUILD, "work_tables.tsv"),
             ["id", "num", "page", "slice", "line", "src_book", "hint_book", "hint_pdf",
              "tgroup"], trows)

    for gname in PAGE_GROUPS:
        dump_tsv(os.path.join(BUILD, "work_groups", "pages_%s.tsv" % gname),
                 ["page", "slice"], [r for r in prows if r["pgroup"] == gname])
    for gname in FORMULA_GROUPS:
        dump_tsv(os.path.join(BUILD, "work_groups", "formulas_%s.tsv" % gname),
                 ["label", "num", "page", "slice", "line", "vol", "src_book", "src_pdf",
                  "hint_book", "hint_pdf"], [r for r in frows if r["fgroup"] == gname])
    for gname in TABLE_GROUPS:
        dump_tsv(os.path.join(BUILD, "work_groups", "tables_%s.tsv" % gname),
                 ["id", "num", "page", "slice", "line", "src_book", "hint_book", "hint_pdf"],
                 [r for r in trows if r["tgroup"] == gname])

    # ---- summary
    print("pages           : %d" % pages)
    print("slices          : %d" % len(units))
    print("eq labels       : %d" % len(frows))
    print("eq w/o aux num  : %d" % sum(1 for r in frows if not r["num"]))
    print("eq w/o fgroup   : %d" % sum(1 for r in frows if not r["fgroup"]))
    print("eq w/o page hint: %d" % sum(1 for r in frows if not (r["hint_pdf"] or r["src_pdf"])))
    print("T2 tables       : %d" % len(trows))
    print("T2 w/o aux page : %d" % sum(1 for r in trows if not r["page"]))
    print("T2 cell hints   : %d" % sum(1 for r in trows if r["hint_pdf"] or r["hint_book"]))
    covered = {}
    for u in units:
        for p in range(u["start_page"], u["end_page"] + 1):
            covered.setdefault(p, []).append(u["slice"])
    gaps = [p for p in range(1, pages + 1) if p not in covered]
    overlap = sorted(p for p, v in covered.items() if len(v) > 1)
    print("page gaps       : %d %s" % (len(gaps), gaps[:12]))
    print("page overlaps   : %d %s" % (len(overlap), overlap[:12]))
    print("")
    print("%-22s %9s %5s %5s %-4s %-9s %s"
          % ("slice", "pages", "eqs", "tabs", "vol", "src_book", "heading"))
    for u in units:
        print("  %-20s %4s-%-4s %4d %4d %-4s %-9s %s"
              % (u["slice"], u["start_page"], u["end_page"], len(u["eqs"]), len(u["tables"]),
                 u["vol"], u["src_book"], (u["heading"] or {}).get("title", "")[:30]))
    print("")
    for gname, slices in FORMULA_GROUPS.items():
        n = sum(1 for r in frows if r["fgroup"] == gname)
        print("  formula group %s: %d eqs  %s" % (gname, n, ",".join(slices)))
    for gname, (lo, hi) in TABLE_GROUPS.items():
        sel = trows[lo:hi]
        print("  table group %s: %d tables  %s" % (gname, len(sel),
                                                  ",".join(t["id"] for t in sel)[:150]))
    for p in problems:
        print("  PROBLEM " + p)
    if check and (gaps or overlap or problems or any(not r["num"] for r in frows)
                  or any(not r["fgroup"] for r in frows)
                  or any(not t["page"] for t in trows)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
