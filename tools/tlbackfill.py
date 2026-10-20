# -*- coding: utf-8 -*-
"""Generate sources/textlayer_backfill.md (residual evidence ledger).

Run: python tools/tlbackfill.py
"""
import glob
import io

FIXED_PAGES = {
    'tab:modes': '书内 p.417—441 / PDF 436—460（§7.1.1—§7.1.7）',
    'tab:raman-bands-c': '书内 p.365—367 / PDF 384—386（§6.3.6 后段）',
}

rows = []
for f in sorted(glob.glob('sources/logs/cells_*.tsv')):
    for ln in io.open(f, encoding='utf-8').read().split('\n'):
        if not ln.strip() or '文字层' not in ln:
            continue
        c = ln.split('\t')
        while len(c) < 7:
            c.append('')
        rows.append((c[0], c[1], c[2], c[3], c[4], c[5], c[6]))

by_label = {}
for r in rows:
    by_label.setdefault(r[0], []).append(r)

out = io.open('sources/textlayer_backfill.md', 'w', encoding='utf-8', newline='\n')
w = out.write
w('# 台账残余：以源文字层为证据的表格单元格\n\n')
w('本文件由 `tools/tlbackfill.py` 从 `sources/logs/cells_*.tsv` 提取生成，列出全部'
  '「证据为源 PDF 文字层、尚未以源页页面图像复核」的单元格。\n')
w('三项验收（`sources/acceptance_report.md`）中表项已全部终判；本清单是**证据等级**的残余，'
  '不是未核项：这些格的数据来源与比对结论已写入 cells 文件，只是复核媒介为文字层。\n\n')
w('提取口径：cells 文件备注列含「文字层」。合计 **%d** 格，涉及 **%d** 张表。\n\n'
  % (len(rows), len(by_label)))
w('## 汇总\n\n')
w('| 表 | 格数 | 源页 |\n|---|---|---|\n')
for label, rs in sorted(by_label.items()):
    pages = FIXED_PAGES.get(label)
    if not pages:
        vals = sorted({r[4] for r in rs if r[4] not in ('同上', '')})
        pages = '；'.join(vals[:3]) if vals else '见各行备注'
    w('| `%s` | %d | %s |\n' % (label, len(rs), pages))
w('\n## 逐格清单\n\n')
for label, rs in sorted(by_label.items()):
    w('### `%s`\n\n' % label)
    w('| 行 | 列 | 改编本内容 | 源页 | 判定 | 备注（节选） |\n|---|---|---|---|---|---|\n')
    for r in rs:
        art = r[3].replace('|', '\\|')
        src = (r[4] if r[4] not in ('同上', '') else '见备注').replace('|', '\\|')
        note = r[6].replace('|', '\\|')[:90]
        w('| %s | %s | %s | %s | %s | %s |\n' % (r[1], r[2], art, src, r[5], note))
    w('\n')

w('## 若要把证据统一为页面图像\n\n')
w('对每张表按其「源页」列渲图后逐格比对，改写对应 cells 行的备注（去掉「文字层」字样'
  '并注明图像文件名），再跑：\n\n')
w('```bash\npython tools/review_ledger.py tables\npython tools/verify_acceptance.py\n```\n')
w('\n渲染命令：`python tools/vpage.py up <PDF页> build/x.png --dpi 200`'
  '（上册 书内 = PDF − 19；下册按章 +508/509/511/512/514，见页眉核对）。\n')
out.close()
print('ok rows=%d labels=%d' % (len(rows), len(by_label)))
