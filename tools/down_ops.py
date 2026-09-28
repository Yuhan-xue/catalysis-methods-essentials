# -*- coding: utf-8 -*-
import numpy as np, pymupdf, os, json
ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
PDF = r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(PDF)
out = []
for p in [17, 18, 19, 59, 60, 224, 225, 226, 296, 297, 371, 372, 373]:
    pg = doc[p - 1]
    out.append(f"===== pdf {p} =====")
    out.append("TEXT:")
    for ln in pg.get_text("text").splitlines():
        out.append("   |" + ln)
    out.append("BLOCKS (x0,y0,x1,y1,text):")
    for b in sorted(pg.get_text("blocks"), key=lambda b: b[1]):
        if b[6] == 0 and b[4].strip():
            out.append(f"   ({b[0]:.0f},{b[1]:.0f},{b[2]:.0f},{b[3]:.0f}) {b[4].strip()[:70]!r}")
    out.append("IMAGES:")
    for im in pg.get_image_info():
        out.append(f"   bbox=({im['bbox'][0]:.0f},{im['bbox'][1]:.0f},{im['bbox'][2]:.0f},{im['bbox'][3]:.0f}) w={im['width']} h={im['height']}")
    pix = pg.get_pixmap(dpi=100, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    d = a < 160
    nz = np.nonzero(d.sum(axis=1))[0]
    out.append(f"INK: total={int(d.sum())} rows {nz.min() if nz.size else None}..{nz.max() if nz.size else None} of {pix.height}")
    bands = [int(d[i*pix.height//20:(i+1)*pix.height//20].sum()) for i in range(20)]
    out.append(f"     20th-bands: {bands}")
open(os.path.join(ROOT, "tools/out/down_ops.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
