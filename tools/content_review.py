#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Generate sources/content_review.md : the page-by-page CONTENT-level review
# ledger.  Two inputs, one output:
#
#   build/content_scan.csv             machine scan of the PDF text layer
#                                      (produced by tools/content_scan.py)
#   sources/content_review_notes.txt   hand-maintained prose and per-page
#                                      judgements: the ONLY file a human edits
#
# The generated .md must never be edited by hand.  Every Chinese string lives in
# the notes file, because this project's file tooling mangles non-ASCII text in
# .py sources; this source is therefore strictly ASCII-only.
#
# Sections of the notes file: #LABELS #DET #HEAD #PAGES #BATCH #TAIL
#   #LABELS  key=value, one per line
#   #DET     name <TAB> level <TAB> what-it-detects   (one row per detector)
#   #HEAD    output prose, before the tables; {placeholders} get substituted
#   #PAGES   page <TAB> read-status <TAB> note
#   #BATCH   batch <TAB> date <TAB> scope <TAB> what-was-done
#   #TAIL    output prose, after the tables
#
# Exit codes
#   0  ledger written; all cross-checks passed
#   1  ledger written; a real inconsistency was found (see CHECK lines)
#   2  ledger NOT written (missing/bad input)
#
# Usage
#   python tools/content_review.py [--csv ...] [--notes ...] [--out ...]
#                                  [--pdf ...] [--date YYYY-MM-DD] [--commit SHA]

import datetime
import os
import re
import sys

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CSV = os.path.join("build", "content_scan.csv")
DEFAULT_NOTES = os.path.join("sources", "content_review_notes.txt")
DEFAULT_OUT = os.path.join("sources", "content_review.md")
DEFAULT_PDF = os.path.join("build", "main.pdf")

SECTIONS = ("#LABELS", "#DET", "#HEAD", "#PAGES", "#BATCH", "#TAIL")

# Labels the generator itself needs.  sec1..sec7 are deliberately absent: the
# section headings are already written into the #HEAD / #TAIL prose.
REQ_LABELS = (
    "title", "subtitle", "gen_note", "baseline_commit",
    "col_page", "col_scan", "col_hits", "col_hits_raw", "col_read", "col_note",
    "col_level", "col_det", "col_det_hits", "col_det_pages", "col_what",
    "col_batch", "col_date", "col_scope", "col_did",
    "read_no", "read_scan", "read_yes", "read_fix", "read_pend",
    "none_mark",
)
STATUS_KEYS = ("read_no", "read_scan", "read_yes", "read_fix", "read_pend")

LEVELS = ("WARN", "INFO")
PH = re.compile(r"\{[a-z_]+\}")


# ---------------------------------------------------------------- notes file

def parse_notes(path):
    """Split the notes file into its sections.  Returns None if unreadable."""
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig") as fh:
        raw = fh.read()
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    sec = {}
    cur = None
    for line in raw.split("\n"):
        tag = line.strip()
        if tag in SECTIONS:
            cur = tag
            sec[cur] = []
            continue
        if cur is not None:
            sec[cur].append(line)
    for tag in list(sec):
        body = sec[tag]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
    for tag in SECTIONS:
        sec.setdefault(tag, [])
    return sec


def parse_labels(lines):
    lab = {}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        lab[k.strip()] = v.strip()
    return lab


def tsv(lines, ncol, what, errs):
    """Parse tab-separated rows with exactly ncol fields."""
    rows = []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        f = [c.strip() for c in line.split("\t")]
        if len(f) != ncol:
            errs.append("%s line %d: expected %d fields, got %d"
                        % (what, i, ncol, len(f)))
            continue
        rows.append(f)
    return rows


# ---------------------------------------------------------------- scan csv

def read_scan_csv(path):
    """Returns (detector names in column order, list of page records)."""
    with open(path, encoding="utf-8-sig") as fh:
        raw = fh.read()
    lines = [ln for ln in raw.replace("\r\n", "\n").split("\n") if ln.strip()]
    header = [c.strip() for c in lines[0].split(",")]
    dets = header[3:-2]
    recs = []
    for ln in lines[1:]:
        f = ln.split(",", len(header) - 1)
        if len(f) < len(header):
            f = f + [""] * (len(header) - len(f))
        rec = {
            "page": int(f[0]),
            "chars": int(f[1] or 0),
            "verdict": f[2].strip(),
            "n_hits": int(f[-2] or 0),
            "hits": f[-1],
        }
        for i, name in enumerate(dets):
            rec[name] = int(f[3 + i] or 0)
        recs.append(rec)
    recs.sort(key=lambda r: r["page"])
    return dets, recs


# ---------------------------------------------------------------- markdown

def cell(s):
    """Escape a value for a markdown table cell."""
    if s is None:
        return ""
    s = " ".join(str(s).replace("\r", " ").replace("\n", " ").split())
    return s.replace("|", "\\|")


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |",
           "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(cell(c) for c in r) + " |")
    return "\n".join(out)


def hits_text(rec, dets):
    parts = ["%s=%d" % (n, rec[n]) for n in dets if rec[n]]
    return ", ".join(parts)


# ---------------------------------------------------------------- git

def head_commit(root):
    """Short HEAD sha, read straight from .git (no subprocess)."""
    git = os.path.join(root, ".git")
    try:
        with open(os.path.join(git, "HEAD"), encoding="ascii", errors="replace") as fh:
            head = fh.read().strip()
    except OSError:
        return "unknown"
    if not head.startswith("ref:"):
        return head[:12]
    ref = head.split(":", 1)[1].strip()
    try:
        with open(os.path.join(git, *ref.split("/")), encoding="ascii",
                  errors="replace") as fh:
            sha = fh.read().strip()
        if sha:
            return sha[:12]
    except OSError:
        pass
    try:
        with open(os.path.join(git, "packed-refs"), encoding="ascii",
                  errors="replace") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line.endswith(" " + ref):
                    return line.split(" ", 1)[0][:12]
    except OSError:
        pass
    return "unknown"


def pdf_pages(path):
    if fitz is None or not os.path.exists(path):
        return None
    try:
        doc = fitz.open(path)
        n = doc.page_count
        doc.close()
        return n
    except Exception:
        return None


# ---------------------------------------------------------------- build

def build(args):
    errs = []
    chk = []

    sec = parse_notes(args.notes)
    if sec is None:
        print("ERROR notes not found: %s" % args.notes)
        return 2
    lab = parse_labels(sec["#LABELS"])
    missing = [k for k in REQ_LABELS if k not in lab]
    if missing:
        print("ERROR notes #LABELS missing: %s" % ", ".join(missing))
        return 2

    det_rows = tsv(sec["#DET"], 3, "#DET", errs)
    page_rows = tsv(sec["#PAGES"], 3, "#PAGES", errs)
    batch_rows = tsv(sec["#BATCH"], 4, "#BATCH", errs)
    if not os.path.exists(args.csv):
        print("ERROR scan csv not found: %s" % args.csv)
        return 2
    dets, recs = read_scan_csv(args.csv)
    if errs:
        for e in errs:
            print("ERROR %s" % e)
        return 2

    # --- cross-check (f): the notes must describe exactly the CSV detectors
    det_names = [r[0] for r in det_rows]
    if set(det_names) != set(dets):
        chk.append(("detectors", False,
                    "csv=%s notes=%s" % (",".join(dets), ",".join(det_names))))
    else:
        chk.append(("detectors", True, "%d" % len(dets)))

    # --- per-detector totals, in CSV column order
    det_hits = dict((n, 0) for n in dets)
    det_pages = dict((n, 0) for n in dets)
    for rec in recs:
        for n in dets:
            if rec[n]:
                det_hits[n] += rec[n]
                det_pages[n] += 1
    det_by_name = dict((r[0], r) for r in det_rows)
    det_table = md_table(
        [lab["col_level"], lab["col_det"], lab["col_det_hits"],
         lab["col_det_pages"], lab["col_what"]],
        [[det_by_name[n][1], n,
          ("%d" % det_hits[n]) if det_hits[n] else "",
          ("%d" % det_pages[n]) if det_pages[n] else "",
          det_by_name[n][2]] for n in dets if n in det_by_name])

    # --- verdict tally
    tally = {}
    for rec in recs:
        tally[rec["verdict"]] = tally.get(rec["verdict"], 0) + 1

    # --- cross-check (b): n_hits equals the sum of the detector columns
    bad_sum = [r["page"] for r in recs
               if r["n_hits"] != sum(r[n] for n in dets)]
    if bad_sum:
        chk.append(("n_hits", False, "pages=%s" % bad_sum[:10]))
    else:
        chk.append(("n_hits", True, "%d rows" % len(recs)))

    # --- cross-check (a): pages are 1..N once each
    nums = [r["page"] for r in recs]
    npdf = pdf_pages(args.pdf)
    seq_ok = nums == list(range(1, len(nums) + 1))
    if npdf is not None and npdf != len(nums):
        chk.append(("pages", False, "csv=%d pdf=%d" % (len(nums), npdf)))
    elif not seq_ok:
        chk.append(("pages", False, "csv rows are not 1..%d" % len(nums)))
    else:
        chk.append(("pages", True, "%d (pdf %s)"
                    % (len(nums), npdf if npdf is not None else "?")))

    # --- notes: page -> (status, note)
    statuses = dict((lab[k], lab[k]) for k in STATUS_KEYS)
    note_map = {}
    for pg, status, note in page_rows:
        try:
            num = int(pg)
        except ValueError:
            errs.append("#PAGES bad page number: %s" % pg)
            continue
        if status not in statuses:
            errs.append("#PAGES page %d bad status: %s" % (num, status))
        note_map[num] = (status, note)
    if errs:
        for e in errs:
            print("ERROR %s" % e)
        return 2

    # --- cross-check (c): note pages exist in the scan
    unknown = sorted(p for p in note_map if p not in set(nums))
    if unknown:
        chk.append(("note-pages", False, "not in csv: %s" % unknown[:10]))
    else:
        chk.append(("note-pages", True, "%d" % len(note_map)))

    # --- cross-check (d): every non-CLEAN page carries a judgement.
    # The notes are allowed to cover MORE pages than the scan flagged: once the
    # page images are read, every read page gets a row (including clean ones),
    # and that is the progress this ledger is meant to record. What must never
    # happen is a flagged page with no recorded judgement.
    flagged = set(r["page"] for r in recs if r["verdict"] != "CLEAN")
    if flagged - set(note_map):
        chk.append(("note-coverage", False,
                    "flagged without judgement: %s" % sorted(flagged - set(note_map))))
    else:
        chk.append(("note-coverage", True,
                    "%d flagged, %d noted" % (len(flagged), len(note_map))))

    # --- (e) is checked on the rendered text at the end.

    # --- tables
    page_table = md_table(
        [lab["col_page"], lab["col_scan"], lab["col_hits"],
         lab["col_read"], lab["col_note"]],
        [[str(r["page"]), r["verdict"],
          hits_text(r, dets) or lab["none_mark"],
          note_map.get(r["page"], (lab["read_no"], ""))[0],
          note_map.get(r["page"], (lab["read_no"], ""))[1]] for r in recs])

    note_sorted = sorted(note_map)
    note_table = md_table(
        [lab["col_page"], lab["col_hits_raw"], lab["col_read"], lab["col_note"]],
        [[str(p),
          hits_text(next(r for r in recs if r["page"] == p), dets) or lab["none_mark"],
          note_map[p][0], note_map[p][1]] for p in note_sorted])

    mapping = {
        "pages": str(len(recs)),
        "csv": args.csv.replace("\\", "/"),
        # The baseline is pinned in the notes file, NOT taken from HEAD: the
        # ledger records which source revision the scan and the page judgements
        # describe.  Reading HEAD would make every commit invalidate the ledger
        # it just committed and start an endless regenerate/commit loop.
        "commit": args.commit or lab["baseline_commit"],
        "date": args.date,
        "gen_note": lab["gen_note"],
        "clean": str(tally.get("CLEAN", 0)),
        "info": str(tally.get("INFO", 0)),
        "warn": str(tally.get("WARN", 0)),
        "det_table": det_table,
        "page_table": page_table,
        "page_note_table": note_table,
    }
    mapping["batch_table"] = ""

    def sub(text):
        return PH.sub(lambda m: mapping.get(m.group(0)[1:-1], m.group(0)), text)

    # the batch rows may themselves carry {placeholders}, so they are rendered
    # only now that the rest of the mapping exists
    mapping["batch_table"] = md_table(
        [lab["col_batch"], lab["col_date"], lab["col_scope"], lab["col_did"]],
        [[r[0], r[1], r[2], sub(r[3])] for r in batch_rows])

    body = "# %s\n\n> %s\n\n%s\n\n%s\n" % (
        lab["title"], lab["subtitle"],
        "\n".join(sec["#HEAD"]), "\n".join(sec["#TAIL"]))
    out = sub(body)

    # Placeholders are a CLOSED vocabulary (the mapping keys): only an
    # unsubstituted *known* placeholder is a failure.  Any other {...} token is
    # just LaTeX, e.g. the notes may legitimately write $S_{\mathrm{total}}$ or
    # $\Delta S_jt-\pi t^2\ell$ -- a bare r"\{[a-z_]+\}" scan would flag
    # "{total}" and fail a perfectly good ledger.
    known = set(mapping)
    leftover = sorted(k for k in known if ("{" + k + "}") in out)
    unknown = sorted(set(PH.findall(out)) - set("{" + k + "}" for k in known))
    if leftover:
        chk.append(("placeholders", False, ", ".join(leftover)))
    else:
        chk.append(("placeholders", True, "none"))
    if unknown:
        print("INFO braces that are not placeholders (LaTeX, ignored): %s"
              % ", ".join(unknown[:10]))

    for name, ok, detail in chk:
        print("CHECK %-14s %s  %s" % (name, "ok  " if ok else "FAIL", detail))

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(out)

    print("PDF %s pages=%s" % (args.pdf.replace("\\", "/"),
                               npdf if npdf is not None else "?"))
    print("csv rows=%d detectors=%d" % (len(recs), len(dets)))
    print("clean=%d info=%d warn=%d"
          % (tally.get("CLEAN", 0), tally.get("INFO", 0), tally.get("WARN", 0)))
    print("notes pages=%d batches=%d" % (len(note_map), len(batch_rows)))
    print("WROTE %s lines=%d chars=%d"
          % (args.out.replace("\\", "/"), out.count("\n") + 1, len(out)))
    return 0 if all(ok for _, ok, _ in chk) else 1


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="generate the content review ledger")
    ap.add_argument("--csv", default=DEFAULT_CSV)
    ap.add_argument("--notes", default=DEFAULT_NOTES)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--pdf", default=DEFAULT_PDF)
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--commit", default="")
    args = ap.parse_args(argv)
    return build(args)


if __name__ == "__main__":
    sys.exit(main())
