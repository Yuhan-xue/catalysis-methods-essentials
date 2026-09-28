# -*- coding: utf-8 -*-
r"""Render a region of OUR OWN book page, for visual acceptance checks.

`vpage.py` only handles the two source PDFs. This one handles `build/main.pdf`,
which is what 阶段5（逐页渲染核查）actually needs.

Usage:
    python tools/vbook.py 16 out.png [--dpi 300] [--top 0.0] [--bottom 1.0]
                                     [--left 0.0] [--right 1.0]

Fractions are of the page box, same convention as vpage.py, so a figure can be
cropped tightly and inspected at high resolution without re-reading whole pages.
"""
import argparse, os, sys

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "build", "main.pdf")

ap = argparse.ArgumentParser()
ap.add_argument("page", type=int, help="1-based page number")
ap.add_argument("out")
ap.add_argument("--dpi", type=int, default=200)
ap.add_argument("--top", type=float, default=0.0)
ap.add_argument("--bottom", type=float, default=1.0)
ap.add_argument("--left", type=float, default=0.0)
ap.add_argument("--right", type=float, default=1.0)
a = ap.parse_args()

doc = pymupdf.open(PDF)
if not (1 <= a.page <= doc.page_count):
    sys.exit(f"page {a.page} out of range (1..{doc.page_count})")
pg = doc[a.page - 1]
r = pg.rect
clip = pymupdf.Rect(
    r.x0 + a.left * r.width,
    r.y0 + a.top * r.height,
    r.x0 + a.right * r.width,
    r.y0 + a.bottom * r.height,
)
pix = pg.get_pixmap(clip=clip, dpi=a.dpi)
out = os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out
os.makedirs(os.path.dirname(out), exist_ok=True)
pix.save(out)
print(f"book p.{a.page} clip={clip} -> {out}  {pix.width}x{pix.height}")
