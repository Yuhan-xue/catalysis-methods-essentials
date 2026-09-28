# -*- coding: utf-8 -*-
"""Locate exact code points that the build reports as missing glyphs."""
import glob, os

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
TARGETS = {
    0x00B5: "MICRO SIGN (safe, Termes has it)",
    0x03BC: "GREEK SMALL LETTER MU",
    0x1D707: "MATHEMATICAL ITALIC SMALL MU  <-- missing",
    0x2218: "RING OPERATOR  <-- missing",
    0x00B0: "DEGREE SIGN (safe)",
}
FILES = sorted(glob.glob(os.path.join(ROOT, "chapters", "**", "*.tex"), recursive=True)) + \
        sorted(glob.glob(os.path.join(ROOT, "style", "*.tex")))

for path in FILES:
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        for cp, name in TARGETS.items():
            if chr(cp) in line:
                rel = os.path.relpath(path, ROOT)
                print(f"{rel}:{i}  U+{cp:04X} {name}")
                print(f"    {line.strip()[:110]}")
