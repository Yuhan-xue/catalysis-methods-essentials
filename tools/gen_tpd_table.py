# -*- coding: utf-8 -*-
# ================================================================
#  tools/gen_tpd_table.py
#  生成 chapters/parts/ch05-a.tex 中 TPD 图（图 5-1）的 tikzpicture 块与坐标表。
#
#  【R5-C01 单位约定，勿再混用】
#      beta 一律按 K/min（与图注、正文、实验惯例一致）；
#      A    一律按 s^-1（与 Redhead 方程、文献惯例一致），并同时给出 min^-1 换算值。
#      数值积分在秒制下完成：beta_s = beta/60，t = (T - T0)/beta_s。
#      当前标定：A = 7.34510e8 s^-1 = 4.40706e10 min^-1，由 n = 1、
#      beta = 10 K/min、Tp = 570.000 K 的解析峰温条件
#          E/(R Tp^2) = (A / beta_s) exp(-E / (R Tp))
#      反解得到。旧版（R5 评审前）把 beta 的 K/min 数值直接当秒制用，
#      等效把升温速率放大 60 倍，与声明的 A 单位矛盾；详见
#      reviews/2026-10-01-round5/01-content.md（R5-C01 / R5-C03）。
#
#  【R5-C03 负号约定】脱附使覆盖度随温度下降，正脱附速率定义为
#      -d(theta)/dT = (A / beta_s) exp(-E/(R T)) theta^n   [K^-1]
#      本脚本输出、图纵轴、图注、正文式(5-39) 后文的约定必须一致。
#
#  模型（书内式(5-39) 所用 Polanyi-Wigner 方程）：
#      d(theta)/dt = -A exp(-E/(RT)) theta^n ,  T = T0 + beta t ,  theta(0) = 1
#  守恒关系：int_0^inf (-d(theta)/dt) dt = theta_0；换成温度域即
#      int (-d(theta)/dT) dT = theta_0（任何 beta、任何 n）。
#
#  校验分三层（R5 评审 03-workflow.md 的建议）：
#      1) --check   坐标再生：.tex 内嵌坐标 == 本脚本求解结果（复制/舍入错误）
#      2) --verify  独立物理约束：两种时间单位独立求解一致；与闭式积分一致；
#                   解析峰温条件交叉检查；覆盖度递减；正速率积分守恒；
#                   欠采样检查（半高交点必须落在 2 K 加密区）
#      3) fig_probe_tpd.py  成品阅读：图例分离、单倍率、刻度可还原
#
#  用法：
#      python tools/gen_tpd_table.py             # 参数 + 峰形表（Tp/峰高/FWHM/面积）
#      python tools/gen_tpd_table.py --coords    # 打印可粘进 tex 的 5 张坐标表
#      python tools/gen_tpd_table.py --emit      # 打印整块 tikzpicture（含坐标）
#      python tools/gen_tpd_table.py --patch     # 把 --emit 的整块回写 ch05-a.tex
#      python tools/gen_tpd_table.py --check     # 复验 .tex 内嵌坐标
#      python tools/gen_tpd_table.py --verify    # 独立数值复算（含图注数字一致性）
# ================================================================
import argparse
import math
import re
from pathlib import Path

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
TEX_PATH = ROOT / 'chapters' / 'parts' / 'ch05-a.tex'

R = 8.314462618
EA = 120e3                  # J/mol
T0 = 300.0                  # K
TH0 = 1.0                   # 饱和覆盖
T_LO, T_HI = 400.0, 900.0   # 显示窗；两端尾部截断合计 < 0.01%
BETAS = (5.0, 10.0, 20.0)   # K/min（与图注、正文一致）
ORDERS = (1, 2)
T_CAL, BETA_CAL = 570.0, 10.0   # 标定点：n=1、10 K/min -> Tp = 570.000 K

# A 由解析峰温条件反解（见文件头注释）：单位 s^-1 与 min^-1 同时声明。
A_PRE_S = (BETA_CAL / 60.0) * (EA / (R * T_CAL ** 2)) * math.exp(EA / (R * T_CAL))
A_PRE_MIN = A_PRE_S * 60.0
FIN_LO, FIN_HI = 500.0, 620.0   # 2 K 加密区（半高交点必须落在此区间内）


def _theta_ode(beta_min, n, t_eval, unit):
    """ODE 求解覆盖度。unit='s' 时 beta 换算为 K/s、A 取 s^-1；'min' 时用 K/min、min^-1。"""
    beta = beta_min / 60.0 if unit == 's' else beta_min
    A = A_PRE_S if unit == 's' else A_PRE_MIN
    tmax = float(t_eval[-1] - T0) / beta

    def rhs(t, y):
        return [-A * math.exp(-EA / (R * (T0 + beta * t))) * y[0] ** n]

    sol = solve_ivp(rhs, [0.0, tmax], [TH0], method='LSODA',
                    rtol=1e-12, atol=1e-18, dense_output=True)
    return np.clip(sol.sol((t_eval - T0) / beta)[0], 0.0, None)


def solve(beta_min, n, t_eval, unit='s'):
    """返回 (T, -d(theta)/dT, theta)。beta 单位 K/min；纵轴约定见文件头（R5-C03）。"""
    T = np.asarray(t_eval, dtype=float)
    th = _theta_ode(beta_min, n, T, unit)
    beta_s = beta_min / 60.0
    rate = A_PRE_S * np.exp(-EA / (R * T)) * th ** n / beta_s
    return T, rate, th


def theta_closed(T, beta_min, n):
    """闭式解（与 ODE 无关）：h = (A/beta_s) ∫ e^{-E/RT'} dT'；theta = e^-h (n=1) 或 1/(1+h)。"""
    h = (A_PRE_S / (beta_min / 60.0)) * quad(
        lambda t: math.exp(-EA / (R * t)), T0, T, epsabs=1e-12, limit=200)[0]
    return math.exp(-h) if n == 1 else 1.0 / (1.0 + h)


def rate_closed(T, beta_min, n):
    """闭式正脱附速率 -d(theta)/dT（quad 积分，独立于 solve_ivp）。"""
    return A_PRE_S / (beta_min / 60.0) * math.exp(-EA / (R * T)) * theta_closed(T, beta_min, n) ** n


def theta_profile(beta_min, n, T):
    """细网格上的闭式覆盖度（累加梯形积分，供递减/守恒检查）。"""
    T = np.asarray(T, dtype=float)
    integrand = np.exp(-EA / (R * T))
    h = (A_PRE_S / (beta_min / 60.0)) * np.concatenate(
        ([0.0], np.cumsum((integrand[1:] + integrand[:-1]) / 2.0 * np.diff(T))))
    return np.exp(-h) if n == 1 else 1.0 / (1.0 + h)


def analytic_tp(beta_min, n):
    """解析峰温条件：E/(R Tp^2) = n (A/beta_s) exp(-E/(R Tp)) theta(Tp)^(n-1)。"""
    def f(t):
        return EA / (R * t * t) - n * (A_PRE_S / (beta_min / 60.0)) * math.exp(-EA / (R * t)) \
            * theta_closed(t, beta_min, n) ** (n - 1)
    return brentq(f, 400.0, 700.0)


def shape(beta_min, n):
    """用闭式解求 (Tp, 峰高, FWHM, 左交点, 右交点)。"""
    tp = minimize_scalar(lambda t: -rate_closed(t, beta_min, n), bounds=(450.0, 650.0),
                         method='bounded').x
    pk = rate_closed(tp, beta_min, n)
    left = brentq(lambda t: rate_closed(t, beta_min, n) - pk / 2, 400.0, tp)
    right = brentq(lambda t: rate_closed(t, beta_min, n) - pk / 2, tp, 800.0)
    return tp, pk, right - left, left, right


def grid():
    """显示网格：2 K 加密区覆盖两级峰的半高交点，两翼 10 K。"""
    ts = list(np.arange(400.0, FIN_LO - 9.0, 10.0))     # 400 ... 490
    ts += list(np.arange(FIN_LO, FIN_HI + 1.0, 2.0))    # 500 ... 620（2 K）
    ts += list(np.arange(FIN_HI + 10.0, 901.0, 10.0))   # 630 ... 900
    return np.array(sorted(set(round(float(x), 1) for x in ts)))


SPECS = ((5.0, 1, '(a) beta=5 n=1'), (10.0, 1, '(a) beta=10 n=1'),
         (20.0, 1, '(a) beta=20 n=1'), (10.0, 1, '(b) n=1'), (10.0, 2, '(b) n=2'))


def report():
    print('E_a = %.0f kJ/mol, A = %.6e s^-1 = %.6e min^-1 (calibrated at beta=%.0f K/min, Tp=%.1f K)'
          % (EA / 1000, A_PRE_S, A_PRE_MIN, BETA_CAL, T_CAL))
    print('theta_0 = %.1f, T0 = %.0f K, display window %.0f-%.0f K, fine zone %.0f-%.0f K (2 K)'
          % (TH0, T0, T_LO, T_HI, FIN_LO, FIN_HI))
    g = grid()
    garea = np.linspace(T_LO, T_HI, 40001)
    gfull = np.linspace(300.0, 1500.0, 120001)
    a5 = None
    for beta in BETAS:
        T, rT, _ = solve(beta, 1, g)
        a = np.trapezoid(solve(beta, 1, garea)[1], garea)
        a5 = a if a5 is None else a5
        af = np.trapezoid(solve(beta, 1, gfull)[1], gfull)
        print('  (a) beta=%-4g K/min  Tp=%7.2f K  peak=%.5e  window_area=%.6f  full_area=%.8f'
              % (beta, T[np.argmax(rT)], rT.max(), a, af))
    print('      window area ratio = %s   (beta ratio is 1 : 2 : 4)'
          % ' : '.join('%.6f' % (np.trapezoid(solve(b, 1, garea)[1], garea) / a5)
                       for b in BETAS))
    for n in ORDERS:
        T, rT, th = solve(10.0, n, g)
        tp, pk, fwhm, left, right = shape(10.0, n)
        af = np.trapezoid(solve(10.0, n, gfull)[1], gfull)
        print('  (b) n=%d  Tp=%7.2f K  peak=%.5e  FWHM=%.4f K (%.1f-%.1f, closed form)'
              '  window_area=%.6f  full_area=%.8f'
              % (n, T[np.argmax(rT)], rT.max(), fwhm, left, right,
                 np.trapezoid(solve(10.0, n, garea)[1], garea), af))
    ratio = shape(10.0, 2)[1] / shape(10.0, 1)[1]
    print('      peak ratio n=2/n=1 = %.6f   FWHM ratio = %.6f'
          % (ratio, shape(10.0, 2)[2] / shape(10.0, 1)[2]))


def parse_tex_tables():
    """从 chapters/parts/ch05-a.tex 抽出图 5-1 的 5 张坐标表（按出现顺序）。"""
    tex = TEX_PATH.read_text(encoding='utf-8')
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


def check(rtol=1e-5):
    """逐点复验：.tex 内嵌坐标必须等于用本脚本参数求解的结果。"""
    tables = parse_tex_tables()
    # 只认图 5-1 的 5 张表：本文件内其余 show 表不匹配该正则，但为稳妥仍按顺序取前 5 张
    tables = tables[:len(SPECS)]
    if len(tables) != len(SPECS):
        print('TPD check: FAIL (.tex embedded tables %d, expected %d)' % (len(tables), len(SPECS)))
        return 1
    g = grid()
    worst = 0.0
    ok = True
    for (beta, n, tag), pts in zip(SPECS, tables):
        _, gen, _ = solve(beta, n, g)
        if len(pts) != len(g) or any(abs(p[0] - x) > 1e-6 for p, x in zip(pts, g)):
            print('TPD check: FAIL  %s grid mismatch (tex %d pts)' % (tag, len(pts)))
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


def check_caption():
    """图注中的标定数字必须与生成器一致（R5-C01/C03 同步纪律）。"""
    tex = TEX_PATH.read_text(encoding='utf-8')
    m = re.search(r'\\caption\{TPD 谱的模型计算.*?\\label\{fig:ch05-tpd\}', tex, re.S)
    if not m:
        print('TPD caption: FAIL (caption block not found)')
        return 1
    cap = m.group(0)
    bad = []
    for needle, why in [
        ('7.35', 'caption must state A = 7.35e8 s^-1'),
        ('4.41', 'caption must state A = 4.41e10 min^-1'),
        ('556', 'caption must state Tp(beta=5) = 556 K'),
        ('585', 'caption must state Tp(beta=20) = 585 K'),
        ('52.3', 'caption must state FWHM(n=1) = 52.3 K'),
        ('73.5', 'caption must state FWHM(n=2) = 73.5 K'),
        ('0.681', 'caption must state peak ratio 0.681'),
        ('更宽', 'caption must describe n=2 as broader'),
        ('-\\mathrm{d}\\theta/\\mathrm{d}T', 'caption must use -dtheta/dT sign convention'),
    ]:
        if needle not in cap:
            bad.append(why)
    if '更窄' in cap:
        bad.append('caption still says n=2 is narrower (更窄)')
    for why in bad:
        print('TPD caption: FAIL (%s)' % why)
    if not bad:
        print('TPD caption: PASS (calibration numbers and sign convention match generator)')
    return 1 if bad else 0


def verify():
    """独立物理约束复算（不调用 --check 的坐标对比）。"""
    print('TPD verify: independent checks (units / closed form / peak condition / conservation)')
    ok = True
    g = grid()
    curves = ((5.0, 1), (10.0, 1), (20.0, 1), (10.0, 2))   # 图上实际绘制的 5 条曲线（10/1 重复一次）

    # 1) 两种时间单位独立求解一致（只用速率高于峰值 1e-9 的区间：远尾在下溢区无意义）
    worst = 0.0
    for beta, n in curves:
        _, rs, ths = solve(beta, n, g, 's')
        _, rm, thm = solve(beta, n, g, 'min')
        mask = rm > 1e-9 * float(np.max(rm))
        rel = max(np.max(np.abs(rs[mask] - rm[mask]) / np.maximum(np.abs(rs[mask]), 1e-30)),
                  np.max(np.abs(ths[mask] - thm[mask]) / np.maximum(np.abs(ths[mask]), 1e-30)))
        worst = max(worst, rel)
    good = worst < 1e-8
    ok = ok and good
    print('TPD verify: %-4s two time units (s / min) agree, worst_rel=%.3e'
          % ('PASS' if good else 'FAIL', worst))

    # 2) 闭式积分（quad）与 ODE 一致（同上阈值，避开 theta 下溢后的裁剪值）
    worst = 0.0
    for beta, n in curves:
        _, rs, _ = solve(beta, n, g)
        rc = np.array([rate_closed(t, beta, n) for t in g])
        mask = rc > 1e-9 * float(np.max(rc))
        rel = np.max(np.abs(rs[mask] - rc[mask]) / np.maximum(np.abs(rc[mask]), 1e-30))
        worst = max(worst, rel)
    good = worst < 1e-7
    ok = ok and good
    print('TPD verify: %-4s closed-form quadrature vs ODE, worst_rel=%.3e'
          % ('PASS' if good else 'FAIL', worst))

    # 3) 解析峰温条件 vs 闭式数值峰位（含 n=2 的 theta_m 因子）
    worst = 0.0
    for beta, n in curves:
        worst = max(worst, abs(analytic_tp(beta, n) - shape(beta, n)[0]))
    good = worst < 1e-3
    ok = ok and good
    print('TPD verify: %-4s analytic peak condition vs numerical peak, worst_dT=%.3e K'
          % ('PASS' if good else 'FAIL', worst))

    # 4) 覆盖度不增 + 正速率 + 正速率积分守恒（300-1500 K 全温区）
    worst_mono, worst_area, tail_bad = 0.0, 0.0, []
    for beta, n in curves:
        Tf = np.linspace(T0, 1500.0, 6001)
        th = theta_profile(beta, n, Tf)
        worst_mono = max(worst_mono, float(np.max(np.diff(th))))
        rf = A_PRE_S / (beta / 60.0) * np.exp(-EA / (R * Tf)) * th ** n
        if np.any(rf < 0.0):
            tail_bad.append('beta=%g n=%d has negative rate' % (beta, n))
        nz = np.nonzero(rf > 0.0)[0]
        # 下溢只允许出现在尾段（峰后且连续到窗口末端），不得在峰前/峰中缺失
        if nz[-1] + 1 < len(rf) and np.any(rf[nz[-1] + 1:] != 0.0):
            tail_bad.append('beta=%g n=%d rate has gaps' % (beta, n))
        if nz[0] != 0 and Tf[nz[0]] > T_LO:
            tail_bad.append('beta=%g n=%d rate zero inside display window' % (beta, n))
        # 面积守恒用 quad（独立于梯形积分）：∫(-dθ/dT)dT = θ(300) - θ(1500)
        area = quad(lambda t: rate_closed(t, beta, n), T0, 1500.0, epsabs=1e-14, limit=400)[0]
        residual = TH0 - theta_closed(1500.0, beta, n)
        worst_area = max(worst_area, abs(area - residual) / max(residual, 1e-30))
    good = worst_mono <= 0.0 and worst_area < 1e-12 and not tail_bad
    ok = ok and good
    print('TPD verify: %-4s theta non-increasing (max dtheta=%.3e), rate positive until tail '
          'underflow, area == theta0 - theta(1500) (worst_rel=%.3e)%s'
          % ('PASS' if good else 'FAIL', worst_mono, worst_area,
             '' if not tail_bad else '; ' + '; '.join(tail_bad)))

    # 5) 欠采样检查：图上 5 条曲线的半高交点必须落在 2 K 加密区
    bad = []
    for beta, n in curves:
        _, _, _, left, right = shape(beta, n)
        if left < FIN_LO or right > FIN_HI:
            bad.append('beta=%g n=%d FWHM=%.1f-%.1f K outside %.0f-%.0f' % (beta, n, left, right, FIN_LO, FIN_HI))
    good = not bad
    ok = ok and good
    print('TPD verify: %-4s half-max crossings inside 2 K fine zone %s'
          % ('PASS' if good else 'FAIL', '' if good else '; '.join(bad)))

    # 6) 图注数字与生成器一致
    cap_ok = check_caption() == 0
    ok = ok and cap_ok

    print('TPD verify: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


# ---------------------------------------------------------------- emit / patch
def _fmt_block():
    g = grid()
    gfull = np.linspace(300.0, 1500.0, 120001)
    areas = {b: np.trapezoid(solve(b, 1, gfull)[1], gfull) for b in BETAS}
    areas_b = {n: np.trapezoid(solve(10.0, n, gfull)[1], gfull) for n in ORDERS}
    L = []
    L.append(r'% 图源：解 Polanyi--Wigner 方程 d(theta)/dt = -A exp(-Ea/RT) theta^n（书内式(5-39) 所用模型），')
    L.append(r'%       T = T0 + beta t，theta(0) = theta_0 = 1（饱和覆盖），T0 = 300 K。')
    L.append(rf'%       单位（R5-C01）：beta = 5/10/20 K/min；A = {A_PRE_S:.6e} s^-1 = {A_PRE_MIN:.6e} min^-1，')
    L.append(r'%       由 n = 1、beta = 10 K/min、Tp = 570.000 K 的解析峰温条件标定；积分在秒制下完成。')
    L.append(r'%       纵轴是正脱附速率 -d(theta)/dT = (A/beta_s) exp(-Ea/RT) theta^n（R5-C03 负号约定），')
    L.append(rf'%       故全温区积分 int (-dtheta/dT) dT = theta_0 = {TH0:.6f}（与本图图注、正文数字一致）：')
    L.append(r'%         (a) beta = 5 / 10 / 20 K/min -> ' + ' / '.join('%.6f' % areas[b] for b in BETAS))
    L.append(r'%         (b) n = 1 / 2（beta = 10 K/min）-> ' + ' / '.join('%.6f' % areas_b[n] for n in ORDERS))
    L.append(r'%       下表坐标由 tools/gen_tpd_table.py 生成（--patch 直接回写本块）。')
    L.append(r'\begin{tikzpicture}')
    L.append(r'\begin{groupplot}[')
    L.append(r'  group style={group size=2 by 1, horizontal sep=7mm},')
    L.append(r'  width=50mm, height=40mm,')
    L.append(r'  xmin=400, xmax=900, ymin=0, ymax=0.019,')
    L.append(r'  xtick={400,500,600,700,800,900}, minor xtick={450,550,650,750,850},')
    L.append(r'  ytick={0,0.005,0.010,0.015}, yticklabels={0,5,10,15},')
    L.append(r'  scaled x ticks=false, scaled y ticks=false,   % 只保留 ylabel 里的一套倍率（R5-U01）')
    L.append(r'  xlabel={$T$ / K}, ylabel={$-\mathrm{d}\theta/\mathrm{d}T$ / $10^{-3}\,\unit{K^{-1}}$},')
    L.append(r'  tick label style={font=\srcsize}, label style={font=\srcsize},')
    L.append(r'  title style={font=\srcsize},')
    L.append(r'  legend style={font=\srcsize, draw=none, fill=none},')
    L.append(r'  every axis plot/.append style={thick},')
    L.append(r']')
    entries_a = [r'$\beta=5$', r'$\beta=10$', r'$\beta=20$']
    entries_b = [r'$n=1$，拖尾', r'$n=2$，对称']
    specs = [
        ('blue', 'solid', entries_a[0], solve(5.0, 1, g)[1]),
        ('red', 'solid', entries_a[1], solve(10.0, 1, g)[1]),
        ('black', 'solid', entries_a[2], solve(20.0, 1, g)[1]),
        ('red', 'solid', entries_b[0], solve(10.0, 1, g)[1]),
        ('black', 'dashed', entries_b[1], solve(10.0, 2, g)[1]),
    ]
    panel = 0
    for k, (colour, dash, legend, col) in enumerate(specs):
        if k in (0, 3):
            titles = [r'(a) 升温速率（一级）', r'(b) 脱附级数（$\beta=10$）']
            L.append(r'\nextgroupplot[title={%s},' % titles[panel])
            # 每组图例单独一列、放在本面板正下方，避免两组图例横向相撞（R5-U01）
            L.append(r'  legend style={at={(0.5,-0.50)}, anchor=north, legend columns=1,')
            L.append(r'                nodes={inner sep=1pt}}]')
            panel += 1
        style = colour + (', dashed' if dash == 'dashed' else '')
        L.append(r'\addplot[%s, thick] table[row sep=\\, y index=1] {' % style)
        L.append(r'%%  T/K      -dtheta/dT / K^{-1}')
        for i, T in enumerate(g):
            L.append(r'  %.1f  %.5e \\' % (T, col[i]))
        L.append(r'};\addlegendentry{%s}' % legend)
    L.append(r'\end{groupplot}')
    L.append(r'\end{tikzpicture}')
    return '\n'.join(L) + '\n'


def emit():
    print(_fmt_block(), end='')


def patch(path=None):
    path = Path(path) if path else TEX_PATH
    tex = path.read_text(encoding='utf-8')
    begin_marker = '% 图源：解 Polanyi'
    end_marker = '\\end{tikzpicture}'
    if tex.count(begin_marker) != 1:
        raise SystemExit('patch: expected exactly one %r marker, found %d' % (begin_marker, tex.count(begin_marker)))
    lines = tex.splitlines(keepends=True)
    i0 = next(i for i, l in enumerate(lines) if begin_marker in l)
    i1 = next(i for i, l in enumerate(lines) if i > i0 and l.strip() == end_marker)
    new_lines = [l + '\n' for l in _fmt_block().rstrip('\n').split('\n')]
    out = ''.join(lines[:i0] + new_lines + lines[i1 + 1:])
    # 仓库约定入库一律 LF（.gitattributes: eol=lf）；Windows 下必须用二进制写，
    # 否则 write_text 会把全文翻成 CRLF，制造整文件级 diff 噪声。
    path.write_bytes(out.encode('utf-8'))
    print('patched %s: replaced lines %d-%d (%d -> %d lines)'
          % (path.relative_to(ROOT), i0 + 1, i1 + 1, i1 - i0 + 1, len(new_lines)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--coords', action='store_true', help='print addplot tables only')
    ap.add_argument('--emit', action='store_true', help='print the whole tikzpicture block')
    ap.add_argument('--patch', action='store_true', help='write the block back into ch05-a.tex')
    ap.add_argument('--tex', default=None, help='tex path for --patch (default chapters/parts/ch05-a.tex)')
    ap.add_argument('--check', action='store_true', help='verify embedded coordinates')
    ap.add_argument('--verify', action='store_true', help='independent numeric checks')
    a = ap.parse_args()
    if a.check:
        raise SystemExit(check())
    if a.verify:
        raise SystemExit(verify())
    if a.patch:
        patch(a.tex)
        raise SystemExit(0)
    if a.emit:
        emit()
        raise SystemExit(0)
    report()
