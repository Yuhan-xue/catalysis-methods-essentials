# -*- coding: utf-8 -*-
"""Compare two builds of the book by content, not by byte hash.

HANDOFF §3 trap 2: the PDF hash legitimately changes on every build
(`/CreationDate` and `/ID`), so "the local tree still reproduces the published
artifact" has to be judged by what a reader sees.

Compared (all must match):
  * page count
  * bookmark tree
  * per-page text layer -- both the normalized text and the normalized
    geometry of every text block
  * per-page vector drawings -- normalized geometry, stroke/fill colour,
    line width and item count (not just the number of drawings)
  * per-page embedded raster images -- content hash plus placement rectangles

Deliberately NOT compared: document metadata (/CreationDate, /ID, title, ...),
because a rebuild legitimately changes it.  A difference that changes only
metadata therefore still reports IDENTICAL CONTENT, which is the intended
positive control.

  python tools/cmp_release_pdf.py OLD.pdf NEW.pdf [--out report.txt]

Exit 0 identical, 1 differs, 2 unusable input (missing file / no PyMuPDF).

Round-6 finding R6-W01: the earlier version compared the text layer plus only
the *number* of drawings per page, so a 60 pt rectangle shift, a raster recolour
with position and size unchanged, and a text block moved from y=40 to y=220 all
returned "IDENTICAL CONTENT".  Geometry and image content are now compared, so
all three of those variants fail while the metadata-only control still passes.
"""
import hashlib
import io
import os
import sys


def norm(s):
    # Collapse whitespace runs: the text layer is re-extracted, not diffed as
    # bytes, so line-break placement inside a paragraph must not count.
    return ' '.join(s.split())


def _round(v):
    return round(float(v), 2)


def _color(c):
    if c is None:
        return None
    try:
        return tuple(_round(x) for x in c)
    except TypeError:
        return c


def _rect(r):
    if r is None:
        return None
    return (_round(r.x0), _round(r.y0), _round(r.x1), _round(r.y1))


def page_signature(doc, page):
    """Return (text_blocks, drawings, images) for one page.

    Every entry carries geometry, so a pure move is visible even when the
    number of objects and their text/colour content are unchanged.
    """
    blocks = []
    for b in page.get_text('blocks'):
        # b = (x0, y0, x1, y1, text, block_no, block_type)
        blocks.append((_round(b[0]), _round(b[1]), _round(b[2]), _round(b[3]),
                       int(b[6]), norm(b[4])))

    drawings = []
    for d in page.get_drawings():
        drawings.append((_rect(d.get('rect')), d.get('type'),
                         _color(d.get('fill')), _color(d.get('color')),
                         _round(d.get('width') or 0.0),
                         len(d.get('items') or [])))

    images = []
    for info in page.get_images(full=True):
        xref = info[0]
        try:
            digest = hashlib.sha1(doc.extract_image(xref)['image']).hexdigest()
        except Exception:
            digest = 'xref:%d' % xref
        rects = []
        try:
            for r in page.get_image_rects(xref):
                rects.append(_rect(r))
        except Exception:
            pass
        images.append((digest, tuple(rects)))

    return blocks, drawings, images


def main(argv):
    argv = list(argv)
    out_path = None
    if '--out' in argv:
        i = argv.index('--out')
        out_path = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    args = argv
    if len(args) != 2:
        print('usage: cmp_release_pdf.py OLD.pdf NEW.pdf [--out report.txt]')
        return 2
    try:
        import fitz
    except ImportError:
        print('UNUSABLE: PyMuPDF (fitz) not installed')
        return 2

    out = []
    docs = []
    for path in args:
        if not os.path.isfile(path):
            print('UNUSABLE: %s not found' % path)
            return 2
        d = fitz.open(path)
        docs.append(d)
        out.append('%-22s pages=%-4d bookmarks=%-4d bytes=%d'
                   % (os.path.basename(path), d.page_count, len(d.get_toc()),
                      os.path.getsize(path)))
    a, b = docs
    bad = 0
    if a.page_count != b.page_count:
        out.append('FAIL page count %d != %d' % (a.page_count, b.page_count))
        bad += 1
    t_a, t_b = a.get_toc(), b.get_toc()
    if t_a != t_b:
        bad += 1
        only_a = [t for t in t_a if t not in t_b]
        only_b = [t for t in t_b if t not in t_a]
        out.append('FAIL bookmark tree differs: %d only in A, %d only in B'
                   % (len(only_a), len(only_b)))
        for t in (only_a[:3] + only_b[:3]):
            out.append('     %s' % (t,))
    else:
        out.append('ok   bookmark tree identical (%d entries)' % len(t_a))

    n = min(a.page_count, b.page_count)
    text_diff, draw_diff, img_diff = [], [], []
    for i in range(n):
        pa, pb = a[i], b[i]
        ba, da, ia = page_signature(a, pa)
        bb, db, ib = page_signature(b, pb)
        if ba != bb:
            text_diff.append(i + 1)
        if da != db:
            draw_diff.append((i + 1, len(da), len(db)))
        if ia != ib:
            img_diff.append((i + 1, len(ia), len(ib)))

    def _report(label, diffs, limit, fmt):
        if diffs:
            out.append('FAIL %s differs on %d of %d pages: %s%s'
                       % (label, len(diffs), n,
                          [fmt(d) for d in diffs[:limit]],
                          ' ...' if len(diffs) > limit else ''))
            return 1
        out.append('ok   %s identical on all %d pages' % (label, n))
        return 0

    bad += _report('text layer (content + block geometry)', text_diff, 12,
                   lambda d: d)
    bad += _report('drawings (geometry + stroke/fill)', draw_diff, 8,
                   lambda d: 'p%d %d!=%d' % d)
    bad += _report('raster images (content + placement)', img_diff, 8,
                   lambda d: 'p%d %d!=%d' % d)

    out.append('note: document metadata (/ID, /CreationDate) is excluded by design')
    out.append('RESULT: %s' % ('IDENTICAL CONTENT' if bad == 0 else
                               'DIFFERS (%d checks failed)' % bad))
    text = '\n'.join(out) + '\n'
    if out_path:
        with io.open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(text)
    try:
        print(text)
    except UnicodeEncodeError:          # GBK console
        print('\n'.join(l.encode('ascii', 'replace').decode('ascii')
                        for l in out))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
