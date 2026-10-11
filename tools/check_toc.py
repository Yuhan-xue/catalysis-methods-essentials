# Check every printed TOC page number by locating the heading text on its page.
#
# Usage: python tools/check_toc.py [out.txt] [pdf]
# Defaults: build/check_toc.txt , build/main.pdf
#
# The TOC carries no hyperref link annotations (links_total=0), so printed
# numbers cannot be checked against destinations. Instead each TOC line is split
# into title + trailing printed number, the title is normalized (whitespace and
# leader dots removed) and searched in the text layer of every non-TOC page; the
# printed number must be among the pages where that text occurs.
# MISMATCH lists the pages where the text really occurs; NOTFOUND means the
# heading text was not found anywhere (renamed or too mangled to match).
#
# Only ASCII on stdout and in the report file.
import io, re, sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/check_toc.txt"
PDF = sys.argv[2] if len(sys.argv) > 2 else "build/main.pdf"
TOCP = (2, 3, 4)

SP = re.compile(r"\s+")
TAIL = re.compile(r"^(.*?)[\s.\u00b7\u2026]*(\d{1,3})\s*$")


def norm(s):
    return SP.sub("", s).replace("\u2026", "").replace("\u00b7", "")


def main():
    doc = fitz.open(PDF)
    buf = ["pdf=%s pages=%d" % (PDF, doc.page_count)]

    pages_norm = []
    for i in range(doc.page_count):
        if (i + 1) in TOCP:
            pages_norm.append("")
            continue
        pages_norm.append(norm(doc[i].get_text()))

    entries = []
    for pno in TOCP:
        for b in doc[pno - 1].get_text("dict")["blocks"]:
            if b.get("type", 0) != 0:
                continue
            for ln in b.get("lines", []):
                txt = "".join(s["text"] for s in ln.get("spans", []))
                t = txt.strip()
                if len(t) < 4:
                    continue
                m = TAIL.match(t)
                if not m:
                    continue
                title = norm(m.group(1))
                if len(title) < 4:
                    continue
                entries.append((pno, m.group(1).strip(), int(m.group(2)), title))
    buf.append("toc_entries=%d" % len(entries))

    ok = 0
    bad = []
    nf = []
    for pno, title, printed, nt in entries:
        hits = [i + 1 for i, txt in enumerate(pages_norm) if nt and nt in txt]
        if not hits:
            nf.append((pno, title, printed))
            continue
        if printed in hits:
            ok += 1
        else:
            bad.append((pno, title[:52], printed, hits[:6]))
    buf.append("found_on_printed_page=%d mismatch=%d not_found=%d"
               % (ok, len(bad), len(nf)))
    for pno, title, printed, hits in bad:
        buf.append("  MISMATCH toc_p%d printed=%d found_at=%s | %s"
                   % (pno, printed, hits, title))
    for pno, title, printed in nf[:30]:
        buf.append("  NOTFOUND toc_p%d printed=%d | %s" % (pno, printed, title[:52]))
    buf.append("DONE")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("WROTE %s lines=%d" % (OUT, len(buf)))
    for ln in buf[:4]:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
