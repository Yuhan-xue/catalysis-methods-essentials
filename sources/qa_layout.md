# 版式标定记录（sources/qa_layout.md）

记录依据：企划 v0.1 §6；标定日期与工程见 `build/`。**本文件是版式契约的实测依据，
改动 preamble 后必须回到这里更新。**

## 1. 实测页面参数

| 项目 | 企划要求 | 实测 | 结论 |
|---|---|---|---|
| 纸张 | A4 竖版 | 595.28 × 841.89 pt | ✔ |
| 水平版心 | 183 mm | 520.685 pt = 183.62 mm | ✔ |
| 栏间距 | 6 mm | 17.07 pt = 6.02 mm | ✔ |
| 栏宽 | ≈ 88.5 mm | 251.807 pt = 88.82 mm | ✔ |
| 版心高 | 页眉页脚计入 | 727.35 pt = 256.5 mm（含 headheight 11 pt、headsep 3.5 mm、footskip 5 mm） | ✔ |
| 正文 | 10 pt | 10 pt（FandolSong） | ✔ |
| 基线距 | ≈12.5 pt（允许 13） | **12.5 pt**（`\linespread{1.0417}`；ctex 默认 15.6 pt 过松，已收紧） | ✔ |
| 西文与数学 | 单一 Times 风格 | TeX Gyre Termes + TeX Gyre Termes Math（unicode-math） | ✔ |
| 中文字体 | 可复现 | Fandol（随 TeX Live 分发） | ✔ |

## 2. 密度标定（`tools/makedensity.py`）

- 9000 个纯汉字 → **4 页**，均值 **2250 字/页**（含章首页，章首页因全宽章标题较少）；
  整页纯文字约 **2500 字**。
- 样板章 `chapters/partsch01-a.tex` 实测：p.1 1798 字 + 2 表；p.2 1133 字 + 1 跨栏图；
  p.3 803 字 + 2 图。含图表页约 **1400—1800 汉字当量**。
- 结论：企划 §6.3 的「1400—2200 汉字当量/页」成立，按其上沿估算全书章节预算。

## 3. 已解决的两个 overfull（重要，会重复出现）

两类原因都已定位到**精确数值**，不是猜的：

1. **pgfplots 的 `width=` 不约束轴标签。**
   实测：`width=\columnwidth`（251.81 pt）且 `ylabel` 用 `\dfrac` 时，
   实际盒子 **260.18 pt**，超栏宽 **8.37 pt**。`scale only axis` 会让情况更糟
   （`width=\columnwidth` 实测 **292.60 pt**，超 40.8 pt）。
   → 对策：`\onecolwidth` 定为 **84 mm**、`\twocolwidth` 定为 **176 mm**，各留余量；
   章作者自行写死宽度时，必须跑 `check_chapter.ps1` 确认无 Overfull。

2. **`groupplot` 的总宽 ≈ 3w + 2·sep + 约 25 pt（标签外扩）。**
   实测：`3×52 mm + 2×11 mm` = **529.01 pt**，超版心（520.69 pt）**8.3 pt**。
   → 对策：IUPAC 六型图改为 `width=50 mm, horizontal sep=9 mm`，实测 **500.56 pt** ✔。

3. 中文断行缺连字点，另设 `\emergencystretch=3em` 兜底。

## 4. 已通过的验收项

- **中文书签**：`\chapterstart` 写入目录与页眉，`\@starttoc` + `bookmark` 生成层级书签 ✔
- **字体嵌入**：7 个字体全部 `EMBEDDED`（FandolSong/Hei、TeXGyreTermes/‑Bold/‑Math/‑Cursor）✔
- **正文可检索**：`get_text` 正常取出中文 ✔
- **章起始**：`\chapterstart{标题}{导读}` 一次完成编号 + 目录 + 页眉 + 全宽章标题，
  不强制起新页、不插空白页，符合企划 §6.1 ✔

## 5. 已排除的坑（记录以免重犯）

| 现象 | 原因 | 处置 |
|---|---|---|
| `Command \c@dblbotnumber already defined` | `stfloats` 与 `dblfloatfix` 冲突 | 只保留 `dblfloatfix` |
| `\begin{complement} ended by \end{list}` | 环境名 `complement` 与 amssymb 的 `\complement`（∁）冲突 | 改名 `crosscheck` |
| 整页文字当正文排出、`#` in horizontal mode | 前一行注释吃掉了换行，`\newcommand` 被注释掉 | 已删；**注释行必须以换行结束** |
| `Dimension too large` | pgfplots 求 `exp(-(x-a)^2/w)`，`w` 过小导致 `e^-24410` | 改用有界式 `1/(1+((x-a)/w)^2)`，或控制指数绝对值 ≲200 |
| `pdfinfo` 参数绑定报错 | PowerShell 局部变量 `$pages` 与 `[switch]$Pages` **大小写不敏感**同名 | 局部变量改名 `$nPages` |
| 脚本无法执行 | 执行策略禁止未签名脚本 | 用 `pwsh -ExecutionPolicy Bypass -File` |
