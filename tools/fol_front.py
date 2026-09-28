# -*- coding: utf-8 -*-
import csv
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
rows = list(csv.DictReader(open(ROOT + r"\tools\out\folio_read.csv", encoding="utf-8")))
out = []
for r in rows:
    p = int(r["pdf_page"])
    if p <= 20 or (r["vol"] == "up" and p >= 534) or (r["vol"] == "down" and p >= 432):
        out.append(f"{r['vol']:5} p{p:>4} read={r['read']:>7} ndig={r['ndig']:>2} slot={r['slot']:>2} "
                   f"err={r['maxerr']:>7} ink={r['ink']}")
open(ROOT + r"\tools\out\folio_front.txt", "w", encoding="utf-8").write("\n".join(out))
print(len(out))
