# -*- coding: utf-8 -*-
"""Merge figure-review fragments into sources/figure_review.md.

Base list: build/work_figures.tsv (produced by tools/figure_worklist.py).
Fragments: sources/logs/figs_*.tsv, one row per figure:

    fig_id <TAB> num <TAB> art_page <TAB> src_anchor <TAB> checks <TAB> verdict <TAB> note

`src_anchor` is the source figure the redraw was checked against, e.g.
`S1 图1-7 / 书内 p.20 / PDF 39`; `checks` is the short list of what was compared
(axes, variables, trends, numbers, labels); `verdict` is one of

    逐图一致             redraw says the same thing as the source figure
    逐图修正             difference found and fixed (tex or caption), say what
    逐图差异·原书自身     source figure itself is inconsistent/wrong, kept as-is
    改编补充自洽          no source counterpart; adaptation, internally consistent

Usage:
  python tools/figure_ledger.py [--out sources/figure_review.md] [--strict]
  --strict exits 1 unless every figure in the base list has a terminal verdict.

Deterministic: the date is a constant, so a rerun on the same commit is
byte-identical (the acceptance replay gate depends on that).
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE = '2026-11-02'
BASE = os.path.join(ROOT, 'build', 'work_figures.tsv')
LOGDIR = os.path.join(ROOT, 'sources', 'logs')

TERMINAL = ('逐图一致', '逐图修正', '逐图差异·原书自身', '改编补充自洽')
COLS = ['fig_id', 'num', 'art_page', 'src_anchor', 'checks', 'verdict', 'note']


def read_tsv(path, cols):
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding='utf-8', errors='replace') as f:
        head = f.readline().rstrip('\n').split('\t')
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln.strip():
                continue
            parts = ln.split('\t')
            row = {}
            for i, c in enumerate(cols):
                row[c] = parts[i] if i < len(parts) else ''
            if 'fig_id' in head:  # header present, use its order
                row = dict(zip(head, parts))
            rows.append(row)
    return rows


def load_base():
    rows = []
    with io.open(BASE, encoding='utf-8') as f:
        head = f.readline().rstrip('\n').split('\t')
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln.strip():
                continue
            rows.append(dict(zip(head, ln.split('\t'))))
    return rows


def load_fragments():
    frags = {}
    if not os.path.isdir(LOGDIR):
        return frags
    names = sorted(n for n in os.listdir(LOGDIR)
                   if n.startswith('figs_') and n.endswith('.tsv'))
    for name in names:
        path = os.path.join(LOGDIR, name)
        for row in read_tsv(path, COLS):
            fid = (row.get('fig_id') or '').strip()
            if not fid or fid.startswith('#'):
                continue
            row['_src'] = name
            frags[fid] = row
    return frags


def main(argv):
    out_path = os.path.join(ROOT, 'sources', 'figure_review.md')
    strict = '--strict' in argv
    for i, a in enumerate(argv):
        if a == '--out' and i + 1 < len(argv):
            out_path = argv[i + 1]

    base = load_base()
    frags = load_fragments()

    lines = []
    done = 0
    per_verdict = {}
    per_chapter = {}
    for r in base:
        f = frags.get(r['fig_id'], {})
        v = (f.get('verdict') or '待核').strip()
        if v in TERMINAL:
            done += 1
            per_verdict[v] = per_verdict.get(v, 0) + 1
        ch = int(r['chapter'])
        c = per_chapter.setdefault(ch, [0, 0])
        c[0] += 1
        if v in TERMINAL:
            c[1] += 1

    lines.append('# 图与原书对照台账')
    lines.append('')
    lines.append('> 生成日期 %s；由 `python tools/figure_ledger.py` 从 '
                 '`build/work_figures.tsv` 与 `sources/logs/figs_*.tsv` 合并生成，请勿手改。' % DATE)
    lines.append('>')
    lines.append('> 本书全部插图都是 TikZ 重画（不是扫描原图），因此逐图核对的对象是'
                 '「重画是否与原书插图说同一件事」：坐标轴与变量、曲线形状与趋势、'
                 '标注与单位、图中数字。每张图的证据是原书页面图像（`tools/vpage.py` 渲染）+ '
                 '成品页面图像（`tools/vbook.py` 渲染），判定与要点写在明细行里。')
    lines.append('')
    lines.append('## 进度')
    lines.append('')
    lines.append('| 项 | 数 |')
    lines.append('| --- | --- |')
    lines.append('| 插图总数 | %d |' % len(base))
    lines.append('| 已终判 | %d |' % done)
    lines.append('| 待核 | %d |' % (len(base) - done))
    for v in TERMINAL:
        lines.append('| %s | %d |' % (v, per_verdict.get(v, 0)))
    lines.append('')
    lines.append('| 章 | 图数 | 已终判 |')
    lines.append('| --- | --- | --- |')
    for ch in sorted(per_chapter):
        t, d = per_chapter[ch]
        lines.append('| 第%d章 | %d | %d |' % (ch, t, d))
    lines.append('')
    lines.append('## 判定口径')
    lines.append('')
    lines.append('- **逐图一致**：重画与原书插图在坐标轴、变量、趋势、标注、数字上一致'
                 '（允许为排版做等比例简化，须在要点里说明简化了什么）。')
    lines.append('- **逐图修正**：核出差异并已改（改 TikZ 或改题注锚点），备注写改了什么。')
    lines.append('- **逐图差异·原书自身**：原书插图自相矛盾或与正文冲突，成品照录并在图注/正文说明。')
    lines.append('- **改编补充自洽**：原书没有对应插图，是改编自绘，须自洽且不冒称原书图。')
    lines.append('')
    lines.append('## 明细')
    lines.append('')
    lines.append('| 图号 | 成品页 | 源图锚点 | 核对要点 | 判定 | 备注 |')
    lines.append('| --- | --- | --- | --- | --- | --- |')

    def esc(s):
        return (s or '').replace('|', '\\|').strip()

    for r in base:
        f = frags.get(r['fig_id'], {})
        v = (f.get('verdict') or '待核').strip()
        lines.append('| %s | %s | %s | %s | %s | %s |' % (
            r['num'], (f.get('art_page') or r['page']), esc(f.get('src_anchor') or r.get('anchor') or r.get('src_hint') or '—'),
            esc(f.get('checks') or '—'), v, esc(f.get('note') or '')))
    lines.append('')

    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    sys.stdout.write('figures=%d terminal=%d pending=%d -> %s\n' % (
        len(base), done, len(base) - done,
        os.path.relpath(out_path, ROOT).replace('\\', '/')))
    for v in TERMINAL:
        sys.stdout.write('  %s %d\n' % (v, per_verdict.get(v, 0)))
    if strict and done != len(base):
        sys.stdout.write('STRICT FAIL: %d figure(s) without terminal verdict\n'
                         % (len(base) - done))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
