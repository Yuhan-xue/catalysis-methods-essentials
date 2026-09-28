# -*- coding: utf-8 -*-
"""Stage 1b/1c: dump TOC pages, build page mapping, detect section-heading anchors.

Outputs (all UTF-8, under sources/):
  toc/up_toc_raw.txt        raw text of UP TOC pages
  toc/down_toc_raw.txt      raw text of DOWN TOC pages
  page_map_down.csv         pdf_page,book_page,chapter  (from running head ·NNN·)
  anchors_up.csv            section heading occurrences in UP body -> pdf_page
  anchors_down.csv          same for DOWN
"""
import os, re, csv, json
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}

TOC_RANGE = {"up": (13, 19), "down": (12, 17)}

os.makedirs(os.path.join(ROOT, "sources", "toc"), exist_ok=True)

# ---------- 1. TOC raw dump ----------
docs = {}
for vol, (a, b) in TOC_RANGE.items():
    doc = pymupdf.open(PDF[vol])
    docs[vol] = doc
    chunks = []
    for p in range(a, b + 1):
        chunks.append(f"\n<<<<< {vol} PDF p.{p} >>>>>\n")
        chunks.append(doc[p - 1].get_text("text"))
    outp = os.path.join(ROOT, f"sources/toc/{vol}_toc_raw.txt")
    open(outp, "w", encoding="utf-8").write("".join(chunks))
    print("toc ->", outp)

# ---------- 2. DOWN page map from running heads ----------
pat_dot = re.compile(r"[·•]\s*(\d{1,4})\s*[·•]")
rows = []
dn = docs["down"]
for p in range(1, dn.page_count + 1):
    t = dn[p - 1].get_text("text")
    head = "\n".join(t.splitlines()[:3])
    m = pat_dot.search(head)
    num = int(m.group(1)) if m else ""
    rows.append({"pdf_page": p, "book_page": num, "head": head.replace("\n", " ")[:70]})
with open(os.path.join(ROOT, "sources/page_map_down.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["pdf_page", "book_page", "head"])
    w.writeheader()
    w.writerows(rows)
found = [r for r in rows if r["book_page"] != ""]
print(f"down page map: {len(found)}/{len(rows)} pages have printed number")
# offset analysis
for r in found[:5] + found[-5:]:
    print("   ", r["pdf_page"], "->", r["book_page"], "off", r["pdf_page"] - r["book_page"])
offs = sorted({r["pdf_page"] - r["book_page"] for r in found})
print("   distinct offsets:", offs[:12], "..." if len(offs) > 12 else "")

# ---------- 3. Heading anchors (both volumes) ----------
# section numbers look like 1.1  /  1.1.2  /  12.5.5 ; UP OCR uses full-width digits
FW = str.maketrans("０１２３４５６７８９．", "0123456789.")
pat_head = re.compile(r"^\s*(\d{1,2}(?:\.\d{1,2}){1,2})\s*[　 \u3000]*([^\s\d].{0,40})$")


def norm(s):
    return s.translate(FW).replace(" ", "").replace("\u3000", "")


for vol, doc in docs.items():
    out = []
    for p in range(1, doc.page_count + 1):
        for line in doc[p - 1].get_text("text").splitlines():
            nl = norm(line)
            m = pat_head.match(nl)
            if m:
                out.append({"pdf_page": p, "sec": m.group(1), "title": m.group(2)[:44]})
    fp = os.path.join(ROOT, f"sources/anchors_{vol}.csv")
    with open(fp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pdf_page", "sec", "title"])
        w.writeheader()
        w.writerows(out)
    print(f"anchors {vol}: {len(out)} -> {fp}")
