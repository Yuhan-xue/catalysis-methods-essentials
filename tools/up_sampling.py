# -*- coding: utf-8 -*-
"""How densely is the UP offset actually sampled?  Largest gap between independent
observations (bitmap folio reads + TOC section anchors)."""
import csv
ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
reads = set()
for r in csv.DictReader(open(ROOT + r"\tools\out\folio_read.csv", encoding="utf-8")):
    if r["vol"] == "up":
        p = int(r["pdf_page"])
        if 20 <= p <= 542 and r["read"] == str(p - 19):
            reads.add(p)
anchors = set()
for r in csv.DictReader(open(ROOT + r"\sources\anchors_up.csv", encoding="utf-8-sig")):
    p = int(r["pdf_page"])
    if 20 <= p <= 542:
        anchors.add(p)
obs = sorted(reads | anchors)
gaps = []
for i in range(1, len(obs)):
    gaps.append((obs[i] - obs[i - 1], obs[i - 1], obs[i]))
gaps.sort(reverse=True)
out = [f"UP independent observations in body: bitmap folio reads {len(reads)}, "
       f"section-anchor pages {len(anchors)}, union {len(obs)}",
       "largest gaps between consecutive observations (gap, pdf_before, pdf_after):"]
for g in gaps[:10]:
    out.append("   " + str(g))
out.append(f"first observation {obs[0]}, last {obs[-1]}")
open(ROOT + r"\tools\out\up_sampling.txt", "w", encoding="utf-8").write("\n".join(out))
print("\n".join(out))
