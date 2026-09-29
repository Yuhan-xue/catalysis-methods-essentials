# -*- coding: utf-8 -*-
r"""自检：gid 解析是否正确。

做法：两个独立来源取同一个字形的墨迹盒，比对
  (a) PDF 的 gid -> 字形名 -> 轮廓盒（绘制时真正用的字形）
  (b) unicode -> cmap -> 字形名 -> 轮廓盒（基准字形）
若 gid 解析正确，(b) 与 (a) 应当**几乎处处相同**；不同的少数应当
全部是**字形变体**（`.st` / `.ss01` / 拼装件），可以逐个核对名字。

CID 键字体若不做 CID->序号换算，(a) 会取到完全不相干的字形，
本自检会立刻暴露（不一致率会非常高）。
"""
import os
import sys
import collections
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))

stat = collections.Counter()
diff_examples = collections.defaultdict(list)
sel = list(range(0, doc.page_count, 17))          # 均匀抽样 16 页
for pno in sel:
    for s in doc[pno].get_texttrace():
        f = s["font"]
        ent = inkbox._load(f)
        if ent is None:
            stat["font-unmapped"] += 1
            continue
        for uni, gid, org, mbox in s["chars"]:
            c = chr(uni)
            if not c.strip():
                continue
            a = inkbox.ink_bbox_gid(f, gid, c)
            b = inkbox.ink_bbox(f, c)
            if a is None or b is None:
                stat["no-ink"] += 1
                continue
            if max(abs(a[i] - b[i]) for i in range(4)) < 1e-6:
                stat["same"] += 1
            else:
                stat["DIFF"] += 1
                if len(diff_examples[f]) < 12:
                    gn_gid = inkbox.glyph_name_of(f, gid, c)
                    gn_uni = ent[1].get(uni)
                    diff_examples[f].append((pno + 1, repr(c), gid, gn_gid, gn_uni))

out = ["抽样页：%s" % sel, "统计：%s" % dict(stat), ""]
for f, ex in diff_examples.items():
    out.append("## %s 差异样例（gid 名 vs unicode 名）" % f)
    for e in ex:
        out.append("   p.%d %s gid=%d  gid名=%s  unicode名=%s" % e)
txt = "\n".join(out)
print(txt)
with open(os.path.join(ROOT, "tools", "_dbg_gidcheck.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
