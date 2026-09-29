# 交接文档 · 《现代催化研究方法精要》

> 最后更新：2026-09-29（v0.5.0-pre 发布后）
> 上一轮负责人上下文已耗尽，本文用于**新会话无缝接手**。

---

## 1. 当前状态

| 项 | 值 |
|---|---|
| 成品 | 《现代催化研究方法精要：原理、读图与方法选择》 |
| 页数 | **309** |
| 分片 | **37**（`chapters/parts/`）|
| 最新提交 | `e75c654` |
| 线上 pre | **v0.5.0-pre**（release id=38）|
| 构建门禁 | errors / overfull>5pt / missing glyphs / undefined refs / dup labels —— **全 0** |
| 日志直查 | Overfull hbox 0 / vbox 0、Float too large 0、Missing character 0、Underfull vbox 0 |
| 叠印 | 图内元素 **0 处**；粗横线 0 / 粗竖线 0 |

**源头**：《现代催化研究方法新编》上、下册扫描 PDF（附件，见 §7）。

---

## 2. 立刻能跑的命令

```powershell
cd C:\Users\53150\Documents\deepseek-harness\default-workspace

# 全书构建 + 六项门禁（-Quick 草稿模式只查前三项；-Release 加 overfull>5pt/未定义引用/重复标签）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release

# 单分片 / 单章
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11-c
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11

# 图内元素叠印（真实墨迹几何，非目测）
python tools/overlap_check.py

# 重复 \input / \IfFileExists（第七项门禁，尚未接入 build.ps1）
python tools/check_includes.py

# 术语一致性
python tools/check_terms.py

# 渲染原书页面供人工读图（上册 up / 下册 down）
python tools/vpage.py up 451 sources/pages/v451.png --dpi 500 --top 0.40 --bottom 0.62
```

---

## 3. 环境事实（不要重新摸索）

| 项 | 值 |
|---|---|
| TeX Live | `C:\texlive\2026\bin\windows\`（`build.ps1` 会动态解析，勿硬编码）|
| 引擎 | **XeLaTeX**（`ctexart` + `fontset=fandol`），`latexmk` 驱动 |
| Python | 3.14，含 `pymupdf` / `Pillow` / `numpy` / `fontTools` |
| Shell | **Windows PowerShell 5.1**，控制台 **GBK** |
| 仓库 | `http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials`（私有，`main`）|
| 认证 | Basic base64(`yuhanxue:ROTATED-2026-10-02`)；git URL 里 `#` 要写成 `%23` |

### ⚠️ 三条会反复咬人的环境陷阱

1. **中文不要经控制台管道。**
   `python -c "...print('中文')"` 或 `| Out-File` 会因 GBK 编码**抛 `UnicodeEncodeError` 并中断**，
   使后续的写文件**根本没执行**（已实际踩过一次：台账没更新，但命令看起来"跑了"）。
   → 一律**写脚本文件、结果写 UTF-8 文件、再 `Get-Content -Encoding utf8` 读**。

2. **提交信息里的特殊字符会被 PowerShell 解析。**
   例如 `git commit -m "... (?<!全)孔体积 ..."` 会把 `(?<!全)` 当命令执行，`commit` 失败。
   → **提交信息一律用 `git commit -F <文件>`**。

3. **`Invoke-RestMethod -Form` 不存在**（PS 5.1）。
   → 上传 release 附件用 `curl.exe -F`。

---

## 4. 项目结构与关键约定

```
main.tex                    封面、目录、按序 \IfFileExists 引入各章
style/preamble.tex          版面契约（geometry、字体、浮动体、间距）
style/macros.tex            六环节环境 + \src/\figsrc/\tocheck/\pedset/\supp/各 mark 宏
chapters/chNN.tex           精简装配器（只列 parts 的 \IfFileExists）
chapters/parts/chNN-x.tex   独立编写的分片（主要写作单位）
sources/                    台账：coverage.csv、page_map_*.csv、formula_verify.md、errata.md…
sources/parts/*.txt         源文本切片（按**页码**切）
tools/                      构建、检查、修复脚本
release/                    （gitignore）release 版 PDF 暂存
reviews/                    gpt6_astra 的评审与 TODO
WRITER_BRIEF.md             ★ 写作规范与全部已知坑，派单前必读
```

### 版面契约

- **单栏**（已从双栏迁移），版心 **165 mm**，A4，10 pt，`twoside`
- 图宽：`\onecolwidth` ≈ 132 mm；`\twocolwidth` ≈ 158 mm
- **禁用 `figure*` / `table*`**（单栏下非法，需用 `tools/unstar_floats.py` 转换）
- 长表用 **`longtable` + 定宽 `p{}`**；**不要用 `xltabular`**（按整表高度反算列宽，30 行表会每页只排一行）

### 写作单位

一个分片 = 2 个 `\subsection` + 若干 `\subsubsection`，含**六环节**各至少一处：
`probout` / `principle` / `measure` / `dataflow` / `pitfall` / `crosscheck`；
外加至少一个读图实例，**`obs` 与 `infer` 严格分开**。

### 页码映射（已验证）

- **上册**：`书内 = PDF − 19`，恒定，无缺页
- **下册**：`书内 = PDF + off`，**8 段**，段边界在 PDF 页 **18 / 19 / 60 / 225 / 226 / 297 / 372 / 373**，`off ∈ {507…514}`
- **7 个印刷页不在 PDF 中**：526、568、734、736、808、884、886
- ⚠️ **逐端点用它自己所在段的偏移换算**——已查出 3 处「第二个端点误用第一个端点所在段的偏移」（差正好 1 页）
- ⚠️ 下册章首页与附录首页带**假书眉**（在文字层里但扫描件上没有）

---

## 5. 未完成事项（按优先级）

### P0 —— 75 张表补来源标注（**当前最大的实质缺口**）

`figure_table_list.csv` 实测：**图 58 张里只缺 9 条来源定位，而表 85 张里 75 张完全无来源标注**，
`ch04` 一章 **14 张表全无**。有定位的 10 张表还用成了 `\figsrc{}` 而非 `\src{}`。

本书的核心承诺是「**每个方法和数据都能追溯到原书**」，**表的可追溯性接近空白**。

清单在 `sources/figure_table_list.csv`（筛 `source_location` 为空且 `kind=table`）。

### P1 —— 公式逐条核对（已完成 1/100+）

台账：`sources/formula_verify.md`。**方法已跑通**（见 §6 的示范案例）：

1. 用文字层 `get_text()` 定位公式所在 PDF 页与关键词
2. `tools/vpage.py` 高分辨率渲染该区域
3. `read_image` 读图
4. **与数值/物理一致性交叉验证**（不要只"看像不像"）

已完成示范：**#19 ATR 穿透深度** → 证实原书符号定义冲突（0.836 μm vs 物理正确值 2.005 μm），
本稿此前的修改正确。

### P2 —— 工程收尾

- `check_includes.py` **接入 `build.ps1`** 作为第七项门禁（脚本已写好，只需调用）
- `chapters/parts/` **行尾风格混用**（17 CRLF-only / 19 LF-only），建议单独一次纯格式提交
- `ch11-b:6`、`ch11-d:8` 两处**过期头注释**
- `fig:ch04b-pld` / `fig:ch04b-texture` 缺 `\modelmark`；`fig:ch07b-co-model` / `fig:ch07c-transient`
  的 `\modelmark` 在图体内、题注外（成品图题看不到）
- 全书**无参考文献机制**（`\cite` 零命中），原书人名+年份无法回溯

---

## 6. 已修 / 已核实（不要重复劳动）

### 引用正确性（全是「编译不报错、门禁查不出」的静默错误）

- **页码标注 1046 条逐条比对**，修 12 条 → **952 条双侧标注 MISMATCH = 0**
  两条已印进成品：引用了**不存在的印刷页 734**、范围末端**指向封底**
- **目录页码修 10 个**（第 9 章曾差 2 页）+ 2 处错误页眉（p191/p271）
- **图号** 11 处补「原书」标记（最严重一处写「**本书**表 7-16」）
- **式号** 修 (11-58) 空号；裸写原书式号加「原书」**55 处**
- **册次码** `ch08-c` 8 处把下册第 8 章写成 `S1`，**指向上册不存在的章**

### 三处覆盖空洞（同一根因，全部已补）

`sources/parts/*.txt` 按**页码**切，节边界不落在页码边界上 → 节被切碎 → 碎块无人认领，
而 `\IfFileExists` **不报任何错**。

| 空洞 | 补为 |
|---|---|
| §6.3 | `ch06-c` |
| §11.5.1 阻抗谱基本原理 | `ch11-d` |
| §11.5.2 前半（书内 p.862—865）| `ch11-e` |

**教训**：源切片边界必须与节边界对账；三处都是靠**人核对分片边界**发现的。

### 其他

- 术语：「现场」→「原位」第 11 章 39 处（含 5 个小节标题）
- 结构：`ch11.tex` 装配顺序 **a→b→d→e→c**（按源书节序）
- 版面：`Underfull \vbox` **92 → 0**（`\raggedbottom`；代价是 96 页底部留白略增）
- 台账：`figure_table_list.csv` **39 → 143 条**全覆盖，`caption_head` **143/143 与成品一致**
- 判定「不改」并记录理由的：`ch01-c` 的「现场」= 工业装置现场；110 个孤儿公式；
  3 个浮动体加 label 后不补引用（可引用位置都指向**原书**图）

---

## 7. 已知坑（WRITER_BRIEF.md 有完整版，这里是高频项）

### 静默失败类（不报错，最难查）

| 坑 | 表现 | 规避 |
|---|---|---|
| `\underbrace` | TeX Gyre Termes Math 缺横向花括号字形 → 退化成 **4.48 pt 粗黑条**。**文字层完全正常**，字符/字体/嵌入检查全查不出 | 全书已无；勿用 |
| `\ce{Mo=O}` | 渲染成两个 en-dash，不是 `=`。**无编译错误、无缺字计数** | 写 `\ce{Mo{=}O}`；**箭头 `<=>` 里的等号不要动** |
| 缺字 | ①–⑤、Ⅰ Ⅱ Ⅲ、𝜇 等 Fandol 无字形，**静默丢字** | `^{\circ}`→字面 `°`；`\unit{\mu m}`→字面 `µm`；已把缺字数设为构建失败条件 |
| **重复 `\input`** | 分片被引入两次、正文重复排页，**六项门禁全报 0**（已实测）| `tools/check_includes.py` |
| `calc` 改写 `\dimexpr` | `p{\dimexpr0.18\onecolwidth\relax}` → `Illegal unit of measure` + `calc Error` | **不要用 `\dimexpr` 派生列宽**，用固定 mm 或纯 `X` |
| `\sloppy` | 会把 `\emergencystretch` 重置为 3em（**比全局 5em 小**），加了反而更易 overfull | 每个 `\sloppy` 后重设 10em |

### 几何类（本项目反复栽跟头）

- **`minimum width` 是"最小"宽度**，文字长时实宽更大（曾按 15 mm 半宽算，实际 24.8 mm，两轮都没修对）
- **`below left=<v> and <h> of <父节点>` 定位的是节点角点** → 多个子节点会从父节点中心散开并互撞。
  **多个子节点请写显式 `at (x,y)` 坐标**
- **承载长文字的 node 必须给 `text width`**
- **pgfplots 的 `width`/`height` 含轴标签与刻度**，不是坐标轴盒。
  `groupplot` 总宽 ≈ `n×width+(n−1)×sep`，**不要再加左侧轴标签宽**（重复计入）
- **`\addplot {fn(\p)}` 报 Undefined control sequence** → 绘图表达式必须传自变量 `x`，写 `{fn(x)}`
- **`legend pos=outer north east` 会把图撑出栏宽**；legend 锚在轴顶时，提高 `ymax` 可压低曲线而图例不动

### 方法类（最贵的教训）

- **没有视觉 ≠ 不能核对图像**。本项目一度以为无法核对，实际**可以且必须做**（§5 P1 的方法）。
  但要**提高渲染质量 + 与文字层/数值交叉验证**，不要只凭"看像不像"
- **归因于外部（OCR、LaTeX、并发）之前，先排除自己的工具**。
  实例：台账里的「OCR 损坏」其实是 `build_figlist.py` 把 `$\theta$` 清成了 `$ $`
- **改了内容就要回头检查所有指向它的说明**（实例：删了一段 `\tocheck`，`\srcnote` 就成了过期注）
- **改了结构就要重新核对所有依赖该结构的指代**（实例：调 `ch11.tex` 顺序后，
  `ch11-c` 的「见上文 §11.5.1」变成假陈述、前一节编号层级变了）
- **「有 N 个 X」不是动手的理由，先问「这算不算错」**。
  实例：110 个孤儿公式不是缺陷（教科书给所有独立公式编号是常规）；去编号会让全书 355 个公式重新编号
- **子代理的结论必须独立复核**。本项目多次出现「声称做了、实际没做」（有一条只发了进度消息就结束）、
  「数字不对」（报 29 处，实测 23 处）、「归因错误」。**查 `git status` 与文件内容，不看措辞**
- **写原子化**：要求子代理**第一个工具调用就落骨架**，再读源文件。
  本项目有 5 次「读到一半超时/崩溃，文件从未落盘」，骨架优先救活了其中 3 次

### 并发类

- **不要在两个 agent 跑同一 `-Chap` 时构建**：`check_chapter.ps1` 曾用通配符删 `build/chk_*.aux`
  且静默吞错，导致「大量假报错而源文件哈希未变」。**已修**（jobname 含 PID+随机串），
  但**判断原则不变：报错先看源文件哈希有没有变**
- **不要在旧作者未结束时派新作者**（本项目出过两个作者并发写同一分片、对同一段阈值给出矛盾数字）
- **派单前先查「这件事是不是已经做完了」**——上一轮有三个任务书前提全是过期的

---

## 8. 如何接手（建议顺序）

1. 读 `WRITER_BRIEF.md` 与本文
2. `pwsh -File tools/build.ps1 -Release` 确认基线是 309 页 / 六项全 0
3. `python tools/check_includes.py`、`python tools/overlap_check.py` 各跑一次
4. 从 §5 的 **P0（75 张表补来源标注）** 开始
5. 每改一处，**说明改前/改后实测值**；判据不要放宽，内容不要删

### 版本发布流程

```powershell
Copy-Item build\main.pdf release\catalysis-methods-essentials-vX.Y.Z-pre.pdf
# 用 REST API 建 release（tag_name/target_commitish/name/body/draft/prerelease）
# 用 curl.exe -F 上传附件（PS 5.1 无 Invoke-RestMethod -Form）
```

---

## 9. 台账文件索引

| 文件 | 内容 |
|---|---|
| `sources/coverage.csv` | 源书章节覆盖表（362 行）|
| `sources/page_map_{up,down}.csv`、`page_map.md` | PDF 页 ↔ 书内页映射 |
| `sources/chapter_ranges.csv` | 各章页码范围 |
| `sources/formula_verify.md` | 公式核对台账（含**核对失败的如实记录**）|
| `sources/errata.md` | 来源书勘误 |
| `sources/terminology_decisions.md` | 术语裁定 + **刻意不改**清单 + 复现方式 |
| `sources/figure_table_list.csv` | 图表来源台账（143 条，19 列）|
| `sources/assignments.md`、`slice_queue.md` | 分片派单与队列 |
| `reviews/2026-09-28-initial/` | gpt6_astra 的评审、TODO、findings.json |
| `_audit/` | 上一轮三路自审核的报告与脚本（**gitignore，但仍在本机**）|
