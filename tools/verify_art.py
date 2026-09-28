# -*- coding: utf-8 -*-
"""Render the printed folio of selected pages as compact ASCII art, in one file.

Each page: crop to the ink bounding box inside the folio slot, downsample x2 so a
digit is about 14x22 characters -> readable as text.
"""
import os
import numpy as np, pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDFS = {
 "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
 "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
DPI = 300
S = DPI / 72.0
RAMP = " .:-=+*#%@"
JOBS = [
    # (vol, page, x0, y0, x1, y1, comment)
    ("up", 22, 380, 26, 455, 56, "UP first text page of ch1 (book 3) - expect running head, folio? "),
    ("up", 23, 380, 26, 455, 56, "UP book 4 (even parity)"),
    ("up", 100, 380, 26, 455, 56, "UP book 81"),
    ("up", 104, 0, 0, 456, 200, "UP ch2 title page (book 85) - top half"),
    ("up", 268, 380, 26, 455, 56, "UP book 249"),
    ("up", 331, 0, 33, 456, 52, "UP book 312 - head line, sec 5.3.2 starts here"),
    ("up", 421, 0, 33, 456, 52, "UP book 402 - head line, sec 6.5"),
    ("up", 462, 0, 33, 456, 52, "UP book 443 - head line, sec 7.2"),
    ("up", 508, 0, 33, 456, 52, "UP book 489 - head line, sec 7.5"),
    ("up", 536, 380, 26, 455, 56, "UP book 517"),
    ("up", 540, 380, 26, 455, 56, "UP book 521"),
    ("up", 542, 380, 26, 455, 56, "UP book 523 (last numbered page)"),
    ("up", 543, 0, 0, 456, 120, "UP back cover"),
    ("down", 20, 40, 34, 440, 62, "DOWN book 528 (verso: folio left + book title)"),
    ("down", 224, 40, 34, 440, 62, "DOWN book 733"),
    ("down", 226, 380, 34, 440, 62, "DOWN book 737"),
    ("down", 297, 380, 34, 440, 62, "DOWN book 809"),
    ("down", 373, 380, 34, 440, 62, "DOWN book 887"),
    ("down", 7, 40, 34, 440, 62, "DOWN 丛书序 first page - is a folio printed?"),
    ("down", 8, 40, 34, 440, 62, "DOWN 丛书序 cont."),
    ("down", 18, 40, 0, 440, 120, "DOWN ch8 title page (book 525) top"),
    ("down", 225, 40, 0, 440, 120, "DOWN ch10 title page (book 735) top"),
]
out = []
for vol, p, x0, y0, x1, y1, cmt in JOBS:
    doc = pymupdf.open(PDFS[vol])
    pg = doc[p - 1]
    pix = pg.get_pixmap(dpi=DPI, clip=pymupdf.Rect(x0, y0, x1, y1), colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(np.float32)
    mask = a < 170
    ys, xs = np.nonzero(mask)
    if ys.size:
        a = a[max(0, ys.min() - 3):ys.max() + 4, max(0, xs.min() - 3):xs.max() + 4]
    k = 2
    hh, ww = a.shape[0] // k, a.shape[1] // k
    if hh < 2 or ww < 2:
        out.append(f"##### {vol} p{p}  [{cmt}]  bbox_px={a.shape} ink={int(mask.sum())}  -- NO INK in this region")
        doc.close()
        continue
    b = a[:hh * k, :ww * k].reshape(hh, k, ww, k).mean(axis=(1, 3))
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())) if ys.size else None
    out.append(f"##### {vol} p{p}  [{cmt}]  bbox_px={bbox} ink={int(mask.sum())}  "
               f"(rendered {ww}x{hh} chars, 1 char = 2x2 px @300dpi)")
    for row in b:
        out.append("".join(RAMP[min(9, int((255 - v) / 25.6))] for v in row))
    doc.close()
open(os.path.join(ROOT, "tools/out/verify_art.txt"), "w", encoding="utf-8").write("\n".join(out))
print("wrote verify_art.txt", len(out), "lines")
