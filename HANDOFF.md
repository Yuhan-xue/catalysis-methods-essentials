# 交接文档 · 《现代催化研究方法精要》

> 最后更新：2026-09-29（v0.5.0-pre 发布后）
> 上一轮负责人上下文已耗尽，本文用于**新会话无缝接手**。

---

## 1. 当前状态

| 项 | 值 |
|---|---|
| 成品 | 《现代催化研究方法精要：原理、读图与方法选择》 |
| 页数 | **310**（P0 收口后；基线 `feb8739` 实测 309，+1 页已对账，见 §5 P0）|
| 分片 | **37**（`chapters/parts/`）|
| 最新提交 | `9e197cd`（P0 收口；此前 `175a8d8`、`78f1c22`、`2325bbf`）|
| 线上 pre | **v0.5.0-pre**（release id=38；**P0 收口后尚未重新发布**）|
| 构建门禁 | errors / overfull>5pt / missing glyphs / undefined refs / dup labels / **dup includes** —— **全 0** |
| 日志直查 | Overfull hbox 0 / vbox 0、Float too large 0、Missing character 0、Underfull vbox 0 |
| 叠印 | 图内元素 **0 处**；粗横线 0 / 粗竖线 0 |

**源头**：《现代催化研究方法新编》上、下册扫描 PDF（附件，见 §7）。

---

## 2. 立刻能跑的命令

```powershell
# 先 cd 到仓库根（下面的路径是上一轮作者的工作副本；仓库可放在任何位置，
# tools/build.ps1 用 $PSScriptRoot 推导根目录，不写死路径）

# 全书构建 + 六项门禁（-Quick 草稿模式只查前三项；-Release 加 overfull>5pt/未定义引用/重复标签）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release

# 单分片 / 单章
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11-c
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11

# 图内元素叠印（真实墨迹几何，非目测）
python tools/overlap_check.py

# 重复 \input / \IfFileExists（第七项门禁，已接入 build.ps1，draft 模式也拦）
python tools/check_includes.py

# 术语一致性
python tools/check_terms.py

# 图表来源标注门禁（P0；见 §5）
python tools/check_src.py                 # 全部表
python tools/check_src.py --unlabeled     # 只看还没写来源的
python tools/check_src.py ch04-c          # 只查一个分片

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

1b. **`.ps1` 文件必须带 UTF-8 BOM。**
   PowerShell 5.1 对**无 BOM** 的文件按 ANSI（本机 = GBK）解码。中文字符串被误解码后仍然
   "能跑"，但 GBK 双字节的**尾字节可以吃掉紧随其后的 ASCII 字符**（`}`、`"` 都在 GBK 尾字节
   范围 0x40–0x7E 内）——于是脚本报出一堆**莫须有的语法错误**（`意外的标记`、`字符串缺少终止符`），
   而错误行号指向几百行之外毫无问题的代码。
   → 2026-09 实测：`tools/build.ps1` 原本就没有 BOM，一直靠运气跑通；给它加了几句中文注释后
   立刻炸。判据与修法（`edit` 类工具会**丢掉** BOM）：
   ```powershell
   $b = [IO.File]::ReadAllBytes($p); '{0:X2} {1:X2} {2:X2}' -f $b[0],$b[1],$b[2]   # 应为 EF BB BF
   $t = [IO.File]::ReadAllText($p, [Text.Encoding]::UTF8)                          # 按 UTF-8 读进来
   [IO.File]::WriteAllText($p, $t, [Text.UTF8Encoding]::new($true))                # 带 BOM 写回
   # 语法自检（不执行）：解析器报错才是真错
   $e = $null; $null = [System.Management.Automation.Language.Parser]::ParseFile($p, [ref]$null, [ref]$e)
   if ($e.Count) { $e | ForEach-Object { $_.Extent.StartLineNumber.ToString() + ' ' + $_.Message } } else { 'syntax OK' }
   ```

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
- ✅ **页标记的语义可以用印刷页码当场自证**（2026-09 新发现，比偏移反推可靠）：
  切片里 `[[UP PDF p.X | 书内 p.Y]]` 之后紧跟的页眉/页脚行**本身就印着书内页码**。实例：
  `sources/parts/ch07-c.txt:958` 的标记是 `[[UP PDF p.525 | 书内 p.506]]`，下一行 `:959`
  OCR 出「５０６　　现代催化研究方法新编（上册）」；`:1077` 下一行出「第７章原位红外光谱方法　·５０７·」；
  `:1213` 下一行出「·５０８　现代催化研究方法新编（上册）」。→ **标记 = 该印刷页内容的起点**，
  标记之后的内容属于标记所写的书内页。**任何对页标记解读的怀疑，用这个办法自证。**
- ⚠️ `tools/check_src.py` 内嵌的 101 条 OCR 表号索引，其页码可能比实测**低 1 页**
  （如 `'7-19': 504`、`'7-20': 505`，实测两表分别在书内 p.505、p.506）。索引**只**用于判定
  「表号是否真实存在」，**页码一律以切片页标记为准**，两者不一致不算错。

---

## 5. 未完成事项（按优先级）

### P0 —— 75 张表补来源标注 ✅ **已完成（2026-09-29 收口）**

`figure_table_list.csv` 实测：**图 58 张里只缺 9 条来源定位，而表 85 张里 75 张完全无来源标注**，
`ch04` 一章 **14 张表全无**。有定位的 10 张表还用成了 `\figsrc{}` 而非 `\src{}`（已改）。

本书的核心承诺是「**每个方法和数据都能追溯到原书**」，**表的可追溯性接近空白**。

**收口状态（一律以命令为准）**：`python tools/check_src.py` → **`checked 85 tables: PASS 85, REVIEW 0, FAIL 0`**
（名单 75 张全部闭环，判据同时覆盖全书 85 张表）。逐分片 `check_src.py <分片>` +
`check_chapter.ps1 -Chap <分片>` 双门全 PASS。完整构建 `tools/build.ps1 -Release` →
**310 页 / errors 0 / overfull>5pt 0 / missing glyphs 0 / undefined refs 0 / dup labels 0**。

**页数 309 → 310 已对账（不是回归）**：同一台机器上把基线提交 `feb8739` 检出到临时 worktree 重跑
`build.ps1 -Release` 得 **309 页**，当前工作树 **310 页**；再逐条对账 `build/main.toc` 的 143 个条目，
**128 条的页码发生位移，首个位移在 §1.3（p.7→8），其后单向累积，净 +1 页**——这是 75 处题注新增
来源句（约 3 千字符）带来的正常内容增长；浮动体错排的特征是局部跳页后回弹，不会一路上移。
`\src{}` 只加文字、内部不含 `\ref`，因此 undefined refs 与 dup labels 不受影响（实测均为 0）。
**接手的 agent 若要复核：`git worktree add --detach <临时目录> feb8739` 后在那里跑 build.ps1 即可，别改本仓库的基线。**

#### 进度与续作（2026-09）

- 已提交 `2325bbf`（7 张）+ `78f1c22`（28 张）；此后按分片成批推进（B1–B6 各 5 个分片，
  每批 5 个并行子代理、写域互不重叠）。**进度以命令为准，不要看这里的数字**：
  `python tools/check_src.py --unlabeled` 的 FAIL 数就是剩余量（曾为 75，收口时 0）。
  每批改完跑该命令复核 + 抽读 `git diff` 与 `sources/_p0_out/<分片>.json` 的 `evidence`
  （**不看措辞，看文件**——本项目已 6 次出现子代理「声称做了、实际没做」）。
- **门禁：`tools/check_src.py`**（受版本控制）。`python tools/check_src.py` 查全部表；
  `--unlabeled` 只看尚未标注的；带分片名只查该分片。判据三条：①题注**内**有 `\src{}`；
  ②引用给出**可信页码对**，或明确声明「非源书」；③引用的原书表号必须在内嵌的
  101 条 OCR 表号索引里（编造表号比写不出更糟）。
  它以交接提交 `feb8739` 为基线做逐端点偏移一致性校验——**不要拿 HEAD 当基线**，
  那等于用自己新写的页码给自己背书。
- **三种模板**（A 照原书某张表 / B 据某节正文归纳 / C 数值是本改编本自造）见
  `sources/_p0_BRIEF.md`——**该文件是本机草稿、未入库**（`.gitignore` 的 `_*` 规则），
  换机器需重写；判据已固化在 `check_src.py` 里，模板写作规则在下方「来源标注约定」。
  同类**未入库**的过程证据还有：`sources/_p0_prompts/<分片>.md`（工作单）、
  `sources/_p0_evidence/<分片>.md`（证据包）、`sources/_p0_out/<分片>.json`（逐表回执，
  含每个页码端点对应的切片行号）。**这些是草稿、不是交付物**——可追溯性由 `\src{}` 本体 +
  `check_src.py`（每次运行都拿 `feb8739` 基线复算偏移）保证，不依赖它们是否随仓库走。
- **`\src{}` 必须写在 `\caption{}` 内部末尾**（STYLE_GUIDE 第 10 节第 7 条：图表都在题注里按
  「是什么—看什么—条件—来源」写全）。这类缺陷共发现 **9 例、两种错法**：①来源行写在
  `\end{tabularx}` 之后、题注之外（`ch02-b`×3、`ch06-c`×2、`ch09-a`、`ch11-c`、`ch12-b` 共 8 例，
  已全部搬入题注）；②来源写在**表格单元格里**、题注反而没有（`ch09-d.tex:199` 的
  `tab:ch09-so`，已把单元格里的 `\src` 移入题注）。
- **多段页码的两种写法在 `check_src.py` 下都能解析**（`、`-分段与分号分段），但已弃用的
  `tools/_p0_verify.py` 只认后者。子代理曾据旧脚本误判「合法的 `、`-分段会被判 FAIL」
  并绕开它（**观测可信、归因错**的第 4 例）——判据一律以 `tools/check_src.py` 为准。
- **不要写进题注的东西：核对状态。** 全书有 250+ 处 `\tocheck{未对照原页面图像：…}`，
  `\tocheck{}` 才是它的用法；`\src{}` 只说明内容出自原书哪一处。本版不标「已核对」，
  该约定已写入 `chapters/ch00-intro.tex` 的「术语、符号与来源约定」。
- **台账是派生的，不要手改**：`sources/figure_table_list.csv` 由 `tools/build_figlist.py`
  从 .tex 里的 `\src{}`/`\figsrc{}` 生成。P0 改完后跑 `tools/build.ps1 -Release`
  再跑 `python tools/build_figlist.py` 即自动同步。`review_status` 一列恒为常量
  「未核对页面图像」，没有区分度，**别拿它当状态位**。
- **`ch12-c` 与 `ch13-synthesis` 没有原书表可引**：第 12 章整章只有图 12-1…图 12-35、
  没有任何编号表格（两轮独立扫描证实，不是 OCR 漏认），第 13 章没有源切片。
  这 4 张表只能走模板 B/C。
- **OCR 会把表号与紧随其后的文字粘连**：`表３一７４种升温速率下热重基础数据` 是「表 3-7」
  +「4 种升温速率下热重基础数据」，`参看表４－７０` 是「表 4-7」+「0」残迹。
  **3-7 与 4-7 都是真实的表**，别当误读丢掉（`check_src.py` 的内嵌索引已收两个别名）。

##### 来源标注约定（选模板时照抄）

```latex
% A —— 原书确有这张表（文本层能读到 表N-M 且内容对得上）
\src{据 S1（上册）表 6-1，书内 p.364 / PDF p.383。}
% B —— 原书没有这张表，是据某节正文归纳的
\src{据 S2 §10.5.3—§10.5.4，书内 p.788—800 / PDF p.277—289 归纳。}
% C —— 数值是本改编本自造的教学设定／模型计算（必须明说）
\src{本表为本改编本归纳，非源书表格；依据 S1 §4.1.2，书内 p.227—231 / PDF p.246—250。
表中消光条件由结构因子 $F(hkl)=0$ 推出，非源书实验数据。}
```

**页码只能从两个地方读出来**：分片里已有的 `\src{}`/`\figsrc{}`，或源切片的
`[[UP PDF p.X | 书内 p.Y]]` 页标记。**不许用偏移量反推页码**（读出后可用 §4 的映射验算）。
页码区间与表号写法**首选跟随所在分片既有写法**，分片内无先例时用长破折号 `—`
和半角连字符 `表 1-10`。


### P1 —— 公式逐条核对（已完成 1/100+）

台账：`sources/formula_verify.md`。**方法已跑通**（见 §6 的示范案例）：

1. 用文字层 `get_text()` 定位公式所在 PDF 页与关键词
2. `tools/vpage.py` 高分辨率渲染该区域
3. `read_image` 读图
4. **与数值/物理一致性交叉验证**（不要只"看像不像"）

已完成示范：**#19 ATR 穿透深度** → 证实原书符号定义冲突（0.836 μm vs 物理正确值 2.005 μm），
本稿此前的修改正确。

### P2 —— 工程收尾

- ✅ `check_includes.py` **已接入 `build.ps1`** 作为第七项门禁（2026-09 完成）。
  它**静态**检查重复 `\input`/`\IfFileExists`，与编译无关，因此 draft 模式也拦
  （该缺陷会让正文重复排页，而其余六项门禁全报 0）。python 或脚本不可用时该项打印
  `skipped` 而不是静默放过。
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
  - ⚠️ **前提是宿主真的有视觉。** 2026-09 续作会话**实测本环境没有**，三层独立证据：
    ①`read_image` 只回传 `image/png image, WxH px, N bytes` + sha256，**无任何像素**；
    ②子代理盲测（随机码图，答案文件已移出仓库）得到逐字相同的回传，答不出码/形状/颜色；
    ③DSH 源码 `@deepseek-ai/dsh-llm/lib/types/content.js:47-50` 有
    `textOnlyImageText(ref)` → `[image omitted because this model accepts text only; attachment sha256:…]`。
    因此 **`STYLE_GUIDE.md` 第 10 节第 3 条「所有公式已对照原页面图像核对」在该会话中无法执行**——
    当时一律按 `\tocheck{待核对}` 处理，**没有假称核对**。接手的 agent 请**先自测一次再决定**：
    渲染一张带随机码的图，把答案写进文件，`read_image` 后核对；答不出就是无视觉。
- **归因于外部（OCR、LaTeX、并发）之前，先排除自己的工具**。
  实例：台账里的「OCR 损坏」其实是 `build_figlist.py` 把 `$\theta$` 清成了 `$ $`
- **改了内容就要回头检查所有指向它的说明**（实例：删了一段 `\tocheck`，`\srcnote` 就成了过期注）
- **改了结构就要重新核对所有依赖该结构的指代**（实例：调 `ch11.tex` 顺序后，
  `ch11-c` 的「见上文 §11.5.1」变成假陈述、前一节编号层级变了）
- **「有 N 个 X」不是动手的理由，先问「这算不算错」**。
  实例：110 个孤儿公式不是缺陷（教科书给所有独立公式编号是常规）；去编号会让全书 355 个公式重新编号
- **子代理的结论必须独立复核**。本项目多次出现「声称做了、实际没做」（有一条只发了进度消息就结束）、
  「数字不对」（报 29 处，实测 23 处）、「归因错误」。**查 `git status` 与文件内容，不看措辞**
  - **观测可信、归因几乎必错**：2026-09 续作里 5 个子代理的*现象观察全部正确*，*因果解释 3 个全错*
    ——三个分片都报「`\src` 里的 `--` 让校验器判 `NO PAGE PAIR`」是真的，
    但都归因成「`PAIR_RANGE` 的字符类不含 ASCII `-`」（原正则 `[—\-–−]` **含** `-`；
    真因是 ASCII 双连字符是两个字符，而字符类只吃一个）。**照着错归因去改会绕过问题而非修好它。**
- **删任何短语之前，先 grep 全书统计一次**。局部看着「不规范」的东西可能是全局惯例。
  实例：2026-09 续作里删了 `ch06-c` 一处 `\tocheck{未对照原页面图像：…}` 前缀，
  随后 grep 发现这是**全书 250+ 处的既有惯例**，只好原样恢复。
  判据：一个只出现在某处的写法才可疑；出现在 20 个分片里的写法是约定。
- **校验器自身也会犯错，而且它错了你不会知道**。实例：`check_src.py` 早期的引用正则用
  `r'书内(.*?)/PDF(.*?)(?=；|。|\n|$)'` 配 `re.S` —— `.` 把换行也吃掉，
  于是惰性匹配一路吃到**几行之后**的下一个 `。`，把不相干的页码吞进同一个「引用」里，
  凭空造出一批越界偏移（`-18`/`-28`/`490`/`530`…），**反而放宽了它的允许集**。
  改成把两侧页码项**显式拼出来**（`p.N` + 顿号/空格分隔的重复）后，分片偏移立刻收敛到
  §4 的权威模型。教训：校验器的输出分布本身要当数据看；**越界的异常值不一定是数据错，
  也可能是量具错**。
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
| `sources/figure_table_list.csv` | 图表来源台账（143 条，19 列）——**由 `tools/build_figlist.py` 从 .tex 派生，不要手改** |
| `sources/assignments.md`、`slice_queue.md` | 分片派单与队列 |
| `reviews/2026-09-28-initial/` | gpt6_astra 的评审、TODO、findings.json |
| `_audit/` | 上一轮三路自审核的报告与脚本（**gitignore，但仍在本机**）|
