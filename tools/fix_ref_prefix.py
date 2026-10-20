# -*- coding: utf-8 -*-
r"""Remove the redundant noun in front of prefix-printing reference macros.

\equref/\tabref/\figref already print「式」「表」「图」(style/preamble.tex:426-428),
so「式~\equref{..}」prints「式 式(4-19)」. This tool rewrites「式[ ~]*\equref」to
「\equref」inside chapters/ only. The noun stays readable because the macro emits it.

Usage: python tools/fix_ref_prefix.py [--dry-run]
Report: build/fix_ref_prefix.txt
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, 'build', 'fix_ref_prefix.txt')
PAIRS = (('式', 'equref'), ('表', 'tabref'), ('图', 'figref'))
PAT = re.compile('([\u4e00-\u9fff])?(式|表|图)[ ~]*\\\\(equref|tabref|figref)')


def main(argv):
    dry = '--dry-run' in argv
    files = sorted(glob.glob(os.path.join(ROOT, 'chapters', '**', '*.tex'), recursive=True))
    rep = []
    total = 0
    for path in files:
        text = io.open(path, encoding='utf-8', newline='').read()
        hits = PAT.findall(text)
        if not hits:
            continue
        new = PAT.sub(lambda m: (m.group(1) or '') + '\\' + m.group(3), text)
        n = len(hits)
        total += n
        rep.append('%s\t%d\t%s' % (os.path.relpath(path, ROOT).replace('\\', '/'), n,
                                   ' '.join('%s%s' % (a, b) for a, b, _ in hits[:4])))
        if not dry:
            io.open(path, 'w', encoding='utf-8', newline='').write(new)
    rep.append('total\t%d\tfiles\t%d\tdry_run=%s' % (total, len(rep), dry))
    io.open(REPORT, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
    print('ref-prefix rewrites=%d files=%d dry_run=%s report=%s'
          % (total, len(rep) - 1, dry, os.path.relpath(REPORT, ROOT)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
