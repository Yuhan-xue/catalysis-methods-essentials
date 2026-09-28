# -*- coding: utf-8 -*-
"""Probe page structure of both volumes -> UTF-8 report file."""
import os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
def load(path):
    t = open(path, encoding="utf-8").read()
    pgs = t.split("\f")
    if pgs and pgs[-1].strip() == "":
        pgs = pgs[:-1]
    return pgs


up = load(os.path.join(ROOT, r"sources\text\up_layout.txt"))
dn = load(os.path.join(ROOT, r"sources\text\down_layout.txt"))

out = []
out.append(f"UP pages={len(up)}  DOWN pages={len(dn)}")


def show(name, arr, nums, nhead=3, ntail=3):
    for n in nums:
        if n - 1 >= len(arr):
            continue
        lines = [l.rstrip() for l in arr[n - 1].splitlines()]
        lines = [l for l in lines if l.strip()]
        out.append(f"===== {name} PDF p.{n}  nonblank={len(lines)} =====")
        for l in lines[:nhead]:
            out.append("  HEAD| " + l[:110])
        if len(lines) > nhead + ntail:
            out.append("   ...")
        for l in lines[-ntail:]:
            out.append("  TAIL| " + l[:110])


show("UP", up, [1, 2, 3, 13, 19, 20, 21, 25, 26, 27, 109])
show("DOWN", dn, [1, 12, 17, 18, 19, 20, 21, 42, 462])
open(os.path.join(ROOT, r"tools\probe_report.txt"), "w", encoding="utf-8").write("\n".join(out))
print("written", len(out), "lines")
