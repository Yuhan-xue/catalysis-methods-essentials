# -*- coding: utf-8 -*-
r"""重排 ch00-intro.tex 的图 0-1（fig:chooseroute），消除框叠印。

问题（用户报告「图 0-1 有重叠」，程序化测量确认）：
TikZ 的 `below left=<v> and <h> of <父节点>` 定位的是**节点的角点**，
于是同一个父节点的多个子节点会从父节点中心向两侧铺开而互相侵入。
实测 p.6 上有 4 对框重叠，最严重一对重叠 66.9 x 28.4 pt——几乎完全重合。

修法：不用 `below left/right`，改为**显式 (x,y) 坐标**。
相邻框中心间距取 28.8 mm = 框宽 23.8 mm（text width 21 mm + 2 x inner sep 1.4 mm）+ 5 mm 缝，
间距是算出来的确定值，不再依赖 TikZ 的相对定位。
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "chapters", "ch00-intro.tex")
s = io.open(P, encoding="utf-8").read()

NEW = r"""\begin{tikzpicture}[
  x=1mm,y=1mm,
  box/.style={draw=accent,line width=0.5pt,rounded corners=1pt,align=center,
              inner sep=1.4mm,font=\fontsize{8}{10}\selectfont,text width=21mm},
  dec/.style={draw=accent,line width=0.5pt,align=center,inner sep=1.5mm,
              font=\fontsize{8}{10}\selectfont,text width=21mm,
              shape=diamond,aspect=2.1},
  ans/.style={align=center,font=\fontsize{8}{10}\selectfont,text width=21mm},
  ar/.style={-{Stealth[length=2mm]},line width=0.6pt,draw=accent}
]
% 【重叠修正·第二轮】原来各子节点用 below left/right=<v> and <h> of <父> 定位——
% 那定位的是**节点角点**，同一父节点的多个子节点会从父节点中心向两侧铺开而互相侵入。
% 实测 p.6 有 4 对框重叠，最严重一对 66.9x28.4 pt（几乎完全重合）。
% 现在全部改用**显式 (x,y) 坐标**：相邻框中心间距 28.8 mm
% = 框宽 23.8 mm（text width 21 + 2x1.4 内边距）+ 5 mm 缝，是算出来的确定值。
% 图幅 x 从 -67.3 到 81.7 mm = 149 mm，小于单栏版心 165 mm。
\node[dec] (q1) at (0,0) {要问的是\\体相还是表面？};
\node[box] (bulk) at (-41,-18) {体相结构\\晶相、晶胞、价态};
\node[box] (surf) at (41,-18) {表面与界面\\组成、位点、吸附态};
\node[dec] (q2) at (-41,-37) {有序还是\\无定形/短程？};
\node[dec] (q3) at (41,-37) {元素、位点\\还是吸附态？};
\node[box] (xrd) at (-55.4,-53) {多晶 XRD\\\chapref{ch:04}};
\node[box] (nmr) at (-26.6,-53) {MAS NMR\\XAFS\\\chapref{ch:08}};
\node[box] (xps) at (12.2,-53) {XPS/AES\\\chapref{ch:09}};
\node[box] (ads) at (41,-53) {化学吸附/TPD\\\chapref{ch:05}};
\node[box] (insitu) at (69.8,-53) {原位 IR/Raman\\原位 NMR\\\chapref{ch:07}\chapref{ch:06}};

\draw[ar] (q1) -- (bulk);
\draw[ar] (q1) -- (surf);
\draw[ar] (bulk) -- (q2);
\draw[ar] (q2) -- (xrd);
\draw[ar] (q2) -- (nmr);
\draw[ar] (surf) -- (q3);
\draw[ar] (q3) -- (xps);
\draw[ar] (q3) -- (ads);
\draw[ar] (q3) -- (insitu);

\node[ans] at (-55.4,-68) {峰位$\to$物相\\峰宽$\to$尺寸};
\node[ans] at (-26.6,-68) {配位\\短程有序};
\node[ans] at (12.2,-68) {元素\\化学态};
\node[ans] at (41,-68) {位点数量\\强度};
\node[ans] at (69.8,-68) {中间物\\反应路径};
\end{tikzpicture}"""

# 替换从 "\begin{tikzpicture}[" 到该图的 "\end{tikzpicture}"（其后紧跟 \caption{方法选择路径）
i = s.index(r"\begin{tikzpicture}[", s.index("方法选择路径") - 4000)
j = s.index(r"\end{tikzpicture}", i) + len(r"\end{tikzpicture}")
s = s[:i] + NEW + s[j:]
io.open(P, "w", encoding="utf-8").write(s)
print("图 0-1 已改为显式坐标布局")
