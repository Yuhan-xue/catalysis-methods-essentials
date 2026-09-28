# -*- coding: utf-8 -*-
"""Validation v2: match DOWN TOC entries by section number + first characters of the
title, against the mapped book page.  Also compare covers numerically."""
import re, csv, glob
import numpy as np, pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDF_UP = glob.glob(r"C:\Users\53150\.dsh\attachments\v1\files\9f\*\*.pdf")[0]
PDF_DN = glob.glob(r"C:\Users\53150\.dsh\attachments\v1\files\a1\*\*.pdf")[0]

pagemap = {}
for r in csv.DictReader(open(ROOT + r"\sources\page_map_down.csv", encoding="utf-8-sig")):
    if r["book_page"].strip().isdigit():
        pagemap[int(r["pdf_page"])] = int(r["book_page"])

toc = []
for line in open(ROOT + r"\sources\toc\down_toc_raw.txt", encoding="utf-8"):
    m = re.match(r"^\s*(\d{1,2}(?:\.\d{1,2}){1,2})\s+(.*?)[·\s]{3,}(\d{2,3})\s*$", line)
    if m:
        toc.append((m.group(1), m.group(2).strip(), int(m.group(3))))

doc = pymupdf.open(PDF_DN)
joined = {}
for p in range(18, 463):
    joined[p] = doc[p - 1].get_text("text").replace(" ", "").replace("\u3000", "").replace("\n", "")

ok = bad = notfound = 0
badlist = []
for sec, title, page in toc:
    probe = (sec + title)[:12]
    found = None
    for p in range(18, 463):
        if probe in joined[p]:
            found = p
            break
    if found is None:
        notfound += 1
        badlist.append((sec, title[:24], page, None, None))
        continue
    if pagemap.get(found) == page:
        ok += 1
    else:
        bad += 1
        badlist.append((sec, title[:24], page, found, pagemap.get(found)))
out = [f"DOWN TOC entries matched by 'sec+title[:8]': exact {ok}, mismatch {bad}, not found {notfound}",
       "(sec, title, toc_page, first_pdf_page, mapped_book_page):"]
for b in badlist:
    out.append("   " + str(b))

# cover comparison: downscale both covers to a common grid
for tag, pdf in (("UP", PDF_UP), ("DOWN", PDF_DN)):
    d = pymupdf.open(pdf)
    n = d.page_count
    a = []
    for p in (1, n):
        pix = d[p - 1].get_pixmap(dpi=50, colorspace=pymupdf.csGRAY)
        m = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
        yi = (np.arange(80) * m.shape[0] / 80).astype(int).clip(0, m.shape[0] - 1)
        xi = (np.arange(60) * m.shape[1] / 60).astype(int).clip(0, m.shape[1] - 1)
        a.append(m[np.ix_(yi, xi)])
    diff = float(np.abs(a[0] - a[1]).mean())
    out.append(f"{tag}: first vs last page, mean|Δ| on a 80x60 grid = {diff:.1f} / 255 "
               f"(ink at 100dpi: {int((a[0] < 170).sum())} vs {int((a[1] < 170).sum())})")
    out.append("     first row means: " + np.array2string(a[0].mean(axis=1)[:6], precision=0))
    out.append("     last  row means: " + np.array2string(a[1].mean(axis=1)[:6], precision=0))
    d.close()
open(ROOT + r"\tools\out\down_toc_validation.txt", "w", encoding="utf-8").write("\n".join(out))
print(out[0][:110])
for l in out[-6:]:
    print(l[:110])
