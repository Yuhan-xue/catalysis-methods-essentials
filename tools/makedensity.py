# -*- coding: utf-8 -*-
"""Generate a controlled pure-text density test and report chars/page."""
import os, re

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
SENT = ("催化剂的比表面积与孔结构决定其活性位的可接近程度，程序的升温速率与载气流速"
        "共同决定脱附峰的形状与位置，因此定量解释之前必须确认传质与再吸附是否可忽略。")

para = SENT * 3          # 每段约 210 字
NPARA = 40               # 约 8400 字
body = "\n\n".join(para for _ in range(NPARA))
nchar = len(re.sub(r"\s", "", body))

tex = r"""\documentclass[UTF8,10pt,a4paper,twoside,twocolumn,fontset=fandol]{ctexart}
\input{../style/preamble}
\input{../style/macros}
\begin{document}
\section{密度标定}
\chapterhead{密度标定}{纯文字页面密度标定，用于校准全书页数预算。}
""" + body + r"""
\end{document}
"""
open(os.path.join(ROOT, "build", "density.tex"), "w", encoding="utf-8").write(tex)
open(os.path.join(ROOT, "build", "density_chars.txt"), "w", encoding="utf-8").write(str(nchar))
print("chars =", nchar)
