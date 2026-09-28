# -*- coding: utf-8 -*-
"""Detect chapter start PDF pages in both volumes by running-head transitions.

Robust to per-glyph span splitting: joins spans into lines first.
Outputs sources/chapter_ranges.csv
"""
import os, re, csv
from collections import defaultdict
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
FW = str.maketrans("０１２３４５６７８９．", "0123456789.")
pat = re.compile(r"第\s*([0-9０-９]{1,2})\s*章")

report = []
ranges = {}

for vol, path in PDF.items():
    doc = pymupdf.open(path)
    headch = {}       # pdf_page -> chapter number seen in the top strip
    topline = {}      # pdf_page -> (text, size) of the largest line in the top strip
    for p in range(1, doc.page_count + 1):
        pg = doc[p - 1]
        d = pg.get_text("dict")
        best = None
        found = None
        for b in d["blocks"]:
            if b.get("type") != 0:
                continue
            for l in b["lines"]:
                txt = "".join(s["text"] for s in l["spans"])
                size = max((s["size"] for s in l["spans"]), default=0)
                y = l["bbox"][1]
                if y < 70:
                    m = pat.search(txt.translate(FW))
                    if m and found is None:
                        found = int(m.group(1))
                if best is None or size > best[1]:
                    best = (txt, size, y)
        if found is not None:
            headch[p] = found
        if best:
            topline[p] = best

    first = {}
    for p in sorted(headch):
        ch = headch[p]
        if ch not in first:
            first[ch] = p
    report.append(f"--- {vol}: chapters seen in running heads: {sorted(first)}")
    for ch in sorted(first):
        report.append(f"    ch{ch:>2}  first running-head page = {first[ch]}")
    ranges[vol] = first

    # also: the largest-type line on a chapter-opening page is usually 第N章
    bigopen = {}
    for p in sorted(topline):
        txt, size, y = topline[p]
        m = pat.search(txt.translate(FW))
        if m and size >= 13:
            ch = int(m.group(1))
            if ch not in bigopen:
                bigopen[ch] = (p, round(size, 1), txt.strip()[:30])
    report.append(f"    large-type chapter openers: {bigopen}")
    ranges[vol + "_big"] = bigopen

open(os.path.join(ROOT, "tools/chapter_ranges_report.txt"), "w", encoding="utf-8").write("\n".join(report))

# write CSV combining the best evidence
rows = []
for vol in ("up", "down"):
    big = ranges.get(vol + "_big", {})
    head = ranges.get(vol, {})
    for ch in sorted(set(list(big.keys()) + list(head.keys()))):
        rows.append({
            "vol": vol,
            "ch": ch,
            "pdf_start_bigtype": big.get(ch, (None,))[0] if ch in big else "",
            "pdf_first_head": head.get(ch, ""),
            "evidence": big.get(ch, (None, None, ""))[2] if ch in big else "",
        })
with open(os.path.join(ROOT, "sources/chapter_ranges.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["vol", "ch", "pdf_start_bigtype", "pdf_first_head", "evidence"])
    w.writeheader()
    w.writerows(rows)
print("\n".join(report))
print("-> sources/chapter_ranges.csv")
