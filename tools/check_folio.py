# Check folio (printed page number) and running-head correctness on every page.
#
# Usage: python tools/check_folio.py [out.txt] [pdf]
# Defaults: build/check_folio.txt , build/main.pdf
#
# What it verifies
#   * every page carries a footer number equal to its PDF page number (BADFOLIO)
#   * which pages carry no footer number at all (NOFOLIO -- p1 is the title page)
#   * the set of running heads and whether each appears on one parity only
#     (MIXEDHEAD would mean a recto/verso mix-up)
# Geometry is the book's: A4, inner 25mm / outer 20mm, top/bottom 18mm,
# headheight 11pt, headsep 4mm, footskip 6mm (style/preamble.tex).
#
# Only ASCII on stdout and in the report file.
import io, re, sys
try:
    import pymupdf as fitz
except ImportError:
    import fitz

OUT = sys.argv[1] if len(sys.argv) > 1 else "build/check_folio.txt"
PDF = sys.argv[2] if len(sys.argv) > 2 else "build/main.pdf"

MM = 72.0 / 25.4
PW, PH = 595.276, 841.89
BOTTOM = 18.0 * MM
FOOTSKIP = 6.0 * MM
HEADH, HEADSEP = 11.0, 4.0 * MM
TOP = 18.0 * MM
foot_top = PH - BOTTOM - FOOTSKIP
head_bottom = TOP + HEADH + HEADSEP

NUM = re.compile(r"^(\d{1,3})$")


def parity(pgs):
    if all(p % 2 for p in pgs):
        return "odd"
    if all(p % 2 == 0 for p in pgs):
        return "even"
    return "MIXED"


def main():
    doc = fitz.open(PDF)
    buf = ["pdf=%s pages=%d" % (PDF, doc.page_count)]
    bad_folio = []
    no_folio = []
    heads = {}
    for i in range(doc.page_count):
        pno = i + 1
        page = doc[i]
        foot = []
        head = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type", 0) != 0:
                continue
            for ln in b.get("lines", []):
                txt = "".join(s["text"] for s in ln.get("spans", [])).strip()
                if not txt:
                    continue
                y0 = ln["bbox"][1]
                if y0 >= foot_top - 1.0:
                    foot.append(txt)
                elif ln["bbox"][3] <= head_bottom + 1.0:
                    head.append(txt)
        nums = [t for t in foot if NUM.match(t)]
        if not nums:
            no_folio.append((pno, foot[:2]))
        elif int(nums[0]) != pno:
            bad_folio.append((pno, int(nums[0])))
        heads.setdefault("".join(head), []).append(pno)

    buf.append("bad_folio=%d no_folio=%d" % (len(bad_folio), len(no_folio)))
    for pno, got in bad_folio[:40]:
        buf.append("  BADFOLIO p%d printed=%d" % (pno, got))
    for pno, t in no_folio[:40]:
        buf.append("  NOFOLIO p%d foot=%s" % (pno, t))
    items = sorted(heads.items(), key=lambda kv: -len(kv[1]))
    buf.append("distinct_running_heads=%d" % len(heads))
    for key, pgs in items[:20]:
        buf.append("  HEAD n=%d %s first_p=%d | %s"
                   % (len(pgs), parity(pgs), pgs[0], key[:60]))
        if parity(pgs) == "MIXED":
            buf.append("  MIXEDHEAD p=%s | %s" % (pgs[:8], key[:60]))
    buf.append("DONE")
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(buf) + "\n")
    print("WROTE %s lines=%d" % (OUT, len(buf)))
    for ln in buf[:3]:
        print(ln)
    return 0


if __name__ == "__main__":
    sys.exit(main())
