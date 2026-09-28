# -*- coding: utf-8 -*-
"""Dump text blocks with bboxes for a page -> UTF-8 report."""
import sys, os
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}

vol = sys.argv[1]
page = int(sys.argv[2])
doc = pymupdf.open(PDF[vol])
pg = doc[page - 1]
lines = [f"vol={vol} page={page} rect={pg.rect}"]
d = pg.get_text("dict")
for b in d["blocks"]:
    if b.get("type") != 0:
        lines.append(f"BLOCK(type={b.get('type')}) bbox={[round(v,1) for v in b['bbox']]}")
        continue
    bt = "".join(s["text"] for l in b["lines"] for s in l["spans"])
    lines.append(f"BLOCK bbox={[round(v,1) for v in b['bbox']]} text={bt[:90]!r}")
    for l in b["lines"]:
        for s in l["spans"]:
            lines.append(
                f"    span bbox={[round(v,1) for v in s['bbox']]} size={round(s['size'],1)} "
                f"font={s['font']!r} text={s['text'][:70]!r}"
            )
out = os.path.join(ROOT, f"tools/blocks_{vol}_p{page}.txt")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("->", out, len(lines), "lines")
