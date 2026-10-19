# -*- coding: utf-8 -*-
r"""Merge the three content-level acceptance ledgers and regenerate the reports.

Usage:
    python tools/review_ledger.py pages      # -> sources/pages_notes_src.txt + sources/content_review.md
    python tools/review_ledger.py formulas   # -> sources/formula_crosscheck.md/.csv
    python tools/review_ledger.py tables     # -> sources/table_cells.md/.tsv + sources/table_status.md
    python tools/review_ledger.py all [--strict]

Inputs written by the reviewers (tab separated, UTF-8, no header):
    sources/logs/page_<group>.tsv     page<TAB>status<TAB>note
    sources/logs/fixes_<group>.tsv    page<TAB>file<TAB>line<TAB>old<TAB>new<TAB>reason
    sources/logs/formulas_<group>.tsv label<TAB>verdict<TAB>src_pages<TAB>note
    sources/logs/tables_<group>.tsv   label<TAB>verdict<TAB>src_pages<TAB>cells<TAB>mismatches<TAB>note
    sources/logs/cells_<label>.tsv    label<TAB>row<TAB>col<TAB>artifact<TAB>source<TAB>action<TAB>note
    sources/logs/batches_page.tsv     date<TAB>scope<TAB>did

The script never touches chapters/, build/main.pdf or the reviewers' logs; it only
rewrites the four generated ledger files and prints an ASCII summary.  --strict
exits non-zero when any page / numbered formula / table still lacks a final verdict.
"""
import csv
import glob
import io
import os
import re
import subprocess
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, 'sources', 'logs')
PAGES_BASE = os.path.join(ROOT, 'sources', 'content_review_notes.txt')
PAGES_SRC = os.path.join(ROOT, 'sources', 'pages_notes_src.txt')
CONTENT_REVIEW = os.path.join(ROOT, 'sources', 'content_review.md')
WORK_FORMULAS = os.path.join(ROOT, 'build', 'work_formulas.tsv')
WORK_TABLES = os.path.join(ROOT, 'build', 'work_tables.tsv')
FORMULA_MD = os.path.join(ROOT, 'sources', 'formula_crosscheck.md')
FORMULA_CSV = os.path.join(ROOT, 'sources', 'formula_crosscheck.csv')
TABLE_MD = os.path.join(ROOT, 'sources', 'table_cells.md')
TABLE_TSV = os.path.join(ROOT, 'sources', 'table_cells.tsv')
REPORT = os.path.join(ROOT, 'build', 'review_ledger_report.txt')

FORMULA_DONE = {'已核对一致', '已核对并修正', '形式一致但符号不同', '原书自身问题', '改编补充'}
TABLE_DONE = {'逐格一致', '逐格修正', '逐格差异·原书自身', '改编补充自洽'}
PAGE_DONE_PREFIX = '已读'

report = []
GEN_DATE = ''


def head_date():
    """Use the HEAD commit date as the ledger's generation date.

    This keeps repeated runs byte-identical (the alternative, today's date,
    would rewrite one line every midnight and make the idempotency check noisy).
    """
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs'], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        d = out.stdout.strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
            return d
    except Exception:
        pass
    return datetime.date.today().isoformat()


def log(msg):
    report.append(msg)


def read_text(path):
    with io.open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def write_text(path, text):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def read_tsv_rows(lines, ncols):
    """Same as read_tsv but for an already-split list of lines (a notes section)."""
    rows = []
    for line in lines:
        line = line.rstrip('\r\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = [p.strip() for p in line.split('\t')]
        while len(parts) < ncols:
            parts.append('')
        rows.append(parts[:ncols])
    return rows


def read_tsv(path, ncols, skip_header=None):
    """Return list of lists (padded/truncated to ncols); skip blanks and # lines."""
    rows = []
    if not os.path.exists(path):
        return rows
    with io.open(path, encoding='utf-8', errors='replace', newline='') as f:
        for line in f:
            line = line.rstrip('\r\n')
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            parts = [p.strip() for p in line.split('\t')]
            if skip_header and parts and parts[0] == skip_header:
                continue
            while len(parts) < ncols:
                parts.append('')
            rows.append(parts[:ncols])
    return rows


# ---------------------------------------------------------------- pages
def parse_notes(path):
    sections = {}
    order = []
    cur = None
    for line in read_text(path).splitlines():
        if line.startswith('#') and line.strip() in (
                '#LABELS', '#DET', '#HEAD', '#PAGES', '#BATCH', '#TAIL'):
            cur = line.strip()
            sections[cur] = []
            order.append(cur)
        elif cur is not None:
            sections[cur].append(line)
    return sections, order


def merge_pages():
    sections, order = parse_notes(PAGES_BASE)
    base_pages = {}
    for parts in read_tsv_rows(sections.get('#PAGES', []), 3):
        if parts[0] == 'page' or not re.match(r'^\d+$', parts[0]):
            continue
        base_pages[int(parts[0])] = (parts[1], parts[2].replace('\t', ' '))
    frag_pages = {}
    frag_files = sorted(glob.glob(os.path.join(LOGS, 'page_*.tsv')))
    for path in frag_files:
        n = 0
        for parts in read_tsv(path, 3, skip_header='page'):
            if not re.match(r'^\d+$', parts[0]):
                continue
            frag_pages[int(parts[0])] = (parts[1], parts[2].replace('\t', ' '))
            n += 1
        log('pages fragment %s rows=%d' % (os.path.basename(path), n))
    merged = dict(base_pages)
    merged.update(frag_pages)

    base_batches = []
    for parts in read_tsv_rows(sections.get('#BATCH', []), 4):
        if parts[0] == 'batch':
            continue
        base_batches.append(parts)
    num_batches = [int(p[0]) for p in base_batches if re.match(r'^\d+$', p[0])]
    next_batch = (max(num_batches) + 1) if num_batches else 1
    new_batches = []
    for parts in read_tsv(os.path.join(LOGS, 'batches_page.tsv'), 4):
        if not parts[0] or parts[0] == 'date':
            continue
        if not re.match(r'^\d+$', parts[0]):
            parts[0] = str(next_batch)
            next_batch += 1
        new_batches.append(parts)

    out = []
    for sec in order:
        out.append(sec)
        if sec == '#PAGES':
            for page in sorted(merged):
                st, note = merged[page]
                out.append('%d\t%s\t%s' % (page, st, note))
        elif sec == '#BATCH':
            for parts in base_batches + new_batches:
                out.append('\t'.join(parts))
        else:
            out.extend(sections[sec])
    text = '\n'.join(out).rstrip('\n') + '\n'
    write_text(PAGES_SRC, text)

    total = 339
    covered = [p for p, (st, _) in merged.items() if st.startswith(PAGE_DONE_PREFIX)]
    log('pages covered=%d/%d batches=%d' % (len(covered), total, len(base_batches) + len(new_batches)))
    missing = [p for p in range(1, total + 1) if p not in merged or not merged[p][0].startswith(PAGE_DONE_PREFIX)]
    if missing:
        log('pages missing: ' + ','.join(map(str, missing[:80])) + (' ...' if len(missing) > 80 else ''))

    # regenerate the human-readable report
    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'content_review.py'),
           '--notes', PAGES_SRC, '--out', CONTENT_REVIEW, '--date', GEN_DATE]
    try:
        subprocess.run(cmd, cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        log('content_review.md regenerated (%d notes rows)' % len(merged))
    except subprocess.CalledProcessError as e:
        log('content_review.py FAILED rc=%s' % e.returncode)
        raise
    return len(missing) == 0


# ---------------------------------------------------------------- formulas
def merge_formulas():
    work = read_tsv(WORK_FORMULAS, 10, skip_header='label')
    led = {}
    for path in sorted(glob.glob(os.path.join(LOGS, 'formulas_*.tsv'))):
        n = 0
        for parts in read_tsv(path, 4, skip_header='label'):
            if not parts[0]:
                continue
            led[parts[0]] = (parts[1], parts[2], parts[3])
            n += 1
        log('formula fragment %s rows=%d' % (os.path.basename(path), n))

    verdicts = ['已核对一致', '已核对并修正', '形式一致但符号不同', '原书自身问题', '改编补充', '未找到', '未覆盖']
    cnt = {v: 0 for v in verdicts}
    rows = []
    for r in work:
        label, num, page, slice_, line, vol, src_book, src_pdf, hint_book, hint_pdf = r
        if not label.startswith('eq:'):
            continue
        verdict, src_pages, note = led.get(label, ('未覆盖', '', ''))
        if verdict not in cnt:
            verdict = '未覆盖'
        cnt[verdict] += 1
        rows.append(dict(label=label, num=num, page=page, slice=slice_, line=line, vol=vol,
                         src_book=src_book, src_pdf=src_pdf, hint_pdf=hint_pdf,
                         verdict=verdict, src_pages=src_pages, note=note))
    total = len(rows)
    done = sum(cnt[v] for v in FORMULA_DONE)
    log('formulas done=%d/%d %s' % (done, total, ' '.join('%s=%d' % (v, cnt[v]) for v in verdicts)))

    slices = []
    seen = set()
    for x in rows:
        if x['slice'] not in seen:
            seen.add(x['slice'])
            slices.append(x['slice'])

    out = []
    out.append('# 全书编号公式逐式复核台账（`sources/formula_crosscheck.md`）')
    out.append('')
    out.append('本文件由 `tools/review_ledger.py formulas` 从磁盘可核验事实生成：')
    out.append('`build/work_formulas.tsv`（`tools/review_worklist.py` 生成的 372 个编号式清单，')
    out.append('含分片、源码行、成品页、源书页范围与提示页）＋ `sources/logs/formulas_*.tsv`')
    out.append('（逐式判决，附源书 PDF 页与并排式子）。生成时间 %s。' % GEN_DATE)
    out.append('')
    out.append('**方法**：每个式先用 `tools/vbook.py` 渲染成品页面图像，读出发行式与编号；')
    out.append('再用 `tools/vpage.py` 渲染源书对应页（上册 `书内页 = PDF页 − 19`，下册 `+507`，')
    out.append('以页眉印刷页码为准），**逐符号**对照变量、上下标、正负号、系数、常数与编号。')
    out.append('OCR 文本只用于定位，不作证据。判决词表与「什么算一致」见 `sources/review_protocol.md` §3.2。')
    out.append('')
    out.append('| 结论 | 式数 |')
    out.append('| --- | --- |')
    for v in verdicts:
        out.append('| %s | %d |' % (v, cnt[v]))
    out.append('| **合计** | **%d** |' % total)
    out.append('')
    if done < total:
        out.append('> 尚有 %d 式未取得终判（`未覆盖`／`未找到`），本台账**不得**用于宣称第二项验收完成。' % (total - done))
        out.append('')
    out.append('## 一、逐式判决')
    out.append('')
    for sl in slices:
        sub = [x for x in rows if x['slice'] == sl]
        sd = sum(1 for x in sub if x['verdict'] in FORMULA_DONE)
        out.append('### %s（%d/%d 式有终判）' % (sl, sd, len(sub)))
        out.append('')
        out.append('| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |')
        out.append('| --- | --- | --- | --- | --- | --- | --- | --- |')
        for x in sub:
            out.append('| `%s` | %s | %s | %s p.%s | %s | %s | %s | %s |' % (
                x['label'], x['num'] or '—', x['page'], x['vol'], x['src_book'] or '—',
                x['hint_pdf'] or x['src_pdf'] or '—', x['verdict'], x['src_pages'] or '—',
                x['note'].replace('|', '\\|')))
        out.append('')
    todo = [x for x in rows if x['verdict'] not in FORMULA_DONE]
    if todo:
        out.append('## 二、未取得终判的式（%d）' % len(todo))
        out.append('')
        out.append('| 式 | 编号 | 成品页 | 分片 | 状态 |')
        out.append('| --- | --- | --- | --- | --- |')
        for x in todo:
            out.append('| `%s` | %s | %s | %s | %s |' % (x['label'], x['num'], x['page'], x['slice'], x['verdict']))
        out.append('')
    out.append('## 三、本台账不主张的东西')
    out.append('')
    out.append('- 不主张「式号对得上」等于「推导正确」：只核印刷形式与符号，不重做推导。')
    out.append('- 不主张 `形式一致但符号不同` 的式与源书等价：只主张已记录符号差异，等价性由正文符号表承担。')
    out.append('- 不主张 `改编补充` 的式有源书出处：这些式源书没有，判据是源书对应页范围无此式。')
    out.append('- 不主张未列入 372 式的行间式已核：清单只覆盖带 `\\label{eq:}` 的编号式。')
    out.append('')
    out.append('复跑：`python tools/review_ledger.py formulas`（判决由 `sources/logs/formulas_*.tsv` 提供）。')
    write_text(FORMULA_MD, '\n'.join(out) + '\n')

    with io.open(FORMULA_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['label', 'slice', 'printed_num', 'artifact_page', 'vol', 'src_book_pages',
                    'src_pdf_range', 'hint_pdf', 'verdict', 'src_pages', 'note'])
        for x in rows:
            w.writerow([x['label'], x['slice'], x['num'], x['page'], x['vol'], x['src_book'],
                        x['src_pdf'], x['hint_pdf'], x['verdict'], x['src_pages'], x['note']])
    return all(x['verdict'] in FORMULA_DONE for x in rows)


# ---------------------------------------------------------------- tables
def merge_tables():
    work = read_tsv(WORK_TABLES, 9, skip_header='id')
    led = {}
    for path in sorted(glob.glob(os.path.join(LOGS, 'tables_*.tsv'))):
        n = 0
        for parts in read_tsv(path, 6, skip_header='label'):
            if not parts[0]:
                continue
            led[parts[0]] = (parts[1], parts[2], parts[3], parts[4], parts[5])
            n += 1
        log('table fragment %s rows=%d' % (os.path.basename(path), n))

    verdicts = ['逐格一致', '逐格修正', '逐格差异·原书自身', '改编补充自洽', '未找到源表', '未覆盖']
    cnt = {v: 0 for v in verdicts}
    rows = []
    for r in work:
        label, num, page, slice_, line, src_book, hint_book, hint_pdf, _grp = r
        if not label.startswith('tab:'):
            continue
        verdict, src_pages, cells, mismatches, note = led.get(label, ('未覆盖', '', '', '', ''))
        if verdict not in cnt:
            verdict = '未覆盖'
        cnt[verdict] += 1
        rows.append(dict(label=label, num=num, page=page, slice=slice_, line=line,
                         src_book=src_book, hint_book=hint_book, hint_pdf=hint_pdf,
                         verdict=verdict, src_pages=src_pages, cells=cells,
                         mismatches=mismatches, note=note))
    total = len(rows)
    done = sum(cnt[v] for v in TABLE_DONE)
    cells_total = sum(int(x['cells']) for x in rows if x['cells'].isdigit())
    mism_total = sum(int(x['mismatches']) for x in rows if x['mismatches'].isdigit())
    log('tables done=%d/%d %s cells=%d mismatches=%d' % (
        done, total, ' '.join('%s=%d' % (v, cnt[v]) for v in verdicts), cells_total, mism_total))

    cells_rows = []
    for path in sorted(glob.glob(os.path.join(LOGS, 'cells_*.tsv'))):
        cells_rows.extend(read_tsv(path, 7, skip_header='label'))
    log('cell-detail rows=%d' % len(cells_rows))

    slices = []
    seen = set()
    for x in rows:
        if x['slice'] not in seen:
            seen.add(x['slice'])
            slices.append(x['slice'])

    out = []
    out.append('# T2 表格逐单元格核对台账（`sources/table_cells.md`）')
    out.append('')
    out.append('本文件由 `tools/review_ledger.py tables` 从磁盘可核验事实生成：')
    out.append('`build/work_tables.tsv`（85 张表清单）＋ `sources/logs/tables_*.tsv`（逐表判决）')
    out.append('＋ `sources/logs/cells_*.tsv`（不一致格的逐格记录）。生成时间 %s。' % GEN_DATE)
    out.append('')
    out.append('**方法**：每个表先渲染成品页面图像（跨页分两张），再渲染源书对应页图像，')
    out.append('**逐单元格**对照行标签、列头、数字、精度、上标、负号、单位、表注；')
    out.append('源书无此表的改编表，逐格核内部自洽（行列合计、百分比、单位、与正文数字一致）。')
    out.append('源书页映射：上册 `书内页 = PDF页 − 19`，下册 `+507`，以页眉印刷页码为准。')
    out.append('')
    out.append('| 结论 | 表数 |')
    out.append('| --- | --- |')
    for v in verdicts:
        out.append('| %s | %d |' % (v, cnt[v]))
    out.append('| **合计** | **%d** |' % total)
    out.append('')
    out.append('已逐格比对单元格 %d 个，记录不一致格 %d 个。' % (cells_total, mism_total))
    out.append('')
    if done < total:
        out.append('> 尚有 %d 张表未取得终判，本台账**不得**用于宣称第三项验收完成。' % (total - done))
        out.append('')
    out.append('## 一、逐表判决')
    out.append('')
    for sl in slices:
        sub = [x for x in rows if x['slice'] == sl]
        sd = sum(1 for x in sub if x['verdict'] in TABLE_DONE)
        out.append('### %s（%d/%d 表有终判）' % (sl, sd, len(sub)))
        out.append('')
        out.append('| 表 | 编号 | 成品页 | 源书页 | 格数 | 不一致 | 结论 | 源书页 | 说明 |')
        out.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
        for x in sub:
            out.append('| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                x['label'], x['num'] or '—', x['page'], x['src_book'] or '—',
                x['cells'] or '—', x['mismatches'] or '—', x['verdict'],
                x['src_pages'] or '—', x['note'].replace('|', '\\|')))
        out.append('')
    if cells_rows:
        out.append('## 二、逐格差异记录（%d 格）' % len(cells_rows))
        out.append('')
        out.append('| 表 | 行 | 列 | 成品 | 源书 | 处置 | 说明 |')
        out.append('| --- | --- | --- | --- | --- | --- | --- |')
        for p in cells_rows:
            out.append('| `%s` | %s | %s | %s | %s | %s | %s |' % (
                p[0], p[1], p[2], p[3].replace('|', '\\|'), p[4].replace('|', '\\|'),
                p[5], p[6].replace('|', '\\|')))
        out.append('')
    todo = [x for x in rows if x['verdict'] not in TABLE_DONE]
    if todo:
        out.append('## 三、未取得终判的表（%d）' % len(todo))
        out.append('')
        out.append('| 表 | 成品页 | 分片 | 状态 |')
        out.append('| --- | --- | --- | --- |')
        for x in todo:
            out.append('| `%s` | %s | %s | %s |' % (x['label'], x['page'], x['slice'], x['verdict']))
        out.append('')
    out.append('## 四、本台账不主张的东西')
    out.append('')
    out.append('- 不主张「逐格一致」等于「表格结论正确」：只核印刷内容与原书一致，不重做数据解释。')
    out.append('- 不主张改编表的数值有权威出处：`改编补充自洽` 只主张内部自洽。')
    out.append('- 不主张未列入 85 表的图形已核：图有单独的 `sources/pixel_verify.md` 口径。')
    out.append('')
    out.append('复跑：`python tools/review_ledger.py tables`，随后 `tools/table_status.py` 重排 `sources/table_status.md`。')
    write_text(TABLE_MD, '\n'.join(out) + '\n')

    with io.open(TABLE_TSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['label', 'verdict', 'src_pages', 'cells_checked', 'mismatches', 'note'])
        for x in rows:
            w.writerow([x['label'], x['verdict'], x['src_pages'], x['cells'], x['mismatches'], x['note']])

    # re-classify the 85-table register from the new evidence
    try:
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'table_status.py')],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        log('table_status.md regenerated')
    except subprocess.CalledProcessError as e:
        log('table_status.py FAILED rc=%s' % e.returncode)
        raise
    return all(x['verdict'] in TABLE_DONE for x in rows)


def main(argv):
    global GEN_DATE
    GEN_DATE = head_date()
    stages = [a for a in argv[1:] if not a.startswith('--')]
    strict = '--strict' in argv[1:]
    if not stages:
        stages = ['all']
    ok = {'pages': True, 'formulas': True, 'tables': True}
    if 'all' in stages or 'pages' in stages:
        ok['pages'] = merge_pages()
    if 'all' in stages or 'formulas' in stages:
        ok['formulas'] = merge_formulas()
    if 'all' in stages or 'tables' in stages:
        ok['tables'] = merge_tables()
    log('OK pages=%s formulas=%s tables=%s strict=%s' % (ok['pages'], ok['formulas'], ok['tables'], strict))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    write_text(REPORT, '\n'.join(report) + '\n')
    # ASCII only on the console (GBK-safe)
    for line in report:
        try:
            line.encode('ascii')
        except UnicodeEncodeError:
            continue
        sys.stdout.write(line + '\n')
    if strict and not all(ok.values()):
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
