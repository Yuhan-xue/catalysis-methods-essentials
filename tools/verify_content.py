# -*- coding: utf-8 -*-
"""改图后的内容留存核查：关键标注串是否仍在 PDF 中。"""
import os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = pymupdf.open(os.path.join(ROOT, "build", "main.pdf"))
txt = []
for pno in range(doc.page_count):
    txt.append(doc[pno].get_text())
book = "\n".join(txt)

need = ["衍射模式", "成像系统", "照明系统", "样品表面", "散射损失", "入射光",
        "势垒区", "功函数", "针尖-样品间距", "组成位移", "覆盖度位移",
        "实心圆点", "实心方点", "衍射花样", "像平面", "晶体结构",
        "背散射电子", "特征", "可见光", "覆盖度位移"]
for s in need:
    print("%-16s %s" % (s, "在" if s in book else "**缺失**"))
print()
print("页数:", doc.page_count)
