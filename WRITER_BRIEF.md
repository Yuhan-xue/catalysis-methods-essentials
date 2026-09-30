# 分片作者简报（WRITER_BRIEF）

写给「只写一个分片」的你。这是**快速上手**：完整契约见 `STYLE_GUIDE.md`，环境事实与坑见 `HANDOFF.md`。

> ⚠️ 本书已是**单栏**（版心 165 mm）。早期简报里的「双栏 / 每栏 84 mm」写法**已作废**。

## 1 你只做三件事

1. **分段读**源文本 `sources/parts/<分片名>.txt`（每页有 `[[UP/DOWN PDF p.n | 书内 p.m]]` 标记）。
2. 写 `chapters/parts/<分片名>.tex`。
3. 跑 `pwsh -NoProfile -File tools/check_chapter.ps1 -Chap <分片名>`，改到 `RESULT: PASS`
   （errors 0 / overfull >5pt 0 / **missing glyphs 0**）。

**不要**动别人的分片、`chapters/chNN.tex`（装配层）、`style/`。

## 2 分片骨架与内容单位

- a 分片开头：`\chapterstart{章标题}{2—4 行导读}` + `\label{ch:NN}`；b/c/d 直接从
  `\subsection` 开始；末分片末尾加 `\srcnote{...}`。
- 层级只用 `\chapterstart / \subsection / \subsubsection`，更细的强调用 `\paragraph`。
- 一个分片 = 2 个 `\subsection` + 若干 `\subsubsection`，**六环节各至少一处**：
  `probout / principle / measure / dataflow / pitfall / crosscheck`；外加至少一个读图实例，
  `obs` 与 `infer` 严格分开。

## 3 可用环境与宏（白名单，别自创）

- 环境：`probout principle measure dataflow pitfall crosscheck keycond methodsum obs infer
  example[标题] fullwidth`（互补回查叫 `crosscheck`，不是 complement）。
- 宏：`\src{S1 §x.y，书内 p.NN / PDF p.MM}` `\srcnote{}` `\figsrc{}`
  `\chapref{} \equref{} \figref{} \tabref{}` `\qty{}{} \num{} \ce{}`
  `\tocheck{} \pedset{} \supp{}` `\modelmark \schemamark \redrawmark`
  `\onecolwidth`（≈132 mm）`\twocolwidth`（≈158 mm）。
- 禁止：`\usepackage`、手写图表编号、负 `\vspace`、用 `\\` 凑版面。

## 4 公式：诚实第一

- 没有视觉时，公式由「OCR 上下文 + 学科标准形式」重建；**变量定义与适用条件以正文为准**。
- 结构复杂／上下标存疑／常数无法确认 → 公式后加
  `\tocheck{未对照原页面图像：<具体存疑点>}`。**不要写「已核对」**，不扣分；假称核对是严重问题。

## 5 图表

- 图题顺序：**图是什么 → 读者看什么 → 条件与局限 → 来源**；图源类别必须标
  `\modelmark`（模型计算）／`\schemamark`（示意）／`\redrawmark`（据原书改绘）。
- 真实谱图默认不要裁；单栏图 `width=\onecolwidth`，跨栏 `\twocolwidth`，**不得超**。
- 承载长文字的 node **必须给 `text width`**；pgfplots 的 `width/height` 含轴标签与刻度，
  不要再额外加「轴标签宽」。
- 长表放单栏整页：`\widepageson / \widepagesoff`，表宽 `\textwidth`，用 **longtable + 定宽 `p{}`**。

## 6 提交前必跑

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap <分片名>`
→ 必须 `RESULT: PASS`，且 errors / overfull >5pt / missing glyphs 全 0。

## 7 高频坑（完整版见 HANDOFF §7 / STYLE_GUIDE）

- **缺字静默丢**：①②⑤、ⅠⅡ、µ 等 Fandol 无字形，TeX 不报错但字符消失 → 已把缺字数设为失败条件。
- `\ce{Mo=O}` 会渲染成两个连字符 → 写 `\ce{Mo{=}O}`（箭头 `<=>` 里的等号不要动）。
- `\underbrace` 在本字体下退化成粗黑条，**禁止使用**。
- **重复 `\input`** 会让正文重复排页而六项门禁全报 0 → `tools/check_includes.py`。
- 不要用 `\dimexpr` 派生列宽；每个 `\sloppy` 后重设 `\emergencystretch` 为 10em。
- pgfplots：绘图表达式必须传自变量（`{fn(x)}`）；`declare function` 放在 `tikzpicture` 之后、
  `groupplot` 之前。

## 8 回复格式（短，不要复述正文）

1. 文件路径、编译页数、覆盖节次；2. **FORMULA_VERIFY 清单**；3. 未完成项与 `\tocheck{}` 项。
