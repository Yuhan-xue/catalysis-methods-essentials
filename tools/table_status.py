# -*- coding: utf-8 -*-
r"""汇总 85 张表的诚实核对状态，输出 sources/table_status.md。

输入（全部为磁盘上可核验的事实）：
  1. sources/figure_table_list.csv        表清单（env in {table,longtable}）
  2. sources/table_class.tsv              分类（A_SOURCE/B_NOTED/C_ADAPT/D_PENDING），
                                         由 build/_tbl_class.txt 一次性导出并入库
  3. sources/table_pixel_verify.md        既有逐格读图台账（14 张真实来源表）
  4. sources/table_cells.tsv              2026-10-19 起的逐单元格核对判决（第三项验收）
  5. chapters/parts/*.tex                 表后就地 \emph{核对说明}

判定优先级（高→低）：
  T1   既有逐格读图：table_pixel_verify.md 有该表结论
  T1c  本次逐单元格核对：table_cells.tsv 给出终判
  T2   就地核对说明且注明「已对照原页面图像」（历史层级，只到说明级）
  T3   改编补充：分类为 C_ADAPT（题注/\\src 自述非源书表）且未逐格核
  T4   未核对页面图像：其余

复跑：python tools/table_status.py
"""
import io
import os
import re
import csv
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, 'sources', 'figure_table_list.csv')
CLASS_TSV = os.path.join(ROOT, 'sources', 'table_class.tsv')
CLASS_PATH = os.path.join(ROOT, 'build', '_tbl_class.txt')  # legacy fallback
PIXEL_PATH = os.path.join(ROOT, 'sources', 'table_pixel_verify.md')
CELLS_TSV = os.path.join(ROOT, 'sources', 'table_cells.tsv')
OUT_PATH = os.path.join(ROOT, 'sources', 'table_status.md')

VERDICTS = ('已核对一致', '已核对并修正', '形式一致但符号不同', '原书自身问题', '改编补充', '未覆盖')
CELL_DONE = {'逐格一致', '逐格修正', '逐格差异·原书自身', '改编补充自洽'}
PAGE_RE = re.compile(r'书内\s*p?\.?\s*(\d+)\s*[—\-–~]\s*(\d+)')
PAGE_RE1 = re.compile(r'书内\s*p?\.?\s*(\d+)')


def head_date():
    """HEAD 提交日（YYYY-MM-DD），仅用于「本文件生成于」这类会随提交变化的说明。

    注意：不要拿它标注「某一轮核对完成于哪天」——那是事实，跟着提交走会让
    每次提交都把台账标题改一遍，复跑字节一致就永远不可能成立。
    """
    try:
        d = subprocess.check_output(['git', 'log', '-1', '--format=%cs'],
                                    cwd=ROOT).decode('utf-8', 'replace').strip()
        if re.match(r'^\d{4}-\d{2}-\d{2}$', d):
            return d
    except Exception:
        pass
    import datetime
    return datetime.date.today().isoformat()


# 逐单元格核对这一轮的实际完成日（事实常量）。
GEN_DATE = '2026-10-21'


def read_text(path):
    with io.open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


# ---------- 1. 表清单 ----------
tables = []
with io.open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        if (r.get('env') or '').strip() in ('table', 'longtable'):
            tables.append(r)
print('tables=%d' % len(tables))

# ---------- 2. 分类 ----------
cls = {}
if os.path.exists(CLASS_TSV):
    with io.open(CLASS_TSV, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            lab = (r.get('label') or '').strip()
            if lab.startswith('tab:'):
                cls[lab] = (r.get('class') or '').strip()
else:
    cur = None
    for line in read_text(CLASS_PATH).splitlines():
        m = re.match(r'^====\s+(\S+)\s+====$', line.strip())
        if m:
            cur = m.group(1)
            continue
        m = re.match(r'^(tab:\S+)\s+(\S+)\s+L(\d+)-(\d+)', line.strip())
        if m and cur:
            cls[m.group(1)] = cur
print('class=%d' % len(cls))

# ---------- 3. 既有逐格读图台账 ----------
pixel_txt = read_text(PIXEL_PATH)
pixel_verdict = {}
sec = None
for line in pixel_txt.splitlines():
    m = re.match(r'^##\s+\d+\.\s+(.*)$', line)
    if m:
        sec = re.findall(r'tab:[A-Za-z0-9\-]+', m.group(1))
        continue
    if sec:
        for v in VERDICTS:
            if v in line:
                for lab in sec:
                    if lab.startswith('tab:') and lab not in pixel_verdict:
                        pixel_verdict[lab] = v
                break
print('pixel_verdict=%d' % len(pixel_verdict))

# ---------- 3b. 本次逐单元格核对 ----------
cells = {}
if os.path.exists(CELLS_TSV):
    with io.open(CELLS_TSV, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f, delimiter='\t'):
            lab = (r.get('label') or '').strip()
            if lab.startswith('tab:'):
                cells[lab] = r
print('cells_verdict=%d' % len(cells))

# ---------- 4. 就地核对说明 ----------
filecache = {}


def shard_lines(relpath):
    if relpath not in filecache:
        p = os.path.join(ROOT, relpath.replace('/', os.sep))
        filecache[relpath] = read_text(p).splitlines() if os.path.exists(p) else None
    return filecache[relpath]


BEGIN_RE = re.compile(r'^\s*\\begin\{(table|longtable|sidewaystable)\*?\}')
END_RE = re.compile(r'^\s*\\end\{(table|longtable|sidewaystable)\*?\}')


def _env_bounds(lines, idx):
    start = idx
    for k in range(idx, max(-1, idx - 160), -1):
        if BEGIN_RE.match(lines[k]):
            start = k
            break
    for k in range(idx, min(len(lines), idx + 200)):
        if END_RE.match(lines[k]):
            return start, k
    return idx, idx


def local_note(relpath, label):
    lines = shard_lines(relpath)
    if lines is None:
        return None
    idx = None
    for i, ln in enumerate(lines):
        if ('\\label{%s}' % label) in ln:
            idx = i
            break
    if idx is None:
        return None
    start, end = _env_bounds(lines, idx)
    lo = min(start, idx)
    hi = max(end + 1, idx + 61)
    buf = []
    for pat in ('\\emph{核对说明}', '核对说明'):
        for j in range(lo, min(hi, len(lines))):
            if pat in lines[j]:
                buf = [lines[j]]
                for k in range(j + 1, min(j + 14, len(lines))):
                    nxt = lines[k]
                    if '核对说明' in nxt or re.match(r'^\\(sub)*section', nxt) or \
                       nxt.startswith('\\begin{table') or nxt.startswith('\\begin{longtable'):
                        break
                    buf.append(nxt)
                break
        if buf:
            break
    if not buf:
        return None
    txt = ' '.join(x.strip() for x in buf)
    txt = re.sub(r'\s+', ' ', txt)
    return txt


def pages_of(text):
    m = PAGE_RE.search(text)
    if m:
        return '%s—%s' % (m.group(1), m.group(2))
    m = PAGE_RE1.search(text)
    return m.group(1) if m else ''


# ---------- 5. 归组 ----------
rows = []
for r in tables:
    lab = r['label'].strip()
    f = r['file'].strip()
    line = (r['line'] or '').strip()
    c = cls.get(lab, '?')
    note = local_note(f, lab)
    has_img_note = bool(note) and ('已对照原页面图像' in note)
    pg = pages_of(note) if note else ''
    cell = cells.get(lab)
    cell_ok = bool(cell) and (cell.get('verdict') or '').strip() in CELL_DONE
    if lab in pixel_verdict:
        tier, verdict, ev = 'T1', pixel_verdict[lab], 'sources/table_pixel_verify.md'
    elif cell_ok:
        tier = 'T1c'
        verdict = cell['verdict'].strip()
        n_cells = (cell.get('cells_checked') or '').strip()
        n_mis = (cell.get('mismatches') or '').strip()
        ev = 'sources/table_cells.md（%s 格/%s 不一致）' % (n_cells or '—', n_mis or '—')
        if cell.get('src_pages'):
            pg = cell['src_pages'].strip()
    elif has_img_note:
        tier, verdict, ev = 'T2', '已核对并修正/一致（就地核对说明）', '就地核对说明（已对照原页面图像）'
    elif c == 'C_ADAPT':
        tier, verdict, ev = 'T3', '改编补充', '题注/\\src 自述非源书表'
    else:
        tier, verdict, ev = 'T4', '未核对页面图像', '—'
    rows.append(dict(label=lab, file=f, line=line, cls=c, tier=tier, verdict=verdict,
                     ev=ev, pg=pg, note=note or ''))

order = {'T1': 0, 'T1c': 1, 'T2': 2, 'T3': 3, 'T4': 4}
rows.sort(key=lambda x: (order[x['tier']], x['file'], int(x['line'] or 0)))

cnt = {}
for x in rows:
    cnt[x['tier']] = cnt.get(x['tier'], 0) + 1
print('T1=%d T1c=%d T2=%d T3=%d T4=%d' % (
    cnt.get('T1', 0), cnt.get('T1c', 0), cnt.get('T2', 0), cnt.get('T3', 0), cnt.get('T4', 0)))

HEAD = {
    'T1': '一、既有逐格读图核对（%d 张）',
    'T1c': '二、' + GEN_DATE + ' 逐单元格核对（%d 张）',
    'T2': '三、仅就地核对说明，未逐格比对（%d 张）',
    'T3': '四、改编补充：自述非源书表且未逐格核（%d 张）',
    'T4': '五、未核对页面图像（%d 张）',
}

out = []
out.append('# 85 张表的核对状态台账（`sources/table_status.md`）')
out.append('')
out.append('本文件由 `tools/table_status.py` 从磁盘可核验事实生成（脚本与输入均已入库，复跑即可重排）。')
out.append('用于逐表回答一个问题：**这张表的内容到底有没有对照过原页面图像、有没有逐格比对？**')
out.append('判定只认四类证据：`sources/table_pixel_verify.md` 的逐格读图段落、')
out.append('`sources/table_cells.tsv` / `sources/table_cells.md` 的逐单元格核对判决、')
out.append('分片文件内注明「已对照原页面图像」的就地 `\\emph{核对说明}`、')
out.append('以及题注/`\\src` 自述「非源书表格」的改编声明。')
out.append('**没有证据的表一律记「未核对页面图像」，不因结构门禁通过或 OCR 文本命中而升级。**')
out.append('')
out.append('表总数 = %d（`env` 为 `table`/`longtable`；figure 行不计入）。' % len(rows))
out.append('')
out.append('| 层级 | 含义 | 张数 |')
out.append('| --- | --- | --- |')
out.append('| T1 | 既有逐格读图核对（`table_pixel_verify.md` 有结论） | %d |' % cnt.get('T1', 0))
out.append('| T1c | %s 逐单元格核对（`table_cells.tsv` 有终判） | %d |' % (GEN_DATE, cnt.get('T1c', 0)))
out.append('| T2 | 仅就地核对说明，注明已对照原页面图像，未逐格比对 | %d |' % cnt.get('T2', 0))
out.append('| T3 | 改编补充（自述非源书表，尚未逐格核内部自洽） | %d |' % cnt.get('T3', 0))
out.append('| T4 | 未核对页面图像 | %d |' % cnt.get('T4', 0))
out.append('')
out.append('> 口径说明：T2 只说明该分片就地留下了「已对照原页面图像」的说明，')
out.append('> 不表示表内每一格都被逐格比对过；T1 与 T1c 才是逐格结论。')
out.append('> T1c 的表若在 `table_cells.tsv` 里判为 `逐格修正`，说明核对后已提出修正；')
out.append('> 判决词表见 `sources/review_protocol.md` §3.3。')
out.append('')
for t in ('T1', 'T1c', 'T2', 'T3', 'T4'):
    sub = [x for x in rows if x['tier'] == t]
    if not sub:
        continue
    out.append('## ' + (HEAD[t] % len(sub)))
    out.append('')
    out.append('| # | 表 | 位置 | 书内页 | 结论 | 证据 |')
    out.append('| --- | --- | --- | --- | --- | --- |')
    for i, x in enumerate(sub, 1):
        loc = '`%s:%s`' % (x['file'].replace('chapters/parts/', ''), x['line'])
        out.append('| %d | `%s` | %s | %s | %s | %s |' % (
            i, x['label'], loc, x['pg'] or '—', x['verdict'], x['ev']))
    out.append('')
    notes = [x for x in sub if x['note'] and x['tier'] == 'T2']
    if notes:
        out.append('<details><summary>就地核对说明摘录</summary>')
        out.append('')
        for x in notes[:40]:
            out.append('- `%s`：%s' % (x['label'], x['note'][:400]))
        out.append('')
        out.append('</details>')
        out.append('')

out.append('## 附：本台账不主张的东西')
out.append('')
out.append('- 不主张 T4 的表「数据错误」——只主张**尚未读图**，对错未知。')
out.append('- 不主张结构门禁（`tools/check_src.py`）或 OCR 文本层命中等于内容核对。')
out.append('- 不主张 T3 的改编表内容正确：没有源表可逐格比对，只能核内部自洽（核过会升到 T1c）。')
out.append('- 不主张 T1c 的 `逐格一致` 超出「与原书印刷内容一致」——不重做数据解释。')
out.append('')

with io.open(OUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(out) + '\n')
print('OK wrote %s lines=%d' % (OUT_PATH, len(out)))
