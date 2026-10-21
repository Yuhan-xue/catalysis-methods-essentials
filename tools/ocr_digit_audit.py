# -*- coding: utf-8 -*-
"""Book-wide digit audit of table cells against *page-image* OCR.

Motivation: the up-volume PDF's embedded text layer is a corrupted publisher OCR
(it turned 820 into 520 and produced a real content defect in the artifact). Every
table cell that carries numbers should therefore be cross-checked against the
rendered page, not only against the text layer.

Scope: cells whose cited source pages fall in the up volume (book page <= 500,
PDF = book + 19). Down-volume cells are counted but not scanned here.

Outputs:
  sources/ocr_digit_audit.md   report (summary + cells with misses)
  build/ocr_digit_audit.tsv    label,row,col,pdf_pages,tokens,hits,misses,verdict

Usage: python tools/ocr_digit_audit.py [--limit N]
"""
import glob
import io
import os
import re
import sys
import time

import pymupdf
from rapidocr_onnxruntime import RapidOCR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS = os.path.join(ROOT, 'sources', 'logs')
OUT_MD = os.path.join(ROOT, 'sources', 'ocr_digit_audit.md')
OUT_TSV = os.path.join(ROOT, 'build', 'ocr_digit_audit.tsv')
CACHE = os.path.join(ROOT, 'build', '_ocr')

SRC_UP = (r'C:\Users\53150\.dsh\attachments\v1\files\9f'
          r'\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7'
          r'\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf')
SRC_DOWN = (r'C:\Users\53150\.dsh\attachments\v1\files\a1'
            r'\a1b8bc6b3dc73c6fdec8445f6d111b9113f551727f34eb01b16150141558f62c'
            r'\现代催化研究方法新编(下册) (辛勤, 罗孟飞, 徐杰) (z-library.sk, 1lib.sk, z-lib.sk).pdf')

# down volume: 书内 = PDF + offset, verified against printed folios
DOWN_OFFSET = {8: 508, 9: 509, 10: 511, 11: 512, 12: 514}

NUM = re.compile(r'\d+(?:\.\d+)?')
BOOK_PAGE = re.compile(r'(?:p\.|书内\s*p?\.?)\s*(\d{3})(?:\s*[—\-–~]\s*(\d{3}))?')
PDF_PAGE = re.compile(r'PDF\s*p?\.?\s*(\d{3})(?:\s*[—\-–~]\s*(\d{3}))?')

DASHES = dict.fromkeys(map(ord, '\u2010\u2011\u2012\u2013\u2014\u2015\u2212\uff0d'), '-')
FW = {ord(f): ord(t) for f, t in zip('０１２３４５６７８９．％', '0123456789.%')}


def norm(s):
    s = s.translate(DASHES).translate(FW)
    s = s.replace('～', '~').replace('∼', '~')
    return re.sub(r'\s+', '', s)


def token_pattern(t):
    """Regex that tolerates OCR dropping the decimal point / separator, but does
    not match inside a longer number."""
    parts = [re.escape(x) for x in t.split('.')]
    body = r'[.,·]?\s?'.join(parts)
    return r'(?<!\d)' + body + r'(?!\d)'


DIGITS = '零一二三四五六七八九'


def cn_num(token):
    """Return the Chinese-numeral spelling of an integer token, or '' if not an integer."""
    if not re.match(r'^\d{1,3}$', token or ''):
        return ''
    n = int(token)
    if n == 0:
        return DIGITS[0]
    if n < 10:
        return DIGITS[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        head = '十' if tens == 1 else DIGITS[tens] + '十'
        return head + (DIGITS[ones] if ones else '')
    hundreds, rest = divmod(n, 100)
    head = DIGITS[hundreds] + '百'
    if not rest:
        return head
    if rest < 10:
        return head + '零' + DIGITS[rest]
    tens, ones = divmod(rest, 10)
    return head + (DIGITS[tens] + '十' if tens > 1 else '十') + (DIGITS[ones] if ones else '')


TRIAGE = {
    ('ch02c-newold', '束斑球差校正器'): ('单位换算', '源页以 Å 给出 2 Å / 1.3 Å，本表按 nm 写 0.20 / 0.13'),
    ('ch06b-molines', '325 nm'): ('改编补充', '11 为荧光/拉曼强度比的模型估算，非源书数值'),
    ('tab:ch04b-extinction', '行标题'): ('误报', '41 是 4₁ 螺旋轴记号，不是数值'),
    ('tab:ch04c-rfactor', 'Rwp'): ('OCR 漏识', '源文 p.284 印「有时也会出现约 20% 的较大值」'),
    ('tab:ch09-bg', 'Shirley'): ('误报', '16 是式号（9-16）'),
    ('tab:ch09-bg', 'Tougaard'): ('误报', '17 是式号（9-17）'),
    ('tab:ch09-so', 'P 2p'): ('改编补充', '自旋轨道分裂列除 S 2p 外为通用文献量级，非源表数值'),
    ('tab:ch09-so', 'Cl 2p'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Ti 2p'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Cu 2p'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Ni 2p'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Mo 3d'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Pd 3d'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Pt 4f'): ('改编补充', '同上'),
    ('tab:ch09-so', 'Au 4f'): ('改编补充', '同上'),
    ('tab:raman-routes', '近红外（FT-Raman，1064 nm）'): ('改编补充', '源书只给「近红外（大于 700 nm）」，532/1064 是常见激发线举例'),
    ('tab:surface-compare', '深度-XPS'): ('改编补充', '源书只给 10 nm 上限，下限 0.5 nm 为本表量级表述'),
    ('tab:ups-xps', '1'): ('舍入', '源页印 21.2 eV，本表写 21.22 eV（He I 精确值）'),
    ('tab:xrd-limits', '注'): ('误报', '220/223/225/227/232 是页码，不是数据'),
}

def tokens(text):
    out = []
    for t in NUM.findall(text):
        if len(t.replace('.', '')) < 2:      # lone digits are not evidence
            continue
        if t not in out:
            out.append(t)
    return out


def load_chapters():
    """label -> chapter number, from sources/figure_table_list.csv."""
    out = {}
    path = os.path.join(ROOT, 'sources', 'figure_table_list.csv')
    for i, line in enumerate(io.open(path, encoding='utf-8')):
        if i == 0:
            continue
        cols = line.split(',')
        if len(cols) < 4:
            continue
        label = cols[0].strip().strip('"')
        try:
            out[label] = int(cols[3])
        except ValueError:
            continue
    return out


def pages_for(src_col, note, chapter=None):
    """cite text -> [(vol, pdf_page)] for the volume that owns the chapter."""
    cite = src_col + ' ' + note
    out = []
    down = chapter is not None and chapter >= 8
    off = DOWN_OFFSET.get(chapter or 0)
    for m in BOOK_PAGE.finditer(cite):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        for book in range(a, min(b, a + 6) + 1):
            if down and off:
                pdf = book - off
                if pdf <= 0:
                    continue
                item = ('down', pdf)
            else:
                if book > 500:
                    continue
                item = ('up', book + 19)
            if item not in out:
                out.append(item)
    if not down:
        for m in PDF_PAGE.finditer(cite):
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            for pdf in range(a, min(b, a + 6) + 1):
                item = ('up', pdf)
                if item not in out:
                    out.append(item)
    return out


def ocr_page(doc, vol, pdf_page, ocr):
    cache = os.path.join(CACHE, '%s_%d.txt' % (vol, pdf_page))
    if os.path.exists(cache):
        return io.open(cache, encoding='utf-8').read()
    png = os.path.join(CACHE, '%s_%d.png' % (vol, pdf_page))
    doc[pdf_page - 1].get_pixmap(dpi=300).save(png)
    t0 = time.time()
    res, _ = ocr(png)
    lines = sorted([(int(min(float(p[1]) for p in box)), text) for box, text, _s in (res or [])])
    out = '\n'.join(t for _y, t in lines)
    io.open(cache, 'w', encoding='utf-8', newline='\n').write(out)
    print('ocr %s p.%d %d lines %.0fs' % (vol, pdf_page, len(lines), time.time() - t0))
    return out


def main():
    limit = None
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])

    chapters = load_chapters()
    rows = []
    for f in sorted(glob.glob(os.path.join(LOGS, 'cells_*.tsv'))):
        for line in io.open(f, encoding='utf-8'):
            cols = line.rstrip('\n').split('\t')
            if len(cols) < 7:
                continue
            label, row, col, artifact, source, action, note = cols[:7]
            toks = tokens(artifact)
            if not toks:
                continue
            pages = pages_for(source, note, chapters.get(label))
            rows.append((label, row, col, artifact, pages, toks, note))
    print('numeric cells', len(rows))
    if limit:
        rows = rows[:limit]

    need = []
    for row in rows:
        for item in row[4]:
            if item not in need:
                need.append(item)
    need.sort()
    print('pages to scan', len(need))

    docs = {'up': pymupdf.open(SRC_UP), 'down': pymupdf.open(SRC_DOWN)}
    ocr = RapidOCR()
    text = {}
    for vol, p in need:
        text[(vol, p)] = norm(ocr_page(docs[vol], vol, p, ocr))

    out_rows = []
    for label, row, col, artifact, pages, toks, note in rows:
        hay = '\n'.join(text[item] for item in pages if item in text)
        hits, hits_loose, hits_cn = [], [], []
        for t in toks:
            if t in hay:
                hits.append(t)
            elif re.search(token_pattern(t), hay):
                hits.append(t)
                hits_loose.append(t)
            else:
                word = cn_num(t)
                if word and word in hay:
                    hits.append(t)
                    hits_cn.append(t)
        miss = [t for t in toks if t not in hits]
        if not pages:
            verdict = '无源页可扫'
        elif not miss:
            if hits_cn:
                verdict = '全部命中（汉字数字）'
            elif hits_loose:
                verdict = '全部命中（去小数点）'
            else:
                verdict = '全部命中'
        elif hits:
            verdict = '部分命中'
        else:
            verdict = '全部未命中'
        cite = ','.join('%s%d' % (vol[0], p) for vol, p in pages)
        tri = TRIAGE.get((label, row), ('', ''))
        triage = (tri[0] + '：' + tri[1]) if tri[0] else ''
        if verdict.startswith('全部命中'):
            triage = ''
        out_rows.append((label, row, col, cite, ' '.join(toks),
                         ' '.join(hits), ' '.join(miss), verdict, triage))

    with io.open(OUT_TSV, 'w', encoding='utf-8', newline='\n') as f:
        f.write('label\trow\tcol\tpdf_pages\ttokens\thits\tmisses\tverdict\ttriage\n')
        for r in out_rows:
            f.write('\t'.join(r) + '\n')

    ok = sum(1 for r in out_rows if r[7].startswith('全部命中'))
    part = sum(1 for r in out_rows if r[7] == '部分命中')
    none = sum(1 for r in out_rows if r[7] == '全部未命中')
    nopage = sum(1 for r in out_rows if r[7] == '无源页可扫')

    md = ['# 表格数值的页面 OCR 普查（上下册，独立于内嵌文字层）', '',
          '起因：上册源 PDF 的内嵌文字层是失真的出版方 OCR——它把 820 误识为 520，'
          '已经导致改编本表 6-10 的过氧谱带错误（见 `sources/logs/fixes_t1.tsv`）。'
          '因此含数值的表格单元格不应只对文字层负责。', '',
          '本文件由 `tools/ocr_digit_audit.py` 生成：把每个含数值单元格所引源页'
          '（上册：PDF = 书内 + 19；下册：PDF = 书内 − 章节偏移，ch08 508／ch09 509／'
          'ch10 511／ch11 512／ch12 514）以 300 dpi 渲图、RapidOCR 独立识别，'
          '再逐格在整页 OCR 文本里找回该格的每个数值 token。', '',
          '口径说明：命中=该数值在整页 OCR 中出现过（不要求同一行）；'
          '「未命中」只表示**需要人工看一眼**，不等于错——上下标、坐标轴刻度、'
          '跨页表述都会造成未命中。', '',
          '| 结论 | 格数 |', '|---|---|',
          '| 全部命中 | %d |' % ok,
          '| 其中靠汉字数字或去小数点命中 | %d |'
          % (sum(1 for r in out_rows if r[7] in ('全部命中（汉字数字）', '全部命中（去小数点）'))),
          '| 部分命中 | %d |' % part,
          '| 全部未命中 | %d |' % none,
          '| 无源页可扫 | %d |' % nopage,
          '| **合计（含数值单元格）** | **%d** |' % len(out_rows), '',
          '## 需要人工看一眼的格（部分命中 / 全部未命中）', '']

    problems = [r for r in out_rows if r[7] in ('部分命中', '全部未命中')]
    if problems:
        md += ['| 表 | 行 | 列 | 改编本内容 | 源 PDF 页 | 未命中 token | 结论 | 分诊 |',
               '|---|---|---|---|---|---|---|---|']
        for rec in problems[:120]:
            label, row, col, pages, toks, hits, miss, verdict = rec[:8]
            triage = rec[8] if len(rec) > 8 else ''
            content = next((a for (l, r, c, a, _p, _t, _n) in rows
                            if (l, r, c) == (label, row, col)), '')
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s |' %
                      (label, row, col, content[:40], pages, miss, verdict,
                       triage.replace('|', '/')))
    else:
        md.append('（无）')
    md.append('')

    groups = {}
    for rec in out_rows:
        triage = rec[8] if len(rec) > 8 else ''
        if not triage:
            continue
        groups.setdefault(triage.split('：', 1)[0], []).append(rec)

    md += ['## 人工分诊（按类别聚合，与 `TRIAGE` 表一一对应）', '']
    order = ['误报', '改编补充', '单位换算', '舍入', 'OCR 漏识', '待人工']
    for cls in order + [c for c in groups if c not in order]:
        if cls not in groups:
            continue
        md += ['### %s（%d 格）' % (cls, len(groups[cls])), '']
        seen = set()
        for rec in groups[cls]:
            line = '- `%s` / %s：%s' % (rec[0], rec[1], rec[8].split('：', 1)[-1])
            if line in seen:
                continue
            seen.add(line)
            md.append(line)
        md.append('')

    md += ['## 已由本审计促成的修正', '',
           '- 表 6-10 过氧谱带 520—550 → 820—842（源页 OCR 只出现 820/842，文字层 520 无据）：'
           '见 `sources/logs/fixes_t1.tsv`。',
           '- 表 6-7 MoO3/γ-Al2O3 一行「约 910（疑 901）、约 2700」统一为 910 / 2720。',
           '- 表 2-10 束斑球差校正器 0.24 nm → 0.20 nm（源页 2 Å→1.3 Å）。', '']

    io.open(OUT_MD, 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')

    print('ok=%d partial=%d none=%d nopage=%d' % (ok, part, none, nopage))
    print('wrote', OUT_MD)
    return 0


if __name__ == '__main__':
    sys.exit(main())
