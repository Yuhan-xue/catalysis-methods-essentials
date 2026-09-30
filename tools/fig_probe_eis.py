# -*- coding: utf-8 -*-
"""图 11-5（ch11-d.tex 的三类等效电路 Nyquist 图）渲染核验探针。

背景：本仓库的维护会话没有视觉能力，图「画出来长什么样」无法用眼睛看。
本探针改用 PDF 自身的矢量图层（绘图算子 + 坐标）与文字层来核验三件事，
全部在 PDF 点坐标系内完成，不需要把点换算回数据坐标。

坐标系事实（实测，2026-09-30）：
  · 面板 (a) 轴框 = (137.0, 79.4)-(267.9, 210.3) pt，正方形 130.9×130.9，
    对应数据范围 x: 0→60 Ω、y: 0→60 Ω ⇒ 1 Ω = 2.1816 pt（两轴等比例，
    因为该 axis 写了 unit vector ratio=1 1 1）。
  · 面板 (b) 轴框 = (331.3, 82.3)-(496.3, 207.5) pt，对应 x: 0→300 Ω、y: 0→260 Ω。
  · pgfplots 画的路径**不带裁剪信息**（PyMuPDF 的 rect 是未裁剪几何），
    所以任何几何判断都必须先用轴框做显式裁剪，否则会把画在框外、
    读者看不到的部分算进来。

三项判据：
  P1 曲线形状：面板 (a) 里虚线（CPE 弧）可见部分的外接框，必须与模型一致。
     模型按 .tex 的解析式（u=Rct·Q·ωⁿ、θ=nπ/2）在该图**实际绘制的频率范围**内采样，
     再用轴框裁剪，算出「应该看得见的外接框」。这样换参数、换窗口、换 domain 都不会
     让判据失真（旧版把 10→60 Ω / 弧顶高度写死，一改 domain 就误报）。
     模型自检：u=1（ω=Rct·Q 的 −1/n 次方 = 2e4 rad/s）处必须恰好给出
     (Z', −Z'') = (60, 39.4168) Ω——这是与画图代码无关的解析锚点。
     把 ω 与 Q 的幂次写错、或 PGF 三角函数把弧度当角度，可见高会掉到 ≈1 pt（近乎压平）。
  P2 标记落线：面板 (a) 每个小填充标记（mark=*、mark=square*）的中心，
     到该面板任一曲线可见折线的最小距离必须 <= --mark-tol 点。
  P3 标注可见：落在轴框内的文字块不得与曲线可见段相交（线条穿字），
     并检查面板字母 (a)/(b) 是否出现在图内文字层里。

用法：
  python tools/fig_probe_eis.py --pdf build/main.pdf
  python tools/fig_probe_eis.py --pdf build/main.pdf --json build/r3/eis_fig.json --out build/r3/eis_fig.txt
退出码：0 全部通过 / 1 有 FAIL / 2 无法检查（找不到图或轴框）
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

try:
    import pymupdf as fitz
except ImportError:  # 旧版 PyMuPDF 只提供 fitz 名字
    import fitz

CAPTION_KEY = "三类等效电路的 Nyquist 图对照"
PANEL_LETTERS = ("(a)", "(b)")

# 模型参数：与 chapters/parts/ch11-d.tex 的 declare function 区同式
CPE_N = 0.85
CPE_RS, CPE_RCT, CPE_CDL = 10.0, 100.0, 0.5e-6
CPE_Q = CPE_CDL ** CPE_N * CPE_RCT ** (CPE_N - 1.0)    # = 2.2086e-6 S·s^n
CPE_PEAK_Z2 = 39.4168          # Ω，弧顶纵坐标（u=1 的解析值，模型自检用）
CPE_LOG10F_DRAWN = (0.3, 4.9)  # .tex 里虚线 CPE 弧的 domain（log10 f / Hz）
AXIS_A_XMAX, AXIS_A_YMAX = 62.0, 62.0
RATIO_TOL = 0.05
WIDTH_TOL_FRAC = 0.04          # 可见宽容差 = 轴宽的 4%
HEIGHT_TOL_FRAC = 0.03         # 可见高容差 = 轴高的 3%
MARK_TOL_PT = 3.0
MIN_SEG_PT = 5.0               # 短于此的线段视为刻度等装饰，不参与相交判断
MIN_CURVE_PT = 40.0            # 可视长度大于此才算「数据曲线」，用于 P1


def cpe_z(omega):
    """CPE（R_ct ∥ Q）串 R_Ω 的阻抗，返回 (Z', -Z'') / Ω。与 .tex 的 dcpx/dcpy 同式。"""
    u = CPE_RCT * CPE_Q * omega ** CPE_N
    th = CPE_N * math.pi / 2.0
    a = 1.0 + u * math.cos(th)
    d = u * math.sin(th)
    den = a * a + d * d
    return CPE_RS + CPE_RCT * a / den, CPE_RCT * d / den


def expected_cpe_bbox_ohm():
    """按 .tex 的绘制频率范围采样、裁到 (0..xmax, 0..ymax) 内，返回可见外接框（Ω）。"""
    lo, hi = CPE_LOG10F_DRAWN
    xs, ys = [], []
    for i in range(2001):
        omega = 2.0 * math.pi * 10.0 ** (lo + (hi - lo) * i / 2000.0)
        x, y = cpe_z(omega)
        if 0.0 <= x <= AXIS_A_XMAX and 0.0 <= y <= AXIS_A_YMAX:
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return min(xs), max(xs), min(ys), max(ys)


def is_dashed(dashes) -> bool:
    if not dashes:
        return False
    s = str(dashes)
    head = s.split("]")[0]
    return any(c.isdigit() and c != "0" for c in head)


def item_segments(d):
    """把 drawing 展开成真实曲线段（只取 l 与 c 算子；re/qu 是轴框、图例框等家具）。

    例外：标记符号（mark=square* 之类）本身就是个很小的 re/qu 填充块，
    尺寸在几个点以内，必须保留，否则标记会被整条丢掉。
    """
    segs = []
    tiny = d["rect"].width < 6 and d["rect"].height < 6
    for it in d["items"]:
        op = it[0]
        if op == "l":
            segs.append((it[1], it[2]))
        elif op == "c":
            segs.append((it[1], it[4]))  # 贝塞尔只取端点，够用于相交与距离近似
        elif op in ("re", "qu") and tiny:
            r = fitz.Rect(it[1])
            if op == "qu":
                r = fitz.Rect(it[1].ul, it[1].lr)
            segs.append((r.tl, r.br))
    return segs


def clip_seg(p, q, rect):
    """Liang-Barsky：把线段裁剪到矩形，返回裁剪后的 (p, q) 或 None。"""
    x0, y0, x1, y1 = rect
    px, py = p[0], p[1]
    qx, qy = q[0], q[1]
    dx, dy = qx - px, qy - py
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, px - x0), (dx, x1 - px), (-dy, py - y0), (dy, y1 - py)):
        if abs(pp) < 1e-12:
            if qq < 0:
                return None
            continue
        r = qq / pp
        if pp < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return None
    return ((px + t0 * dx, py + t0 * dy), (px + t1 * dx, py + t1 * dy))


def seg_len(s):
    (ax, ay), (bx, by) = s
    return ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5


def seg_rect_intersect(p, q, rect, pad=0.0):
    r = (rect[0] - pad, rect[1] - pad, rect[2] + pad, rect[3] + pad)
    return clip_seg(p, q, r) is not None


def pt_seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    den = vx * vx + vy * vy
    t = 0.0 if den == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / den))
    return ((px - (ax + t * vx)) ** 2 + (py - (ay + t * vy)) ** 2) ** 0.5


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--json", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--mark-tol", type=float, default=MARK_TOL_PT)
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    page = None
    cap_rect = None
    # 排版会在中西文之间插入或不插入空格（实测渲染成「三类等效电路的Nyquist 图对照」），
    # 所以匹配前剥掉所有空白，否则 search_for / 精确匹配都会漏。
    key = "".join(CAPTION_KEY.split())
    for pno in range(doc.page_count):
        pg = doc[pno]
        found = None
        for b in pg.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for line in b.get("lines", []):
                s = "".join(sp["text"] for sp in line.get("spans", []))
                if key in "".join(s.split()):
                    found = fitz.Rect(line["bbox"])
                    break
            if found is not None:
                break
        if found is not None:
            page, cap_rect = pg, found
            break
    if page is None:
        print("UNUSABLE: caption key not found in %s" % args.pdf)
        return 2

    draws = [d for d in page.get_drawings() if d["rect"].y1 <= cap_rect.y0 + 3]
    # 轴框 = 大尺寸的 re/qu 描边矩形（pgfplots 的 axis frame）
    frames = []
    for d in draws:
        r = d["rect"]
        if r.width > 50 and r.height > 50 and any(it[0] in ("re", "qu") for it in d["items"]):
            frames.append((r.x0, r.y0, r.x1, r.y1))
    if len(frames) < 2:
        print("UNUSABLE: expected >=2 axis frames above the caption, found %d" % len(frames))
        return 2
    frames.sort(key=lambda f: f[0])
    fa, fb = frames[0], frames[1]

    report = {"pdf": os.path.basename(args.pdf), "page": page.number + 1,
              "caption_top": round(cap_rect.y0, 1), "frame_a": [round(v, 1) for v in fa],
              "frame_b": [round(v, 1) for v in fb], "checks": {}, "fail": [], "info": {}}

    def fail(code, msg):
        report["fail"].append({"code": code, "msg": msg})

    # 模型自检：先把「模型自己算得对不对」验掉，再谈 PDF 画得对不对。
    _sx, _sy = cpe_z(2.0e4)
    report["info"]["model_selfcheck"] = {"omega": 2.0e4, "z_re": round(_sx, 6),
                                         "minus_z_im": round(_sy, 6),
                                         "expect": [60.0, CPE_PEAK_Z2]}
    if abs(_sx - 60.0) > 1e-3 or abs(_sy - CPE_PEAK_Z2) > 1e-3:
        sys.stdout.write("UNUSABLE: model self-check failed: cpe_z(2e4) = (%.6f, %.6f)\n"
                         % (_sx, _sy))
        return 2

    # 每条 drawing 归属哪个面板：按「在哪个轴框内的可见长度更长」判定
    panels = {"a": [], "b": []}
    for d in draws:
        segs = item_segments(d)
        if not segs:
            continue
        clipped = {}
        for key_p, fr in (("a", fa), ("b", fb)):
            cs = [c for c in (clip_seg(p, q, fr) for p, q in segs) if c]
            clipped[key_p] = cs
        la = sum(seg_len(s) for s in clipped["a"])
        lb = sum(seg_len(s) for s in clipped["b"])
        which = "a" if la >= lb else "b"
        if max(la, lb) <= 0:
            continue
        panels[which].append({"dashes": is_dashed(d.get("dashes")), "segments": clipped[which],
                              "rect": [round(v, 1) for v in d["rect"]],
                              "n_items": len(d["items"]), "fill": d.get("fill") is not None,
                              "vis_len": round(max(la, lb), 1),
                              "raw_rect": [round(v, 1) for v in (d["rect"].x0, d["rect"].y0,
                                                                 d["rect"].x1, d["rect"].y1)]})
    report["info"]["panel_a_paths"] = len(panels["a"])
    report["info"]["panel_b_paths"] = len(panels["b"])

    # --- P1 曲线形状 ---
    wide_dashed = [p for p in panels["a"] if p["dashes"] and p["vis_len"] >= MIN_CURVE_PT]
    report["info"]["panel_a_dashed_curves"] = len(wide_dashed)
    if len(wide_dashed) != 1:
        fail("P1", "panel (a): expected exactly 1 dashed curve with visible length >= %.0f pt, found %d"
             % (MIN_CURVE_PT, len(wide_dashed)))
    else:
        pts = [pt for s in wide_dashed[0]["segments"] for pt in s]
        w = max(p[0] for p in pts) - min(p[0] for p in pts)
        h = max(p[1] for p in pts) - min(p[1] for p in pts)
        frame_h = fa[3] - fa[1]
        ratio = h / w if w else 0.0
        box = expected_cpe_bbox_ohm()
        if box:
            bx0, bx1, by0, by1 = box
            exp_w = (bx1 - bx0) / AXIS_A_XMAX * (fa[2] - fa[0])
            exp_h = (by1 - by0) / AXIS_A_YMAX * frame_h
        else:
            exp_w, exp_h = 0.0, 0.0
        exp_ratio = exp_h / exp_w if exp_w else 0.0
        report["checks"]["P1_cpe_visible_bbox"] = {
            "visible_w_pt": round(w, 2), "visible_h_pt": round(h, 2), "ratio": round(ratio, 4),
            "expected": {"w_pt": round(exp_w, 2), "h_pt": round(exp_h, 2), "ratio": round(exp_ratio, 4)},
            "tols": {"ratio": RATIO_TOL, "height_frac": HEIGHT_TOL_FRAC}}
        if abs(ratio - exp_ratio) > RATIO_TOL:
            fail("P1", "CPE arc visible bbox ratio %.4f vs model %.4f (flat/degenerate curve?)"
                 % (ratio, exp_ratio))
        if abs(w - exp_w) > WIDTH_TOL_FRAC * (fa[2] - fa[0]):
            fail("P1", "CPE arc visible width %.2f pt vs model %.2f pt (+-%.1f)"
                 % (w, exp_w, WIDTH_TOL_FRAC * (fa[2] - fa[0])))
        if abs(h - exp_h) > HEIGHT_TOL_FRAC * frame_h:
            fail("P1", "CPE arc visible height %.2f pt vs model %.2f pt (+-%.1f)"
                 % (h, exp_h, HEIGHT_TOL_FRAC * frame_h))

    # --- P2 标记落线 ---
    # 只看「数据曲线」级的 drawing（可见长度 >= MIN_CURVE_PT），并且**不做短段过滤**：
    # 虚线的每一节 dash 只有约 3 pt，若按 MIN_SEG_PT=5 过滤，整条 CPE 弧会被从判据
    # 里删掉，落在 CPE 弧上的标记就只能去跟另一条弧比距离（实测假 FAIL 22.32 pt）。
    marks = [p for p in panels["a"] if p["fill"] and p["n_items"] <= 4 and p["vis_len"] <= 8]
    curve_paths = [p for p in panels["a"] if not p["fill"] and p["vis_len"] >= MIN_CURVE_PT]
    all_segs = [s for p in curve_paths for s in p["segments"]]
    report["info"]["panel_a_curve_paths"] = len(curve_paths)
    mark_res = []
    for p in marks:
        xs = [pt[0] for s in p["segments"] for pt in s]
        ys = [pt[1] for s in p["segments"] for pt in s]
        c = (sum(xs) / len(xs), sum(ys) / len(ys))
        best = min((pt_seg_dist(c, s[0], s[1]) for s in all_segs), default=1e9)
        mark_res.append({"center": [round(c[0], 2), round(c[1], 2)], "dist_to_curve_pt": round(best, 3)})
        if best > args.mark_tol:
            fail("P2", "marker at (%.1f, %.1f) is %.2f pt away from any curve (tol %.1f)"
                 % (c[0], c[1], best, args.mark_tol))
    report["checks"]["P2_markers"] = {"n": len(marks), "tol_pt": args.mark_tol, "marks": mark_res}
    if not marks:
        fail("P2", "no filled markers found in panel (a)")

    # --- P3 文字与曲线 ---
    def in_frames(r):
        return any(r.intersects(fitz.Rect(fr)) for fr in (fa, fb))

    text_blocks = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        r = fitz.Rect(b["bbox"])
        if not in_frames(r):
            continue
        snippet = "".join(sp["text"] for l in b.get("lines", []) for sp in l.get("spans", [])).strip()
        text_blocks.append({"rect": [round(v, 1) for v in r], "text": snippet[:70]})
    crossed = []
    for tb in text_blocks:
        r = tb["rect"]
        for panel in ("a", "b"):
            for p in panels[panel]:
                if p["fill"]:
                    continue  # 标记不是线
                for s in p["segments"]:
                    if seg_len(s) < MIN_SEG_PT:
                        continue
                    if seg_rect_intersect(s[0], s[1], r, pad=0.5):
                        crossed.append({"panel": panel, "text": tb["text"][:40],
                                        "segment": [[round(v, 1) for v in s[0]],
                                                    [round(v, 1) for v in s[1]]]})
                        break
                else:
                    continue
                break
            else:
                continue
            break
    joined = " ".join(tb["text"] for tb in text_blocks)
    missing_letters = [L for L in PANEL_LETTERS if L not in joined]
    report["checks"]["P3_text"] = {"n_blocks": len(text_blocks), "blocks": text_blocks,
                                   "text_curve_intersections": crossed,
                                   "panel_letters_present": [L for L in PANEL_LETTERS if L in joined],
                                   "panel_letters_missing": missing_letters}
    if crossed:
        fail("P3", "%d text block(s) crossed by curves" % len(crossed))
    if missing_letters:
        fail("P3", "panel letter(s) missing inside the figure area: %s" % ", ".join(missing_letters))

    report["ok"] = not report["fail"]

    lines = ["fig 11-5 render probe: %s" % ("PASS" if report["ok"] else "FAIL")]
    lines.append("pdf=%s page=%d frame_a=%s frame_b=%s" % (os.path.basename(args.pdf), report["page"],
                                                           report["frame_a"], report["frame_b"]))
    c1 = report["checks"].get("P1_cpe_visible_bbox")
    if c1:
        lines.append("P1 CPE visible bbox %.2f x %.2f pt ratio=%.4f (model %.2f x %.2f pt ratio=%.4f)"
                     % (c1["visible_w_pt"], c1["visible_h_pt"], c1["ratio"],
                        c1["expected"]["w_pt"], c1["expected"]["h_pt"], c1["expected"]["ratio"]))
    c2 = report["checks"]["P2_markers"]
    lines.append("P2 markers n=%d tol=%.1fpt %s" % (c2["n"], c2["tol_pt"],
                 " ".join("d=%.2fpt" % m["dist_to_curve_pt"] for m in c2["marks"])))
    c3 = report["checks"]["P3_text"]
    lines.append("P3 text blocks=%d crossings=%d letters_missing=%s"
                 % (c3["n_blocks"], len(c3["text_curve_intersections"]), c3["panel_letters_missing"]))
    for f in report["fail"]:
        lines.append("FAIL %s: %s" % (f["code"], f["msg"]))
    for x in c3["text_curve_intersections"][:8]:
        lines.append("  crossed(p%s): %s at %s" % (x["panel"], x["text"][:36], x["segment"]))
    text = "\n".join(lines) + "\n"

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    sys.stdout.write("".join(l + "\n" for l in lines if all(ord(ch) < 128 for ch in l)))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
