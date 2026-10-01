# -*- coding: utf-8 -*-
"""图 5-1（TPD 双面板图，ch05-a.tex）渲染核验探针。

背景（R5-U01）：本仓库的维护会话没有视觉能力，图的「看起来」无法用肉眼检查。
本探针从 PDF 的矢量图层（绘图算子）与文字层核验四件事，全部在 PDF 点坐标系内完成：

  P1 图例分离：两个面板的图例（文字 + 线段样本）必须各自成簇、不得跨面板相撞；
     每簇的「线段样本 ↔ 文字」必须一一配对（同一行、水平紧邻），行与行按基线
     分开（R5-U01 的缺陷正是左图例 β=20 的文字压到右图例 n=1 的红色线段上）。
  P2 只有一套倍率：图上不得出现 pgfplots 自动倍率「·10⁻²」之类的符号
     （U+22C5 等）。纵轴倍率只允许出现在 ylabel 的「10⁻³ K⁻¹」里，
     于是刻度值 {0,5,10,15} 的读数规则唯一。
  P3 刻度可还原：两个面板的 y 刻度 {0,5,10,15} 与 x 刻度 {400..900} 的中心位置
     必须落在同一条线性映射上（残差 ≤ 0.7 pt），说明刻度值—数据值线性对应、
     没有缺刻度或错位。
  P4 负号约定（R5-C03）：两个面板的 ylabel 旋转文字序列必须自下而上读作
     「−dθ/dT / 10⁻³ K⁻¹」，第一个字符是负号——图上的量是正脱附速率 −dθ/dT。

为什么能替代放大目视：PDF 文字与线条是矢量对象，100% 与 200% 查看只是同一几何的
线性缩放；本探针直接检查几何本身（字号 ≥ 8 pt、行距、相邻间距、无叠字），因此
结论对缩放不变。判据的灵敏度由 --selftest 的合成反例保证（阈值小到能抓到实际
缺陷）。

用法：
  python tools/fig_probe_tpd.py --pdf build/main.pdf
  python tools/fig_probe_tpd.py --pdf build/main.pdf --json build/tpd_fig.json --out build/tpd_fig.txt
  python tools/fig_probe_tpd.py --selftest
退出码：0 全部通过 / 1 有 FAIL / 2 无法检查（找不到图或刻度）
"""
from __future__ import annotations

import argparse
import json
import re
import sys

try:
    import pymupdf as fitz
except ImportError:  # 旧版 PyMuPDF 只提供 fitz 名字
    import fitz

CAPTION_KEY = 'TPD 谱的模型计算'
Y_TICK_VALUES = {0.0: '0', 5.0: '5', 10.0: '10', 15.0: '15'}   # 数据值(×10⁻³) -> 标签
X_TICK_VALUES = {400: '400', 500: '500', 600: '600', 700: '700', 800: '800', 900: '900'}
LEGEND_SIZE = 8.5                # 图例字号（版式要求 8.5 pt，下限 8.0）
TICK_TOL_PT = 0.7                # 刻度中心对线性映射的最大残差
PAIR_DY_PT = 1.5                 # 线段样本与文字行的垂直中心差
PAIR_GAP_MIN, PAIR_GAP_MAX = 0.0, 5.0   # 线段末端到文字起点的水平间距
ROW_BASELINE_MIN = 8.0           # 相邻图例行的最小基线间距
CLUSTER_GAP_PT = 20.0            # 图例分簇的最小水平间隔
MIN_LINE_PT, MAX_LINE_PT = 10.0, 24.0   # 图例线段样本的长度范围
MULTIPLIER_CHARS = ('⋅', '·', '∙')      # U+22C5 / U+00B7 / U+2219
LABEL_GLYPHS = re.compile(r'^[−\-]$|^d$|^θ$|^/$|^T$|^ /$|^ 10$|^ K$|^−3$|^−1$')


def _center(box):
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def find_caption_page(doc):
    for i in range(doc.page_count):
        if CAPTION_KEY in doc[i].get_text():
            return i
    return None


def collect(page):
    """返回 (spans, legend_lines)。只取图区：caption 顶部往上 160 pt 的带。"""
    cap_y = None
    for blk in page.get_text('dict')['blocks']:
        if blk.get('type') != 0:
            continue
        for ln in blk['lines']:
            line_text = ''.join(sp['text'] for sp in ln['spans'])
            if CAPTION_KEY in line_text:
                cap_y = min(sp['bbox'][1] for sp in ln['spans'])
                break
        if cap_y is not None:
            break
    band_lo, band_hi = cap_y - 160.0, cap_y - 2.0
    spans = []
    for blk in page.get_text('dict')['blocks']:
        if blk.get('type') != 0:
            continue
        for ln in blk['lines']:
            for sp in ln['spans']:
                x0, y0, x1, y1 = sp['bbox']
                if not sp['text'].strip():
                    continue
                if band_lo <= y0 <= band_hi:
                    spans.append({'text': sp['text'], 'bbox': (x0, y0, x1, y1), 'size': sp['size']})
    lines = []
    for dr in page.get_drawings():
        r = dr['rect']
        if dr['type'] != 's' or dr.get('color') is None:
            continue
        if r.height > 0.6 or not (MIN_LINE_PT <= r.width <= MAX_LINE_PT):
            continue
        if band_lo <= r.y0 <= band_hi:
            lines.append({'bbox': (r.x0, r.y0, r.x1, r.y1),
                          'color': tuple(round(c, 2) for c in dr['color'])})
    return spans, lines


def panel_anchors(spans):
    """按 x 排序的 '400' 刻度标签找出两个面板的锚点；返回 [dict(left,right,x400)] 或 None。"""
    x400 = sorted([s for s in spans if s['text'].strip() == '400'], key=lambda s: _center(s['bbox'])[0])
    if len(x400) < 2:
        return None
    panels = []
    for i in (0, 1):
        p = {'x400': _center(x400[i]['bbox'])[0], 'x400_left': x400[i]['bbox'][0]}
        x900 = [s for s in spans if s['text'].strip() == '900'
                and _center(s['bbox'])[0] > p['x400']]
        x900 = sorted(x900, key=lambda s: _center(s['bbox'])[0])
        if not x900:
            return None
        p['x900'] = _center(x900[0]['bbox'])[0]
        panels.append(p)
    return panels


def panel_ticks(spans, panel):
    """取一个面板的 y 刻度标签（x1 贴近面板左界）与 x 刻度标签（y 在轴框下方）。"""
    y_ticks, x_ticks = {}, {}
    y0_anchor = None
    for s in spans:
        x0, y0, x1, y1 = s['bbox']
        cx, cy = _center(s['bbox'])
        t = s['text'].strip()
        # y 刻度：右端贴在 '400' 左侧 0.1–3.5 pt
        if t in Y_TICK_VALUES.values() and panel['x400_left'] - 3.5 <= x1 <= panel['x400_left'] - 0.1:
            y_ticks[t] = (cx, cy)
    if '0' not in y_ticks:
        return None, None
    frame_bottom = y_ticks['0'][1]
    for s in spans:
        x0, y0, x1, y1 = s['bbox']
        cx, cy = _center(s['bbox'])
        t = s['text'].strip()
        if t in X_TICK_VALUES.values() and frame_bottom + 3.0 <= y0 <= frame_bottom + 16.0 \
                and panel['x400'] - 15 <= cx <= panel['x900'] + 15:
            x_ticks[t] = (cx, cy)
    return y_ticks, x_ticks


def linear_residual(points):
    """points: [(value, coord)]，对 coord = a*value + b 的最小二乘最大残差。"""
    if len(points) < 2:
        return None, None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    b = my - a * mx
    return max(abs(a * x + b - y) for x, y in zip(xs, ys)), a


def check_multiplier(spans):
    bad = [s['text'] for s in spans if any(ch in s['text'] for ch in MULTIPLIER_CHARS)]
    return (not bad), bad


def check_ticks(spans, panels, mid_x):
    details, ok = {}, True
    for tag, panel in zip(('a', 'b'), panels):
        yc, xc = panel_ticks(spans, panel)
        if yc is None:
            details[tag] = {'ok': False, 'reason': 'no y ticks'}
            ok = False
            continue
        ypts = [(v, yc[label][1]) for v, label in Y_TICK_VALUES.items() if label in yc]
        xpts = [(v, xc[label][0]) for v, label in X_TICK_VALUES.items() if label in xc]
        ry, ay = linear_residual(ypts)
        rx, ax = linear_residual(xpts)
        det = {'y_n': len(ypts), 'x_n': len(xpts), 'y_res': ry, 'x_res': rx,
               'y_pt_per_001': ay, 'frame_bottom': yc['0'][1]}
        good = (len(ypts) == 4 and len(xpts) == 6 and ry is not None and rx is not None
                and ry <= TICK_TOL_PT and rx <= TICK_TOL_PT and (ay or 0) < 0 and (ax or 0) > 0)
        det['ok'] = good
        details[tag] = det
        ok = ok and good
    return ok, details


def group_legend_rows(spans, mid_x):
    """图例文字按面板分簇、按 y 分行；行文字拼接后去空白。"""
    out = {'a': [], 'b': []}
    legend = [s for s in spans if abs(s['size'] - LEGEND_SIZE) < 0.25]
    for tag, is_left in (('a', True), ('b', False)):
        sub = [s for s in legend if (_center(s['bbox'])[0] < mid_x) == is_left]
        buckets = {}
        for s in sub:
            key = round(_center(s['bbox'])[1] / 4.0)
            buckets.setdefault(key, []).append(s)
        rows = []
        for items in buckets.values():
            items.sort(key=lambda s: s['bbox'][0])
            rows.append({'y': sum(_center(s['bbox'])[1] for s in items) / len(items),
                         'x0': items[0]['bbox'][0], 'x1': items[-1]['bbox'][2],
                         'y1': max(s['bbox'][3] for s in items),
                         'text': re.sub(r'\s+', ' ', ''.join(s['text'] for s in items)).strip(),
                         'size': items[0]['size']})
        rows.sort(key=lambda r: r['y'])
        out[tag] = rows
    return out


def check_legends(spans, lines, mid_x, frame_bottom, expect_a=None, expect_b=None, caption_top=None):
    rows = group_legend_rows(spans, mid_x)
    det = {'rows_a': [r['text'] for r in rows['a']], 'rows_b': [r['text'] for r in rows['b']]}
    ok = True
    got_a = [r['text'] for r in rows['a']]
    got_b = [r['text'] for r in rows['b']]
    if expect_a is not None and (got_a != expect_a or got_b != expect_b):
        ok = False
        det['entry_mismatch'] = {'a': got_a, 'b': got_b}
    xa = [r['x1'] for r in rows['a']] or [0.0]
    xb = [r['x0'] for r in rows['b']] or [1e9]
    det['gap_pt'] = round(xb[0] - max(xa), 2)
    if det['gap_pt'] < CLUSTER_GAP_PT:
        ok = False
    ymin = min([r['y'] for r in rows['a'] + rows['b']] or [1e9])
    det['legend_top_pt'] = round(ymin, 2)
    det['frame_bottom_pt'] = round(frame_bottom, 2)
    if ymin <= frame_bottom:
        ok = False
    for tag in ('a', 'b'):
        ys = [r['y'] for r in rows[tag]]
        det['row_dy_' + tag] = [round(ys[i + 1] - ys[i], 2) for i in range(len(ys) - 1)]
        if any(d < ROW_BASELINE_MIN for d in det['row_dy_' + tag]):
            ok = False
    # 图例底部与图注之间必须留有空隙（不能压到图注首行）
    if caption_top is not None and rows['a'] + rows['b']:
        low = max(r['y1'] for r in rows['a'] + rows['b'])
        det['caption_gap_pt'] = round(caption_top - low, 2)
        if det['caption_gap_pt'] < 0.5:
            ok = False
    pairs = []
    for ln in lines:
        lx0, ly0, lx1, ly1 = ln['bbox']
        lcy = (ly0 + ly1) / 2.0
        tag = 'a' if (lx0 + lx1) / 2.0 < mid_x else 'b'
        best, bestdy = None, 1e9
        for r in rows[tag]:
            dy = abs(r['y'] - lcy)
            if dy < bestdy:
                best, bestdy = r, dy
        gap = (best['x0'] - lx1) if best else 1e9
        pairs.append({'tag': tag, 'dy': round(bestdy, 2), 'gap': round(gap, 2),
                      'color': ln['color'], 'text': best['text'] if best else None})
        if best is None or bestdy > PAIR_DY_PT or not (PAIR_GAP_MIN <= gap <= PAIR_GAP_MAX):
            ok = False
    det['pairs'] = pairs
    return ok, det


def check_ylabel(spans, panels):
    """两个面板的 ylabel 旋转文字序列（按 y 从上到下 = 自下而上阅读）都要以负号开头。"""
    res, ok = {}, True
    for tag, panel in zip(('a', 'b'), panels):
        lo, hi = panel['x400_left'] - 31.0, panel['x400_left'] - 6.0
        glyphs = [s for s in spans if lo <= _center(s['bbox'])[0] <= hi and s['size'] >= 6.0
                  and LABEL_GLYPHS.match(s['text'].strip())]
        glyphs.sort(key=lambda s: -_center(s['bbox'])[1])
        seq = re.sub(r'\s+', ' ', ''.join(s['text'] for s in glyphs)).strip()
        good = seq.startswith('−dθ/dT') or seq.startswith('-dθ/dT')
        res[tag] = {'ok': good, 'sequence': seq}
        ok = ok and good
    return ok, res


def run(pdf, out=None, json_path=None):
    doc = fitz.open(pdf)
    pi = find_caption_page(doc)
    if pi is None:
        print('fig_probe_tpd: UNUSABLE (caption %r not found)' % CAPTION_KEY)
        return 2
    spans, lines = collect(doc[pi])
    panels = panel_anchors(spans) if spans else None
    if spans is None or panels is None:
        print('fig_probe_tpd: UNUSABLE (figure spans or x ticks missing on page %d)' % (pi + 1))
        return 2
    caption_top = min((s['bbox'][1] for s in spans if 'Polanyi' in s['text']), default=None)
    if caption_top is None:
        caption_top = max(s['bbox'][3] for s in spans) + 2.0
    mid_x = (panels[0]['x900'] + panels[1]['x400']) / 2.0
    yc_a, _ = panel_ticks(spans, panels[0])
    if yc_a is None:
        print('fig_probe_tpd: UNUSABLE (y ticks missing on page %d)' % (pi + 1))
        return 2
    frame_bottom = yc_a['0'][1]

    res = {'page': pi + 1}
    ok = True
    good, bad = check_multiplier(spans)
    res['P2_multiplier'] = {'ok': good, 'found': bad}
    ok = ok and good
    good, det = check_ticks(spans, panels, mid_x)
    res['P3_ticks'] = {'ok': good, **det}
    ok = ok and good
    good, det = check_legends(spans, lines, mid_x, frame_bottom,
                              ['β = 5', 'β = 10', 'β = 20'], ['n = 1，拖尾', 'n = 2，对称'],
                              caption_top)
    det['line_count'] = len(lines)
    if len(lines) != 5:
        good = False
    res['P1_legends'] = {'ok': good, **det}
    ok = ok and good
    good, det = check_ylabel(spans, panels)
    res['P4_ylabel'] = {'ok': good, **det}
    ok = ok and good
    res['overall'] = 'PASS' if ok else 'FAIL'

    for k in ('P1_legends', 'P2_multiplier', 'P3_ticks', 'P4_ylabel'):
        v = res[k]
        # 控制台只给 ASCII（ensure_ascii=True）：本仓库控制台是 GBK，非 ASCII 会抛
        # UnicodeEncodeError 并中断；文件输出仍用 UTF-8。
        print('fig_probe_tpd: %-4s %s %s' % ('PASS' if v['ok'] else 'FAIL', k,
                                            '' if v['ok'] else json.dumps(v, ensure_ascii=True)))
    print('fig_probe_tpd: %s (page %d)' % (res['overall'], pi + 1))
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(json.dumps(res, ensure_ascii=False, indent=2) + '\n')
    if json_path:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
    return 0 if ok else 1


def _row(text, y, x0=100.0, x1=115.0, size=LEGEND_SIZE):
    """合成一行图例文字（py 侧的假 span，用于 selftest）。"""
    return [{'text': text, 'bbox': (x0, y - 4.0, x0 + 4.0, y + 4.0), 'size': size},
            {'text': text, 'bbox': (x0 + 4.0, y - 4.0, x1, y + 4.0), 'size': size}]


def selftest():
    fails = []
    r, _ = linear_residual([(0, 100.0), (5, 90.1), (10, 80.0), (15, 69.9)])
    if r is None or r > TICK_TOL_PT:
        fails.append('linear_ok')
    r2, _ = linear_residual([(0, 100.0), (5, 90.0), (10, 84.0), (15, 70.0)])
    if r2 is None or r2 <= TICK_TOL_PT:
        fails.append('linear_detect')
    if check_multiplier([{'text': '⋅10', 'bbox': (0, 0, 10, 8), 'size': 8.0}])[0]:
        fails.append('multiplier_detect')
    if not check_multiplier([{'text': '10', 'bbox': (0, 0, 10, 8), 'size': 8.0}])[0]:
        fails.append('multiplier_ok')
    # 行分组：两行必须切成两行
    spans = _row('β = 5', 300.0) + _row('β = 10', 309.2)
    if len(group_legend_rows(spans, 500.0)['a']) != 2:
        fails.append('row_grouping')
    # 配对：线段离文字 >1.5 pt 必须失败
    rows = group_legend_rows(spans, 500.0)
    lines_ok = [{'bbox': (80.0, 300.0, 96.0, 300.0), 'color': (0.0, 0.0, 1.0)}]
    lines_bad = [{'bbox': (80.0, 294.0, 96.0, 294.0), 'color': (0.0, 0.0, 1.0)}]
    good_ok, _ = check_legends(spans, lines_ok, 500.0, 280.0)
    good_bad, _ = check_legends(spans, lines_bad, 500.0, 280.0)
    if not good_ok or good_bad:
        fails.append('pair_sensitivity')
    # ylabel 序列：负号在最下（y 最大）时必须通过；拿掉负号必须失败
    yl = [{'text': '−', 'bbox': (10, 50, 12, 60), 'size': 8.0},
          {'text': 'd', 'bbox': (10, 40, 12, 50), 'size': 8.0},
          {'text': 'θ', 'bbox': (10, 30, 12, 40), 'size': 8.0},
          {'text': '/', 'bbox': (10, 20, 12, 30), 'size': 8.0},
          {'text': 'd', 'bbox': (10, 10, 12, 20), 'size': 8.0},
          {'text': 'T', 'bbox': (10, 0, 12, 10), 'size': 8.0}]
    panel = {'x400': 40.0, 'x400_left': 36.0, 'x900': 90.0}
    if not check_ylabel(yl, [panel, panel])[0]:
        fails.append('ylabel_ok')
    if check_ylabel([s for s in yl if s['text'] != '−'], [panel, panel])[0]:
        fails.append('ylabel_detect')
    if fails:
        print('SELFTEST FAIL ' + ' '.join(fails))
        return 1
    print('SELFTEST PASS legend_cluster / multiplier / ticks_linear / ylabel_sign / row_grouping')
    print('selftest: PASS')
    return 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', default='build/main.pdf')
    ap.add_argument('--out', default=None)
    ap.add_argument('--json', dest='json_path', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        raise SystemExit(selftest())
    raise SystemExit(run(a.pdf, a.out, a.json_path))
