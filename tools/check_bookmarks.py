# Check that every PDF bookmark lands on the page carrying its heading.
#
# Usage: python tools/check_bookmarks.py [out.txt] [pdf]
# Defaults: build/check_bookmarks.txt , build/main.pdf
#
# get_toc() yields [level, title, page]. The normalized text of that page must
# contain the tail of the normalized bookmark title; the tail is used because a
# bookmark title may carry a section number or prefix that is not printed
# verbatim on the heading line. NOTFOUND = title text nowhere in the book;
# MISMATCH = title text found, but not on the bookmarked page (the report lists
# the pages where it really occurs).
#
# Only ASCII on stdout and in the report file.
import io, re, sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/check_bookmarks.txt"
PDF = sys.argv[2] if len(sys.argv) > 2 else "build/main.pdf"

SP = re.compile(r"\s+")
TAIL = 8
# A bookmark title may start with its list number ("2 Titre"). That number does
# not abut the title text on the printed heading ("chapter 2 Titre"), so when the
# plain tail does not match we retry with the leading number dropped.
NUMPFX = re.compile(r"^[0-9]+(?:[.][0-9]+)*")


def norm(s):
    return SP.sub("", s)


def main():
    doc = fitz.open(PDF)
    toc = doc.get_toc()
    buf = ["pdf=%s pages=%d bookmarks=%d" % (PDF, doc.page_count, len(toc))]

    pages_norm = [norm(doc[i].get_text()) for i in range(doc.page_count)]

    ok = 0
    fb = 0
    bad = []
    nf = []
    for level, title, page in toc:
        nt = norm(title)
        key = nt[-TAIL:] if len(nt) > TAIL else nt
        if len(key) < 3:
            nf.append((level, title, page, "too_short"))
            continue
        if not page or page < 1 or page > doc.page_count:
            nf.append((level, title, page, "no_page"))
            continue
        if key in pages_norm[page - 1]:
            ok += 1
            continue
        nt2 = NUMPFX.sub("", nt)
        key2 = nt2[-TAIL:] if len(nt2) > TAIL else nt2
        if len(key2) >= 3 and key2 in pages_norm[page - 1]:
            ok += 1
            fb += 1
            continue
        hits = [i + 1 for i, txt in enumerate(pages_norm) if key in txt]
        if hits:
            bad.append((level, title, page, hits[:6]))
        else:
            nf.append((level, title, page, "not_in_book"))
    buf.append("ok=%d mismatch=%d notfound=%d fallback=%d"
               % (ok, len(bad), len(nf), fb))
    for level, title, page, hits in bad:
        buf.append("  MISMATCH L%d p%d found_at=%s | %s"
                   % (level, page, hits, title[:56]))
    for level, title, page, why in nf[:30]:
        buf.append("  NOTFOUND L%d p%d %s | %s" % (level, page, why, title[:56]))
    buf.append("DONE")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("WROTE %s lines=%d" % (OUT, len(buf)))
    for ln in buf[:4]:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
