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

Three conclusions, kept apart (R2-W03)
-------------------------------------
A PASS from this tool used to be readable as "the source citation is fine". It is
not. The tool now prints three *distinguishable* conclusions per table, and the
summary counts them separately:

  ① 标注格式合格 -- the checks in 1.-4. above (this is what the tool decides);
  ② 目标页可达   -- the cited pages must exist: PDF page <= that volume's actual
     PDF page count, book page <= that volume's printed-page maximum, and every
     cited page must appear in sources/page_map_up.csv / page_map_down.csv (the
     page map built from the PDFs themselves). The original-book table number is
     also related to the cited pages: |cited page - OCR index page| <= PAGE_TOL,
     distance measured to the nearest cited page range;
  ③ 内容人工核对 -- **this tool does NOT do it.** It only reads the ledger's
     review_status column and reports 已核对/未核对. Whether the cited table really
     says what the caption claims is a human judgement on the page image.

Why the original-table-number tolerance is PAGE_TOL = 2 pages: the OCR table index
was read off the PDF text layer, and for some tables that layer puts the number one
page lower than the printed table (the number is found in the running text of the
page before, or the table's caption line falls on the next PDF page). A 1-page
discrepancy is therefore expected noise, not evidence of a wrong citation; 2 pages
leaves one page of headroom on top of the observed worst case (measured: all
tables 0, one table 1) while still failing a citation that names an unrelated table.

The table set is also compared both ways against the ledger: a \begin{table} in the
tree that has no ledger row is NOT checked by this tool (未检查 ≠ 通过) and makes the
exit status 1; a ledger row whose float has disappeared is reported as stale.

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
# 2026-10-02: the credential-scrub rewrite (`git filter-repo` over the whole
# history) re-hashed every commit from that point on, so the handoff commit
# `feb8739` is now `74e4015`.  An unresolvable ref here is not a manuscript
# defect: it silently empties the trusted page pairs and the run degrades into
# ~80 bogus FAILs (that is exactly what happened before this line was pinned).
# Old->new mapping: reviews/2026-10-02-history-cleanup/commit-map.txt
BASELINE = os.environ.get('P0_BASELINE', '74e4015')

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


# ------------------------------------------------- 结论② : 目标页可达（页码证据）
# Tolerance between the cited page and the OCR index page of the cited original
# table number. Reason (measured, see module docstring): the OCR text layer puts
# some table numbers one page lower than the printed table, so a 1-page delta is
# expected noise; 2 pages keeps one page of headroom while still failing a
# citation that names an unrelated table.
PAGE_TOL = 2

VOLUMES = (('up', 'page_map_up.csv', u'上册'), ('down', 'page_map_down.csv', u'下册'))


def load_page_map():
    """Read both volume page maps (pdf_page <-> book_page). Derived from the PDFs.

    Read through module-level ROOT so a probe that rebinds ROOT redirects it.
    book_page may be a roman numeral or empty (front matter) -- only rows whose
    book_page parses as a number become 'printed page exists' evidence.
    """
    vols = {}
    for key, fn, label in VOLUMES:
        vol = {'file': fn, 'label': label, 'n': 0, 'pdf_max': 0, 'book_max': 0,
               'pdfs': set(), 'books': set(), 'rows': {}, 'missing': False}
        path = os.path.join(ROOT, 'sources', fn)
        if not os.path.exists(path):
            vol['missing'] = True
            vols[key] = vol
            continue
        with io.open(path, encoding='utf-8-sig', newline='') as fh:
            for row in csv.DictReader(fh):
                if None in row:
                    del row[None]
                vol['n'] += 1
                try:
                    pdf = int((row.get('pdf_page') or '').strip())
                except ValueError:
                    continue
                vol['pdfs'].add(pdf)
                vol['pdf_max'] = max(vol['pdf_max'], pdf)
                bp = (row.get('book_page') or '').strip()
                if re.match(r'^\d+$', bp):
                    b = int(bp)
                    vol['books'].add(b)
                    vol['rows'][pdf] = b
                    vol['book_max'] = max(vol['book_max'], b)
        vols[key] = vol
    return vols


def index_distance(idx, ranges):
    """Distance from the OCR index page to the nearest cited book-page range (0 if inside)."""
    best = None
    for bl, bh in ranges:
        lo, hi = (bl, bh) if bl <= bh else (bh, bl)
        d = 0 if lo <= idx <= hi else (lo - idx if idx < lo else idx - hi)
        best = d if best is None else min(best, d)
    return best


def fmt_ranges(ranges):
    return u'、'.join(u'p.%d—%d' % (bl, bh) if bl != bh else u'p.%d' % bl for bl, bh in ranges)


def check_reachable(vol, ps):
    """② 目标页可达：页码必须在册内、必须在页码表里、且两侧指向同一行。"""
    probs = []
    if vol is None or vol.get('missing'):
        return [u'页码表缺失（%s），无法判断目标页是否存在' % (vol or {}).get('file', '?')]
    for (bl, bh, pl, ph) in ps:
        if ph > vol['pdf_max']:
            probs.append(u'PDF p.%d 超出%s PDF 实际页数 %d' % (ph, vol['label'], vol['pdf_max']))
        if bh > vol['book_max']:
            probs.append(u'书内 p.%d 超出%s 印刷页上限 %d' % (bh, vol['label'], vol['book_max']))
        miss_pdf = [p for p in range(pl, ph + 1) if p not in vol['pdfs']]
        if miss_pdf:
            probs.append(u'PDF p.%s 不在 %s 中（页码表无此行 → 无法确认该页存在）'
                         % (u','.join(str(p) for p in miss_pdf), vol['file']))
        miss_book = [b for b in range(bl, bh + 1) if b not in vol['books']]
        if miss_book:
            probs.append(u'书内 p.%s 不在 %s 中（该印刷页不在页码表：缺失页/非正文页）'
                         % (u','.join(str(b) for b in miss_book), vol['file']))
        row = vol['rows'].get(pl)
        if row is not None and row != bl:
            probs.append(u'%s：PDF p.%d 对应书内 p.%d，引用写的是 p.%d'
                         % (vol['file'], pl, row, bl))
    return probs


TABLE_LABEL_PREFIX = 'tab:'


def scan_tex_tables():
    """③的前置：树里实际存在的**每一个** table/longtable 环境（R3-W01）。

    清点口径 = 「文件 + 表环境起始行」，label 只是这条记录的**属性**，不再是筛选条件。
    旧实现只收 `tab:` 前缀标签并放进 dict，于是无标签表、非 `tab:` 标签表整个从分母里
    消失（新增一张无来源无标签的表，仍报 85 PASS、差异 0）；重复标签也被
    `setdefault` 静默吃掉一个。返回 list[dict(file, line, env, labels)]。

    read_lines is looked up at call time on purpose: a probe can rebind it to
    inject an unregistered float without touching the working tree.
    """
    found = []
    opener = re.compile(r'\s*\\begin\{(table|longtable)(\*?)\}')
    closer = re.compile(r'\s*\\end\{(table|longtable)\*?\}')
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, 'chapters')):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith('.'))
        for fn in sorted(filenames):
            if not fn.endswith('.tex'):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
            lines = read_lines(path)
            i = 0
            while i < len(lines):
                m = opener.match(lines[i])
                if not m:
                    i += 1
                    continue
                end, depth = i, 1
                while end + 1 < len(lines):
                    end += 1
                    if opener.match(lines[end]):
                        depth += 1
                    elif closer.match(lines[end]):
                        depth -= 1
                        if depth == 0:
                            break
                body = '\n'.join(lines[i:end + 1])
                labels = [lab.strip() for lab, _a, _b in balanced(body, '\\label')]
                found.append(dict(file=rel, line=i + 1,
                                  env='%s%s' % (m.group(1), m.group(2)),
                                  labels=labels))
                i = end + 1
    return found


def classify_tex_tables(scan, ledger_labels):
    """把扫描到的表分成「已检查」与五类「未检查」，标签问题单列（R3-W01）。

    未检查 ≠ 通过：任何一类未检查都写 FAIL 并让退出码非零。
    """
    by_label = {}
    for rec in scan:
        for lab in rec['labels']:
            by_label.setdefault(lab, []).append(rec)
    dup_labels = sorted(l for l, rs in by_label.items() if len(rs) > 1)
    checked, unchecked = [], []
    for rec in scan:
        where = '%s:%d' % (rec['file'], rec['line'])
        labs = rec['labels']
        if not labs:
            why = u'无 \\label（台账无从关联）'
        elif len(labs) > 1:
            why = u'一个表环境里 %d 个 \\label：%s' % (len(labs), u'、'.join(labs))
        elif labs[0] in dup_labels:
            why = u'重复标签 %s（共 %d 处）' % (labs[0], len(by_label[labs[0]]))
        elif not labs[0].startswith(TABLE_LABEL_PREFIX):
            why = u'标签不合规范 %s（表标签须以 %s 开头）' % (labs[0], TABLE_LABEL_PREFIX)
        elif labs[0] not in ledger_labels:
            why = u'台账缺项 %s（.tex 有而 sources/figure_table_list.csv 无）' % labs[0]
        else:
            checked.append(dict(where=where, label=labs[0], env=rec['env']))
            continue
        unchecked.append(dict(where=where, label=(labs[0] if labs else u'（无标签）'),
                              env=rec['env'], why=why))
    ledger_only = sorted(ledger_labels - set(by_label))
    return dict(checked=checked, unchecked=unchecked, dup_labels=dup_labels,
                ledger_only=ledger_only, scanned=len(scan))


# ------------------------------------------------- ③ 台账 review_status 解析
# R3-W02：旧判据是「文本含『未核对』→ 未核对，否则 → 已核对」，于是清空单元格、
# 填「待复核」、写成错别字都会被**静默计成已完成**（0/85 → 1/84）。
# 现判据：显式枚举 + 白名单前缀 + 证据字段四要素齐全，未知取值一律**失败关闭**
# （计入未完成，绝不默认已完成）。
REVIEW_STATES = (u'未核对', u'待复核', u'已核对', u'不适用')
REVIEW_BUCKETS = (u'已核对', u'已核对（缺证据）', u'未核对', u'待复核', u'不适用', u'未识别')
# 四类证据字段（验收口径：页面、核验者、时间、结论）。台账没有独立列，证据写在
# review_status 单元格内，用 ; ； | ｜ 分隔，形如
#   已核对; 页面=PDF p.36 / 书内 p.17; 核验者=张三; 时间=2026-09-30; 结论=与源书一致
REVIEW_EVIDENCE = ((u'页面', (u'页面', u'页码', 'page', 'pages')),
                   (u'核验者', (u'核验者', u'核对人', u'核对人', 'verifier', 'reviewer', 'by')),
                   (u'时间', (u'时间', u'日期', 'date', 'time')),
                   (u'结论', (u'结论', u'判定', 'verdict', 'conclusion', 'result')))
REVIEW_SEP_RE = re.compile(u'[;；|｜]')
REVIEW_EV_RE = re.compile(u'\\s*([^=:：;；|｜]+?)\\s*[=:：]\\s*([^;；|｜]*)')


def parse_review(raw):
    """把一个 review_status 单元格解析成 {state, done, token, missing, evidence, note}。

    判定顺序：精确匹配 → 白名单前缀匹配（只认四个规范态）→ 未识别。
    未识别 / 已核对但缺证据 → done=False，即**只在证据齐全时**才计入已完成。
    """
    text = (raw or '').strip()
    if not text:
        return dict(raw='', state=u'未核对', token=u'（空）', done=False,
                    missing=[], evidence={}, note=u'单元格为空，按未核对计')
    parts = REVIEW_SEP_RE.split(text)
    token = parts[0].strip()
    rest = ';'.join(parts[1:])
    ev, why = {}, ''
    for name, val in REVIEW_EV_RE.findall(rest):
        key = name.strip().lower()
        for canon, aliases in REVIEW_EVIDENCE:
            if key == canon.lower() or key in aliases:
                if val.strip():
                    ev.setdefault(canon, val.strip())
    state = None
    if token in REVIEW_STATES:
        state = token
    else:
        for canon in REVIEW_STATES:
            if token.startswith(canon):
                state, why = canon, u'前缀匹配「%s…」' % canon
                break
    if state is None:
        return dict(raw=text, state=u'未识别', token=token, done=False,
                    missing=[c for c, _ in REVIEW_EVIDENCE], evidence=ev,
                    note=u'取值不在枚举 未核对/待复核/已核对/不适用 内（错别字或未定义）')
    missing = [c for c, _ in REVIEW_EVIDENCE if c not in ev]
    if state == u'已核对':
        if missing:
            return dict(raw=text, state=u'已核对（缺证据）', token=token, done=False,
                        missing=missing, evidence=ev,
                        note=u'声明已核对但缺 %s' % u'、'.join(missing))
        return dict(raw=text, state=u'已核对', token=token, done=True,
                    missing=[], evidence=ev, note=why)
    return dict(raw=text, state=state, token=token, done=False,
                missing=[], evidence=ev, note=why)


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

    # The trusted page pairs and the per-shard offset sets are read from
    # BASELINE; if that ref does not resolve, every offset check loses its
    # reference and the run degrades into ~80 bogus FAILs.  Say that once,
    # loudly, instead of blaming the manuscript.
    if subprocess.call(['git', 'rev-parse', '--verify', '--quiet',
                        BASELINE + '^{commit}'], cwd=ROOT,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print('FAIL baseline ref %r does not resolve -- history rewritten? '
              'pin it with P0_BASELINE=<ref>; old->new map in '
              'reviews/2026-10-02-history-cleanup/commit-map.txt' % BASELINE)
        return 1

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

    page_map = load_page_map()
    tex_scan = scan_tex_tables()
    out, fail, npass, nrev = [], 0, 0, 0
    # 三层结论分别计数：①②由本工具判定，③只读台账（不判定内容）
    n_fmt_fail = n_page_fail = n_page_na = n_num_fail = 0
    n_manual = dict((k, 0) for k in REVIEW_BUCKETS)
    man_bad, accounting_bad = [], []
    tol_used = 0
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
        ps = []
        page_bad = []
        num_bad = []
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
            ranges = [(bl, bh) for (bl, bh, _pl, _ph) in ps]
            for m in TABREF.finditer(src):
                key = '%s-%s' % (m.group(1), m.group(2))
                if key not in OCR_TABLE_INDEX:
                    anchor += ' | table %s not in OCR index' % key
                    continue
                idx = OCR_TABLE_INDEX[key]
                if not ranges:
                    anchor += u' | 原表号 %s：OCR 索引页 %d（无页对可比）' % (key, idx)
                    continue
                d = index_distance(idx, ranges)
                if d > PAGE_TOL:
                    num_bad.append(key)
                    anchor += (u' | 原表号 %s 与页码不符：OCR 索引页 %d 距引用书页 %s 最近 %d 页 > 容差 %d 页'
                               % (key, idx, fmt_ranges(ranges), d, PAGE_TOL))
                else:
                    if d:
                        tol_used += 1
                    anchor += (u' | 原表号 %s ↔ OCR 索引页 %d 差 %d 页（≤ %d 页容差）'
                               % (key, idx, d, PAGE_TOL))

            # 结论② 目标页可达：独立于①的格式判定（页码是否存在，不代替人看内容）
            if ps:
                page_bad = check_reachable(page_map.get(book), ps)
                if page_bad:
                    anchor += u' | ② ' + u'; '.join(page_bad)

        verdict = 'PASS'
        if (status[0] != 'has \\src' or len(status) > 1 or 'BAD' in anchor
                or 'NO PAGE PAIR' in anchor or 'not in OCR index' in anchor
                or num_bad or page_bad):
            verdict = 'FAIL'
        elif note:
            verdict = 'REVIEW'
        if verdict == 'PASS':
            npass += 1
        elif verdict == 'REVIEW':
            nrev += 1
        else:
            fail += 1
        fmt_state = 'PASS'
        if status[0] != 'has \\src' or len(status) > 1 or 'BAD' in anchor:
            fmt_state = 'FAIL'
        elif 'NO PAGE PAIR' in anchor:
            fmt_state = 'REVIEW'
        if src is None or not ps:
            page_state = u'N/A（无页对或声明非源书）'
        else:
            page_state = 'FAIL' if page_bad else 'PASS'
        num_state = u'N/A' if src is None else ('FAIL' if num_bad else 'PASS')
        man_raw = (r.get('review_status') or '').strip()
        man = parse_review(man_raw)
        man_state = man['state']
        n_manual[man_state] = n_manual.get(man_state, 0) + 1
        if man_state in (u'未识别', u'已核对（缺证据）'):
            man_bad.append(u'%s（%s:%s）review_status=%r → %s：%s'
                           % (r['label'], r['file'], line_no, man_raw,
                              man_state, man['note']))
        if fmt_state == 'FAIL':
            n_fmt_fail += 1
        if page_state == 'FAIL':
            n_page_fail += 1
        elif page_state.startswith('N/A'):
            n_page_na += 1
        if num_state == 'FAIL':
            n_num_fail += 1
        out.append('%-6s %-26s %-30s %s:%s' % (verdict, r['label'], r['number'],
                                               r['file'], line_no))
        out.append('        %s | %s' % (status[0], anchor))
        man_show = man_raw or u'（空）'
        man_extra = u''
        if man_state == u'已核对（缺证据）':
            man_extra = u'；缺证据字段：' + u'、'.join(man['missing'])
        elif man_state == u'未识别':
            man_extra = u'；取值不在枚举内（首段=%r）' % man['token']
        elif man['note'].startswith(u'前缀匹配') or man['note'].startswith(u'单元格为空'):
            man_extra = u'；%s' % man['note']
        out.append(u'        ①②③ 标注格式=%s 目标页可达=%s（原表号↔页码=%s）'
                   u' 内容人工核对=%s［台账 review_status=%s%s；本工具不替代人看页面图像］'
                   % (fmt_state, page_state, num_state, man_state, man_show, man_extra))
        for extra in status[1:]:
            out.append('        %s' % extra)
        if src:
            out.append('        src = %s' % src.replace('\n', ' '))

    checked = npass + nrev + fail
    # R3-W02：③ 的完成数是「证据齐全的已核对」，其余（未核对/待复核/未识别/
    # 已核对但缺证据）全算未完成；不适用单列，不计入完成也不计入未完成。
    n_manual_done = n_manual[u'已核对']
    n_manual_na = n_manual[u'不适用']
    n_manual_todo = checked - n_manual_done - n_manual_na
    if sum(n_manual.values()) != checked:
        accounting_bad.append(u'③ 台账对账不平：分桶合计 %d ≠ 已检查表数 %d'
                              % (sum(n_manual.values()), checked))
    ledger_labels = set((r['label'] or '').strip() for r in rows
                        if (r['kind'] or '').strip() == 'table')
    # R3-W01：分母 = .tex 里真实存在的**每一个**表环境（文件 + 起始行），
    # 不再是「台账里登记过的 tab: 标签」——后者会让无标签表 / 非 tab: 标签表
    # 直接从分母里消失，新增一张这样的表仍然报 85 PASS、差异 0。
    tex_cov = classify_tex_tables(tex_scan, ledger_labels)
    tex_unchecked, tex_dup = tex_cov['unchecked'], tex_cov['dup_labels']
    ledger_only = tex_cov['ledger_only']
    n_tex_scanned = tex_cov['scanned']
    n_tex_checked = len(tex_cov['checked'])
    # `only` (single shard) and `--unlabeled` both narrow *targets* to a subset
    # of the corpus while the .tex census always counts every table, so the two
    # numbers are not comparable in those modes.  (Before this guard,
    # `--unlabeled` on a fully annotated tree -- 0 targets -- exited 1 with a
    # bogus "85 != 0" accounting FAIL.)
    if not only and not unlabeled and n_tex_checked != checked:
        accounting_bad.append(
            u'.tex 已检查表数 %d ≠ 台账已检查行数 %d（清点口径与检查口径不一致）'
            % (n_tex_checked, checked))
    up, down = page_map['up'], page_map['down']
    out += ['',
            'checked %d tables: PASS %d, REVIEW %d, FAIL %d' % (checked, npass, nrev, fail),
            'trusted page pairs (from %s): %d' % (BASELINE, len(trusted)),
            'shard offsets: ' + '; '.join('%s=%s' % (os.path.basename(f), sorted(o))
                                          for f, o in sorted(shard_offs.items())),
            'global offsets: up=%s down=%s' % (sorted(global_offs['up']),
                                               sorted(global_offs['down'])),
            '',
            u'三层结论（本工具的判定边界，R2-W03）—— 三者不可互相替代：',
            u'  ① 标注格式合格（本工具判定）：PASS %d / FAIL %d'
            % (checked - n_fmt_fail, n_fmt_fail),
            u'  ② 目标页可达（本工具判定；依据 sources/%s %d 行 / sources/%s %d 行）：'
            u'PASS %d / FAIL %d / N/A %d'
            % (up['file'], up['n'], down['file'], down['n'],
               checked - n_page_fail - n_page_na, n_page_fail, n_page_na),
            u'     册页数：%s PDF %d 页、印刷页到 %d 页；%s PDF %d 页、印刷页到 %d 页'
            % (up['label'], up['pdf_max'], up['book_max'],
               down['label'], down['pdf_max'], down['book_max']),
            u'  ③ 内容人工核对（**本工具不判定**，只读台账 review_status；枚举：'
            u'未核对 / 待复核 / 已核对 / 不适用）：已完成 %d / 未完成 %d'
            u'（未核对 %d、待复核 %d、未识别 %d、已核对但缺证据 %d）、不适用 %d'
            u' —— 只有「已核对」且带齐 页面/核验者/时间/结论 四类证据才计入完成；'
            u'台账无独立证据列，证据写在 review_status 单元格内（分号分隔，形如'
            u'「已核对; 页面=PDF p.36; 核验者=…; 时间=…; 结论=…」）；'
            u'引用内容对不对必须人看页面图像'
            % (n_manual_done, n_manual_todo, n_manual[u'未核对'], n_manual[u'待复核'],
               n_manual[u'未识别'], n_manual[u'已核对（缺证据）'], n_manual_na),
            u'原表号↔页码：容差 %d 页（已知 OCR 索引对部分表低 1 页，留 1 页余量；'
            u'理由见模块 docstring）；用到容差（差 1–%d 页）的表 %d 个，超出容差 %d 个'
            % (PAGE_TOL, PAGE_TOL, tol_used, n_num_fail),
            u'.tex 表清点（口径＝「文件 + 表环境起始行」，R3-W01）：扫描到 %d 张、'
            u'已检查 %d 张、未检查 %d 张；台账登记 %d 张；台账有而 .tex 无 %d 张'
            % (n_tex_scanned, n_tex_checked, len(tex_unchecked), len(ledger_labels),
               len(ledger_only))]
    out.append(u'')
    if tex_unchecked:
        out.append(u'    未检查的表（新增表若不写 tab: 标签或不入台账，旧口径会当它不存在）：')
    for rec in tex_unchecked:
        out.append(u'    FAIL %s %s [%s] —— %s（未检查 ≠ 通过）'
                   % (rec['where'], rec['label'], rec['env'], rec['why']))
    if tex_dup:
        out.append(u'    重复标签：%s —— 同一标签出现在多个表环境，页面/台账关联不可靠'
                   % u'、'.join(tex_dup))
    for lab in ledger_only:
        out.append(u'    WARN 台账有而 .tex 无：%s —— 台账可能过期，请重新生成' % lab)
    if man_bad:
        out.append(u'')
        out.append(u'    ③ 台账 review_status 问题行（均计入「未完成」，不会默认已完成）：')
        for msg in man_bad:
            out.append(u'    WARN ' + msg)
    for msg in accounting_bad:
        out.append(u'    FAIL ' + msg)

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
    print(next((ln for ln in out if ln.startswith('checked ')), out[-1]))
    if tex_unchecked:
        unregistered = [r['label'] for r in tex_unchecked if u'台账缺项' in r['why']]
        if unregistered:
            sys.stderr.write('unregistered tables (not checked): %s\n'
                             % ', '.join(unregistered))
        sys.stderr.write('unchecked tables: %d (scanned %d, checked %d)\n'
                         % (len(tex_unchecked), n_tex_scanned, n_tex_checked))
    return 1 if (fail or tex_unchecked or accounting_bad) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
