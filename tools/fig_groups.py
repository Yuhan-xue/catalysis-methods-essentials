# -*- coding: utf-8 -*-
"""Split build/work_figures.tsv into per-chapter groups under build/fig_groups/."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, 'build', 'work_figures.tsv')
outdir = os.path.join(ROOT, 'build', 'fig_groups')
os.makedirs(outdir, exist_ok=True)

lines = io.open(src, encoding='utf-8').read().rstrip('\n').split('\n')
head = lines[0]
groups = {}
for ln in lines[1:]:
    ch = ln.split('\t')[2]
    groups.setdefault(ch, []).append(ln)

for ch, rows in sorted(groups.items()):
    p = os.path.join(outdir, 'figs_ch%02d.tsv' % int(ch))
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(head + '\n')
        f.write('\n'.join(rows) + '\n')
    print('ch%s %d figures -> %s' % (ch, len(rows), os.path.relpath(p, ROOT).replace('\\', '/')))
