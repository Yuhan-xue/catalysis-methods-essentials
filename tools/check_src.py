r"""Source-mark gate: every table in the book must carry a \src{} that is
anchored in a page reference that the rest of the book already corroborates.

What it checks, per table float
-------------------------------
1. the float's \caption has a \src{...};
2. the float does **not** use \figsrc{} (that macro is for figure captions --
   it emits a \\ line break, which is wrong at the end of a table float);
3. every 「书内 p.X[—Y] / PDF p.A[B]」 pair inside that \src is
   * internally consistent -- (X - A) == (Y - B) for both endpoints;
   * uses a book-page-minus-PDF-page offset that the same shard already uses
     elsewhere (a shard-local offset set learned from the baseline commit);
   * when it cites an original-book table number 表 N-M, that number appears in
     the OCR table index (a second, independent scan found the index complete);
4. a \src without any page pair is only accepted when it explicitly declares the
   table is not the source book's table (「非源书」/「本改编本归纳」/「原书无」...).
   Otherwise it is a hard FAIL -- "I could not find it" must be said out loud.

The trusted offset sets come from BASELINE (default: the handoff commit), never
from HEAD: once you commit your own edits, HEAD would let your citations vouch
for themselves.

Usage
-----
    python tools/check_src.py                    # every table in the ledger
    python tools/check_src.py --unlabeled        # only tables still missing a source
    python tools/check_src.py ch10-b ch10-c      # restrict to shards
    python tools/check_src.py --legacy-out ch10-b  # write sources/_p0_verify_*.txt
    P0_BASELINE=<ref> python tools/check_src.py  # pin a different baseline

Report goes to build/check_src[__<shards>].txt (or sources/_p0_verify_* with
--legacy-out). Exit status is 0 when nothing FAILs, 1 otherwise, so it can be
wired into tools/build.ps1 as an extra gate.
"""
import csv
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, 'sources', 'figure_table_list.csv')

# Handoff commit. Deliberately not HEAD -- see module docstring.
BASELINE = os.environ.get('P0_BASELINE', 'feb8739')

# Dashes occur in three shapes across the manuscript: em dash (most, 327 sites),
# TeX's `--` (131 sites) and the odd full-width/minus sign. All must be accepted;
# a one-character class silently rejected `--` and made 131 citations invisible.
DASH = r'\s*[—\-–−－]{1,2}\s*'

# `书内 <page items> / PDF <page items>`. Grouped citations such as
# 「书内 p.227—231、p.239—241 / PDF p.246—250、p.258—260」 are one block with
# items paired positionally; a plain adjacent-pair regex cannot see them.
# Both sides are spelled out as *page items only*, so the match cannot run off
# the end of the citation into following prose (a lazy `.*?` with re.S did
# exactly that, because `.` swallowed the newlines the lookahead stopped on,
# and the run only ended at the next ；or 。-- sometimes lines later).
ITEM = r'p\.\s*\d+(?:' + DASH + r'\d+)?'
ITEM_LIST = r'(?:' + ITEM + r'[\s、，,和至及~]*)+'
PAIR_BLOCK = re.compile(r'书内\s*(' + ITEM_LIST + r')\s*/\s*PDF\s*(' + ITEM_LIST + r')')
PAGE_ITEM = re.compile(r'p\.\s*(\d+)(?:' + DASH + r'(\d+))?')
TABREF = re.compile(r'表\s*([0-9]{1,2})' + DASH + r'([0-9]{1,2})')

# A \src stating outright that the table is not the source book's table may go
# without page numbers: the shards with no slice (ch00-intro, ch12-c, ch13-...)
# have nowhere to point. Silence still fails.
NONSOURCE = re.compile(u'非源书|本改编本归纳|原书无|未在源书|原书文本层未见')

# Original-book table numbers read out of the OCR text layer by two independent
# scans (the second one using much looser patterns, finding no new numbers).
# A number absent from here cannot be cited as an original-book table.
# 3-74 and 4-70 are OCR damage, not typos: the table number ran into the text
# that followed it -- `表３一７４种升温速率…` is 表 3-7 + 「4 种升温速率…」,
# `参看表４－７０` is 表 4-7 + 「0」 residue. Both 3-7 and 4-7 are real tables.
OCR_TABLE_INDEX = {
    '1-1': 5, '1-2': 19, '1-3': 21, '1-4': 23, '1-5': 34, '1-6': 37, '1-7': 50, '1-8': 50,
    '1-9': 50, '1-10': 64, '2-1': 99, '3-1': 171, '3-2': 185, '3-3': 186, '3-4': 187,
    '3-5': 187, '3-6': 192, '3-7': 192, '3-8': 193, '3-10': 194, '3-11': 196, '3-74': 192, '4-1': 224,
    '4-2': 226, '4-3': 228, '4-4': 229, '4-5': 230, '4-6': 232, '4-7': 247, '4-8': 280, '4-9': 291,
    '4-10': 291, '4-11': 292, '4-70': 247, '5-1': 303, '5-2': 305, '5-3': 315, '5-4': 320,
    '5-6': 329, '5-7': 330, '6-1': 364, '6-2': 364, '6-3': 370, '7-1': 421, '7-2': 426,
    '7-3': 433, '7-5': 464, '7-6': 465, '7-7': 468, '7-8': 469, '7-9': 471, '7-10': 471,
    '7-12': 475, '7-13': 477, '7-14': 478, '7-15': 478, '7-16': 480, '7-18': 485,
    '7-19': 504, '7-20': 505, '8-1': 552, '8-2': 553, '9-1': 570, '9-2': 570, '9-3': 571,
    '9-4': 571, '9-5': 584, '9-6': 586, '9-7': 595, '9-8': 596, '9-9': 599, '9-10': 608,
    '9-11': 608, '9-12': 626, '9-13': 626, '9-14': 631, '9-15': 631, '9-16': 637,
    '9-17': 642, '9-18': 643, '9-19': 644, '9-20': 645, '9-21': 646, '9-22': 655,
    '9-23': 664, '9-24': 664, '9-25': 673, '9-26': 674, '9-27': 681, '9-28': 699,
    '9-29': 699, '9-30': 701, '9-31': 701, '9-32': 703, '9-33': 704, '9-34': 708,
    '9-35': 708, '9-36': 711, '9-37': 712, '10-1': 760, '10-2': 763, '10-3': 784,
    '11-1': 860,
}


# --------------------------------------------------------------------- parsing
def balanced(text, macro, start=0):
    """Yield (body, span_start, span_end) for every `macro{...}` at any depth."""
    out = []
    key = macro + '{'
    i = start
    while True:
        i = text.find(key, i)
        if i < 0:
            return out
        j = i + len(key)
        depth = 1
        k = j
        while k < len(text) and depth:
            c = text[k]
            if c == '\\':
                k += 2
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    out.append((text[j:k], i, k + 1))
                    break
            k += 1
        else:
            return out
        i = k + 1


def pairs_of(text):
    """All (book_lo, book_hi, pdf_lo, pdf_hi) page pairs in a citation text.

    Items on the two sides of `/` are paired positionally, so grouped citations
    with several ranges in one clause are read correctly. Returns (pairs, notes).
    """
    pairs, notes = [], []
    flat = re.sub(r'\s+', ' ', text)      # citations wrap across source lines
    for m in PAIR_BLOCK.finditer(flat):
        book = [(int(a), int(b or a)) for a, b in PAGE_ITEM.findall(m.group(1))]
        pdf = [(int(a), int(b or a)) for a, b in PAGE_ITEM.findall(m.group(2))]
        if not book or not pdf:
            continue
        if len(book) != len(pdf):
            notes.append('page-item count differs: %d book vs %d pdf (%s)'
                         % (len(book), len(pdf), flat[m.start():m.end()].strip()))
        for (bl, bh), (pl, ph) in zip(book, pdf):
            pairs.append((bl, bh, pl, ph))
    return pairs, notes


def offsets_of(text):
    """book-page minus PDF-page for every endpoint of every citation in text."""
    s = set()
    for bl, bh, pl, ph in pairs_of(text)[0]:
        s.add(bl - pl)
        s.add(bh - ph)
    return s


def git_show(path):
    try:
        return subprocess.check_output(['git', 'show', BASELINE + ':' + path],
                                       cwd=ROOT, stderr=subprocess.DEVNULL).decode('utf-8')
    except subprocess.CalledProcessError:
        return ''


def label_after(text, pos, limit=600):
    """The first \\label{...} appearing after a caption's closing brace."""
    m = re.search(r'\\label\{([^}]*)\}', text[pos:pos + limit])
    return m.group(1).strip() if m else None


def read_lines(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read().replace('\r\n', '\n').split('\n')


def float_bounds(lines, line_no):
    """1-based inclusive span of the table/figure/longtable float around line_no.

    The ledger records the line **at or just before** the float's \\begin, so the
    scan starts one line later and walks back. Starting any earlier runs into the
    preceding figure, and the whole figure body then looks like part of the table
    (that false positive made four tables report a stray \\figsrc).
    """
    opener = re.compile(r'\s*\\begin\{(table|figure|longtable)\*?\}')
    closer = re.compile(r'\s*\\end\{(table|figure|longtable)\*?\}')

    def bounds_at(beg):
        if beg < 0 or beg >= len(lines) or not opener.match(lines[beg]):
            return None
        end = beg
        while end < len(lines) and not closer.match(lines[end]):
            end += 1
        return None if end >= len(lines) else (beg, end)

    beg = min(line_no, len(lines) - 1)
    while beg >= 0 and not opener.match(lines[beg]):
        beg -= 1
    found = bounds_at(beg)
    if found and opener.match(lines[found[0]]).group(1) in ('table', 'longtable'):
        return found
    # the ledger line may sit inside the float already -- look forward instead
    fwd = min(line_no, len(lines) - 1)
    while fwd < len(lines):
        if opener.match(lines[fwd]):
            r = bounds_at(fwd)
            if r and opener.match(lines[r[0]]).group(1) in ('table', 'longtable'):
                return r
        fwd += 1
    return found


# ------------------------------------------------------------------------ main
def main(argv):
    only, unlabeled, legacy_out = set(), False, False
    for a in argv:
        if a == '--unlabeled':
            unlabeled = True
        elif a == '--legacy-out':
            legacy_out = True
        elif a.startswith('-'):
            sys.stderr.write('unknown option %s\n' % a)
            return 2
        else:
            only.add(a)

    with io.open(LEDGER, encoding='utf-8-sig', newline='') as fh:
        rows = [r for r in csv.DictReader(fh)]
    if rows and None in rows[0]:      # stray columns beyond the header
        del rows[0][None]

    targets = [r for r in rows if (r['kind'] or '').strip() == 'table']
    if unlabeled:
        targets = [r for r in targets if not (r['source_location'] or '').strip()]

    # trusted page pairs + per-shard offset sets, all read from BASELINE
    baseline = {}
    for r in rows:
        if r['file'] not in baseline:
            baseline[r['file']] = git_show(r['file'])
    trusted = set()
    for text in baseline.values():
        for body, _a, _b in balanced(text, '\\src') + balanced(text, '\\figsrc'):
            trusted.update(pairs_of(body)[0])
    shard_offs, global_offs = {}, {'up': set(), 'down': set()}
    for f, text in baseline.items():
        o = offsets_of(text)
        if not o:
            continue
        shard_offs[f] = o
        m = re.match(r'ch(\d{2})', os.path.splitext(os.path.basename(f))[0])
        global_offs['up' if (m and int(m.group(1)) <= 7) else 'down'] |= o

    out, fail, npass, nrev = [], 0, 0, 0
    for r in sorted(targets, key=lambda x: (x['file'], int(x['line'] or 0))):
        shard = os.path.splitext(os.path.basename(r['file']))[0]
        if only and shard not in only:
            continue
        path = os.path.join(ROOT, r['file'].replace('/', os.sep))
        lines = read_lines(path)
        joined = '\n'.join(lines)
        line_no = int(r['line'] or 1)

        # Bind every \caption to the \label that follows it, then look this table
        # up by label. Scanning "the first caption within N lines" silently picks
        # up the caption of an earlier *figure* and reports MISSING \src on a
        # table that has one.
        order, by_label = [], {}
        for body, a, b in balanced(joined, '\\caption'):
            lab = label_after(joined, b)
            ln = joined.count('\n', 0, a) + 1
            order.append((lab, body, ln))
            if lab:
                by_label.setdefault(lab, (body, ln))
        note = ''
        hit = by_label.get(r['label'])
        if hit is None:
            best = None
            for lab, body, ln in order:
                d = abs(ln - line_no)
                if best is None or d < best[0]:
                    best = (d, lab, body, ln)
            if best is not None and best[0] <= 60:
                hit = (best[2], best[3])
                note = 'caption matched by proximity, label=%r' % (best[1],)
            else:
                note = 'NO CAPTION FOUND'

        status, src = [], None
        if hit is None:
            status.append('MISSING \\src')
        elif balanced(hit[0], '\\src'):
            src = balanced(hit[0], '\\src')[-1][0]
            status.append('has \\src')
        else:
            status.append('MISSING \\src')

        # \figsrc must not appear anywhere in a table float -- not just in the
        # caption. Seven tables carried it after \end{tabularx}, where the \\
        # it emits has no line to end.
        bounds = float_bounds(lines, line_no)
        if bounds:
            body_lines = '\n'.join(lines[bounds[0]:bounds[1] + 1])
            if balanced(body_lines, '\\figsrc'):
                status.append('\\figsrc in table float (must be \\src)')

        anchor = 'n/a'
        if src is not None:
            ps, pnotes = pairs_of(src)
            m2 = re.match(r'ch(\d{2})', shard)
            book = 'up' if (m2 and int(m2.group(1)) <= 7) else 'down'
            offs = shard_offs.get(r['file']) or global_offs[book]
            if not ps:
                anchor = ('no page pair (declared non-source)'
                          if NONSOURCE.search(src) else 'NO PAGE PAIR')
            else:
                probs, inline = [], list(pnotes)
                for (bl, bh, pl, ph) in ps:
                    if bl - pl != bh - ph:
                        probs.append('endpoint offsets disagree %s' % ((bl, bh, pl, ph),))
                        continue
                    off = bl - pl
                    if off not in offs:
                        probs.append('offset %d not used by this shard (shard uses %s)'
                                     % (off, sorted(offs)))
                    if (bh - bl) != (ph - pl):
                        inline.append('span %d book pages vs %d pdf pages %s'
                                      % (bh - bl + 1, ph - pl + 1, (bl, bh, pl, ph)))
                    if (bl, bh, pl, ph) in trusted:
                        inline.append('exact hit in baseline')
                anchor = ('BAD ' + '; '.join(probs) if probs
                          else 'all %d pairs offset-consistent' % len(ps))
                if inline:
                    anchor += ' | ' + '; '.join(inline)
            for m in TABREF.finditer(src):
                key = '%s-%s' % (m.group(1), m.group(2))
                if key not in OCR_TABLE_INDEX:
                    anchor += ' | table %s not in OCR index' % key

        verdict = 'PASS'
        if (status[0] != 'has \\src' or len(status) > 1 or 'BAD' in anchor
                or 'NO PAGE PAIR' in anchor or 'not in OCR index' in anchor):
            verdict = 'FAIL'
        elif note:
            verdict = 'REVIEW'
        if verdict == 'PASS':
            npass += 1
        elif verdict == 'REVIEW':
            nrev += 1
        else:
            fail += 1
        out.append('%-6s %-26s %-30s %s:%s' % (verdict, r['label'], r['number'],
                                               r['file'], line_no))
        out.append('        %s | %s' % (status[0], anchor))
        for extra in status[1:]:
            out.append('        %s' % extra)
        if src:
            out.append('        src = %s' % src.replace('\n', ' '))

    checked = npass + nrev + fail
    out += ['',
            'checked %d tables: PASS %d, REVIEW %d, FAIL %d' % (checked, npass, nrev, fail),
            'trusted page pairs (from %s): %d' % (BASELINE, len(trusted)),
            'shard offsets: ' + '; '.join('%s=%s' % (os.path.basename(f), sorted(o))
                                          for f, o in sorted(shard_offs.items())),
            'global offsets: up=%s down=%s' % (sorted(global_offs['up']),
                                               sorted(global_offs['down']))]

    if legacy_out:
        name = '_p0_verify_%s.txt' % '_'.join(sorted(only)) if only else '_p0_verify.txt'
        dest = os.path.join(ROOT, 'sources', name)
    else:
        name = 'check_src%s.txt' % ('__' + '_'.join(sorted(only)) if only else '')
        dest = os.path.join(ROOT, 'build', name)
    if not os.path.isdir(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    with io.open(dest, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')
    print('wrote %s' % os.path.relpath(dest, ROOT).replace('\\', '/'))
    print(out[-4] if len(out) >= 4 else out[-1])
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
