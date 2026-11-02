# -*- coding: utf-8 -*-
"""Align two builds page-by-page after an edit that changed pagination.

Usage: python tools/page_align.py <old.pdf> <new.pdf> [out.tsv]

For every old page find the new page with the highest text similarity, and
report whether the mapping is monotone and which pages are new-only. Writes a
TSV: old<TAB>new<TAB>ratio<TAB>note. ASCII-only stdout.
"""
import difflib
import io
import os
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pages(path):
    doc = pymupdf.open(path)
    out = []
    for i in range(doc.page_count):
        t = doc[i].get_text('text')
        out.append(''.join(t.split()))
    return out


def main():
    old = pages(sys.argv[1])
    new = pages(sys.argv[2])
    out_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        ROOT, 'build', 'page_align.tsv')
    rows = []
    used = {}
    for oi, text in enumerate(old, 1):
        best, best_r = None, 0.0
        for ni in range(max(1, oi - 4), min(len(new), oi + 4) + 1):
            r = difflib.SequenceMatcher(None, text, new[ni - 1]).quick_ratio()
            if r > best_r:
                r = difflib.SequenceMatcher(None, text, new[ni - 1]).ratio()
                if r > best_r:
                    best, best_r = ni, r
        note = ''
        if best is not None:
            used[best] = used.get(best, 0) + 1
        if best == oi:
            note = 'same'
        elif best is not None and best > oi:
            note = 'shifted+%d' % (best - oi)
        elif best is not None and best < oi:
            note = 'shifted%d' % (best - oi)
        rows.append((oi, best, best_r, note))
    extra = [n for n in range(1, len(new) + 1) if n not in used]
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('old_page\tnew_page\tratio\tnote\n')
        for oi, best, r, note in rows:
            fh.write('%d\t%s\t%.3f\t%s\n' % (oi, best, r, note))
        fh.write('# new-only pages: %s\n' % (','.join(map(str, extra)) or 'none'))
    mono = all((rows[i][1] or 0) <= (rows[i + 1][1] or 0) for i in range(len(rows) - 1))
    print('old=%d new=%d monotone=%s new_only=%s out=%s'
          % (len(old), len(new), mono, extra or 'none', out_path))
    low = [(o, n, r) for o, n, r, _ in rows if n and r < 0.85]
    print('low_confidence=%d %s' % (len(low), low[:8]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
