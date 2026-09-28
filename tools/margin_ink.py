# -*- coding: utf-8 -*-
"""Find ink-bearing regions in page margins -> locate printed page numbers.

For each requested page, render at low dpi, threshold, then report
connected ink bands in the top / bottom / left / right margin strips.
"""
import sys, os
import numpy as np
import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}


def bands(mask, axis, min_gap=3):
    """Return list of (start,end) runs of True along axis=0 (rows) / 1 (cols)."""
    prof = mask.any(axis=1 - axis)
    idx = np.where(prof)[0]
    if len(idx) == 0:
        return []
    out = []
    s = idx[0]
    p = idx[0]
    for i in idx[1:]:
        if i - p > min_gap:
            out.append((int(s), int(p)))
            s = i
        p = i
    out.append((int(s), int(p)))
    return out


def main():
    vol = sys.argv[1]
    pages = [int(x) for x in sys.argv[2].split(",")]
    dpi = 200
    doc = pymupdf.open(PDF[vol])
    lines = []
    for pno in pages:
        pg = doc[pno - 1]
        pix = pg.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        ink = arr < 128
        H, W = ink.shape
        # margin strips
        top = ink[: int(0.09 * H), :]
        bot = ink[int(0.90 * H) :, :]
        lines.append(f"=== {vol} p.{pno}  {pix.width}x{pix.height}  inkpix={int(ink.sum())}")
        lines.append(f"   FULL       row bands: {bands(ink,0)[:6]}")
        lines.append(f"   TOP9%      row bands: {bands(top,0)}  col bands: {bands(top,1)}")
        lines.append(f"   BOT10%     row bands: {bands(bot,0)}  col bands: {bands(bot,1)}")
        lines.append(f"   FULL       col bands: {bands(ink,1)[:8]}")
    out = os.path.join(ROOT, f"tools/margin_{vol}.txt")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print("->", out)


if __name__ == "__main__":
    main()
