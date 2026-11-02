# -*- coding: utf-8 -*-
"""Build the figure worklist for the figure-vs-source review.

Every figure in the artifact is a TikZ redraw, so nothing is copied from the
source book: what has to be checked is whether the redraw says the same thing
as the source figure (same variables, axes, trends, numbers, labels) or
declares itself an adaptation with no source counterpart.

Output: build/work_figures.tsv
    fig_id <TAB> num <TAB> chapter <TAB> file <TAB> line <TAB> page <TAB>
    caption <TAB> src_hint

Usage:  python tools/figure_worklist.py [--pdf build/main.pdf] [--out ...]
ASCII-only stdout so it survives the Windows console.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, 'chapters', 'parts')

CHAP_RE = re.compile(r'\\chapter\{')          # only used to sanity-check files
FIG_BEGIN = re.compile(r'\\begin\{figure(\*?)\}')
FIG_END = re.compile(r'\\end\{figure\*?\}')
LABEL_RE = re.compile(r'\\label\{(fig:[A-Za-z0-9:_-]+)\}')
SRC_RE = re.compile(r'书内\s*p?\.?\s*(\d{2,4})(?:\s*[—\-–~]\s*(\d{2,4}))?')
PDFPAGE_RE = re.compile(r'PDF\s*p?\.?\s*(\d{2,4})')

TEX_CMD = re.compile(r'\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^{}]*\})?')
DROP_CMDS = ('label', 'caption', 'centering')


def strip_tex(s):
    """Flatten a TeX caption to plain text (good enough for matching/search)."""
    s = re.sub(r'%.*', '', s)
    s = s.replace('~', ' ')
    # drop braces-based markup but keep inner text
    s = re.sub(r'\\[A-Za-z@]+\*?\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\[A-Za-z@]+\*?', ' ', s)
    s = s.replace('{', '').replace('}', '')
    s = re.sub(r'\s+', '', s)
    return s.strip()


def read(path):
    with io.open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def caption_of(lines, start):
    """Return the caption text of the figure starting at line index `start`."""
    buf = []
    depth = 0
    seen = False
    for ln in lines[start:start + 140]:
        i = 0
        while i < len(ln):
            if ln.startswith('\\caption{', i):
                seen = True
                depth = 1
                i += len('\\caption{')
                continue
            if seen:
                ch = ln[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return ''.join(buf)
                buf.append(ch)
            i += 1
        if seen and depth == 0:
            break
    return ''.join(buf)


ANCHOR_RE = re.compile(
    r'S([12])\s*[（(]?[上下]?[册]?[)）]?\s*图\s*([0-9]+[-.][0-9]+)'
    r'[^。；;]{0,40}?书内\s*p?\.?\s*(\d{2,4})'
    r'(?:[^。；;]{0,20}?PDF\s*p?\.?\s*(\d{2,4}))?')


def anchor_of(raw_caption):
    """Pull the '据 S1 图1-7 … 书内 p.20 / PDF 39' anchor out of a caption."""
    m = ANCHOR_RE.search(raw_caption)
    if not m:
        f = re.search(r'\\figsrc\{([^}]*)\}', raw_caption)
        if f:
            txt = re.sub(r'\s+', ' ', f.group(1)).strip()
            return txt[:70]
        return ''
    s = 'S%s 图%s / 书内 p.%s' % (m.group(1), m.group(2), m.group(3))
    if m.group(4):
        s += ' / PDF %s' % m.group(4)
    return s


def chapters():
    """Yield (chapter_no, [part files]) in reading order."""
    groups = {}
    for name in sorted(os.listdir(PARTS)):
        m = re.match(r'ch(\d{2})-([a-z])\.tex$', name)
        if not m:
            continue
        groups.setdefault(m.group(1), []).append(name)
    for no in sorted(groups):
        yield no, [os.path.join(PARTS, n) for n in groups[no]]


def main(argv):
    pdf_path = os.path.join(ROOT, 'build', 'main.pdf')
    out_path = os.path.join(ROOT, 'build', 'work_figures.tsv')
    for i, a in enumerate(argv):
        if a == '--pdf' and i + 1 < len(argv):
            pdf_path = argv[i + 1]
        if a == '--out' and i + 1 < len(argv):
            out_path = argv[i + 1]

    rows = []
    for no, files in chapters():
        seq = 0
        for path in files:
            lines = read(path).split('\n')
            for idx, ln in enumerate(lines):
                if not FIG_BEGIN.search(ln):
                    continue
                seq += 1
                label = ''
                for ln2 in lines[idx:idx + 160]:
                    m = LABEL_RE.search(ln2)
                    if m:
                        label = m.group(1)
                        break
                raw_cap = caption_of(lines, idx)
                cap = strip_tex(raw_cap)
                anchor = anchor_of(raw_cap)
                ctx = '\n'.join(lines[max(0, idx - 25):idx])
                hint = ''
                m = SRC_RE.search(ctx)
                if m:
                    hint = '书内 p.%s' % m.group(1)
                    if m.group(2):
                        hint += '-%s' % m.group(2)
                m = PDFPAGE_RE.search(ctx)
                if m:
                    hint += (' / ' if hint else '') + 'PDF p.%s' % m.group(1)
                rows.append({
                    'fig_id': label or ('fig:ch%s-%d' % (no, seq)),
                    'num': int(no),
                    'chapter': int(no),
                    'file': os.path.relpath(path, ROOT).replace('\\', '/'),
                    'line': idx + 1,
                    'page': 0,
                    'caption': cap[:120],
                    'src_hint': hint,
                    'anchor': anchor,
                })

    # locate artifact pages by caption text, fall back to "图N-K"
    pages = []
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        for p in doc:
            pages.append(''.join(doc[p.number].get_text('text').split()))
    except Exception as e:
        sys.stdout.write('WARN pymupdf unavailable: %s\n' % e)

    per_chapter = {}
    for r in rows:
        per_chapter[r['chapter']] = per_chapter.get(r['chapter'], 0) + 1
    seen = {}
    last_page = 0
    for r in rows:
        r['numlabel'] = '图%d-%d' % (r['chapter'], seen.get(r['chapter'], 0) + 1)
        seen[r['chapter']] = seen.get(r['chapter'], 0) + 1
        cap = r['caption']
        segs = [x for x in cap.split('。') if '书内p.' not in x and '书内 p.' not in x]
        capbody = '。'.join(segs).strip()
        page = 0
        if pages:
            for probe_len in (24, 16, 10):
                probe = re.sub(r'\s+', '', r['numlabel'] + capbody[:probe_len])
                if len(capbody) < 6:
                    break
                hit = [i + 1 for i, t in enumerate(pages) if probe in t]
                if hit:
                    page = hit[0]
                    break
            if not page:
                for probe_len in (24, 16, 10):
                    probe = re.sub(r'\s+', '', cap[:probe_len])
                    if len(probe) < 6:
                        break
                    hit = [i + 1 for i, t in enumerate(pages) if probe in t]
                    if hit:
                        page = hit[0]
                        break
            if not page:
                hit = [i + 1 for i, t in enumerate(pages) if r['numlabel'] in t]
                page = hit[0] if hit else 0
            # 图按文档顺序出现：成品页必须不早于上一张图，否则命中的是正文交叉引用
            later = [x for x in ([page] if page else []) if x >= last_page]
            if not later:
                alt = [i + 1 for i, t in enumerate(pages)
                       if r['numlabel'] in t and i + 1 >= last_page]
                page = alt[0] if alt else page
        r['page'] = page
        if page:
            last_page = page

    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('fig_id\tnum\tchapter\tfile\tline\tpage\tcaption\tsrc_hint\tanchor\n')
        for r in rows:
            f.write('%s\t%s\t%d\t%s\t%d\t%d\t%s\t%s\t%s\n' % (
                r['fig_id'], r['numlabel'], r['chapter'], r['file'],
                r['line'], r['page'], r['caption'].replace('\t', ' '),
                r['src_hint'], r['anchor'].replace('\t', ' ')))
    sys.stdout.write('figures=%d pages_mapped=%d\n' % (
        len(rows), sum(1 for r in rows if r['page'])))
    sys.stdout.write('wrote %s\n' % os.path.relpath(out_path, ROOT).replace('\\', '/'))
    # per-chapter tally
    tally = {}
    for r in rows:
        tally[r['chapter']] = tally.get(r['chapter'], 0) + 1
    sys.stdout.write('per_chapter ' + ' '.join(
        '%d:%d' % (k, tally[k]) for k in sorted(tally)) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
