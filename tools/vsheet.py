# -*- coding: utf-8 -*-
"""Contact sheet of consecutive pages from a source volume (for locating figures).

Usage:
  python tools/vsheet.py <up|down> <first> <last> <out.png>
                        [--cols N] [--dpi N] [--label]

Each page is rendered small and laid out in a grid, with its PDF page number and
printed (book) page number drawn in the corner, so a figure can be located
before rendering the page at full resolution.
"""
import sys

import pymupdf

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
sys.path.insert(0, _os.path.join(ROOT, 'tools'))
import pagemap_lib as pm  # noqa: E402

PDF = {
    "up": r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
    "down": r"C:\Users\53150\.dsh\attachments\v1\files\a1\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf",
}


def arg(flag, default):
    if flag in sys.argv:
        return sys.argv[sys.argv.index(flag) + 1]
    return default


def main():
    vol, first, last, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    cols = int(arg('--cols', 4))
    dpi = int(arg('--dpi', 64))
    label = '--label' in sys.argv

    doc = pymupdf.open(PDF[vol])
    pages = list(range(first, min(last, doc.page_count - 1) + 1))
    rows = (len(pages) + cols - 1) // cols
    zoom = dpi / 72.0
    pw, ph = doc[pages[0]].rect.width * zoom, doc[pages[0]].rect.height * zoom
    sheet = pymupdf.open()
    pg = sheet.new_page(width=pw * cols, height=ph * rows)
    for i, p in enumerate(pages):
        r = pymupdf.Rect(i % cols * pw, i // cols * ph, (i % cols + 1) * pw, (i // cols + 1) * ph)
        pg.show_pdf_page(r, doc, p - 1)
        if label:
            book = pm.book(vol, p)
            pg.insert_text((r.x0 + 4, r.y0 + 12), 'pdf %d / p.%d' % (p, book),
                           fontsize=7, color=(1, 0, 0))
    pg.get_pixmap(dpi=72).save(out)
    sys.stdout.write('sheet %s pages %d-%d -> %s (%dx%d px)\n' % (
        vol, first, last, out, int(pw * cols), int(ph * rows)))


if __name__ == '__main__':
    main()
