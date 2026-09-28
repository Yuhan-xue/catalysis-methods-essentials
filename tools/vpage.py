# -*- coding: utf-8 -*-
"""Render / crop pages from the two source volumes.

Usage:
  python tools/vpage.py <up|down> <page> <out.png> [--dpi N]
                        [--top F] [--bottom F] [--left F] [--right F]

Fractions are 0..1 of page width/height. Default = whole page.
"""
import sys, os
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}


def argval(flag, default):
    if flag in sys.argv:
        return float(sys.argv[sys.argv.index(flag) + 1])
    return default


def main():
    vol = sys.argv[1]
    page = int(sys.argv[2])
    out = sys.argv[3]
    dpi = int(argval("--dpi", 300))
    top = argval("--top", 0.0)
    bottom = argval("--bottom", 1.0)
    left = argval("--left", 0.0)
    right = argval("--right", 1.0)

    doc = pymupdf.open(PDF[vol])
    pg = doc[page - 1]
    r = pg.rect
    clip = pymupdf.Rect(
        r.x0 + left * r.width,
        r.y0 + top * r.height,
        r.x0 + right * r.width,
        r.y0 + bottom * r.height,
    )
    pix = pg.get_pixmap(dpi=dpi, clip=clip, colorspace=pymupdf.csRGB)
    out = os.path.join(ROOT, out) if not os.path.isabs(out) else out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pix.save(out)
    print(f"{vol} p.{page} clip={clip} -> {out}  {pix.width}x{pix.height}")


if __name__ == "__main__":
    main()
