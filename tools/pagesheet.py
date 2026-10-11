# -*- coding: utf-8 -*-
"""Contact sheets: tile many PDF pages into one low-dpi PNG.

Reading 340 pages one at a time costs far too much; a contact sheet lets a
reviewer see layout (overlap, overflow, blank areas, float holes, bad breaks)
for 20 pages in a single look.  Text is NOT readable at this scale -- that is
the point: this tool is for layout acceptance, not content proofreading.  When
a cell looks wrong, re-render that page alone with tools/vpage.py at 150+ dpi.

Usage
-----
    python tools/pagesheet.py build/sheets/s01.png 1 2 3 4
    python tools/pagesheet.py build/sheets/s01.png --range 1-20
    python tools/pagesheet.py build/sheets/all.png --all --dpi 30
Options
-------
    --pdf    source PDF (default build/main.pdf)
    --dpi    render dpi per page (default 34; ~250x350 px per A4 cell)
    --cols   columns (default 5)
    --rows   rows (default 4)
    --pad    gutter px (default 6)
    --nolabel  suppress the corner page number
Pages are laid out left-to-right, top-to-bottom in the order given.  The cell
carries a small page number in its top-left corner.  Only pages present in the
document are rendered; missing numbers are reported and skipped.
"""
import argparse
import io
import os
import sys

try:
    import pymupdf as fitz
except ImportError:  # older builds expose the fitz alias only
    import fitz

from PIL import Image, ImageDraw


def parse_range(txt):
    out = []
    for part in txt.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def render(doc, page_no, dpi):
    page = doc[page_no - 1]
    # get_pixmap(dpi=...) demands an int; use an explicit zoom matrix instead so
    # fractional contact-sheet resolutions stay available.
    zoom = float(dpi) / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom),
                          colorspace=fitz.csRGB, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img


def main(argv=None):
    ap = argparse.ArgumentParser(description="tile PDF pages into a contact sheet")
    ap.add_argument("out", help="output PNG path")
    ap.add_argument("pages", nargs="*", type=int, help="1-based page numbers")
    ap.add_argument("--pdf", default="build/main.pdf")
    ap.add_argument("--dpi", type=float, default=34.0)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=4)
    ap.add_argument("--pad", type=int, default=6)
    ap.add_argument("--range", dest="rng", default=None,
                    help="page range, e.g. 1-20 or 3,7,9-12")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--nolabel", action="store_true")
    args = ap.parse_args(argv)

    if not os.path.exists(args.pdf):
        sys.stderr.write("MISSING %s\n" % args.pdf)
        return 2

    doc = fitz.open(args.pdf)
    n = doc.page_count

    if args.rng:
        want = parse_range(args.rng)
    elif args.all:
        want = list(range(1, n + 1))
    else:
        want = list(args.pages)

    seen, pages = set(), []
    for p in want:
        if p < 1 or p > n:
            continue
        if p in seen:
            continue
        seen.add(p)
        pages.append(p)
    if not pages:
        sys.stderr.write("NO PAGES (pdf has %d)\n" % n)
        return 2

    cap = args.cols * args.rows
    if len(pages) > cap:
        sys.stdout.write("NOTE %d pages given, sheet holds %d; using the first %d\n"
                         % (len(pages), cap, cap))
        pages = pages[:cap]

    imgs = [(p, render(doc, p, args.dpi)) for p in pages]
    cw = max(im.width for _, im in imgs)
    ch = max(im.height for _, im in imgs)
    cols = min(args.cols, len(imgs))
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * args.pad,
                              rows * ch + (rows + 1) * args.pad),
                      (210, 210, 210))
    draw = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(imgs):
        cx = i % cols
        cy = i // cols
        x = args.pad + cx * (cw + args.pad)
        y = args.pad + cy * (ch + args.pad)
        sheet.paste(im, (x, y))
        if not args.nolabel:
            tag = str(p)
            draw.rectangle([x, y, x + 7 * len(tag) + 4, y + 13], fill=(255, 255, 255))
            draw.text((x + 3, y + 2), tag, fill=(190, 0, 0))

    outdir = os.path.dirname(args.out)
    if outdir and not os.path.isdir(outdir):
        os.makedirs(outdir)
    sheet.save(args.out)
    sys.stdout.write("WROTE %s pages=%d cell=%dx%d dpi=%.0f\n"
                     % (args.out, len(imgs), cw, ch, args.dpi))
    sys.stdout.write("list: %s\n" % ",".join(str(p) for p, _ in imgs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
