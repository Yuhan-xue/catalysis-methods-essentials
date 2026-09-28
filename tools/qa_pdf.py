# -*- coding: utf-8 -*-
"""QA: bookmarks, embedded fonts, per-page ink coverage, text extractability."""
import sys, os
import pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
pdf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "main.pdf")
out = []
doc = pymupdf.open(pdf)
out.append(f"file={pdf}  pages={doc.page_count}")

toc = doc.get_toc()
out.append(f"\n--- bookmarks ({len(toc)}) ---")
for lvl, title, page in toc[:30]:
    out.append(f"  {'  ' * (lvl - 1)}[{lvl}] {title}  -> p.{page}")

fonts = set()
for p in range(doc.page_count):
    for f in doc[p].get_fonts():
        # (xref, ext, type, basefont, name, encoding)
        fonts.add((f[3], f[1], f[2]))
out.append(f"\n--- fonts ({len(fonts)}) ---")
for base, ext, typ in sorted(fonts):
    emb = "EMBEDDED" if ext else "NOT-EMBEDDED"
    out.append(f"  {emb:<12} {typ:<10} {base}")

out.append("\n--- per page: chars, ink%, first line ---")
for p in range(doc.page_count):
    pg = doc[p]
    t = pg.get_text("text")
    n = len([c for c in t if not c.isspace()])
    pix = pg.get_pixmap(dpi=50, colorspace=pymupdf.csGRAY)
    import numpy as np
    a = np.frombuffer(pix.samples, dtype=np.uint8)
    ink = float((a < 200).mean()) * 100
    first = next((l for l in t.splitlines() if l.strip()), "")
    out.append(f"  p.{p+1:>3}  chars={n:>5}  ink={ink:5.1f}%  {first[:46]}")

open(os.path.join(ROOT, "tools/qa_report.txt"), "w", encoding="utf-8").write("\n".join(out))
print("->", os.path.join(ROOT, "tools/qa_report.txt"))
