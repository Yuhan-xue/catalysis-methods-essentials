# -*- coding: utf-8 -*-
"""第 85 张表的**来源内容**交叉核对（OCR 文本层，非像素核对）。

背景：tools/check_src.py 已保证每题注里有 \\src{}、页码对与基线偏移一致、且引用的原书
表号出现在内嵌 OCR 索引里。但那仍是**结构/页码**层：评审多次指出「85 表结构 PASS 不等于
内容已核对页面图像」。本工具在**不依赖像素**的前提下再进一步：

  对每个表，取它 \\src{} 里引用的原书表号（如 6-1）与书内页范围，去
  sources/parts/*.txt 的页标记（[[UP/DOWN PDF p.x | 书内 p.y]]）重建的 OCR 文本里，
  在引用页 ±2 范围内查找该表号字符串是否真的出现，并抄下命中的 OCR 行。

它验证的是「该表号确实出现在被引的那几页 OCR 文本里」，**不是**逐字核对表内容/数值。
结论口径：FOUND / MISS / NO_TABLE_NO（模板 B/C，没有原书表号）/ NON_SOURCE（明说非源书）。
MISS 只说明「在可用 OCR 文本里找不到该表号」，不等于表一定错——但它正是后续人工核图时
最该先看的那几条。真正的像素级核对仍需有视觉的人或能看图的通道。

用法：
    python tools/check_table_content.py                 # 输出 build/table_content_check.csv + 控制台汇总
    python tools/check_table_content.py --csv <路径>
退出码：0 全部 FOUND/跳过项；1 有 MISS；2 输入/环境错误。
"""
from __future__ import annotations

import argparse
import csv
import glob
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FW = str.maketrans('０１２３４５６７８９', '0123456789')
MARKER = re.compile(r'\[\[(UP|DOWN) PDF p\.(\d+) \| 书内 p\.(\d+)\]\]')
DASHES = '[-—–−－一]'


def _load_check_src():
    path = os.path.join(ROOT, 'tools', 'check_src.py')
    spec = importlib.util.spec_from_file_location('check_src_mod', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = _load_check_src()


def build_pages():
    pages = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'sources', 'parts', '*.txt'))):
        with open(f, encoding='utf-8', errors='replace') as fh:
            txt = fh.read()
        ms = list(MARKER.finditer(txt))
        for i, m in enumerate(ms):
            vol = 'up' if m.group(1) == 'UP' else 'down'
            bp = int(m.group(3))
            seg = txt[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(txt)]
            pages.setdefault((vol, bp), []).append(seg)
    return {k: '\n'.join(v) for k, v in pages.items()}


def extract_float(lines, start_line):
    op = re.compile(r'\s*\\begin\{(table|longtable)\*?\}')
    cl = re.compile(r'\s*\\end\{(table|longtable)\*?\}')
    i, end, depth = start_line - 1, start_line - 1, 0
    while end < len(lines):
        if op.match(lines[end]):
            depth += 1
        elif cl.match(lines[end]):
            depth -= 1
            if depth == 0:
                break
        end += 1
    return '\n'.join(lines[i:end + 1])


def src_text(body):
    for macro in ('\\src', '\\figsrc'):
        found = cs.balanced(body, macro)
        if found:
            return found[0][0]
    return ''


TABREF_TOL = re.compile(u'表[~\\s\\u00a0]*([0-9]{1,2})\\s*' + DASHES + u'{0,2}\\s*([0-9]{1,2})')


def table_number(src):
    # 比 check_src.TABREF 更宽：源文里可能出现 LaTeX 连接号「表~4-7」或多余空白。
    m = TABREF_TOL.search(src) or cs.TABREF.search(src)
    return (int(m.group(1)), int(m.group(2))) if m else None


def vol_from_src(src):
    if u'上册' in src or re.search(r'(?<![0-9A-Za-z])S1(?![0-9])', src):
        return 'up'
    if u'下册' in src or re.search(r'(?<![0-9A-Za-z])S2(?![0-9])', src):
        return 'down'
    return None


def book_pages(src):
    pairs, _ = cs.pairs_of(src)
    if not pairs:
        return []
    return [(lo, hi) for lo, hi, _pl, _ph in pairs]


def search(pages, n, m, vol, pageset, tol=2):
    pat = re.compile(u'表\\s*' + str(n) + u'\\s*' + DASHES + u'{0,2}\\s*' + str(m) + u'(?![0-9])')
    vols = [vol] if vol else ['up', 'down']
    for lo, hi in pageset:
        for p in range(lo - tol, hi + tol + 1):
            for v in vols:
                txt = pages.get((v, p))
                if not txt:
                    continue
                t = txt.translate(FW)
                mm = pat.search(t)
                if mm:
                    snip = re.sub(r'\\s+', ' ', txt[max(0, mm.start() - 6): mm.start() + 46]).strip()
                    return v, p, snip
    return None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default=os.path.join(ROOT, 'sources', 'table_content_check.csv'))
    args = ap.parse_args(argv)

    pages = build_pages()
    if not pages:
        sys.stderr.write('UNUSABLE: no page text indexed from sources/parts/*.txt\n')
        return 2

    scan = cs.scan_tex_tables()
    rows, miss = [], []
    for rec in scan:
        rel = rec['file']
        path = os.path.join(ROOT, rel)
        with open(path, encoding='utf-8', errors='replace') as fh:
            lines = fh.read().replace('\r\n', '\n').split('\n')
        body = extract_float(lines, rec['line'])
        src = src_text(body)
        label = rec['labels'][0] if len(rec['labels']) == 1 else (u'（%d 标签）' % len(rec['labels']) if rec['labels'] else u'（无标签）')
        where = '%s:%d' % (rel, rec['line'])
        row = dict(label=label, where=where, source_table='', vol='', book_pages='', status='', found_on='', snippet='')
        if not src:
            row['status'] = 'NO_SRC'
            rows.append(row)
            continue
        if cs.NONSOURCE.search(src):
            row['status'] = 'NON_SOURCE'
            rows.append(row)
            continue
        tn = table_number(src)
        if not tn:
            row['status'] = 'NO_TABLE_NO'
            rows.append(row)
            continue
        n, m = tn
        row['source_table'] = '%d-%d' % (n, m)
        vol = vol_from_src(src)
        bp = book_pages(src)
        row['vol'] = vol or ''
        row['book_pages'] = '; '.join('%d-%d' % (a, b) for a, b in bp)
        hit = search(pages, n, m, vol, bp) if bp else None
        if hit:
            v, p, snip = hit
            row['status'] = 'FOUND'
            row['found_on'] = '%s p.%d' % (v, p)
            row['snippet'] = snip[:80]
        else:
            # 文本层没找到时，退回内嵌 OCR 表号索引：索引命中只算「弱确认」，
            # 因为索引页可能来自另一份扫描，且 OCR 常把表号印在图片区而文字层缺失。
            idx_page = cs.OCR_TABLE_INDEX.get('%d-%d' % (n, m))
            if idx_page is not None and bp and any(abs(idx_page - lo) <= cs.PAGE_TOL or abs(idx_page - hi) <= cs.PAGE_TOL or lo <= idx_page <= hi for lo, hi in bp):
                row['status'] = 'INDEX_OK'
                row['found_on'] = 'index p.%d' % idx_page
            else:
                row['status'] = 'MISS'
                miss.append(row)
        rows.append(row)

    os.makedirs(os.path.dirname(args.csv) or '.', exist_ok=True)
    cols = ['label', 'where', 'source_table', 'vol', 'book_pages', 'status', 'found_on', 'snippet']
    with open(args.csv, 'w', encoding='utf-8', newline='\n') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    counts = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print('table content cross-check (OCR text layer, NOT pixel verification)')
    print('  tables scanned: %d' % len(rows))
    for k in ('FOUND', 'INDEX_OK', 'MISS', 'NO_TABLE_NO', 'NON_SOURCE', 'NO_SRC'):
        if counts.get(k):
            print('  %-12s %d' % (k, counts[k]))
    print('  csv: %s' % os.path.relpath(args.csv, ROOT))
    for r in miss:
        print('  MISS %s  table=表%s  cited pages=%s  @%s' % (r['label'], r['source_table'], r['book_pages'], r['where']))
    return 0 if not miss else 1


if __name__ == '__main__':
    raise SystemExit(main())
