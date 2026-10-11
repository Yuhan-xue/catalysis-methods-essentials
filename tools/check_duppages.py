# Detect duplicated pages in the built PDF.
#
# Usage: python tools/check_duppages.py [out.txt] [pdf]
# Defaults: build/check_duppages.txt , build/main.pdf
#
# Running heads and folios are excluded (they legitimately differ from page to
# page), so only body text is compared. Two pages are reported as EXACT when
# their normalized body text is identical, and as NEAR when the Jaccard overlap
# of their normalized line sets exceeds 0.60. A page pulled in twice by a
# duplicated \input shows up as a near-identical pair.
#
# Only ASCII on stdout and in the report file.
import io, re, sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/check_duppages.txt"
PDF = sys.argv[2] if len(sys.argv) > 2 else "build/main.pdf"

MM = 72.0 / 25.4
PH = 841.89
TOP = 18.0 * MM
HEADH, HEADSEP, FOOTSKIP = 11.0, 4.0 * MM, 6.0 * MM
HEAD_BOTTOM = TOP + HEADH + HEADSEP
FOOT_TOP = PH - 18.0 * MM - FOOTSKIP

SP = re.compile(r"\s+")
NEAR = 0.60


def body_lines(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type", 0) != 0:
            continue
        for ln in b.get("lines", []):
            y0, y1 = ln["bbox"][1], ln["bbox"][3]
            if y1 <= HEAD_BOTTOM + 1.0 or y0 >= FOOT_TOP - 1.0:
                continue
            t = SP.sub("", "".join(s["text"] for s in ln.get("spans", [])))
            if len(t) >= 4:
                out.append(t)
    return out


def main():
    doc = fitz.open(PDF)
    buf = ["pdf=%s pages=%d" % (PDF, doc.page_count)]
    pages = [body_lines(doc[i]) for i in range(doc.page_count)]
    empty = [i + 1 for i, ls in enumerate(pages) if not ls]
    buf.append("with_body_text=%d empty_body=%d"
               % (doc.page_count - len(empty), len(empty)))
    if empty:
        buf.append("  EMPTY (no body text; not comparable) %s" % empty[:40])

    groups = {}
    for i, ls in enumerate(pages):
        if ls:
            groups.setdefault("\n".join(ls), []).append(i + 1)
    exact = [v for v in groups.values() if len(v) > 1]

    sets = [set(ls) for ls in pages]
    near = []
    for i in range(len(sets)):
        if not sets[i]:
            continue
        for j in range(i + 1, len(sets)):
            if not sets[j]:
                continue
            inter = len(sets[i] & sets[j])
            if not inter:
                continue
            jac = float(inter) / len(sets[i] | sets[j])
            if jac > NEAR:
                near.append((i + 1, j + 1, jac))
    near.sort(key=lambda t: -t[2])

    buf.append("exact_duplicate_groups=%d near_duplicate_pairs=%d (Jaccard>%.2f)"
               % (len(exact), len(near), NEAR))
    for g in exact[:20]:
        buf.append("  EXACT %s | %s" % (g, pages[g[0] - 1][0][:40]))
    for a, b, jac in near[:20]:
        buf.append("  NEAR p%d ~ p%d jaccard=%.3f | %s"
                   % (a, b, jac, pages[a - 1][0][:40]))
    buf.append("DONE")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("WROTE %s lines=%d" % (OUT, len(buf)))
    for ln in buf[:3] + buf[3:6]:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
