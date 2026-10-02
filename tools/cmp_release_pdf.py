# -*- coding: utf-8 -*-
"""Compare two builds of the book by content, not by byte hash.

HANDOFF §3 trap 2: the PDF hash legitimately changes on every build
(`/CreationDate` and `/ID`), so "the local tree still reproduces the published
artifact" has to be judged by what a reader sees -- page count, per-page text
layer, bookmark tree and per-page drawing counts.  This is the implementation
of that rule, and the check used to prove the local release build equals the
published `v0.6.5-pre` attachment (314 pages / 144 bookmarks, IDENTICAL
CONTENT) after the 2026-10-02 history rewrite moved every commit hash.

  python tools/cmp_release_pdf.py OLD.pdf NEW.pdf [--out report.txt]

Exit 0 identical, 1 differs, 2 unusable input (missing file / no PyMuPDF).
"""
import io
import os
import sys


def norm(s):
    # Collapse whitespace runs: the text layer is re-extracted, not diffed as
    # bytes, so line-break placement inside a paragraph must not count.
    return ' '.join(s.split())


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
    n = min(a.page_count, b.page_count)
    text_diff, draw_diff = [], []
    for i in range(n):
        pa, pb = a[i], b[i]
        if norm(pa.get_text()) != norm(pb.get_text()):
            text_diff.append(i + 1)
        da, db = len(pa.get_drawings()), len(pb.get_drawings())
        if da != db:
            draw_diff.append((i + 1, da, db))
    if text_diff:
        bad += 1
        out.append('FAIL text layer differs on %d of %d pages: %s%s'
                   % (len(text_diff), n, text_diff[:12],
                      ' ...' if len(text_diff) > 12 else ''))
    else:
        out.append('ok   text layer identical on all %d pages' % n)
    if draw_diff:
        bad += 1
        out.append('FAIL drawing counts differ on %d pages: %s%s'
                   % (len(draw_diff), draw_diff[:8],
                      ' ...' if len(draw_diff) > 8 else ''))
    else:
        out.append('ok   drawing counts identical on all %d pages' % n)
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
