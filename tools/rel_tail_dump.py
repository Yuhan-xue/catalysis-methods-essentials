# -*- coding: utf-8 -*-
"""Dump the tail pages of the shipped release PDF for a ledger-vs-artifact check."""
import sys

import pymupdf

path = 'release/catalysis-methods-essentials-v1.1.3.pdf'
doc = pymupdf.open(path)
out = []
out.append('pages=%d' % doc.page_count)
for i in range(max(0, doc.page_count - 3), doc.page_count):
    out.append('===== rel p.%d =====' % (i + 1))
    out.append(doc[i].get_text())
io = __import__('io')
io.open('build/_rel_tail.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('wrote build/_rel_tail.txt')
