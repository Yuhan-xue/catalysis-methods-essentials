# 分片作者简报（WRITER_BRIEF）

写给「只写一个分片」的你。**先读这一页，不要先去读 STYLE_GUIDE.md**（那是完整契约，
遇到拿不准的地方再查它）。

工作目录：`C:\Users\53150\Documents\deepseek-harness\default-workspace`

---

## 1. 你只做三件事

1. 读你的源文本 `sources/parts/<分片名>.txt`。**分段读**，不要一次读完
   （例如用 read 的 offset/limit 分 3 次）。每页有 `[[UP PDF p.n | 书内 p.m]]` 标记。
2. 写一个文件：`chapters/parts/<分片名>.tex`。
3. 跑编译检查，改到通过。

**不要**动别人的分片，不要动 `chapters/chNN.tex`（装配层），不要动 `style/`。

---

## 2. 分片文件长什么样

**a 分片**开头两行（照抄，只换标题与导读文字）：
```latex
\chapterstart{章标题}{本章导读：回答什么问题 + 内容导航，2—4 行}
\label{ch:NN}
```
**b/c/d 分片**不要写 `\chapterstart`，直接从 `\subsection{...}` 开始。
末分片末尾加 `\srcnote{...}`。

层级只用三级：`\chapterstart`（仅 a）／`\subsection`／`\subsubsection`。
更细的强调用 `\paragraph{...}`。

---

## 3. 可用环境（白名单，别自创）

```
probout      问题与输出        principle    原理与公式
measure      测量与条件        dataflow     数据到结论
pitfall      误判与边界        crosscheck   互补与回查
keycond      关键条件          methodsum    方法摘要
obs          观察              infer        推断
example[标题] 例题（自动编号）   fullwidth    跨栏非浮动区块
```

注意：互补与回查的环境叫 `crosscheck`，**不是** `complement`（后者与数学符号冲突）。

## 4. 可用宏

```
\src{S1 §x.y，书内 p.NN / PDF p.MM}   行内来源（8pt）
\srcnote{...}                          节/章末来源短注
\figsrc{...}                           图题内来源，自动换行
\chapref{ch:04} \equref{eq:x} \figref{fig:x} \tabref{tab:x}
\qty{214.5}{m^2.g^{-1}}  \num{1.2e-3}  \ce{MoO3/Al2O3}
\tocheck{...}   \pedset{...}   \supp{...}
\modelmark  \schemamark  \redrawmark
\onecolwidth (84mm)   \twocolwidth (176mm)
```

**禁止**：`\usepackage`、手写「图 4-2」这类编号、负 `\vspace`、`\\` 凑版面。

---

## 5. 公式：你没有视觉能力，这一点必须诚实

`read_image` 只回传元数据，你看不到像素；本环境已实测确认。

- OCR 层对**散文**可靠，对**公式**必然失真（上下标、希腊字母、正负号、分式会烂掉）。
- 变量定义和适用条件通常写在正文里，**那部分可靠，必须用**。
- 用「OCR 上下文 + 学科标准形式」重建公式。Bragg、Scherrer、BET、Langmuir、Arrhenius、
  Fick、Butler–Volmer、Tafel、Nernst、Langmuir–Hinshelwood、Eyring 等都是标准形式，可可靠重建。
  风险在**本书的符号约定与常数取值**——以 OCR 正文的变量定义为准。
- 结构复杂／上下标存疑／常数取值无法确认 → 公式后加
  `\tocheck{未对照原页面图像：<具体存疑点>}`。
- **不要写「已核对」**。写 `\tocheck{}` 不扣分，假称核对是严重问题。
- 回复里附 **FORMULA_VERIFY 清单**：`<册> <PDF 页序> — <公式> — <存疑点>`，Lead 会集中核验。

---

## 6. 图表

- 图源类别必须在图题里标：`\redrawmark`（据原书改绘）／`\modelmark`（模型计算）／
  `\schemamark`（示意）。真实谱图要裁原页面，你没视觉能力，**默认不要裁图**，改画原理图。
- 图题顺序：**图是什么 → 读者应看什么 → 条件与局限 → 来源**。
- 单栏图 `width=\onecolwidth`，跨栏图 `width=\twocolwidth`，**不要超**。
- **PGFPlots 禁忌**：不要写 `exp(-(x-a)^2/w)` 且 w 很小 → 会 `Dimension too large`。
  改用有界式 `1/(1+((x-a)/w)^2)`，或把指数绝对值控制在约 200 以内。
- `groupplot` 总宽 ≈ 3w + 2·sep + 25pt，必须 ≤ 520pt。用 3 列时建议 `width=50mm, horizontal sep=9mm`。
- **`declare function` 的作用域陷阱**（两条都实际踩过）：
  - 放进某个 `\nextgroupplot[...]` 的选项里 → **只对该子图有效**，别的子图用就报
    `Unknown function 'xxx'`。
  - 放进 `\begin{groupplot}[...]` 的公共选项 → 报 `I do not know the key '/pgfplots/declare function'`。
  - **正确写法**：在 `\begin{tikzpicture}` 之后、`\begin{groupplot}` 之前用
    `\tikzset{declare function={...}}` 声明，图内所有 axis 共用。
- **承载长文字的 TikZ node 必须给 `text width`**（实际踩过，超版心 66 pt）。
  不设宽度时，最长的那行说明文字会直接决定整个图宽，而它往往远宽于 `\columnwidth`。
  例：`\node[align=left, text width=74mm, anchor=north west] at (5,-11) {...};`
  另外手写的 `figure` 里 tikzpicture 若超宽，**不要**用 `\resizebox` 硬缩
  （会把图内文字压到 8 pt 以下，违反规范），应改坐标或给 node 限宽。
- 表：三线表，列 ≤5；超过就拆表或改跨栏表。
- **长表要放单栏整页**：双栏正文里每栏只有 88.5mm，直接用 `\twocolwidth` 宽的表会超版心约 88mm。
  用 `\widepageson` / `\widepagesoff` 切换，表宽用 `\textwidth`。

---

## 7. 提交前必跑

```
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap <分片名>
```
必须打印 `RESULT: PASS`，且 `errors 0`、`overfull >5pt 0`、**`missing glyphs 0`**。
失败就修到通过。

### 7.1 静默丢字（必读——本项目一次性丢掉过 76 个字符）

xeCJK 把某些码位判给**西文字体**（TeX Gyre Termes），而该字体没有这些字形时，
TeX **不报错、不中断**，只在 log 里留一行 `Missing character`，PDF 上那个字符直接消失。
这是企划验收「无缺字」的硬指标，已被加进 `check_chapter.ps1` / `build.ps1` 当错误处理。

已确认不可用的写法与替代：

| 不要写 | 原因 | 改写成 |
|---|---|---|
| `^{\circ}` | `\circ` 在 unicode-math 下是 U+2218，Termes 与 Fandol 都没有 | `°`（U+00B0，直写字面字符） |
| `\unit{{\circ}}` / `\unit{\degree}` | 同上 | `°` |
| `\degC` 展开成 `^{\circ}` 或 `\celsius` | 前者丢字；后者**只在 `\qty{}{\celsius}` 参数内有效**，独立使用会 `\ERROR` | 已统一为 `\degC`（内部用 `°`），直接用即可 |
| `\qty{25}{\micro m}` / `\unit{\mu m}` | siunitx 把 `\micro` 排成 U+1D707，Termes 无此字形 | `25\,µm` 或 `\qty{25}{µm}`（字面 U+00B5） |
| 数学模式里的中文 | 汉字被送进数学字体，静默丢字 | 一般不用管：已在导言区开 `\xeCJKsetup{CJKmath=true}` |
| `①` `②` `Ⅰ` `Ⅱ` | xeCJK 默认判为 Latin → Termes 无字形 | 一般不用管：已在导言区把这些码位改判为 CJK（Fandol 有） |

**自查方法**：编译后 log 里搜 `Missing character`。`check_chapter.ps1` 已经替你查了。

### 7.2 其他已确认的坑

- **`\renewcommand{\circ}` 会破坏 siunitx**（24 处 `Missing { inserted`）。度数符号不要动 `\circ`。
- TikZ node 的 `font=\fontsize{8}{9.5}\selectfont` 建议加花括号写成
  `font={\fontsize{8}{9.5}\selectfont}`，否则偶发 `Giving up on this path`。
- 双栏里 TikZ 的「自然宽度」**不含轴标签外溢**；承载长文字的 node 设了 `text width` 后，
  其内容实际宽度仍会撑大整图。写完务必跑 `check_chapter.ps1` 看 overfull。

### 7.3 尺寸与坐标的三个坑（新，都由分片作者实测报回）

- **不要给含系数的宽度宏再加系数**：`\onecolwidth` 本身是 `0.80\textwidth`，
  写 `height=0.46\onecolwidth` 会展开成「`0.46 0.80\textwidth`」**两个数连排**，
  报 `Illegal unit of measure (pt inserted)`。尺寸键只能用**单系数**尺寸，
  如 `height=6.1cm`；或在导言区另定义一个纯长度宏。
- **`\tocheck{}` 等宏的正文里出现数学符号必须加 `$`**：写成 `a_M`、`c_M` 会报 `Missing $`。
  这类报错位置离真正的原因很远，容易查偏。
- **图比版心宽是本项目 overfull 的唯一根因**（两处实测都是）。写完按下面两条自查，
  不用编译就能算出来：
  - `groupplot`：总宽 ≈ `n×width + (n−1)×sep + 左侧轴标签宽`（`ylabels at=edge left` 时约 15 mm），
    必须 ≤ 165 mm。实测 `3×48+2×8+15 = 175 mm` 就超了 10 mm。
  - 手工 TikZ（`x=1mm`）：看**最大 x 坐标**，再加上最右那个 node 的文字宽度。
    实测最大坐标 166.4 mm 已超版心，加注记后约 178 mm。
  超了要么收窄尺寸，要么整体 `\resizebox{\textwidth}{!}{...}`。

### 7.4 没有视觉能力时怎么查「图元素重叠」

不要凭想象判断。**用坐标区间做静态核算**：把每个 node 的 x 区间与 y 区间算出来，
两两求交；相交即会压叠。本项目有分片作者靠这个办法查出并修掉两处
（面板标目与枪框在 y≈7.78 处相碰；HAADF 标签起点落在探头环半径内）。
这比「看起来应该没问题」可靠得多，也是子代理唯一能做的图形自检。


### 7.5 TikZ / pgfplots 声明函数与 groupplot 的坑（新，由分片作者实测报回）

- \	ikzset{declare function={...}}\ 的参数名**必须用单字母但不能用 \x、\u**
  （它们是 LaTeX 重音命令）：多字母（\xx）报 \Missing control sequence inserted\；
  用 \x/\u 报 \ill-formatted floating point number\。改用 \p、\q 之类。
- 函数体里**乘法要加括号**：4-(100*\p)\，直接写 @*\p\ 会出问题。
- **groupplot 的公共 \domain\ 会被每个子面板继承**。若各面板横轴范围不同，
  必须**在每个 \nextgroupplot 里显式覆盖 domain**，否则报 \Dimension too large\。
  实测：group 设 domain=1700:2200，面板 (c) 横轴 0—0.6，直接崩。
- **未加载 amssymb，不要用 \lacksquare\**（改用 \\circ\ 或文字）。
- Fandol 无「鎓」(U+9393)，写「吡啶阳离子」。


---

## 8. 回复格式（短，不要复述正文）

1. 文件路径、编译页数、覆盖节次
2. **FORMULA_VERIFY 清单**
3. 没写完的部分、`\tocheck{}` 项、不确定的结论

---

## 9. 关于页数目标（重要，与早期简报相比有更新）

简报里给的「目标 N 页」是**为了控制单次任务的规模、提高一次成功的概率**，
**不是上限，也不是配额**。全书目标是约 200 页，目前**进度落后于页数目标**
（已完成的 15 个分片合计约 78 页）。因此：

- **写多了是好事**，不要为了凑「目标页数」而删掉受命覆盖的内容或压缩掉成立条件。
- 已有多个分片实际产出 5—7 页（目标 3.5—4 页），质量与覆盖都更好，全部保留。
- 真正要守的是**内容契约**：六环节落点、读图实例、公式成立条件、误判与边界、
  来源定位。这些一项都不能为页数让路。
- 唯一要避免的是**注水**（重复叙述、空泛铺陈）。判据是：这句话是否帮助读者
  判断适用条件或正确解释数据？不是，就删。

## 10. 需要完整细则时

查 `STYLE_GUIDE.md`：§3 禁止事项、§5 内容规范（观察/推断分离）、§7 图表参数、§8 来源规范。
样板分片：`chapters/parts/ch01-a.tex`（可只读前 120 行看写法）。
