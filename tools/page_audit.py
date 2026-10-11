# -*- coding: utf-8 -*-
r"""Whole-book per-page structural audit (goal: page-by-page acceptance).

Purpose
-------
The release gate checks aggregate counters (errors / overfull>5pt / missing
glyphs / undefined refs / dup labels / dup includes / overlap).  Those are
book-wide sums: a defect that is invisible to the LaTeX log (bad float
placement, a page whose body runs into the footer, a heading left alone at
the bottom of a page, a page that is accidentally near-empty, a duplicated
text block from a bad \input) never shows up in them.

This tool walks every page of the built PDF and derives one row of objective
measurements per page, so the page-by-page acceptance ledger can be built
from data instead of impressions.

Reference frame ("banxin") is taken from style/preamble.tex:
    a4paper, inner=25mm, outer=20mm, top=18mm, bottom=18mm,
    includeheadfoot, headheight=11pt, headsep=4mm, footskip=6mm
twoside => inner margin alternates (odd pages recto).

Checks per page
---------------
  chars        body characters (text outside header/footer zones)
  lines        body lines
  y_tail       body_bottom - max(y1)      : bottom whitespace (0 = full page)
  rowl/rowr    body_left - min(x0)  and  max(x1) - body_right  (negative = OK)
  ink_out      count of drawings/images extending past the inner frame by >tol
  gap_max      largest vertical gap between consecutive body lines (pt)
  gap_ct       same, but over text + in-frame vector/raster content. A float
               filling mid-page closes the hole text-only gap_max reports:
               measured on this book p192/p200 = 64.3/88.3 (text) vs
               22.0/31.5 (content), while real bottom-float bands on
               p8/p93/p104/p110/p245 stay 138.0/105.4/158.0/176.3/133.9.
  orphan       heading near the page bottom with < --min-follow body lines
  dup_lines    body lines whose normalised text appears >= 2 times on the page
  tofu         count of U+FFFD replacement characters
  no_head      running head missing
  no_folio     page number (footer) missing
  imgs/draws   raster images / vector drawings

Outputs
-------
  --csv   one row per page (UTF-8, all metrics)
  --md    ranked anomaly list for human triage
  --json  machine-readable summary + rows

Usage
-----
  python tools/page_audit.py --pdf build/main.pdf \
      --csv build/page_audit.csv --md build/page_audit.md --json build/page_audit.json

Exit codes: 0 = audit produced (informational), 2 = prerequisite missing.
Console output is ASCII-safe; Chinese detail goes to the files.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover
    import fitz

MM = 72.0 / 25.4
GEOM = {
    "inner": 25.0 * MM,
    "outer": 20.0 * MM,
    "top": 18.0 * MM,
    "bottom": 18.0 * MM,
    "headheight": 11.0,
    "headsep": 4.0 * MM,
    "footskip": 6.0 * MM,
}

HEAD_RE = re.compile(r"^\s*(?:\d+(?:\.\d+){0,3})\s*\S")
SPACE_RE = re.compile(r"\s+")

# xeCJK default PunctStyle=CJK permits "hanging punctuation" (biao dian xuan gua):
# closing punctuation may protrude into the right margin at a line end, and
# opening punctuation may be outdented into the left margin at a line start.
# Such protrusion is typographic by design -- LaTeX does not count it as an
# overfull box (this book's log has 0 overfull hboxes) -- so it must be
# reported separately from real text-past-frame defects.
PUNCT_R = frozenset(
    [
        0x3001, 0x3002, 0xFF0C, 0xFF0E, 0xFF1B, 0xFF1A, 0xFF01, 0xFF1F,
        0xFF09, 0x3009, 0x300B, 0x300D, 0x300F, 0x3011, 0x3015, 0x3017,
        0x3019, 0x301B, 0x201D, 0x2019, 0xFF3D, 0xFF5D, 0x3005, 0xFF0F,
        0x2026, 0xFF64, 0x00B7,
    ]
)
PUNCT_L = frozenset(
    [
        0x3008, 0x300A, 0x300C, 0x300E, 0x3010, 0x3014, 0x3016, 0x3018,
        0x301A, 0xFF08, 0xFF3B, 0xFF5B, 0x201C, 0x2018, 0xFF62, 0x3005,
    ]
)

# Sub-tolerance edge offsets are reported as info only. Report floor: raw
# PyMuPDF glyph bboxes carry ~0.002pt of float noise, which would otherwise
# turn ~114 pages of pure noise into "edge offset" rows once the value is
# merely > 0.0. 0.05pt = 0.018mm is far below anything printable.
EDGE_MIN = 0.05


def edge_char(text, side):
    """First (side='l') / last (side='r') non-space char of a line, as int."""
    s = text.strip()
    if not s:
        return -1
    return ord(s[0] if side == "l" else s[-1])


def body_frame(width, height, page_no):
    """Return (left, top, right, bottom) of the text body for this page."""
    odd = (page_no % 2 == 1)
    left = GEOM["inner"] if odd else GEOM["outer"]
    right = width - (GEOM["outer"] if odd else GEOM["inner"])
    top = GEOM["top"] + GEOM["headheight"] + GEOM["headsep"]
    bottom = height - GEOM["bottom"] - GEOM["footskip"]
    return (left, top, right, bottom)


def zones(height):
    head_bottom = GEOM["top"] + GEOM["headheight"] + 1.0
    foot_top = height - GEOM["bottom"] - GEOM["footskip"] - 1.0
    return head_bottom, foot_top


def collect_lines(page):
    """Return list of dicts for every text line on the page."""
    out = []
    d = page.get_text("dict")
    for blk in d.get("blocks", []):
        if blk.get("type", 0) != 0:
            continue
        for ln in blk.get("lines", []):
            spans = ln.get("spans", [])
            if not spans:
                continue
            text = "".join(s.get("text", "") for s in spans)
            if not text.strip():
                continue
            size = max(float(s.get("size", 0.0)) for s in spans)
            bold = any(bool(int(s.get("flags", 0)) & 16) for s in spans)
            out.append(
                {
                    "text": text,
                    "x0": float(ln["bbox"][0]),
                    "y0": float(ln["bbox"][1]),
                    "x1": float(ln["bbox"][2]),
                    "y1": float(ln["bbox"][3]),
                    "size": size,
                    "bold": bold,
                }
            )
    out.sort(key=lambda r: (round(r["y0"], 1), r["x0"]))
    return out


def _max_gap(items):
    """Largest vertical hole over a set of (y0, y1) bands.

    Vertical neighbours that overlap merge into one band, so a paragraph
    sitting beside a float never reads as a hole. This is the content-aware
    companion to the text-only gap: a float filling the middle of a page
    closes the hole it would otherwise look like.
    """
    ys = sorted((float(a), float(b)) for a, b in items)
    if not ys:
        return 0.0
    best = 0.0
    cur_end = ys[0][1]
    for y0, y1 in ys[1:]:
        if y0 > cur_end:
            g = y0 - cur_end
            if g > best:
                best = g
            cur_end = y1
        elif y1 > cur_end:
            cur_end = y1
    return best


def audit_page(page, page_no, min_follow, tol):
    w, h = page.rect.width, page.rect.height
    left, top, right, bottom = body_frame(w, h, page_no)
    head_bottom, foot_top = zones(h)
    lines = collect_lines(page)

    body = [r for r in lines if r["y0"] >= top - 4.0 and r["y1"] <= bottom + 8.0]
    heads = [r for r in lines if r["y1"] <= head_bottom + 1.0]
    foots = [r for r in lines if r["y0"] >= foot_top - 1.0]

    row = {
        "page": page_no,
        "chars": sum(len(r["text"].strip()) for r in body),
        "lines": len(body),
        "draws": 0,
        "imgs": 0,
        "ink_out": 0,
        "tofu": 0,
        "no_head": 0,
        "no_folio": 0,
        "gap_max": 0.0,
        "gap_ct": 0.0,
        "y_tail": 0.0,
        "rowl": -1.0,
        "rowr": -1.0,
        "hang_l": 0.0,
        "hang_r": 0.0,
        "edge_l": 0.0,
        "edge_r": 0.0,
        "y_hi": 0.0,
        "orphan": 0,
        "orphan_txt": "",
        "dup_lines": 0,
        "dup_over": 0,
        "dup_txt": "",
        "x0": 0.0,
        "x1": 0.0,
        "y0": 0.0,
        "y1": 0.0,
    }

    for r in body:
        row["tofu"] += r["text"].count("\ufffd")

    if body:
        row["x0"] = min(r["x0"] for r in body)
        row["x1"] = max(r["x1"] for r in body)
        row["y0"] = min(r["y0"] for r in body)
        row["y1"] = max(r["y1"] for r in body)
        row["rowl"] = left - row["x0"]
        row["rowr"] = row["x1"] - right
        row["y_tail"] = bottom - row["y1"]
        row["y_hi"] = top - row["y0"]

        # Split edge protrusion into design (hanging punctuation) vs defect.
        # The extreme line on each side decides: if the protruding character is
        # hanging punctuation the protrusion is typographic, not an overflow.
        if row["rowr"] > 0.0:
            extreme_r = max(body, key=lambda r: r["x1"])
            if edge_char(extreme_r["text"], "r") in PUNCT_R:
                row["hang_r"] = row["rowr"]
                row["rowr"] = -1.0
        if row["rowl"] > 0.0:
            extreme_l = min(body, key=lambda r: r["x0"])
            if edge_char(extreme_l["text"], "l") in PUNCT_L:
                row["hang_l"] = row["rowl"]
                row["rowl"] = -1.0

        # Offsets within tol are measurement/centring level, not defects.
        # Measured example: a longtable 1.84pt narrower than \textwidth centres
        # its \textwidth-wide caption on the table, pushing it out by 0.92pt
        # (p160, four caption lines). 0.92pt = 0.32mm, i.e. invisible.
        if 0.0 < row["rowr"] <= tol:
            row["edge_r"] = row["rowr"]
            row["rowr"] = -1.0
        if 0.0 < row["rowl"] <= tol:
            row["edge_l"] = row["rowl"]
            row["rowl"] = -1.0

        # largest vertical gap between consecutive body lines that overlap in x
        prev = None
        for r in body:
            if prev is not None:
                xov = min(prev["x1"], r["x1"]) - max(prev["x0"], r["x0"])
                if xov > 0.0:
                    g = r["y0"] - prev["y1"]
                    if g > row["gap_max"]:
                        row["gap_max"] = g
            prev = r

        # repeated lines: informational. `dup_lines` counts repeated normalised
        # text (table cells sharing a row, TOC leaders, axis labels, math
        # fragments all repeat legitimately). `dup_over` counts the subset that
        # is a true OVERPRINT: identical text whose boxes overlap in BOTH axes,
        # which is what a bad \input or a doubled typesetting pass looks like.
        seen = {}
        for r in body:
            key = SPACE_RE.sub("", r["text"])
            if len(key) < 4:
                continue
            seen.setdefault(key, []).append(r)
        rows = [v for v in seen.values() if len(v) >= 2]
        row["dup_lines"] = len(rows)
        over = 0
        for occ in rows:
            hit = False
            for i in range(len(occ)):
                for j in range(i + 1, len(occ)):
                    a, b = occ[i], occ[j]
                    ox = min(a["x1"], b["x1"]) - max(a["x0"], b["x0"])
                    oy = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
                    wa = min(a["x1"] - a["x0"], b["x1"] - b["x0"])
                    ha = min(a["y1"] - a["y0"], b["y1"] - b["y0"])
                    if wa > 0.0 and ha > 0.0 and ox / wa > 0.5 and oy / ha > 0.5:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                over += 1
                if not row["dup_txt"]:
                    row["dup_txt"] = occ[0]["text"].strip()[:60]
        row["dup_over"] = over

        # heading orphan: heading in the lower part of the body with too few
        # body lines after it
        low = top + 0.70 * (bottom - top)
        cands = [
            r
            for r in body
            if r["y0"] >= low
            and (r["size"] >= 11.0 or (r["bold"] and r["size"] >= 10.0))
            and HEAD_RE.match(r["text"]) is not None
        ]
        if cands:
            hd = cands[-1]
            after = [r for r in body if r["y0"] > hd["y1"] + 1.0]
            if len(after) < min_follow:
                row["orphan"] = 1
                row["orphan_txt"] = hd["text"].strip()[:60]

    row["no_head"] = 0 if any(r["text"].strip() for r in heads) else 1
    row["no_folio"] = 0 if any(r["text"].strip() for r in foots) else 1

    # vector drawings and raster images outside the frame. The same single
    # pass feeds the content-aware gap: text-only gap_max reports a hole
    # wherever a figure or table fills the page between two text blocks.
    citems = [(r["y0"], r["y1"]) for r in body]
    for d in page.get_drawings():
        row["draws"] += 1
        r = d.get("rect")
        if r is None:
            continue
        if r.x1 > right + tol or r.x0 < left - tol:
            row["ink_out"] += 1
        if (
            r.y1 > top - 4.0
            and r.y0 < bottom + 8.0
            and r.x1 > left - tol
            and r.x0 < right + tol
        ):
            citems.append((float(r.y0), float(r.y1)))
    for info in page.get_images(full=True):
        xref = info[0]
        row["imgs"] += 1
        try:
            rects = page.get_image_rects(xref)
        except Exception:
            rects = []
        for r in rects:
            if r.x1 > right + tol or r.x0 < left - tol:
                row["ink_out"] += 1
            if r.y1 > top - 4.0 and r.y0 < bottom + 8.0:
                citems.append((float(r.y0), float(r.y1)))
    row["gap_ct"] = _max_gap(citems)

    return row


CSV_FIELDS = [
    "page",
    "chars",
    "lines",
    "rowl",
    "rowr",
    "hang_l",
    "hang_r",
    "edge_l",
    "edge_r",
    "y_tail",
    "y_hi",
    "gap_max",
    "gap_ct",
    "ink_out",
    "orphan",
    "dup_lines",
    "dup_over",
    "tofu",
    "no_head",
    "no_folio",
    "imgs",
    "draws",
    "x0",
    "x1",
    "y0",
    "y1",
    "orphan_txt",
    "dup_txt",
]


def fmt(v):
    if isinstance(v, float):
        return round(v, 2)
    return v


def main(argv=None):
    ap = argparse.ArgumentParser(description="per-page structural audit")
    ap.add_argument("--pdf", default=os.path.join("build", "main.pdf"))
    ap.add_argument("--csv", default=os.path.join("build", "page_audit.csv"))
    ap.add_argument("--md", default=os.path.join("build", "page_audit.md"))
    ap.add_argument("--json", default=os.path.join("build", "page_audit.json"))
    ap.add_argument("--min-follow", type=int, default=2)
    ap.add_argument("--tol", type=float, default=2.0)
    args = ap.parse_args(argv)

    if not os.path.exists(args.pdf):
        sys.stderr.write("MISSING %s\n" % args.pdf)
        return 2

    doc = fitz.open(args.pdf)
    rows = []
    for i in range(doc.page_count):
        rows.append(audit_page(doc[i], i + 1, args.min_follow, args.tol))

    # ---------------- write csv ----------------
    with io.open(args.csv, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        wr.writeheader()
        for r in rows:
            wr.writerow({k: fmt(r[k]) for k in CSV_FIELDS})

    # ---------------- calibration ----------------
    def top_values(key, n=4):
        hist = {}
        for r in rows:
            v = round(float(r[key]), 1)
            hist[v] = hist.get(v, 0) + 1
        return sorted(hist.items(), key=lambda kv: -kv[1])[:n]

    calib = {
        "pages": doc.page_count,
        "x0_modes": top_values("x0"),
        "x1_modes": top_values("x1"),
        "y0_modes": top_values("y0"),
        "y1_modes": top_values("y1"),
        "frames": {
            "odd": [round(v, 2) for v in body_frame(595.276, 841.89, 1)],
            "even": [round(v, 2) for v in body_frame(595.276, 841.89, 2)],
        },
    }

    # ---------------- anomaly ranking ----------------
    def rank(key, reverse=True):
        return sorted(rows, key=lambda r: r[key], reverse=reverse)

    checks = {
        "rowr>tol (real text past right edge)": [r for r in rows if r["rowr"] > 0.0],
        "rowl>tol (real text past left edge)": [r for r in rows if r["rowl"] > 0.0],
        "hang_r>0 (right hanging punct, by design)": [r for r in rows if r["hang_r"] > 0.5],
        "hang_l>0 (left hanging punct, by design)": [r for r in rows if r["hang_l"] > 0.5],
        "edge_r (sub-tol right offset, info)": [r for r in rows if r["edge_r"] > EDGE_MIN],
        "edge_l (sub-tol left offset, info)": [r for r in rows if r["edge_l"] > EDGE_MIN],
        "y_hi>4 (text above body top)": [r for r in rows if r["y_hi"] > 4.0],
        "ink_out>0 (ink past side frame)": [r for r in rows if r["ink_out"] > 0],
        "orphan": [r for r in rows if r["orphan"]],
        "dup_over>0 (true overprint)": [r for r in rows if r["dup_over"] > 0],
        "dup_lines>0 (repeated lines, info)": [r for r in rows if r["dup_lines"] > 0],
        "tofu>0": [r for r in rows if r["tofu"] > 0],
        "no_folio": [r for r in rows if r["no_folio"]],
        "no_head": [r for r in rows if r["no_head"]],
        "near_empty (chars<200)": [r for r in rows if r["chars"] < 200],
        "tail>120 (short page)": [r for r in rows if r["y_tail"] > 120.0],
        "gap_ct>60 (large vertical hole)": [r for r in rows if r["gap_ct"] > 60.0],
    }

    summary = {k: len(v) for k, v in checks.items()}

    # ---------------- write md ----------------
    out = []
    out.append("# page audit (per-page structural sweep)\n")
    out.append("pdf: `%s`  pages: %d  min_follow=%d  tol=%.1fpt\n"
               % (args.pdf.replace("\\", "/"), doc.page_count, args.min_follow, args.tol))
    out.append("frame odd (recto): left=%.2f top=%.2f right=%.2f bottom=%.2f\n"
               % tuple(calib["frames"]["odd"]))
    out.append("frame even (verso): left=%.2f top=%.2f right=%.2f bottom=%.2f\n"
               % tuple(calib["frames"]["even"]))
    out.append("observed x0 modes: %s\n" % (calib["x0_modes"],))
    out.append("observed x1 modes: %s\n" % (calib["x1_modes"],))
    out.append("observed y0 modes: %s\n" % (calib["y0_modes"],))
    out.append("observed y1 modes: %s\n" % (calib["y1_modes"],))
    out.append("\n## counts\n")
    for k in checks:
        out.append("- %s: **%d**\n" % (k, summary[k]))

    DETAIL = (
        "rowr>tol (real text past right edge)",
        "rowl>tol (real text past left edge)",
        "edge_r (sub-tol right offset, info)",
        "edge_l (sub-tol left offset, info)",
        "hang_r>0 (right hanging punct, by design)",
        "hang_l>0 (left hanging punct, by design)",
        "y_hi>4 (text above body top)",
        "ink_out>0 (ink past side frame)",
        "orphan",
        "dup_over>0 (true overprint)",
        "tofu>0",
        "near_empty (chars<200)",
    )
    val_of = {
        "rowr>tol (real text past right edge)": lambda r: "%.2f" % r["rowr"],
        "rowl>tol (real text past left edge)": lambda r: "%.2f" % r["rowl"],
        "edge_r (sub-tol right offset, info)": lambda r: "%.2f" % r["edge_r"],
        "edge_l (sub-tol left offset, info)": lambda r: "%.2f" % r["edge_l"],
        "hang_r>0 (right hanging punct, by design)": lambda r: "%.2f" % r["hang_r"],
        "hang_l>0 (left hanging punct, by design)": lambda r: "%.2f" % r["hang_l"],
        "y_hi>4 (text above body top)": lambda r: "%.2f" % r["y_hi"],
        "ink_out>0 (ink past side frame)": lambda r: "%d" % r["ink_out"],
        "orphan": lambda r: "%d lines" % r["lines"],
        "dup_over>0 (true overprint)": lambda r: "%d" % r["dup_over"],
        "tofu>0": lambda r: "%d" % r["tofu"],
        "near_empty (chars<200)": lambda r: "%d chars" % r["chars"],
    }

    for name in DETAIL:
        items = checks[name]
        out.append("\n## %s  (%d)\n" % (name, len(items)))
        if not items:
            out.append("none\n")
            continue
        out.append("| page | value | note |\n|---|---|---|\n")
        for r in items[:60]:
            v = val_of[name](r)
            note = (r["orphan_txt"] or r["dup_txt"] or "").replace("|", "\\|")
            out.append("| %d | %s | %s |\n" % (r["page"], v, note))
        if len(items) > 60:
            out.append("| ... | (%d more) | |\n" % (len(items) - 60))

    for name, key, rev in (("short pages (tail whitespace)", "y_tail", True),
                           ("large vertical holes (gap_ct)", "gap_ct", True)):
        out.append("\n## %s  top 25\n" % name)
        out.append("| page | pt | lines | chars |\n|---|---|---|---|\n")
        for r in rank(key, rev)[:25]:
            out.append("| %d | %.1f | %d | %d |\n"
                       % (r["page"], r[key], r["lines"], r["chars"]))

    with io.open(args.md, "w", encoding="utf-8") as fh:
        fh.write("".join(out))

    with io.open(args.json, "w", encoding="utf-8") as fh:
        json.dump({"summary": summary, "calibration": calib,
                   "rows": [{k: fmt(v) for k, v in r.items()} for r in rows]},
                  fh, ensure_ascii=False, indent=1)

    # ---------------- ascii console ----------------
    sys.stdout.write("PDF %s pages=%d\n" % (args.pdf, doc.page_count))
    for k in checks:
        sys.stdout.write("  %-44s %d\n" % (k, summary[k]))
    sys.stdout.write("calib x0 modes %s\n" % (calib["x0_modes"],))
    sys.stdout.write("calib x1 modes %s\n" % (calib["x1_modes"],))
    sys.stdout.write("calib y0 modes %s\n" % (calib["y0_modes"],))
    sys.stdout.write("calib y1 modes %s\n" % (calib["y1_modes"],))
    sys.stdout.write("WROTE %s %s %s\n" % (args.csv, args.md, args.json))
    return 0


if __name__ == "__main__":
    sys.exit(main())
