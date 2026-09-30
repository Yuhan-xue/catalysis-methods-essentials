# -*- coding: utf-8 -*-
"""图 3-x（ch03-b.tex 的 TG/DTG 模型曲线）坐标生成器。

第三轮把 TG/DTG 示意曲线换成一级速率方程的积分曲线，但生成脚本只放在被 .gitignore
忽略的 build/r3/recompute_ch03b_dtg.py，干净检出无法重现（R4-W02）。本文件把生成逻辑
纳入受版本管理的 tools/，输入参数、采样规则与容差全部可追踪。

模型（与 chapters/parts/ch03-b.tex 的注释一致）
    d(alpha)/dT = (A/beta) * exp(-E/(R T)) * (1-alpha),  alpha(300 K) = 0
    TG(T)  = 100 - 20*alpha(T)
    DTG(T) = -dm/dT = 20*d(alpha)/dT
四条曲线共用同一组 E 与 A：E = 180 kJ/mol，A 由 beta = 5 K/min 时 Tp = 673.000 K 定出
    A = 5*E/(R*673^2) * exp(E/(R*673))。

采样规则（对每个 beta 相同）
    x = 排序去重( [523, 545, 568, 585]            # 低温平台粗采样
                + 595:2.5:770                      # 反应区间细采样
                + [780, 795, 810, 823]             # 高温平台粗采样
                + {Tp-3, Tp, Tp+3} )               # 精确峰温节点
    其中 Tp 由 A/beta*exp(-E/(R*Tp)) = E/(R*Tp^2) 解出；峰节点保证画出的峰位就是模型峰位。
每组点数两分量相同，八组共 654 点（TG 4 组 + DTG 4 组；与 .tex 内嵌坐标一致）。

容差与判据
    --check（默认）逐点比对 .tex 内嵌坐标：x 容差 1e-6 K，TG 容差 2e-4 %，
    DTG 容差 1e-5 %/K（内嵌值分别按 4/5 位小数打印）。容差按内嵌坐标的打印精度
    与原生成器精度设定：本题实测最大偏差 TG 1.02e-4 %、DTG 5.0e-6 %/K，与 R4 独立复算
    （reviews/2026-09-30-round4/verification.json）一致，x 逐点相等。任一组点数不符或超差即 FAIL。
    --emit 打印可粘贴回 .tex 的 coordinates 块；参数与采样规则改动后请同步正文峰值表。

用法（仓库根目录；需要 numpy/scipy）
    python tools/recompute_ch03b_dtg.py                 # 复算并与 .tex 比对
    python tools/recompute_ch03b_dtg.py --json build/r4/ch03b_dtg.json
    python tools/recompute_ch03b_dtg.py --emit          # 输出坐标块
退出码：0 一致 / 1 超差 / 2 输入或环境错误。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "chapters" / "parts" / "ch03-b.tex"

R_GAS = 8.314462618        # J/(mol K)
E_A = 180000.0             # J/mol
T_REF = 673.0              # K，beta=5 时的模型峰温
T0 = 300.0                 # K，积分起点
BETAS = (2.5, 5.0, 10.0, 20.0)

COARSE_LEFT = (523.0, 545.0, 568.0, 585.0)
FINE_LO, FINE_HI, FINE_STEP = 595.0, 770.0, 2.5
COARSE_RIGHT = (780.0, 795.0, 810.0, 823.0)
PEAK_OFFSETS = (-3.0, 0.0, 3.0)

X_TOL = 1e-6               # K（x 与内嵌值逐点相等）
TG_TOL = 2e-4              # %（内嵌值 4 位小数；与原生成器的实测最大偏差 1.02e-4）
DTG_TOL = 1e-5             # %/K（内嵌值 5 位小数；实测最大偏差 5.0e-6）


def pre_exponential() -> float:
    """由 beta=5 时 Tp=673.000 K 定出的 A（1/min）。"""
    return 5.0 * E_A / (R_GAS * T_REF ** 2) * math.exp(E_A / (R_GAS * T_REF))


A_PRE = pre_exponential()


def alpha(T: float, beta: float) -> float:
    h = quad(lambda t: A_PRE / beta * math.exp(-E_A / (R_GAS * t)), T0, T, epsabs=1e-12)[0]
    return -math.expm1(-h)


def dalpha_dT(T: float, beta: float) -> float:
    return A_PRE / beta * math.exp(-E_A / (R_GAS * T)) * (1.0 - alpha(T, beta))


def peak_T(beta: float) -> float:
    f = lambda t: A_PRE / beta * math.exp(-E_A / (R_GAS * t)) - E_A / (R_GAS * t * t)
    return brentq(f, T0, T0 + 700.0)


def x_grid(beta: float) -> list[float]:
    tp = peak_T(beta)
    xs = list(COARSE_LEFT)
    n = int(round((FINE_HI - FINE_LO) / FINE_STEP))
    xs += [FINE_LO + FINE_STEP * i for i in range(n + 1)]
    xs += list(COARSE_RIGHT)
    xs += [tp + d for d in PEAK_OFFSETS]
    # 峰温节点按 .tex 内嵌坐标的打印精度取到 3 位小数；基础栅格本就精确，不受影响。
    return sorted(set(round(x, 3) for x in xs))


def fmt_x(v: float) -> str:
    s = ("%.3f" % round(v, 3)).rstrip("0")
    return s[:-1] if s.endswith(".") else s


def block(beta: float, panel: str) -> list[tuple[float, float]]:
    pts = []
    for x in x_grid(beta):
        y = 100.0 - 20.0 * alpha(x, beta) if panel == "TG" else 20.0 * dalpha_dT(x, beta)
        pts.append((x, y))
    return pts


def format_block(pts, panel: str) -> str:
    out = []
    for x, y in pts:
        ys = ("%.4f" % y) if panel == "TG" else ("%.5f" % y)
        out.append("(%s,%s)" % (fmt_x(x), ys))
    return " ".join(out)


PLOT_RE = re.compile(r"\\addplot[^;]*?coordinates\s*\{(.*?)\};", re.S)
PAIR_RE = re.compile(r"\(([0-9.]+),([0-9.]+)\)")


def embedded_blocks():
    tex = TEX.read_text(encoding="utf-8")
    blocks = PLOT_RE.findall(tex)
    if len(blocks) != 8:
        raise SystemExit("FAIL: expected 8 coordinate blocks in %s, found %d"
                         % (TEX, len(blocks)))
    parsed = []
    for i, b in enumerate(blocks):
        pts = [(float(a), float(c)) for a, c in PAIR_RE.findall(b)]
        parsed.append({"panel": "TG" if i < 4 else "DTG", "beta": BETAS[i % 4], "points": pts})
    return parsed


def check() -> int:
    emb = embedded_blocks()
    report = {"tex": str(TEX.relative_to(ROOT)), "params": {"E_J_per_mol": E_A, "A_per_min": A_PRE,
              "T0_K": T0, "T_ref_K": T_REF}, "groups": [], "fail": []}
    total = 0
    for i, e in enumerate(emb):
        gen = block(e["beta"], e["panel"])
        total += len(gen)
        row = {"panel": e["panel"], "beta": e["beta"], "n_expected": len(e["points"]),
               "n_generated": len(gen)}
        if len(gen) != len(e["points"]):
            report["fail"].append("group %d (%s beta=%s): %d generated vs %d embedded"
                                  % (i, e["panel"], e["beta"], len(gen), len(e["points"])))
            report["groups"].append(row)
            continue
        max_dx = max(abs(g[0] - p[0]) for g, p in zip(gen, e["points"]))
        tol = TG_TOL if e["panel"] == "TG" else DTG_TOL
        max_dy = max(abs(g[1] - p[1]) for g, p in zip(gen, e["points"]))
        row.update({"max_dx_K": max_dx, "max_dy": max_dy, "dy_tol": tol,
                    "peak_T_K": peak_T(e["beta"])})
        report["groups"].append(row)
        if max_dx > X_TOL:
            report["fail"].append("group %d: x mismatch %.3e > %.1e" % (i, max_dx, X_TOL))
        if max_dy > tol:
            report["fail"].append("group %d: y mismatch %.3e > %.1e" % (i, max_dy, tol))
    report["total_points"] = total
    report["ok"] = not report["fail"]
    return (0 if report["ok"] else 1), report


def emit() -> int:
    for beta in BETAS:
        for panel in ("TG", "DTG"):
            print("%% %s : beta = %s K/min, Tp = %.3f K" % (panel, beta, peak_T(beta)))
            print("%s" % format_block(block(beta, panel), panel))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true", help="打印坐标块而不是比对")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    if args.emit:
        return emit()

    code, report = check()
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    print("ch03b TG/DTG generator: %s" % ("PASS" if code == 0 else "FAIL"))
    print("  params: E=%g J/mol A=%.6f /min T0=%g K T_ref=%g K"
          % (E_A, A_PRE, T0, T_REF))
    for row in report["groups"]:
        print("  %-3s beta=%-5s n=%3d max_dx=%.2e max_dy=%.2e (tol %.0e)"
              % (row["panel"], row["beta"], row["n_generated"], row.get("max_dx_K", float("nan")),
                 row.get("max_dy", float("nan")), row.get("dy_tol", float("nan"))))
    print("  total points: %d" % report["total_points"])
    for f in report["fail"]:
        print("  FAIL %s" % f)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
