# -*- coding: utf-8 -*-
"""Front-matter analysis for both volumes: where is the folio and what does it read?"""
import os
import numpy as np, pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDFS = {
 "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
 "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}
RANGE = {"up": range(1, 21), "down": range(1, 19)}
S = 200 / 72.0
out = []
for vol, rng in RANGE.items():
    doc = pymupdf.open(PDFS[vol])
    for p in rng:
        pg = doc[p - 1]
        w, h = pg.rect.width, pg.rect.height
        pix = pg.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        whole = int((a < 170).sum())

        def dk(r):
            x0 = max(0, int(r[0] * S)); x1 = min(a.shape[1], int(r[2] * S))
            y0 = max(0, int(r[1] * S)); y1 = min(a.shape[0], int(r[3] * S))
            if x1 <= x0 or y1 <= y0:
                return -1
            return int((a[y0:y1, x0:x1] < 170).sum())

        # all text lines with y0 < 0.08*h  (running head / folio zone)
        d = pg.get_text("dict")
        head = []
        for blk in d["blocks"]:
            if blk.get("type") != 0:
                continue
            for ln in blk["lines"]:
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t and ln["bbox"][1] < 0.09 * h:
                    head.append((round(ln["bbox"][0], 1), round(ln["bbox"][1], 1), t[:40],
                                 dk(ln["bbox"])))
        out.append(f"--- {vol} pdf {p}  {w:.0f}x{h:.0f}  page_ink={whole}")
        for x, y, t, ink in head:
            out.append(f"      x0={x:6.1f} y0={y:5.1f} ink={ink:6d}  {t!r}")
        if not head:
            out.append("      (no line in the top 9%)")
open(os.path.join(ROOT, "tools/out/frontmatter.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
