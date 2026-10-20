# -*- coding: utf-8 -*-
"""Apply review fix records (sources/logs/fixes_*.tsv, formula_fixes_*.tsv).

Record shape: page/verdict<TAB>file<TAB>line<TAB>old<TAB>new<TAB>reason[...]

Rules (kept deliberately conservative):
  * if `new` is already present and `old` is not, the record counts as applied;
  * otherwise the occurrence is located by exact `old` text; when it occurs on
    several lines the line nearest the recorded line is used;
  * a record whose `old` text cannot be found at all is reported, not guessed.

Usage: python tools/apply_fixes.py [--dry-run] [fixfile ...]
Report: build/apply_fixes.txt (UTF-8) and a short ASCII summary on stdout.
"""
import glob
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, 'build', 'apply_fixes.txt')
LOGS = os.path.join(ROOT, 'sources', 'logs')


def rel(p):
    return os.path.relpath(p, ROOT).replace('\\', '/')


def read(p):
    with io.open(p, encoding='utf-8', newline='') as f:
        return f.read()


def write(p, text):
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def rows_of(path):
    out = []
    for ln in read(path).splitlines():
        if not ln.strip() or ln.lstrip().startswith('#'):
            continue
        cells = [c for c in ln.split('\t')]
        if len(cells) >= 5:
            out.append(cells)
    return out


def main(argv):
    dry = '--dry-run' in argv
    files = [a for a in argv[1:] if not a.startswith('--')]
    if not files:
        files = sorted(glob.glob(os.path.join(LOGS, 'fixes_*.tsv'))) + \
                sorted(glob.glob(os.path.join(LOGS, 'formula_fixes_*.tsv')))
    rep = []
    done = applied = stale = skipped = 0
    for path in files:
        for cells in rows_of(path):
            done += 1
            target, linen, old, new = cells[1].strip(), cells[2].strip(), cells[3], cells[4]
            tpath = os.path.join(ROOT, target.replace('/', os.sep))
            tag = '%s | %s:%s' % (rel(path), target, linen)
            if not os.path.exists(tpath):
                stale += 1
                rep.append('MISSING %s | target file absent' % tag)
                continue
            text = read(tpath)
            if new in text and old not in text:
                skipped += 1
                rep.append('ALREADY %s | replacement already present' % tag)
                continue
            lines = text.split('\n')
            hits = [i for i, ln in enumerate(lines) if old in ln]
            if not hits:
                if new in text:
                    skipped += 1
                    rep.append('ALREADY %s | old gone, new present' % tag)
                else:
                    stale += 1
                    rep.append('STALE   %s | old text not found: %r' % (tag, old[:60]))
                continue
            try:
                want = int(linen) - 1
            except ValueError:
                want = hits[0]
            pick = min(hits, key=lambda i: abs(i - want))
            before = text.count(old)
            lines[pick] = lines[pick].replace(old, new, 1)
            text2 = '\n'.join(lines)
            after = text2.count(old)
            if not dry:
                write(tpath, text2)
            applied += 1
            rep.append('APPLY   %s | line %d | old-count %d -> %d' % (tag, pick + 1, before, after))
    rep.append('')
    rep.append('rows=%d applied=%d already=%d stale=%d dry_run=%s'
               % (done, applied, skipped, stale, dry))
    io.open(REPORT, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
    print('rows=%d applied=%d already=%d stale=%d report=%s'
          % (done, applied, skipped, stale, rel(REPORT)))
    return 0 if stale == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
