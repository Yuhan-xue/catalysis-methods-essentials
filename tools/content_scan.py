#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Content-level scan of our own book page by page (text layer of build/main.pdf).

tools/page_audit.py looks at GEOMETRY.  This scan looks at the TEXT of every page
for the content defects a machine can actually catch:

  md       markdown leaked into the PDF (**bold**, `code`, [link](url), ![img])
  tex      a LaTeX command leaked into the output (\textbf, \emph, \ref, ...)
  repl     U+FFFD replacement character
  ctrl     control character other than newline / tab
  invis    invisible character (NBSP, soft hyphen, zero width, BOM)
  rare     astral / private-use / surrogate code point
  tocheck  the \tocheck marker (must be 0 once the pixel pass closed out)
  dupp     doubled CJK punctuation (。。 ，， 、、 ；；)
  dupc     doubled high-risk CJK character (的的 是是 在在 不不 ...)
  halfw    halfwidth , ; : ! ? ( ) sitting between two CJK characters
  bal      unbalanced CJK bracket / quote pair on one page
  cjksp    a literal space between two CJK characters

WHAT THIS TOOL IS NOT
  A machine can only flag CANDIDATES.  A clean scan does not mean the page is
  clean: a typo made of two valid characters (戌/戊, 己/已, 末/未, a wrong digit in
  a number) is invisible to this scan.  Every hit still has to be read on the page
  image before anything is called verified, and the ledger has to say which pages
  were actually looked at.  The scan is the cheap filter, not the verdict.

Usage:
    python tools/content_scan.py [--pdf build/main.pdf] [--csv build/content_scan.csv]
                                 [--md build/content_scan.md] [--first N] [--last N]
"""
import argparse
import csv
import io
import os
import re
import sys

try:
    import pymupdf as fitz
except ImportError:  # pragma: no cover - older installs
    import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- code points (source stays ASCII-only: project tooling mangles CJK in .py) --
CJK = "[\u4e00-\u9fff\u3400-\u4dbf]"
PAIRS = [
    (0xFF08, 0xFF09),  # ( )
    (0x300A, 0x300B),  # << >>
    (0x201C, 0x201D),  # curly double quotes
    (0x300C, 0x300D),  # corner brackets
    (0x3010, 0x3011),  # lenticular brackets
    (0x3008, 0x3009),  # angle brackets
    (0x3014, 0x3015),  # tortoise brackets
    (0xFF3B, 0xFF3D),  # fullwidth square brackets
    (0x2018, 0x2019),  # curly single quotes
]
DUP_PUNCT = "".join(chr(c) for c in (
    0x3002, 0xFF0C, 0x3001, 0xFF1B, 0xFF1A, 0xFF01, 0xFF1F, 0x2026))
DUP_CHARS = "".join(chr(c) for c in (
    0x7684, 0x662F, 0x5728, 0x548C, 0x4E0E, 0x4E86, 0x4E0D, 0x6709, 0x4E3A,
    0x800C, 0x5176, 0x4E5F, 0x5C31, 0x90FD, 0x8FD8, 0x53C8, 0x66F4, 0x5F88,
    0x4E2D, 0x4E0A, 0x4E0B, 0x5185, 0x5916, 0x524D, 0x540E))

# Two markdown detectors on purpose: the strong markers (** __ ` ~~ ![) never
# occur legitimately in this book, while "]( " does - a closing bracket directly
# followed by an opening paren is ordinary math (e.g. "(1/Vp) dn/dt](1/cs)"),
# so that one is kept at INFO level and must be read on the page before judging.
RX_MD = re.compile(r"\*\*|`|!\[|__|~~")
RX_MDLINK = re.compile(r"\]\(")
RX_TEX = re.compile(r"\\[A-Za-z]{2,}")
RX_REPL = re.compile("\ufffd")
RX_INVIS = re.compile("[\u00a0\u00ad\u2000-\u200d\u202f\u205f\ufeff]")
RX_TOCHECK = re.compile("tocheck")
# NB: the backreference must sit OUTSIDE the character class, otherwise re
# raises "invalid group reference 1" (a class body has no groups).
RX_DUPP = re.compile("([" + DUP_PUNCT + "])\\1")
RX_DUPC = re.compile("([" + DUP_CHARS + "])\\1")
RX_HALFW = re.compile("(?<=" + CJK + ")[,;:!?()](?=" + CJK + ")")
RX_CJKSP = re.compile("(?<=" + CJK + ")[ \t\u00a0\u3000](?=" + CJK + ")")

CTX = 14
MAX_PER_DET = 8
MAX_HITS_CHARS = 700


def snippet(text, i, n):
    s = text[max(0, i - CTX):i + n + CTX]
    s = s.replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()


def det_re(text, rx):
    return [snippet(text, m.start(), m.end() - m.start()) for m in rx.finditer(text)]


def det_ctrl(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if (cp < 0x20 and ch not in "\n\r\t") or cp == 0x7F:
            out.append("U+%04X" % cp)
    return out


def det_rare(text):
    out = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        if cp >= 0x20000 or 0xE000 <= cp <= 0xF8FF or 0xD800 <= cp <= 0xDFFF:
            out.append("U+%05X " % cp + snippet(text, i, 1))
    return out


def det_bal(text):
    out = []
    for a, b in PAIRS:
        ca, cb = text.count(chr(a)), text.count(chr(b))
        if ca != cb:
            out.append("U+%04X x%d vs U+%04X x%d" % (a, ca, b, cb))
    return out


DETECTORS = [
    ("md", "WARN", lambda t: det_re(t, RX_MD)),
    ("mdlink", "INFO", lambda t: det_re(t, RX_MDLINK)),
    ("tex", "WARN", lambda t: det_re(t, RX_TEX)),
    ("repl", "WARN", lambda t: det_re(t, RX_REPL)),
    ("ctrl", "WARN", det_ctrl),
    ("invis", "WARN", lambda t: det_re(t, RX_INVIS)),
    ("rare", "WARN", det_rare),
    ("tocheck", "WARN", lambda t: det_re(t, RX_TOCHECK)),
    ("dupp", "INFO", lambda t: det_re(t, RX_DUPP)),
    ("dupc", "INFO", lambda t: det_re(t, RX_DUPC)),
    ("halfw", "INFO", lambda t: det_re(t, RX_HALFW)),
    ("bal", "INFO", det_bal),
    ("cjksp", "INFO", lambda t: det_re(t, RX_CJKSP)),
]
NAMES = [n for n, _, _ in DETECTORS]
LEVEL = dict((n, lv) for n, lv, _ in DETECTORS)
WARN_NAMES = [n for n in NAMES if LEVEL[n] == "WARN"]

# Detectors that are still reported but never decide a page's verdict.  "bal"
# belongs here: a quote or a parenthesis may legitimately open on one page and
# close on the next, so it fires on 118 of 340 pages and a page-level flag would
# carry no information.  The counts stay in the CSV so a reader can still see
# them; the page-level judgement ignores them.
VERDICT_IGNORE = set(["bal"])


def scan_page(text):
    hits = {}
    for name, _lv, fn in DETECTORS:
        got = fn(text)
        if got:
            hits[name] = got
    decisive = [n for n in hits if n not in VERDICT_IGNORE]
    verdict = "CLEAN"
    if any(n in WARN_NAMES for n in decisive):
        verdict = "WARN"
    elif decisive:
        verdict = "INFO"
    return hits, verdict


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=os.path.join(ROOT, "build", "main.pdf"))
    ap.add_argument("--csv", default=os.path.join(ROOT, "build", "content_scan.csv"))
    ap.add_argument("--md", default=os.path.join(ROOT, "build", "content_scan.md"))
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--last", type=int, default=0)
    a = ap.parse_args(argv)

    doc = fitz.open(a.pdf)
    last = a.last or doc.page_count
    rows = []
    for pno in range(a.first, min(last, doc.page_count) + 1):
        text = doc[pno - 1].get_text().replace("\r", "")
        hits, verdict = scan_page(text)
        rows.append({"page": pno, "chars": len(text), "verdict": verdict, "text": text,
                     "hits": hits})
    doc.close()

    with open(a.csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["page", "chars", "verdict"] + NAMES + ["n_hits", "hits"])
        for r in rows:
            detail = []
            for n in NAMES:
                for s in r["hits"].get(n, [])[:MAX_PER_DET]:
                    detail.append("%s: %s" % (n, s))
            joined = " | ".join(detail)
            if len(joined) > MAX_HITS_CHARS:
                joined = joined[:MAX_HITS_CHARS] + " ..."
            w.writerow([r["page"], r["chars"], r["verdict"]]
                       + [len(r["hits"].get(n, [])) for n in NAMES]
                       + [sum(len(v) for v in r["hits"].values()), joined])

    rep = io.StringIO()
    total = dict((n, 0) for n in NAMES)
    for r in rows:
        for n in NAMES:
            total[n] += len(r["hits"].get(n, []))
    n_clean = sum(1 for r in rows if r["verdict"] == "CLEAN")
    n_info = sum(1 for r in rows if r["verdict"] == "INFO")
    n_warn = sum(1 for r in rows if r["verdict"] == "WARN")
    rep.write("pdf=%s pages=%d scanned=%d\n" % (a.pdf, doc_page_count(a.pdf), len(rows)))
    rep.write("clean=%d info=%d warn=%d\n" % (n_clean, n_info, n_warn))
    rep.write("\n--- detector totals (level name hits pages) ---\n")
    for n in NAMES:
        pages = sum(1 for r in rows if r["hits"].get(n))
        rep.write("  %-8s %-4s %6d %6d\n" % (n, LEVEL[n], total[n], pages))
    rep.write("\n--- pages with hits ---\n")
    for r in rows:
        if not r["hits"]:
            continue
        rep.write("\n[%s] p%d  chars=%d\n" % (r["verdict"], r["page"], r["chars"]))
        for n in NAMES:
            for s in r["hits"].get(n, [])[:MAX_PER_DET]:
                rep.write("    %-8s %s\n" % (n, s))
    with open(a.md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(rep.getvalue())

    print("pdf=%s pages=%d scanned=%d" % (a.pdf, doc_page_count(a.pdf), len(rows)))
    print("clean=%d info=%d warn=%d" % (n_clean, n_info, n_warn))
    for n in NAMES:
        pages = sum(1 for r in rows if r["hits"].get(n))
        print("  %-8s %-4s hits=%-6d pages=%d" % (n, LEVEL[n], total[n], pages))
    print("WROTE %s" % a.csv)
    print("WROTE %s" % a.md)
    return 0


def doc_page_count(path):
    try:
        d = fitz.open(path)
        n = d.page_count
        d.close()
        return n
    except Exception:
        return -1


if __name__ == "__main__":
    sys.exit(main())
