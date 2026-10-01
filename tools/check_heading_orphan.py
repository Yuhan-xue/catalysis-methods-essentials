# -*- coding: utf-8 -*-
"""标题孤悬检查（R5-U02）：小节的标题、来源行与首段至少两行必须同页。

背景：reviews/2026-10-01-round5 报告 p.186 页尾只剩「8.5 分子筛催化反应的原位
MAS NMR」与来源行，正文全部翻到下一页。修法是在分片开头加 \\needspace（只做落页
判断，不把整节设成不可分页的大盒）。本探针独立复验修复后的分页：

  - 找到标题所在的页；
  - 统计该页标题之后、正文区内的文本行数（不含页码/页眉）：< --min-follow 判 FAIL；
  - 同时报告该页与前一页最后一条正文行的 y（用于人工核对页尾留白是否异常）。

判据是「标题后同页至少 N 行」，比「整节不可分页」宽松：只要求首个内容块与标题
同页，不阻止长节跨页。

用法：
  python tools/check_heading_orphan.py --pdf build/main.pdf \
      --heading "分子筛催化反应的原位 MAS NMR" --min-follow 3
退出码：0 PASS / 1 FAIL / 2 前置不足（找不到标题）
"""
from __future__ import annotations

import argparse
import json
import re
import sys

try:
    import pymupdf as fitz
except ImportError:
    import fitz

BODY_TOP, BODY_BOTTOM = 60.0, 780.0   # pt：正文区（排除页眉/页脚页码）
HEADING_MIN_SIZE = 10.5               # 标题字号下限
BODY_MAX_SIZE = 10.5                  # 正文行字号上限


def norm(s: str) -> str:
    return re.sub(r'\s+', '', s or '')


def page_lines(page):
    lines = []
    for blk in page.get_text('dict')['blocks']:
        if blk.get('type') != 0:
            continue
        for ln in blk['lines']:
            text = ''.join(sp['text'] for sp in ln['spans']).strip()
            if not text:
                continue
            y0, y1 = ln['bbox'][1], ln['bbox'][3]
            if y0 < BODY_TOP or y0 > BODY_BOTTOM:
                continue
            lines.append({'text': text, 'n': norm(text), 'y0': y0, 'y1': y1,
                          'size': max(sp['size'] for sp in ln['spans'])})
    lines.sort(key=lambda l: l['y0'])
    return lines


def check(pdf, heading, min_follow):
    doc = fitz.open(pdf)
    key = norm(heading)
    page_no = None
    head = None
    for i in range(doc.page_count):
        for l in page_lines(doc[i]):
            if key in l['n'] and l['size'] >= HEADING_MIN_SIZE:
                page_no, head = i, l
                break
        if page_no is not None:
            break
    if page_no is None:
        print('heading_orphan: UNUSABLE (heading %r with size >= %.1f not found in %s)'
              % (heading, HEADING_MIN_SIZE, pdf))
        return 2, None
    lines = page_lines(doc[page_no])
    follow = [l for l in lines if l['y0'] > head['y0'] + 1.0]
    body_follow = [l for l in follow if l['size'] <= BODY_MAX_SIZE]
    prev_last = None
    if page_no > 0:
        plines = page_lines(doc[page_no - 1])
        if plines:
            prev_last = plines[-1]
    info = {
        'pdf': str(pdf), 'heading': heading, 'page': page_no + 1,
        'heading_y': round(head['y0'], 1), 'follow_lines': len(follow),
        'body_follow_lines': len(body_follow),
        'tail_text': [l['text'][:40] for l in follow[-3:]],
        'prev_page_last_body_y': round(prev_last['y0'], 1) if prev_last else None,
        'prev_page_last_text': prev_last['text'][:40] if prev_last else None,
        'min_follow': min_follow,
    }
    ok = len(follow) >= min_follow
    info['ok'] = ok
    status = 'PASS' if ok else 'FAIL'
    print('heading_orphan: %s  page=%d  heading_y=%.1f  follow_lines=%d (min %d)'
          % (status, info['page'], info['heading_y'], info['follow_lines'], min_follow))
    if follow:
        print('  tail: ' + ' | '.join(l['text'][:28] for l in follow[-2:]))
    if prev_last:
        print('  prev page last body line y=%.1f  %r' % (prev_last['y0'], prev_last['text'][:28]))
    doc.close()
    return (0 if ok else 1), info


def main(argv=None):
    ap = argparse.ArgumentParser(description='标题孤悬检查（R5-U02）')
    ap.add_argument('--pdf', default='build/main.pdf')
    ap.add_argument('--heading', default='分子筛催化反应的原位 MAS NMR')
    ap.add_argument('--min-follow', type=int, default=3,
                    help='标题之后同页至少要有多少文本行（默认 3：来源行 + 首段两行）')
    ap.add_argument('--json', default=None)
    a = ap.parse_args(argv)
    code, info = check(a.pdf, a.heading, a.min_follow)
    if a.json and info:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
