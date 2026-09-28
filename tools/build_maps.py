# -*- coding: utf-8 -*-
"""Rebuild page maps for both volumes from running heads / TOC anchors.

Outputs (UTF-8):
  tools/out/down_heads.txt     per-page running-head facts for DOWN
  tools/out/up_toc_parsed.txt  parsed UP TOC (sec, printed page)
  tools/out/down_toc_parsed.txt parsed DOWN TOC
  tools/out/report.txt         diagnostics
"""
import os, re, csv, sys, json
import pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
OUT = os.path.join(ROOT, "tools", "out")
os.makedirs(OUT, exist_ok=True)
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
FW = str.maketrans("０１２３４５６７８９．", "0123456789.")


def norm(s):
    return s.translate(FW).replace(" ", "").replace("\u3000", "")


def top_head(pg):
    """Return (text_of_topmost_text_region, y0, page_h)."""
    h = pg.rect.height
    blocks = [b for b in pg.get_text("blocks") if b[6] == 0 and b[4].strip()]
    blocks.sort(key=lambda b: (b[1], b[0]))
    for b in blocks:
        if b[1] < 0.12 * h:
            return b[4].strip().replace("\n", " "), b[1], h
    return "", None, h


PAT_DOT = re.compile(r"[·•]\s*(\d{1,4})\s*[·•]")
PAT_ROMAN = re.compile(r"[·•]\s*([ivxIVX]{1,7})\s*[·•]")

doc_dn = pymupdf.open(PDF["down"])
lines = []
heads = {}
for p in range(1, doc_dn.page_count + 1):
    pg = doc_dn[p - 1]
    txt = pg.get_text("text")
    headtxt, y0, h = top_head(pg)
    first3 = " | ".join(x.strip() for x in txt.splitlines()[:3] if x.strip())
    m = PAT_DOT.search(headtxt[:90])
    num = int(m.group(1)) if m else ""
    mr = PAT_ROMAN.search(headtxt[:90])
    rom = mr.group(1) if mr else ""
    # fallback: whole page
    if num == "":
        m2 = PAT_DOT.search(first3)
        if m2:
            num = int(m2.group(1))
            src = "fallback3line"
        else:
            src = ""
    else:
        src = "topblock"
    heads[p] = {"num": num, "rom": rom, "src": src, "head": headtxt[:80],
                "first3": first3[:110], "y0": y0, "h": round(h, 1)}
    lines.append(f"p{p:>4} y0={y0} h={h:.0f} num={num!r:>6} rom={rom!r:>5} src={src:<14} head={headtxt[:80]!r}")
open(os.path.join(OUT, "down_heads.txt"), "w", encoding="utf-8").write("\n".join(lines))

with open(os.path.join(OUT, "down_heads.txt"), encoding="utf-8") as f:
    print("wrote down_heads.txt", len(lines), "lines")

# ---- offset steps in DOWN (Arabic only) ----
found = [(p, v["num"]) for p, v in sorted(heads.items()) if v["num"] != ""]
offrep = []
prev = None
for p, b in found:
    off = p - b
    if prev is not None and off != prev[1]:
        offrep.append(f"STEP at pdf {prev[0]}(bp {prev[2]}, off {prev[1]}) -> pdf {p}(bp {b}, off {off})  jump={off - prev[1]}  => missing printed page(s): "
                      + ",".join(str(x) for x in range(prev[2] + 1, b)))
    prev = (p, off, b)
print("arabic entries:", len(found), " first:", found[0], " last:", found[-1])
print("steps:", len(offrep))
for s in offrep:
    print("  ", s)

# consecutive-pdf-page consistency: same-page-number duplicates or non +1 increments
bad = []
for i in range(1, len(found)):
    dp = found[i][0] - found[i - 1][0]
    db = found[i][1] - found[i - 1][1]
    if dp != 1 or db != 1:
        bad.append(f"pdf {found[i-1][0]}->{found[i][0]} (d_pdf={dp}) bp {found[i-1][1]}->{found[i][1]} (d_bp={db})")
print("irregular adjacencies:", len(bad))
for s in bad[:40]:
    print("  ", s)

# missing pdf pages inside the arabic run
pp = [p for p, _ in found]
gaps = [p for p in range(min(pp), max(pp) + 1) if p not in pp]
print("pdf pages inside arabic run without a number:", gaps)
print("front-matter pages (1..%d) states:" % (min(pp) - 1))
for p in range(1, min(pp)):
    v = heads[p]
    print(f"   p{p}: num={v['num']!r} rom={v['rom']!r} first3={v['first3'][:90]!r}")
print("tail pages:")
for p in range(max(pp) + 1, doc_dn.page_count + 1):
    v = heads[p]
    print(f"   p{p}: num={v['num']!r} rom={v['rom']!r} first3={v['first3'][:90]!r}")
