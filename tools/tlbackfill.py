# -*- coding: utf-8 -*-
"""Regenerate sources/textlayer_backfill.md.

A cell counts as a residual only while it has no second evidence channel. Two
channels are recognised:
  * numeric cells whose values were found again by the page-image OCR run
    (build/ocr_matches.tsv, verdict `OCR 命中全部数值`),
  * qualitative cells verified against page images by hand
    (UPGRADED below; each entry is documented in sources/evidence_upgrade.md).
"""
import glob
import io
import os

CELLS = 'sources/logs/cells_*.tsv'
MATCHES = 'build/ocr_matches.tsv'
OUT = 'sources/textlayer_backfill.md'

UPGRADED = {
    ('tab:ch07c-criteria', '四、毒化／组合'): '页面图像复核：p.499「盐酸和乙酸预处理…浓度减小到十分之一，但活性却没有」',
    ('tab:modes', '漫反射 DRIFT'): '页面图像复核：p.427 印 Kubelka—Munk 函数式（原「文字层未检索到」已删）',
    ('tab:modes', '衰减全反射 ATR'): '页面图像复核：p.431—432 讲全反射、临界角与穿透深度，未用「倏逝波」一词',
    ('tab:modes', '红外合频 SFG'): '页面图像复核：p.434「非线性光学过程的产生要求介质是非中心对称的」',
    ('tab:modes', '时间分辨 TR-IR'): '页面图像复核：p.439 用「Pump-Probe」原文，中文「泵浦—探测」为改编',
}


def ocr_verdicts():
    got = {}
    if not os.path.exists(MATCHES):
        return got
    for line in io.open(MATCHES, encoding='utf-8'):
        cols = line.rstrip('\n').split('\t')
        if len(cols) < 8 or cols[3] == 'pdf_pages':
            continue
        got[(cols[0], cols[1], cols[2])] = (cols[4], cols[7])
    return got


def main():
    verdicts = ocr_verdicts()
    rows = []
    for path in sorted(glob.glob(CELLS)):
        for line in io.open(path, encoding='utf-8'):
            cols = line.rstrip('\n').split('\t')
            if len(cols) < 7 or '文字层' not in cols[6]:
                continue
            rows.append(cols)

    dual, imaged, todo = [], [], []
    for cols in rows:
        label, row, col = cols[0], cols[1], cols[2]
        toks, verdict = verdicts.get((label, row, col), ('', ''))
        if verdict == 'OCR 命中全部数值':
            dual.append(cols)
        elif (label, row) in UPGRADED:
            imaged.append(cols)
        else:
            todo.append(cols)

    tables = sorted({c[0] for c in rows})
    out = io.open(OUT, 'w', encoding='utf-8', newline='\n')
    w = out.write
    w('# 台账残余：以源文字层为证据的表格单元格\n\n')
    w('本文件由 `tools/tlbackfill.py` 生成，列出 cells 备注仍写「文字层」的单元格，'
      '并按**第二条证据通道**分三档。\n\n')
    w('| 档位 | 格数 | 含义 |\n|---|---|---|\n')
    w('| 已数值双证 | %d | 页面图像 OCR 独立找回该格全部数值（见 `sources/ocr_backfill.md`） |\n' % len(dual))
    w('| 已图像复核（定性） | %d | 无数值可比，本轮逐页读图核对原句（见 `sources/evidence_upgrade.md`） |\n' % len(imaged))
    w('| **仍需人工** | **%d** | 尚无第二条证据通道 |\n\n' % len(todo))
    w('合计 **%d** 格，涉及 **%d** 张表：%s。\n\n'
      % (len(rows), len(tables), '、'.join('`%s`' % t for t in tables)))

    for title, group in (('仍需人工（若有）', todo), ('已图像复核（定性）', imaged),
                         ('已数值双证', dual)):
        w('## %s\n\n' % title)
        if not group:
            w('（无）\n\n')
            continue
        w('| 表 | 行 | 列 | 改编本内容 | 判定 | 证据 |\n|---|---|---|---|---|---|\n')
        for cols in group:
            ev = UPGRADED.get((cols[0], cols[1]), '页面 OCR 命中全部数值')
            w('| `%s` | %s | %s | %s | %s | %s |\n'
              % (cols[0], cols[1], cols[2], cols[3][:40].replace('|', '/'), cols[5], ev))
        w('\n')
    out.close()
    print('dual=%d imaged=%d todo=%d' % (len(dual), len(imaged), len(todo)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
