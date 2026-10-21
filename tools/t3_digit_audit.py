# -*- coding: utf-8 -*-
"""Digit audit for the 12 T3 (adapted) tables.

These tables have no source table, but several of their numbers do come from the
source text. This script extracts the numeric tokens from each table block, OCRs
the pages the table's \\src cites, and reports how many tokens are found again.

Reuses the helpers of tools/ocr_digit_audit.py (token parsing, page resolution,
RapidOCR with build/_ocr cache).

Writes sources/t3_digit_audit.md.
"""
import importlib.util
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

spec = importlib.util.spec_from_file_location(
    'oda', os.path.join(ROOT, 'tools', 'ocr_digit_audit.py'))
oda = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oda)

T3 = [
    ('chapters/ch00-intro.tex', 'tab:selector'),
    ('chapters/ch13-synthesis.tex', 'tab:evidence-level'),
    ('chapters/ch13-synthesis.tex', 'tab:matrix'),
    ('chapters/parts/ch01-c.tex', 'tab:ch01c-density'),
    ('chapters/parts/ch02-a.tex', 'tab:ring-index'),
    ('chapters/parts/ch02-b.tex', 'tab:ch02b-smsi'),
    ('chapters/parts/ch03-b.tex', 'tab:ch03b-hyphenated'),
    ('chapters/parts/ch04-a.tex', 'tab:extinction-ch04'),
    ('chapters/parts/ch04-c.tex', 'tab:ch04c-scherrer'),
    ('chapters/parts/ch09-d.tex', 'tab:ch09-problems'),
    ('chapters/parts/ch10-b.tex', 'tab:ch10-window'),
    ('chapters/parts/ch10-b.tex', 'tab:ch10-resid-diag'),
]
OUT = os.path.join(ROOT, 'sources', 't3_digit_audit.md')


def block(text, label):
    idx = text.find('\\label{%s}' % label)
    if idx < 0:
        return ''
    start = text.rfind('\\begin{table', 0, idx)
    end = text.find('\\end{table', idx)
    return text[start:end if end > 0 else len(text)]


BOOK = re.compile(r'(?:书内\s*p?\.?|(?<![\w.])p\.)\s*(\d{2,3})'
                  r'(?:\s*[—\-–~]\s*(\d{2,3}))?')
PDFP = re.compile(r'PDF\s*p?\.?\s*(\d{2,3})(?:\s*[—\-–~]\s*(\d{2,3}))?')


def resolve_pages(cite, chapter):
    """Like oda.pages_for but accepts 2- or 3-digit book pages."""
    out = []
    down = chapter is not None and chapter >= 8
    off = oda.DOWN_OFFSET.get(chapter or 0)
    for m in BOOK.finditer(cite):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        for book in range(a, min(b, a + 6) + 1):
            if down and off:
                pdf = book - off
                if pdf > 0 and ('down', pdf) not in out:
                    out.append(('down', pdf))
            elif not down and book <= 500:
                if ('up', book + 19) not in out:
                    out.append(('up', book + 19))
    if not down:
        for m in PDFP.finditer(cite):
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else a
            for pdf in range(a, min(b, a + 6) + 1):
                if ('up', pdf) not in out:
                    out.append(('up', pdf))
    return out


def main():
    import pymupdf
    from rapidocr_onnxruntime import RapidOCR

    ocr = RapidOCR()
    chapters = oda.load_chapters()
    chapters['tab:selector'] = 0
    chapters['tab:evidence-level'] = 13
    chapters['tab:matrix'] = 13
    docs = {
        'up': pymupdf.open(oda.SRC_UP),
        'down': pymupdf.open(oda.SRC_DOWN),
    }

    out = io.open(OUT, 'w', encoding='utf-8', newline='\n')
    w = out.write
    w('# T3 改编补充表的数值回查（12 张）\n\n')
    w('这些表在题注里自述「非源书表」，所以没有源表可逐格比对；但不少数值其实取自原书正文。\n'
      '本文件由 `tools/t3_digit_audit.py` 生成：抽出表块内的数值 token，把该表 `\\src` 指到的源页\n'
      '渲图后 OCR，逐 token 回找。判词只有三种：**命中**（OCR 文本里能找到）、\n'
      '**未命中**（可能属改编设定，也可能 OCR 漏识）、**无源页**（该表没有可定位的书内页）。\n\n')
    w('| # | 表 | 数值 token | 源页 | 命中 | 未命中 |\n|---|---|---|---|---|---|\n')

    detail = []
    for i, (path, label) in enumerate(T3, 1):
        full = os.path.join(ROOT, path)
        text = io.open(full, encoding='utf-8').read()
        blk_raw = block(text, label)
        src = re.search(r'\\src\{(.{0,400})', blk_raw, re.S)
        cite = re.sub(r'\s+', ' ', src.group(1)) if src else ''
        # page citations inside the table body are not data: drop them first,
        # and strip TeX comments (the column-width note carries mm values)
        blk = re.sub(r'(?<!\\)%.*', ' ', blk_raw)
        blk = re.sub(r'(?:书内|PDF)\s*p?\.?\s*\d+(?:\s*[—\-–~]\s*\d+)?', ' ', blk)
        blk = re.sub(r'(?<![\w.])p\.\s*\d+(?:\s*[—\-–~]\s*\d+)?', ' ', blk)
        tks = oda.tokens(blk) if blk else []
        pages = resolve_pages(cite, chapters.get(label))
        ocr_text = ''
        for vol, pdf in pages:
            try:
                ocr_text += '\n' + oda.ocr_page(docs[vol], vol, pdf, ocr)
            except Exception as exc:  # noqa: BLE001
                ocr_text += '\n'
                print('ocr fail %s %s: %r' % (vol, pdf, exc))
        hit, miss = [], []
        for t in tks:
            if not ocr_text:
                break
            if re.search(oda.token_pattern(t), oda.norm(ocr_text)):
                hit.append(t)
            else:
                miss.append(t)
        w('| %d | `%s` | %d | %s | %d | %d |\n'
          % (i, label, len(tks),
             '%s…' % (cite[:34] + '…' if len(cite) > 34 else cite) if cite else '（无 \\src）',
             len(hit), len(miss)))
        detail.append((label, tks, hit, miss, pages))

    w('\n## 未命中的 token（供人工分诊）\n\n')
    any_miss = False
    for label, tks, hit, miss, pages in detail:
        if not miss:
            continue
        any_miss = True
        w('- `%s`：%s\n' % (label, '、'.join(miss[:20])))
    if not any_miss:
        w('（无）\n')

    w('\n## 人工分诊结论\n\n')
    w('- **计算或模型生成，预期不命中**：`tab:ring-index`（d/n 由 λ 与 θ 算出）、\n'
      '  `tab:ch04c-scherrer`（由 λ、β、θ 换算的示例值）、`tab:ch10-window`（题注已自述为\n'
      '  按 L-H 模型生成的教学设定数据）。这三张表的未命中格不构成证据缺口。\n')
    w('- **表内编号噪声**：`tab:selector` 的 14 个 token 全部是 `\\chapref` 的章号与 §1.1.2 的节号，\n'
      '  该表是纯定性选型矩阵、本就不含数据值；`tab:ch02b-smsi` 的 02 等同理。\n')
    w('- **仍需人工确认**：`tab:ring-index`、`tab:ch01c-density` 的少量换算值（如 0.71、3.0、1.6），\n'
      '  它们由公式算出而非照抄，属「改写口径」而非「抄错数字」；如要定论需逐条追到具体正文。\n')
    w('- **完全无源页**：`tab:evidence-level`（0 个数值）、`tab:matrix`（归纳自本书章节，\n'
      '  不引外部源页）、`tab:ch09-problems`（题注自述本节无对应 OCR 文本）。\n')

    w('\n## 口径说明\n\n')
    w('- 「未命中」不等于错误：改编表里有大量教学设定值与换算值，本来就不该出现在源书里；\n'
      '  真正需要人工看的，是**声称取自原文却没找到**的数值，这需要逐 token 对照语境，本脚本不做自动判定。\n')
    w('- 源页定位沿用 `tools/ocr_digit_audit.py`：上册 书内 = PDF − 19；下册按章偏移\n'
      '  （ch08 +508、ch09 +509、ch10 +511、ch11 +512、ch12 +514）。OCR 缓存在 `build/_ocr/`。\n')
    out.close()
    print('tables=%d' % len(T3))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
