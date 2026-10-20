# -*- coding: utf-8 -*-
"""Run the repository's text-level checkers against the current build and write an
ASCII summary to build/qa_suite.txt. Read-only w.r.t. tracked sources (checkers
may rewrite build/ artefacts, which are gitignored).

Run: python tools/qa_suite.py
"""
import io
import subprocess
import sys

CHECKS = [
    'check_src.py',
    'check_numbers.py',
    'check_terms.py',
    'check_toc.py',
    'check_bookmarks.py',
    'check_duppages.py',
    'check_folio.py',
    'check_includes.py',
    'overlap_check.py',
    'check_table_content.py',
    'content_scan.py',
]

out = io.open('build/qa_suite.txt', 'w', encoding='utf-8', newline='\n')
for name in CHECKS:
    p = 'tools/' + name
    try:
        r = subprocess.run([sys.executable, p], capture_output=True, timeout=900)
        txt = (r.stdout + r.stderr).decode('utf-8', 'replace')
        lines = [l for l in txt.split('\n') if l.strip()]
        tail = lines[-4:] if lines else []
        out.write('=== %s  exit=%d  lines=%d\n' % (name, r.returncode, len(lines)))
        for l in tail:
            out.write('    ' + l[:200] + '\n')
    except subprocess.TimeoutExpired:
        out.write('=== %s  TIMEOUT\n' % name)
    except Exception as e:
        out.write('=== %s  ERROR %r\n' % (name, e))
out.close()
print('wrote build/qa_suite.txt')
