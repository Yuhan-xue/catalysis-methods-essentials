# Check figure/table/equation number continuity -- captions only.
#
# Usage: python tools/check_numbers.py [out.txt] [pdf]
# Defaults: build/check_numbers.txt , build/main.pdf
#
# A CAPTION line begins with the number (FIG/TAB prefix + "2-11" ...); an in-text
# cross reference (e.g. "see FIG 2-18") does not. Matching only line-initial
# occurrences is what makes the check meaningful: an earlier version matched the
# pattern anywhere in a page and produced hundreds of phantom gaps, because a
# cross reference was counted as evidence that the caption exists.
#
# Equation numbers are the only content of their line, in parentheses.
#
# What a hole does NOT mean. Figure/table/equation numbers in this book are
# emitted by the LaTeX counters: chapters/ carries no hardcoded caption number,
# no \tag, and no \addtocounter/\setcounter on those counters, so the printed
# sequence is continuous by construction and cannot skip. A hole in 1..max
# therefore means this extractor failed to see the caption line -- a wrapped
# paragraph starting with a cross reference adds members, and a caption whose
# text layer does not begin the line (or a two-column / float interleave) loses
# them. The list below is a list of lines NOT SEEN in caption position, not a
# list of defects, and it is reported as UNSEEN for that reason.
#
# When the "with_unseen" count is non-zero, read it as "this many families have
# at least one caption this extractor could not see", and settle the question
# against the source rather than against this output.
#
# Only ASCII on stdout and in the report file.
import io, re, sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/check_numbers.txt"
PDF = sys.argv[2] if len(sys.argv) > 2 else "build/main.pdf"

FIG = chr(0x56FE)
TAB = chr(0x8868)
DASH = "[" + chr(0x2013) + chr(0x2014) + chr(0x2D) + "]"
SP = re.compile(r"\s+")
KIND = {"fig": 0, "tab": 1, "eq": 2}
CAP_FT = re.compile("^([" + FIG + TAB + "])\\s*(\\d{1,2})\\s*" + DASH
                    + "\\s*(\\d{1,2})(?![0-9])")
CAP_EQ = re.compile("^\\(\\s*(\\d{1,2})\\s*" + DASH + "\\s*(\\d{1,3})\\s*\\)$")
TITLE = {FIG: "fig", TAB: "tab"}


def main():
    doc = fitz.open(PDF)
    buf = ["pdf=%s pages=%d" % (PDF, doc.page_count)]
    buf.append("note=numbers come from the LaTeX counters (no hardcoded number,")
    buf.append("     no tag, no counter reset in chapters/), so the printed")
    buf.append("     sequence is continuous by construction; UNSEEN below means")
    buf.append("     THIS EXTRACTOR did not see the caption line, not a defect.")
    fam = {}
    first = {}
    for i in range(doc.page_count):
        for ln in doc[i].get_text("text").splitlines():
            s = SP.sub("", ln)
            if not s:
                continue
            m = CAP_FT.match(s)
            if m:
                kind = TITLE.get(m.group(1), "?")
                key = (kind, int(m.group(2)))
                fam.setdefault(key, set()).add(int(m.group(3)))
                first.setdefault(key, (i + 1, s[:46]))
                continue
            m = CAP_EQ.match(s)
            if m:
                key = ("eq", int(m.group(1)))
                fam.setdefault(key, set()).add(int(m.group(2)))
                first.setdefault(key, (i + 1, s[:46]))

    keys = sorted(fam, key=lambda k: (KIND.get(k[0], 9), k[1]))
    gaps = []
    for key in keys:
        nums = fam[key]
        mx = max(nums)
        missing = [n for n in range(1, mx + 1) if n not in nums]
        if missing:
            gaps.append((key, mx, len(nums), missing))
    buf.append("families=%d with_unseen=%d" % (len(keys), len(gaps)))
    for key, mx, cnt, missing in gaps:
        p0, t0 = first[key]
        shown = missing if len(missing) <= 20 else missing[:20] + ["..."]
        buf.append("  UNSEEN %s ch%-2d max=%d seen=%d not_seen=%s | first p%d %s"
                   % (key[0], key[1], mx, cnt, shown, p0, t0))
    buf.append("--- all families (kind ch max seen) ---")
    for key in keys:
        nums = fam[key]
        buf.append("  %-4s ch%-2d max=%-4d seen=%-4d first_p=%d"
                   % (key[0], key[1], max(nums), len(nums), first[key][0]))
    buf.append("DONE")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("WROTE %s lines=%d" % (OUT, len(buf)))
    for ln in buf[:4]:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
