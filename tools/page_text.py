# -*- coding: utf-8 -*-
"""Dump the text layer of one page of the built book (build/main.pdf).

Usage:
    python tools/page_text.py <page> <out.txt>

The output is written as UTF-8 so that it can be read with the file reader
instead of being printed to the GBK console.
"""
import io
import os
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, 'build', 'main.pdf')


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 2
    page = int(argv[1])
    out = argv[2]
    if not os.path.isabs(out):
        out = os.path.join(ROOT, out)
    doc = pymupdf.open(PDF)
    if not 1 <= page <= doc.page_count:
        sys.stderr.write('page out of range 1..%d\n' % doc.page_count)
        return 2
    text = doc[page - 1].get_text()
    os.makedirs(os.path.dirname(out), exist_ok=True) if os.path.dirname(out) else None
    with io.open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    sys.stdout.write('page %d -> %s chars=%d\n' % (page, out, len(text)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
