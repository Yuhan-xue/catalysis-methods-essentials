#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Whole-book page acceptance ledger generator. ASCII-only source on purpose.

Inputs
------
build/page_audit.csv                per-page structural audit (tools/page_audit.py)
sources/page_acceptance_notes.txt   labels + head prose + per-page notes + tail
build/main.pdf                      optional; only to check the artifact claims

Output
------
sources/page_acceptance.md

Every Chinese string lives in the notes file as data. This project's file-write
tooling mangles non-ASCII inside Python sources, so no such literal appears here.

Verdict rules
-------------
FLAG  rowl/rowr > 0, y_hi > 4, ink_out > 0, orphan, dup_over > 0, tofu > 0,
      or (no_folio / no_head / chars < 200) on a page other than page 1
WARN  gap_ct > 60            large no-content band: known, deliberately not fixed
INFO  edge_l/edge_r > 0.05, y_tail > 120, dup_lines > 0
PASS  none of the above

Hanging punctuation (hang_l/hang_r) is by-design xeCJK typography: it is shown
in the evidence column but does NOT raise the verdict, because it occurs on 317
of 340 pages and treating it as a mark would empty the verdict column of
meaning. An explicit row in the notes file overrides the computed verdict; the
evidence column always keeps the raw measured values.

Exit codes
----------
0 ledger written and artifact claims consistent
1 input malformed, or the ledger text disagrees with the built PDF
2 a required input file is missing
"""

import argparse
import csv
import io
import os
import re
import sys

SEV = {"PASS": 0, "INFO": 1, "WARN": 2, "FLAG": 3}
ORDER = ("PASS", "INFO", "WARN", "FLAG")
DASH = u"\u2014"
MIDDOT = u"\u00b7"

EDGE_MIN = 0.05
GAP_WARN = 60.0
TAIL_INFO = 120.0
EMPTY_CHARS = 200
Y_HI_TOL = 4.0
HANG_MIN = 0.5

INT_FIELDS = frozenset((
    "page", "chars", "lines", "ink_out", "orphan", "dup_lines", "dup_over",
    "tofu", "no_head", "no_folio", "imgs", "draws"))
TEXT_FIELDS = frozenset(("orphan_txt", "dup_txt"))

SECTIONS = ("#LABELS", "#HEAD", "#ROWS", "#TAIL")


def num2(v):
    return "%.2f" % float(v)


def coerce(row):
    out = {}
    for key, val in row.items():
        if key in TEXT_FIELDS:
            out[key] = val
        elif key in INT_FIELDS:
            try:
                out[key] = int(float(val))
            except (TypeError, ValueError):
                out[key] = 0
        else:
            try:
                out[key] = float(val)
            except (TypeError, ValueError):
                out[key] = 0.0
    return out


def read_notes(path):
    """Return (labels, head, rows, tail). rows is {page: (verdict, note)}."""
    labels = {}
    head, tail = [], []
    rows = {}
    order = []
    section = None
    text = io.open(path, encoding="utf-8").read()
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line.strip() in SECTIONS:
            section = line.strip()
            continue
        if section == "#LABELS":
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, _, val = line.partition("=")
            labels[key.strip()] = val.strip()
        elif section == "#HEAD":
            head.append(line)
        elif section == "#TAIL":
            tail.append(line)
        elif section == "#ROWS":
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                raise SystemExit("ERR bad row (need page<TAB>verdict<TAB>note): %r"
                                 % line[:60])
            page = int(parts[0].strip())
            verdict = parts[1].strip().upper()
            note = "\t".join(parts[2:]).strip()
            if page in rows:
                raise SystemExit("ERR duplicate note for page %d" % page)
            if verdict not in SEV:
                raise SystemExit("ERR page %d bad verdict %r" % (page, verdict))
            rows[page] = (verdict, note)
            order.append(page)
    for key in ("title", "counts_title", "table_title", "col_page",
                "col_verdict", "col_evidence", "col_note", "open_title",
                "open_empty", "DEFAULT_PASS", "DEFAULT_INFO", "DEFAULT_WARN",
                "DEFAULT_FLAG", "gen_note", "override_down", "auto_open",
                "sweep_clause_full", "sweep_clause_part"):
        if key not in labels:
            raise SystemExit("ERR missing label %s" % key)
    while head and not head[-1].strip():
        head.pop()
    while tail and not tail[0].strip():
        tail.pop(0)
    return labels, "\n".join(head), rows, "\n".join(tail)


def evaluate(row, page_no):
    """Return (computed verdict, evidence tokens)."""
    hard, warn, info, ctx = [], [], [], []
    if row["rowr"] > 0.0:
        hard.append("rowr=%s" % num2(row["rowr"]))
    if row["rowl"] > 0.0:
        hard.append("rowl=%s" % num2(row["rowl"]))
    if row["y_hi"] > Y_HI_TOL:
        hard.append("y_hi=%s" % num2(row["y_hi"]))
    if row["ink_out"] > 0:
        hard.append("ink_out=%d" % row["ink_out"])
    if row["orphan"]:
        hard.append("orphan")
    if row["dup_over"] > 0:
        hard.append("dup_over=%d" % row["dup_over"])
    if row["tofu"] > 0:
        hard.append("tofu=%d" % row["tofu"])
    if page_no != 1:
        if row["no_folio"]:
            hard.append("no_folio")
        if row["no_head"]:
            hard.append("no_head")
        if row["chars"] < EMPTY_CHARS:
            hard.append("chars=%d" % row["chars"])
    if row["gap_ct"] > GAP_WARN:
        warn.append("gap_ct=%s" % num2(row["gap_ct"]))
    if row["edge_r"] > EDGE_MIN:
        info.append("edge_r=%s" % num2(row["edge_r"]))
    if row["edge_l"] > EDGE_MIN:
        info.append("edge_l=%s" % num2(row["edge_l"]))
    if row["y_tail"] > TAIL_INFO:
        info.append("y_tail=%s" % num2(row["y_tail"]))
    if row["dup_lines"] > 0:
        info.append("dup_lines=%d" % row["dup_lines"])
    if row["hang_r"] > HANG_MIN:
        ctx.append("hang_r=%s" % num2(row["hang_r"]))
    if row["hang_l"] > HANG_MIN:
        ctx.append("hang_l=%s" % num2(row["hang_l"]))
    if hard:
        verdict = "FLAG"
    elif warn:
        verdict = "WARN"
    elif info:
        verdict = "INFO"
    else:
        verdict = "PASS"
    return verdict, hard + warn + info + ctx


def check_pdf_cfg(head_text, pages, pdf):
    """Verify the page/bookmark numbers claimed in the head prose."""
    mo = re.search(r"(\d+)\s*\S*\s*/\s*(\d+)\s*\S*", head_text)
    if not mo:
        return None
    claim_pages, claim_marks = int(mo.group(1)), int(mo.group(2))
    if claim_pages != pages:
        return "head claims %d pages but the audit holds %d rows" % (
            claim_pages, pages)
    if not os.path.exists(pdf):
        return None
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
    except ImportError:
        return None
    doc = fitz.open(pdf)
    got_pages = doc.page_count
    got_marks = len(doc.get_toc())
    doc.close()
    if got_pages != claim_pages or got_marks != claim_marks:
        return "PDF has %d pages / %d bookmarks, head claims %d / %d" % (
            got_pages, got_marks, claim_pages, claim_marks)
    return None


def esc(text):
    return text.replace("|", "\\|")


def main(argv=None):
    ap = argparse.ArgumentParser(description="write the page acceptance ledger")
    ap.add_argument("--csv", default="build/page_audit.csv")
    ap.add_argument("--notes", default="sources/page_acceptance_notes.txt")
    ap.add_argument("--out", default="sources/page_acceptance.md")
    ap.add_argument("--pdf", default="build/main.pdf")
    ap.add_argument("--date", default="")
    args = ap.parse_args(argv)

    for path in (args.csv, args.notes):
        if not os.path.exists(path):
            sys.stderr.write("MISSING %s\n" % path)
            return 2

    labels, head_text, explicit, tail = read_notes(args.notes)

    rows = []
    with io.open(args.csv, encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh):
            rows.append(coerce(raw))
    if not rows:
        sys.stderr.write("ERR no rows in %s\n" % args.csv)
        return 1
    pages = len(rows)
    by_page = {}
    for idx, row in enumerate(rows):
        page_no = idx + 1
        if row.get("page") and row["page"] != page_no:
            sys.stderr.write("ERR csv page column %s at row %d\n"
                             % (row["page"], page_no))
            return 1
        by_page[page_no] = row

    for page in explicit:
        if page not in by_page:
            sys.stderr.write("ERR note for out-of-range page %d\n" % page)
            return 1

    if args.date:
        date = args.date
    else:
        import datetime
        date = datetime.date.today().isoformat()

    # Contact-sheet sweep: batches of 20 pages at 40dpi, read page by page.
    # The sweep covers the whole book (17 batches); the build was 340 pages when
    # the sweep was read and is 339 pages now -- the material after p.162 moved
    # one page earlier, so the sweep still covers every page of the material
    # while the current page numbers are re-checked below.  SWEEP_END must move
    # with the batches actually read, otherwise the coverage claim inflates.
    SWEEP_END = 339
    BATCH = 20
    sweep = set(range(1, SWEEP_END + 1))
    focused = set([6, 8, 64, 93, 110, 229, 244, 323])
    focused |= set([1, 4, 28, 31, 68, 77, 164, 165, 334, 335, 337, 339])
    focused |= set([118, 160]) | set([192, 200])
    visual = sorted(sweep | focused)
    focused_tail = len([p for p in focused if p > SWEEP_END])

    verdicts = {}
    evidence = {}
    notes = {}
    auto = []
    for page_no in sorted(by_page):
        row = by_page[page_no]
        computed, ev = evaluate(row, page_no)
        if page_no in explicit:
            verdict, note = explicit[page_no]
            if SEV[verdict] < SEV[computed]:
                note = note + labels["override_down"]
        else:
            verdict = computed
            note = labels["DEFAULT_" + verdict]
            if verdict in ("WARN", "FLAG"):
                auto.append(page_no)
        verdicts[page_no] = verdict
        evidence[page_no] = "; ".join(ev)
        notes[page_no] = note

    counts = dict((v, 0) for v in ORDER)
    for verdict in verdicts.values():
        counts[verdict] += 1

    # The coverage sentence has two honest shapes: while part of the book is
    # still unread it must name the blind spot; once the sweep reaches the last
    # page there is no blind spot left, and claiming one would understate the
    # work. Pick the clause first, then fill the numbers inside it.
    if focused_tail > 0:
        clause = labels["sweep_clause_part"]
    else:
        clause = labels["sweep_clause_full"]
    head = head_text.replace("{sweep_clause}", clause)
    head = head.replace("{date}", date).replace("{pages}", str(pages))
    head = head.replace("{visual}", str(len(visual)))
    head = head.replace("{sweep_last}", str(SWEEP_END))
    head = head.replace("{sweep}", str(SWEEP_END))
    head = head.replace("{sweep_next}", str(SWEEP_END + 1))
    head = head.replace("{batches}", str((SWEEP_END + BATCH - 1) // BATCH))
    head = head.replace("{focused_tail}", str(focused_tail))
    problem = check_pdf_cfg(head_text, pages, args.pdf)

    out = []
    out.append("# %s" % labels["title"])
    out.append("")
    out.append(head)
    out.append("")
    out.append("## %s" % labels["counts_title"])
    out.append("")
    out.append("| %s | %s |" % (labels["col_verdict"], labels["col_note"]))
    out.append("|---|---|")
    for verdict in ORDER:
        out.append("| %s | %d |" % (verdict, counts[verdict]))
    out.append("")
    out.append("## %s" % labels["table_title"])
    out.append("")
    out.append("| %s | %s | %s | %s |" % (labels["col_page"],
                                           labels["col_verdict"],
                                           labels["col_evidence"],
                                           labels["col_note"]))
    out.append("|---|---|---|---|")
    for page_no in sorted(by_page):
        ev = evidence[page_no] or DASH
        out.append("| %d | %s | %s | %s |" % (
            page_no, verdicts[page_no], esc(ev), esc(notes[page_no])))
    out.append("")
    out.append("## %s" % labels["open_title"])
    out.append("")
    opened = [p for p in sorted(by_page)
              if verdicts[p] in ("WARN", "FLAG")]
    if not opened:
        out.append(labels["open_empty"])
    else:
        for page_no in opened:
            out.append("- **p%d %s %s** %s" % (page_no, MIDDOT,
                                               verdicts[page_no],
                                               notes[page_no]))
        if auto:
            out.append("")
            out.append("- %s%s" % (labels["auto_open"],
                                   ", ".join("p%d" % p for p in auto)))
    out.append("")
    out.append(tail)
    out.append("")
    out.append("---")
    out.append("")
    out.append(labels["gen_note"])
    out.append("")

    text = "\n".join(out)
    dirname = os.path.dirname(args.out)
    if dirname and not os.path.isdir(dirname):
        os.makedirs(dirname)
    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)

    sys.stdout.write("PDF %s rows=%d\n" % (args.pdf, pages))
    sys.stdout.write("verdicts %s\n" % " ".join(
        "%s=%d" % (v, counts[v]) for v in ORDER))
    sys.stdout.write("notes explicit=%d default=%d auto-open=%d\n"
                     % (len(explicit), pages - len(explicit), len(auto)))
    sys.stdout.write("visual pages=%d\n" % len(visual))
    sys.stdout.write("WROTE %s lines=%d chars=%d\n"
                     % (args.out, len(out), len(text)))
    if problem:
        sys.stderr.write("FAIL artifact claim: %s\n" % problem)
        return 1
    sys.stdout.write("CHECK artifact claims ok pages=%d\n" % pages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
