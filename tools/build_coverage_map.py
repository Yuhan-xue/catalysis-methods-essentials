# -*- coding: utf-8 -*-
"""G-04：原书节 -> 本书来源宏（src/figsrc）覆盖映射（机器初筛，需人工确认）。

判据：该原书节号（或其任一子节号）是否作为「§X.Y」引用（含「§a—§b」区间展开）出现在
chapters/ 的 .tex 里。level==2 的一级判断是 G-04 的硬指标；level==3 作为信息项。
「有落点」只代表书里引用过该节号，不代表内容已核对；「未映射」不一定是漏项，可能是经记录的删节。

用法：python tools/build_coverage_map.py
"""
from __future__ import annotations

import csv
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERAGE = os.path.join(ROOT, 'sources', 'coverage.csv')
OUT = os.path.join(ROOT, 'sources', 'coverage_map.md')

SEC_RE = re.compile(u'§\\s*([0-9]+(?:\\.[0-9]+)*)(?:\\s*[—–\\-~]+\\s*§?\\s*([0-9]+(?:\\.[0-9]+)*))?')
# 也认「第 5.2 节」「5.2 节」这种不带 § 的引用（书里确实这样写过）。
NODE_RE = re.compile(u'([0-9]+(?:\\.[0-9]+)+)\\s*节')


def expand(a, b):
    try:
        ta, tb = a.split('.'), b.split('.')
        if len(ta) != len(tb) or ta[:-1] != tb[:-1]:
            return {a, b}
        lo, hi = int(ta[-1]), int(tb[-1])
        if hi < lo or hi - lo > 60:
            return {a, b}
        return {'.'.join(ta[:-1] + [str(k)]) for k in range(lo, hi + 1)}
    except ValueError:
        return {a, b}


def cited_sections():
    covered = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'chapters', '**', '*.tex'), recursive=True)):
        rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
        with open(f, encoding='utf-8', errors='replace') as fh:
            txt = fh.read()
        # 书里节号用 LaTeX 的 \\S（\S 2.3 或 \S\\,2.3--2.6），统一成 § 再匹配。
        txt = re.sub(chr(92) + chr(92) + 'S' + chr(92) + 's*,?', '§', txt)
        for m in SEC_RE.finditer(txt):
            a, b = m.group(1), m.group(2)
            for s in (expand(a, b) if b else {a}):
                covered.setdefault(s, set()).add(rel)
        for m in NODE_RE.finditer(txt):
            covered.setdefault(m.group(1), set()).add(rel)
    return covered


def main():
    with open(COVERAGE, encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    covered = cited_sections()
    kids = {}
    for s in covered:
        parts = s.split('.')
        for k in range(1, len(parts)):
            kids.setdefault('.'.join(parts[:k]), set()).add(s)

    def has_landing(sec):
        return sec in covered or bool(kids.get(sec))

    unmapped2, unmapped3 = [], []
    per_ch = {}
    for r in rows:
        sec = (r.get('sec') or '').strip()
        if not sec:
            continue
        ch = r.get('ch') or ''
        stat = per_ch.setdefault(ch, dict(t2=0, m2=0, u2=0, t3=0, m3=0, u3=0))
        lvl = (r.get('level') or '').strip()
        ok = has_landing(sec)
        if lvl == '2':
            stat['t2'] += 1
            stat['m2' if ok else 'u2'] += 1
            if not ok:
                unmapped2.append((sec, r))
        elif lvl == '3':
            stat['t3'] += 1
            stat['m3' if ok else 'u3'] += 1
            if not ok:
                unmapped3.append((sec, r))

    t2 = sum(s['t2'] for s in per_ch.values()); m2 = sum(s['m2'] for s in per_ch.values())
    t3 = sum(s['t3'] for s in per_ch.values()); m3 = sum(s['m3'] for s in per_ch.values())
    lines = [u'# 原书节覆盖映射（G-04 机器初筛）', u'',
             u'由 `tools/build_coverage_map.py` 生成。判据：该节号（或其任一子节号）是否作为 `§X.Y` 引用',
             u'（含区间展开）出现在 `chapters/**/*.tex` 里。**「有落点」只代表书里引用过该节号，不代表内容已核对；',
             u'「未映射」不一定是漏项，可能是经记录的删节。** 见 `sources/ch08_coverage_note.md`、',
             u'`sources/ch09_coverage_matrix.md` 与各 `reviews/*/CLOSURE.md`。', u'',
             u'合计：**二级节 %d 个，有落点 %d、未映射 %d**；三级节 %d 个，有落点 %d、未映射 %d。'
             % (t2, m2, len(unmapped2), t3, m3, len(unmapped3)), u'',
             u'## 逐章统计', u'',
             u'| 章 | 二级节 | 有落点 | 未映射 | 三级节 | 有落点 | 未映射 |',
             u'|---:|---:|---:|---:|---:|---:|---:|']
    for ch in sorted(per_ch, key=lambda x: (len(x), x)):
        s = per_ch[ch]
        lines.append(u'| %s | %d | %d | %d | %d | %d | %d |'
                     % (ch, s['t2'], s['m2'], s['u2'], s['t3'], s['m3'], s['u3']))

    def table(title, items):
        out = [u'', u'## ' + title, u'', u'| 节 | 标题 | 书内页 | 台账 id |', u'|---|---|---:|---|']
        for sec, r in items:
            out.append(u'| §%s | %s | %s | %s |' % (sec, (r.get('title') or '').strip(),
                                                     (r.get('book_page') or '').strip(),
                                                     (r.get('id') or '').strip()))
        return out

    lines += table(u'未映射的二级节（G-04 硬指标：须逐条给出目标位置或删节理由）', unmapped2)
    lines += table(u'未映射的三级节（信息项：多为在更高层级归纳，或案例/结束语不展开）', unmapped3)
    lines.append('')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(u'\n'.join(lines))
    print('wrote %s' % os.path.relpath(OUT, ROOT))
    print('level2: total=%d mapped=%d unmapped=%d' % (t2, m2, len(unmapped2)))
    print('level3: total=%d mapped=%d unmapped=%d' % (t3, m3, len(unmapped3)))
    for sec, r in unmapped2:
        print('  UNMAPPED-L2 §%s  %s  p.%s' % (sec, (r.get('title') or '').strip(), (r.get('book_page') or '').strip()))


if __name__ == '__main__':
    main()
