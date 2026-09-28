# -*- coding: utf-8 -*-
"""Diagnose DOWN pdf pages 16-20: geometry, rotation, ink rows."""
import numpy as np, pymupdf, os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
doc = pymupdf.open(PDF)
out = []
for p in [16, 17, 18, 19, 20, 21]:
    pg = doc[p - 1]
    pix = pg.get_pixmap(dpi=100, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    dark = a < 160
    rowsum = dark.sum(axis=1)
    nz = np.nonzero(rowsum)[0]
    out.append(f"pdf {p}: rect={pg.rect} rot={pg.rotation} mediabox={pg.mediabox} cropbox={pg.cropbox} "
               f"pix={pix.width}x{pix.height} dark_total={int(dark.sum())} "
               f"ink_rows={nz.min() if nz.size else None}..{nz.max() if nz.size else None}")
    # ink profile in 10 bands
    bands = [int(dark[i * pix.height // 10:(i + 1) * pix.height // 10].sum()) for i in range(10)]
    out.append(f"        band ink (10ths): {bands}")
    # sample of text
    t = pg.get_text("text").splitlines()
    out.append(f"        nlines={len(t)} first={t[:3]!r}")
    out.append(f"        images_on_page={len(pg.get_images(full=True))}")
open(os.path.join(ROOT, "tools/out/down_diag.txt"), "w", encoding="utf-8").write("\n".join(out))
print("ok")
