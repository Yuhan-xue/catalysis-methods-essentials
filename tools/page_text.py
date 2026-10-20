# -*- coding: utf-8 -*-
"""Dump the text layer of artifact pages to a UTF-8 file for content proofreading.

Usage:
    python tools/page_text.py <first> <last> [--out build/_txt_p<first>-<last>.txt]

Each page is emitted as:
    ===== p.185 =====
    <text layer>
so several pages can be read in one go without image tokens. The artifact PDF is
build/main.pdf; page numbers are 1-based physical pages.
"""
import argparse
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'build', 'main.pdf')


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('first', type=int)
    ap.add_argument('last', type=int)
    ap.add_argument('--out', default='')
    args = ap.parse_args(argv[1:])
    if not os.path.exists(PDF):
        sys.stderr.write('missing %s\n' % PDF)
        return 1
    import fitz
    doc = fitz.open(PDF)
    if args.first < 1 or args.last > doc.page_count or args.first > args.last:
        sys.stderr.write('bad range %d..%d (pdf has %d pages)\n'
                         % (args.first, args.last, doc.page_count))
        return 1
    out = args.out or os.path.join(ROOT, 'build', '_txt_p%d-%d.txt' % (args.first, args.last))
    if not os.path.isabs(out):
        out = os.path.join(ROOT, out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    chunks = []
    for p in range(args.first, args.last + 1):
        chunks.append('===== p.%d =====' % p)
        chunks.append(doc[p - 1].get_text('text').rstrip('\n'))
        chunks.append('')
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(chunks) + '\n')
    print('wrote %d pages -> %s' % (args.last - args.first + 1,
                                    os.path.relpath(out, ROOT).replace('\\', '/')))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
