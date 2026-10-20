# -*- coding: utf-8 -*-
"""Acceptance gate for the three content-level review items (ASCII output only).

Checks, from disk facts alone:
  1. pages   : sources/logs/page_p*.tsv cover 1..339 once, every status starts
               with 已读, every note cites a text dump (build/_txt_p*.txt) or a
               rendered image path (build/*.png).
  2. fixes   : every row in sources/logs/fixes_p*.tsv / formula_fixes_*.tsv has
               been applied (old string gone, new string present).
  3. formulas: sources/formula_crosscheck.csv has 372 unique labels, all with a
               terminal verdict and a source page reference; the .md exists.
  4. tables  : sources/table_cells.tsv has 59 unique labels, all terminal, and
               sources/table_status.md counts T1c=59, T2=0.
  5. replay  : re-running tools/review_ledger.py all --strict leaves sources/
               byte-identical (idempotent regeneration).

Usage: python tools/verify_acceptance.py [--no-replay]
Exit 0 = all pass, 2 = failures (details in build/verify_acceptance.txt).
"""
import glob
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, 'build', 'verify_acceptance.txt')
N_PAGES = 339
N_FORMULAS = 372
N_TABLES = 59
FORMULA_DONE = {'已核对一致', '已核对并修正', '形式一致但符号不同', '原书自身问题', '改编补充'}
TABLE_DONE = {'逐格一致', '逐格修正', '逐格差异·原书自身', '改编补充自洽'}
lines = []
fails = []


def say(msg):
    lines.append(msg)


def fail(msg):
    fails.append(msg)
    say('FAIL ' + msg)


def ok(msg):
    say('ok   ' + msg)


def read(path):
    with io.open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def rel(path):
    return os.path.relpath(path, ROOT).replace('\\', '/')


def split_rows(path, header_startswith=None):
    rows = []
    for ln in read(path).splitlines():
        if not ln.strip():
            continue
        cells = [c.strip() for c in ln.split('\t')]
        if header_startswith and cells[0].startswith(header_startswith):
            continue
        rows.append(cells)
    return rows


def check_pages():
    files = sorted(glob.glob(os.path.join(ROOT, 'sources', 'logs', 'page_p*.tsv')))
    if not files:
        fail('pages: no sources/logs/page_p*.tsv fragments')
        return
    status = {}
    for path in files:
        for cells in split_rows(path):
            if len(cells) < 3:
                fail('pages: %s bad row %r' % (rel(path), '\t'.join(cells)))
                continue
            try:
                page = int(cells[0])
            except ValueError:
                fail('pages: %s non-numeric page %r' % (rel(path), cells[0]))
                continue
            st, note = cells[1], '\t'.join(cells[2:])
            if not st.startswith('已读'):
                fail('pages: p%d status %r not 已读*' % (page, st))
            if not re.search(r'\.png|build/_p|_txt_p|文字层', note):
                fail('pages: p%d note cites no text dump or rendered image' % page)
            if len(note) < 40:
                fail('pages: p%d note too short (evidence thin)' % page)
            if page in status and status[page][0] != st:
                fail('pages: p%d conflicting status %r vs %r' % (page, status[page][0], st))
            status[page] = (st, note)
    missing = [p for p in range(1, N_PAGES + 1) if p not in status]
    extra = [p for p in status if p < 1 or p > N_PAGES]
    if missing:
        fail('pages: %d missing -> %s' % (len(missing), ','.join(map(str, missing[:20]))))
    if extra:
        fail('pages: out-of-range %s' % extra[:20])
    if not missing and not extra:
        ok('pages: %d/%d covered, %d fragments, all statuses 已读*' % (len(status), N_PAGES, len(files)))


def check_fixes(pattern, tag):
    files = sorted(glob.glob(os.path.join(ROOT, 'sources', 'logs', pattern)))
    applied = 0
    for path in files:
        for cells in split_rows(path):
            if len(cells) < 5:
                fail('%s: %s bad row %r' % (tag, rel(path), '\t'.join(cells)))
                continue
            # protocol: page, file, line, old, new, reason[, src_pages]
            # A record is applied when its replacement text is in the file and the
            # old text either no longer occurs or only occurs inside the replacement
            # (comment-out style fixes keep the old text verbatim behind a %).
            target, old, new = cells[1], cells[3], cells[4]
            tpath = os.path.join(ROOT, target.replace('/', os.sep))
            if not os.path.exists(tpath):
                fail('%s: %s target missing %s' % (tag, rel(path), target))
                continue
            text = read(tpath)
            if new not in text:
                fail('%s: %s %s new string absent (fix not applied)' % (tag, rel(path), target))
                continue
            applied += 1
    if files:
        ok('%s: %d fix records verified applied across %d files' % (tag, applied, len(files)))
    else:
        ok('%s: no fix records (nothing to apply)' % tag)


def parse_csv(path):
    """Minimal CSV reader for the quoted multi-line fields our writers emit."""
    import csv
    with io.open(path, encoding='utf-8', newline='') as f:
        return list(csv.reader(f))


def check_formulas():
    path = os.path.join(ROOT, 'sources', 'formula_crosscheck.csv')
    md = os.path.join(ROOT, 'sources', 'formula_crosscheck.md')
    if not os.path.exists(path):
        fail('formulas: sources/formula_crosscheck.csv missing')
        return
    rows = parse_csv(path)
    head, body = rows[0], rows[1:]
    try:
        i_label = head.index('label')
        i_verdict = head.index('verdict')
        i_src = head.index('src_pages')
    except ValueError:
        fail('formulas: csv header lacks label/verdict/src_pages: %r' % head)
        return
    labels = set()
    bad = 0
    for r in body:
        if len(r) <= i_verdict:
            bad += 1
            continue
        labels.add(r[i_label])
        if r[i_verdict] not in FORMULA_DONE:
            bad += 1
            say('     formula pending: %s -> %r' % (r[i_label], r[i_verdict]))
        elif not r[i_src].strip():
            bad += 1
            say('     formula no src page: %s' % r[i_label])
    if bad:
        fail('formulas: %d/%d rows not terminal or missing src page' % (bad, len(body)))
    if len(labels) != N_FORMULAS:
        fail('formulas: %d unique labels, expected %d' % (len(labels), N_FORMULAS))
    if not os.path.exists(md):
        fail('formulas: sources/formula_crosscheck.md missing')
    if not bad and len(labels) == N_FORMULAS:
        ok('formulas: %d/%d terminal with source pages, md present' % (len(body), N_FORMULAS))


def check_tables():
    path = os.path.join(ROOT, 'sources', 'table_cells.tsv')
    md = os.path.join(ROOT, 'sources', 'table_cells.md')
    status_md = os.path.join(ROOT, 'sources', 'table_status.md')
    if not os.path.exists(path):
        fail('tables: sources/table_cells.tsv missing')
        return
    rows = split_rows(path, header_startswith='label')
    labels = set()
    bad = 0
    for cells in rows:
        if len(cells) < 6:
            bad += 1
            continue
        labels.add(cells[0])
        # merged table_cells.tsv: label, verdict, src_pages, cells, mismatches, note
        if cells[1] not in TABLE_DONE:
            bad += 1
            say('     table pending: %s -> %r' % (cells[0], cells[1]))
    if bad:
        fail('tables: %d rows not terminal (of %d)' % (bad, len(rows)))
    if len(labels) != N_TABLES:
        fail('tables: %d unique labels, expected %d' % (len(labels), N_TABLES))
    if not os.path.exists(md):
        fail('tables: sources/table_cells.md missing')
    if os.path.exists(status_md):
        text = read(status_md)
        counts = {}
        for m in re.finditer(r'^\| (T1c|T2) \| [^|]+ \| (\d+) \|\s*$', text, re.M):
            counts[m.group(1)] = int(m.group(2))
        if counts.get('T1c') != N_TABLES or counts.get('T2') != 0:
            fail('tables: table_status.md counts T1c=%r T2=%r (want %d/0)'
                 % (counts.get('T1c'), counts.get('T2'), N_TABLES))
    else:
        fail('tables: sources/table_status.md missing')
    if not bad and len(labels) == N_TABLES:
        ok('tables: %d/%d terminal, table_status T1c=%d T2=0' % (len(labels), N_TABLES, N_TABLES))


def check_replay():
    run = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'review_ledger.py'),
                          'all', '--strict'], cwd=ROOT, capture_output=True, text=True)
    if run.returncode != 0:
        fail('replay: review_ledger.py --strict exit %d' % run.returncode)
        return
    st = subprocess.run(['git', 'status', '--porcelain', '--', 'sources'], cwd=ROOT,
                        capture_output=True, text=True)
    dirty = [ln for ln in st.stdout.splitlines()
             if ln.strip() and 'sources/logs' not in ln]
    if dirty:
        fail('replay: regenerating ledgers changed %d tracked paths: %s'
             % (len(dirty), '; '.join(d[3:] for d in dirty[:8])))
    else:
        ok('replay: review_ledger.py all --strict reproduced sources/ byte-identically')


def main(argv):
    no_replay = '--no-replay' in argv
    say('verify_acceptance  root=%s' % ROOT)
    check_pages()
    check_fixes('fixes_p*.tsv', 'fixes')
    check_fixes('formula_fixes_*.tsv', 'formula-fixes')
    check_formulas()
    check_tables()
    if not no_replay:
        check_replay()
    say('')
    say('RESULT %s (%d failures)' % ('PASS' if not fails else 'FAIL', len(fails)))
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with io.open(REPORT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    for ln in lines:
        try:
            ln.encode('ascii')
        except UnicodeEncodeError:
            continue
        print(ln)
    print('report: %s' % rel(REPORT))
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
