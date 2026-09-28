# -*- coding: utf-8 -*-
"""Render the section-number prefix of UP section headings as ASCII art.

For each requested UP pdf page we locate the first heading line (font size >= 11.5),
then render the left part of that line (the section number + a couple of title chars)
so the printed number can be read back from the bitmap.
"""
import os
import numpy as np, pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
DPI = 300
S = DPI / 72.0
K = 3
RAMP = " .:-=+*#%@"
PAGES = [190, 226, 241, 257, 297, 331, 339, 344, 364, 421, 436, 462, 467, 508, 522, 527]
doc = pymupdf.open(P)
out = []
for p in PAGES:
    pg = doc[p - 1]
    found = None
    for blk in pg.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk["lines"]:
            t = "".join(s["text"] for s in ln["spans"]).strip()
            size = max(s["size"] for s in ln["spans"])
            if t and t[0].isdigit() and size >= 11.4 and ln["bbox"][1] > 55:
                found = (ln["bbox"], t, size)
                break
        if found:
            break
    if not found:
        out.append(f"##### up p{p} (book {p-19}) -- no heading line found")
        continue
    (x0, y0, x1, y1), t, size = found
    x1 = min(x1, x0 + 7 * size + 4)
    pix = pg.get_pixmap(dpi=DPI, clip=pymupdf.Rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2),
                        colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
    ys, xs = np.nonzero(a < 170)
    if ys.size:
        a = a[max(0, ys.min() - 2):ys.max() + 3, max(0, xs.min() - 2):xs.max() + 3]
    hh, ww = a.shape[0] // K, a.shape[1] // K
    if hh < 2 or ww < 2:
        out.append(f"##### up p{p} -- region too small")
        continue
    b = a[:hh * K, :ww * K].reshape(hh, K, ww, K).mean(axis=(1, 3))
    out.append(f"##### up p{p} -> book {p-19} | textlayer says size={size:.1f} text={t[:26]!r} "
               f"| art {ww}x{hh}, 1 char = {K}x{K} px @300dpi")
    for row in b:
        out.append("".join(RAMP[min(9, int((255 - v) / 25.6))] for v in row))
open(os.path.join(ROOT, "tools/out/verify_headings.txt"), "w", encoding="utf-8").write("\n".join(out))
print("lines:", len(out))
