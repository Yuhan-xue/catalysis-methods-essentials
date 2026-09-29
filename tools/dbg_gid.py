# -*- coding: utf-8 -*-
r"""验证：PDF 文本层里的 gid 是否等于**原字体**的字形序号。

若相等，就能用 gid 直接取真实字形（而不是按 unicode 取基准字形）——
这对 GlyphAssembly 拼装件（uni20D7.lft/.ex/.rt 这类**不在 cmap 里**的零件）
是必须的：它们的 ToUnicode 一律映射到 U+20D7，按 unicode 取盒会取错字形。
"""
import os
import sys
import collections
import pymupdf
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))

cache = {}
def gorder(font_name):
    key = inkbox.font_key(font_name)
    if key not in cache:
        f = TTFont(inkbox.font_path(font_name), fontNumber=0, lazy=True)
        cache[key] = (f.getGlyphOrder(), f.getBestCmap())
    return cache[key]

stat = collections.Counter()
examples = []
for pno in (0, 15, 65, 79, 93, 142, 200, 267):
    page = doc[pno]
    for s in page.get_texttrace():
        order, cmap = gorder(s["font"])
        for uni, gid, org, mbox in s["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            gname = cmap.get(uni)
            if gname is None:
                stat["unicode-not-in-cmap"] += 1
                if len(examples) < 15:
                    examples.append((pno + 1, s["font"], repr(c), gid, None))
                continue
            try:
                want = order.index(gname)
            except ValueError:
                stat["glyph-not-in-order"] += 1
                continue
            if want == gid:
                stat["gid-match"] += 1
            else:
                stat["gid-MISMATCH"] += 1
                if len(examples) < 15:
                    examples.append((pno + 1, s["font"], repr(c), gid,
                                     (want, gname), order[gid] if gid < len(order) else "??"))

out = ["统计：%s" % dict(stat), "", "样例："]
for e in examples:
    out.append("   p.%d %s %s gid=%s 期望=%s 实际字形=%s" % e)
txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "tools", "_dbg_gid.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
