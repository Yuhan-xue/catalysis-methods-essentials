# -*- coding: utf-8 -*-
# ================================================================
#  tools/gen_tpd_table.py
#  生成 chapters/parts/ch05-a.tex 中 TPD 图（图 5-?）的坐标表。
#
#  【为什么存在这个脚本】评审 C05-02：原图用手调的四次函数
#      A/[1+((T-Tp)/w)^4]
#  作图，而该函数的整轴面积解析值为 A*w*pi/sqrt(2)；原参数下三条曲线
#  的面积比是 1 : 2.1122 : 4.4860，与图注声称的「严格按 1:2:4 增长」不符，
#  二级曲线面积也不等于一级。图注声称「按脱附速率方程与 Redhead 峰温关系
#  参数化生成」，但四次函数既不是该方程的解，也不是它的任何近似。
#
#  本脚本改为直接数值求解书内式(5-39) 所用的 Polanyi-Wigner 方程：
#      d(theta)/dt = -A exp(-E_a/RT) theta^n ,  T = T0 + beta t ,  theta(0)=theta_0
#  固定 theta_0 时的守恒关系（正是图注应当陈述的那一条）：
#      int_0^inf (dtheta/dt) dt = theta_0           （任何 beta、任何 n）
#      int (dtheta/dT) dT       = theta_0           （图纵轴取 d(theta)/dT）
#  即「峰面积标定的是初始覆盖度，不随升温速率成倍放大」。
#  按时间计的速率 d(theta)/dt 才随 beta 放大，两者只差一个因子 beta。
#
#  参数（图注、正文必须与本表一致）：
#      E_a = 120 kJ/mol     theta_0 = 1（饱和覆盖）     T0 = 300 K
#      A   = 4.39753e10 s^-1（按一级、beta = 10 K/min 时 Tp = 570.0 K 标定）
#      (a) n = 1，beta = 5 / 10 / 20 K/min  ->  Tp = 555.9 / 570.0 / 584.9 K
#      (b) beta = 10 K/min，n = 1 / 2       ->  Tp = 570.0 / 568.6 K
#
#  用法：
#      python tools/gen_tpd_table.py            # 参数 + 积分校验
#      python tools/gen_tpd_table.py --coords   # 另外打印可粘进 tex 的坐标表
# ================================================================
import argparse
import math

import numpy as np
from scipy.integrate import solve_ivp

R = 8.314462618
EA = 120e3
A_PRE = 4.39753e10          # s^-1
TH0 = 1.0
T0 = 300.0
T_LO, T_HI = 400.0, 900.0   # 显示窗；两端尾部截断合计 < 0.15%
BETAS = (5.0, 10.0, 20.0)
ORDERS = (1, 2)


def solve(beta, n, t_eval):
    """返回 (T, dtheta/dT, theta)。t_eval 单位为 K，内部换算成时间。"""
    tmax = float(t_eval[-1] - T0) / beta

    def rhs(t, y):
        return [-A_PRE * math.exp(-EA / (R * (T0 + beta * t))) * y[0] ** n]

    sol = solve_ivp(rhs, [0.0, tmax], [TH0], method='LSODA',
                    rtol=1e-12, atol=1e-18, dense_output=True)
    th = np.clip(sol.sol((t_eval - T0) / beta)[0], 0.0, None)
    return t_eval, A_PRE * np.exp(-EA / (R * t_eval)) * th ** n / beta, th


def grid():
    """非均匀网格：峰区 2 K，两翼 10 K（峰值位置需落在网格点上，故峰区加密）。"""
    ts = list(np.arange(400.0, 520.0, 10.0))
    ts += list(np.arange(520.0, 601.0, 2.0))
    ts += list(np.arange(610.0, 901.0, 10.0))
    out = sorted(set(round(float(x), 1) for x in ts))
    return np.array(out)


def report():
    g = grid()
    garea = np.linspace(T_LO, T_HI, 40001)      # 面积一律用细网格算，避免折线插值误差
    print('E_a = %.0f kJ/mol, A = %.6e s^-1, theta_0 = %.1f, T0 = %.0f K, 显示窗 %.0f-%.0f K'
          % (EA / 1000, A_PRE, TH0, T0, T_LO, T_HI))
    gfull = np.linspace(300.0, 1500.0, 120001)
    a5 = None
    for beta in BETAS:
        T, rT, _ = solve(beta, 1, g)
        a = np.trapezoid(solve(beta, 1, garea)[1], garea)
        a5 = a if a5 is None else a5
        af = np.trapezoid(solve(beta, 1, gfull)[1], gfull)
        print('  (a) beta=%-4g K/min  Tp=%7.2f K  peak=%.5e  显示窗面积=%.6f'
              '  全温区(300-1500K)面积=%.8f' % (beta, T[np.argmax(rT)], rT.max(), a, af))
    print('      显示窗面积之比 = %s   （beta 之比是 1 : 2 : 4）'
          % ' : '.join('%.6f' % (np.trapezoid(solve(b, 1, garea)[1], garea) / a5)
                       for b in BETAS))
    for n in ORDERS:
        T, rT, _ = solve(10.0, n, g)
        af = np.trapezoid(solve(10.0, n, gfull)[1], gfull)
        print('  (b) n=%d  Tp=%7.2f K  peak=%.5e  显示窗面积=%.6f  全温区面积=%.8f'
              % (n, T[np.argmax(rT)], rT.max(),
                 np.trapezoid(solve(10.0, n, garea)[1], garea), af))
    print('      峰值之比 n=2/n=1 = %.6f'
          % (solve(10.0, 2, g)[1].max() / solve(10.0, 1, g)[1].max()))


def emit():
    """打印可直接粘进 chapters/parts/ch05-a.tex 的 pgfplots 代码。"""
    g = grid()
    specs = [
        ('blue', 'solid', r'$\beta=5$', solve(5.0, 1, g)[1]),
        ('red', 'solid', r'$\beta=10$', solve(10.0, 1, g)[1]),
        ('black', 'solid', r'$\beta=20$', solve(20.0, 1, g)[1]),
        ('red', 'solid', r'$n=1$，拖尾', solve(10.0, 1, g)[1]),
        ('black', 'dashed', r'$n=2$，对称', solve(10.0, 2, g)[1]),
    ]
    for colour, dash, legend, col in specs:
        style = colour + (', dashed' if dash == 'dashed' else '')
        print(r'\addplot[%s, thick] table[row sep=\\, y index=1] {' % style)
        print(r'%%  T/K      dtheta/dT / K^{-1}')
        for i, T in enumerate(g):
            print(r'  %.1f  %.5e \\' % (T, col[i]))
        print(r'};\addlegendentry{%s}' % legend)
        print()


def parse_tex_tables():
    """从 chapters/parts/ch05-a.tex 抽出图 5-? 的 5 张坐标表（按出现顺序）。"""
    import re
    from pathlib import Path
    tex = (Path(__file__).resolve().parents[1] / 'chapters' / 'parts' / 'ch05-a.tex').read_text(encoding='utf-8')
    lines = tex.splitlines()
    tables, i = [], 0
    while i < len(lines):
        if lines[i].startswith('\\addplot[') and 'table[row sep=' in lines[i]:
            pts, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith('};'):
                m = re.match(r'\s*([0-9.]+)\s+([0-9.eE+-]+)\s*\\\\\s*$', lines[i])
                if m:
                    pts.append((float(m.group(1)), float(m.group(2))))
                i += 1
            tables.append(pts)
        i += 1
    return tables


SPECS = ((5.0, 1, '(a) beta=5 n=1'), (10.0, 1, '(a) beta=10 n=1'), (20.0, 1, '(a) beta=20 n=1'),
         (10.0, 1, '(b) n=1'), (10.0, 2, '(b) n=2'))


def check(rtol=1e-5):
    """逐点复验：.tex 内嵌坐标必须等于用本脚本参数求解的结果（R4 继承项 C05-02）。"""
    tables = parse_tex_tables()
    if len(tables) != len(SPECS):
        print('TPD check: FAIL（.tex 内坐标表 %d 张，期望 %d 张）' % (len(tables), len(SPECS)))
        return 1
    g = grid()
    worst = 0.0
    ok = True
    for (beta, n, tag), pts in zip(SPECS, tables):
        gen = solve(beta, n, g)[1]
        if len(pts) != len(g) or any(abs(p[0] - x) > 1e-6 for p, x in zip(pts, g)):
            print('TPD check: FAIL  %s 栅格不一致（tex %d 点）' % (tag, len(pts)))
            ok = False
            continue
        rel = max(abs(p[1] - yv) / max(abs(yv), 1e-30) for p, yv in zip(pts, gen))
        worst = max(worst, rel)
        good = rel <= rtol
        ok = ok and good
        print('TPD check: %-4s %-16s rel_max=%.3e (%d pts)'
              % ('PASS' if good else 'FAIL', tag, rel, len(pts)))
    print('TPD check: %s  worst_rel=%.3e  rtol=%.1e' % ('PASS' if ok else 'FAIL', worst, rtol))
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--coords', action='store_true')
    ap.add_argument('--check', action='store_true', help='逐点复验 .tex 内嵌坐标')
    a = ap.parse_args()
    if a.check:
        raise SystemExit(check())
    report()
    if a.coords:
        print()
        emit()
