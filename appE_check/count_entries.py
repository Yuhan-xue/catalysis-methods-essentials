import re

path = r"C:\Users\53150\Documents\mec\mechanics-textbook\src\appendices\appD_misconceptions.tex"
d = open(path, encoding="utf-8").read()
tables = re.findall(r"\\begin\{longtable\}.*?\\end\{longtable\}", d, flags=re.S)
print("longtables in appendix D:", len(tables))
total = 0
for i, t in enumerate(tables, 1):
    rows = [ln for ln in t.split("\n") if ln.rstrip().endswith("\\\\")]
    entries = [ln for ln in rows if "textbf{误区" not in ln and "caption" not in ln]
    total += len(entries)
    print("  table %2d: non-entry rows=%d  entries=%d" % (i, len(rows) - len(entries), len(entries)))
print("TOTAL ENTRIES:", total)
