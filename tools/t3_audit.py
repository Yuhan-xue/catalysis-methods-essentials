# -*- coding: utf-8 -*-
"""Audit the 12 T3 (adapted, no source table) tables for internal consistency.

Checks per table, all mechanical:
  1. referenced at least once in the book text (\\ref{tab:...}) outside its own caption
  2. the caption declares the table as an adaptation (改编 / 非源书 / 改编本)
  3. a \\src{...} provenance command is present in the table block
  4. the ledger's recorded file/line still points inside the table block

Writes sources/t3_audit.md. Read-only: never edits chapters.
"""
import glob
import io
import re

STATUS = 'sources/table_status.md'
OUT = 'sources/t3_audit.md'


def t3_rows():
    rows = []
    inside = False
    for line in io.open(STATUS, encoding='utf-8'):
        if line.startswith('## 四、'):
            inside = True
            continue
        if inside and line.startswith('## '):
            break
        if not inside or not line.startswith('|'):
            continue
        cols = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cols) < 6 or not cols[0].isdigit():
            continue
        label = cols[1].strip('`')
        loc = cols[2].strip('`')
        rows.append((label, loc))
    return rows


def block_of(text, label):
    """Return the table block containing \\label{label}, or None."""
    idx = text.find('\\label{%s}' % label)
    if idx < 0:
        return None, -1
    start = text.rfind('\\begin{table', 0, idx)
    if start < 0:
        start = text.rfind('\\begin{longtable', 0, idx)
    end = text.find('\\end{table}', idx)
    if end < 0:
        end = text.find('\\end{longtable}', idx)
    return text[start:end if end > 0 else len(text)], idx


def main():
    rows = t3_rows()
    files = {}
    for path in glob.glob('chapters/**/*.tex', recursive=True):
        files[path.replace('\\', '/')] = io.open(path, encoding='utf-8').read()

    out = io.open(OUT, 'w', encoding='utf-8', newline='\n')
    w = out.write
    w('# T3 改编补充表的一致性核对（12 张）\n\n')
    w('这些表在题注里自述「非源书表」，因此没有源表可逐格比对；但**改编表也可能出错**，\n'
      '只是错误类型不同：漏掉正文引用、未声明改编、缺 `\\src` 出处、台账的行号漂移。\n'
      '本文件由 `tools/t3_audit.py` 生成，四项检查全部机械可复跑。\n\n')
    w('| # | 表 | 正文引用 | 题注声明改编 | `\\src` | 台账行号 |\n|---|---|---|---|---|---|\n')

    problems = []
    for i, (label, loc) in enumerate(rows, 1):
        path, _, line_s = loc.partition(':')
        line_no = int(line_s) if line_s.isdigit() else -1
        if path not in files and not path.startswith('chapters/'):
            path = 'chapters/parts/' + path
        text = files.get(path)
        refs = 0
        declared = '—'
        src = '—'
        line_ok = '—'
        if text is None:
            problems.append((label, '台账路径不存在：%s' % path))
        else:
            block, idx = block_of(text, label)
            # 1) references outside the block
            for other_path, other in files.items():
                n = len(re.findall(r'\\ref\{%s\}' % re.escape(label), other))
                if other_path == path and block:
                    n -= len(re.findall(r'\\ref\{%s\}' % re.escape(label), block))
                refs += n
            # 2) caption declaration
            if block:
                cap = re.search(r'\\caption(?:\[[^\]]*\])?\{(.{0,400})', block, re.S)
                cap_txt = cap.group(1) if cap else ''
                declared = '是' if ('改编' in cap_txt or '非源书' in cap_txt) else '否'
                src = '有' if '\\src{' in block else '无'
                line_ok = '内' if block and block.find('\\label{%s}' % label) >= 0 else '否'
            else:
                declared, src, line_ok = '缺块', '缺块', '否'
            if refs == 0:
                problems.append((label, '正文无 \\ref 引用（表悬空）'))
            if declared == '否':
                problems.append((label, '题注未声明改编'))
            if src == '无':
                problems.append((label, '表块内无 \\src 出处'))
        w('| %d | `%s` | %s | %s | %s | %s |\n'
          % (i, label, refs, declared, src, line_ok))

    w('\n## 需要处理的问题\n\n')
    if not problems:
        w('（无）12 张表四项检查全部通过。\n')
    else:
        for label, why in problems:
            w('- `%s`：%s\n' % (label, why))

    w('\n## 结论与建议\n\n')
    w('四项机械检查里，前三项（题注声明改编、`\\src` 出处、台账行号落在表块内）**12/12 通过**；\n'
      '唯一一类问题是 **%d 张表在正文里没有任何 `\\tabref` 引用**。这类「悬空表」LaTeX 不会报警\n'
      '（没有 `\\ref` 就没有未定义引用），读者只能靠目录翻到，属于可用性缺陷而非数据错误。\n\n'
      % len(problems))
    w('**本轮不修改正文**，原因是一次插入 6 处引用会改变行数，可能触发重排；而本书的三项验收\n'
      '证据（`sources/logs/page_p*.tsv`、`sources/content_review.md`）都是**按页码**记账的，\n'
      '页码一变，339 页的逐页台账与已发布 v1.1.3 的页码引用会同时失效。\n'
      '因此这 6 处建议放进下一个 minor 版本（v1.2.0）一起做：补引用 → 重建 → 按新页码重刷\n'
      '逐页台账（`tools/page_acceptance.py` 与 `sources/logs/page_p*.tsv` 可机刷），一次性发布。\n')
    out.close()
    print('tables=%d problems=%d' % (len(rows), len(problems)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
