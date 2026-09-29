# 交接文档 · 《现代催化研究方法精要》

> 最后更新：2026-09-30（v0.6.0-pre 发布后）
> 上一轮负责人上下文已耗尽，本文用于**新会话无缝接手**。

---

## 1. 当前状态

| 项 | 值 |
|---|---|
| 成品 | 《现代催化研究方法精要：原理、读图与方法选择》 |
| 页数 | **313**（R2 修复后；P0 收口时 310、基线 `feb8739` 实测 309。中途曾因 `\samepage` 惩罚参数泄漏涨到 345 页，见 §6 方法类教训）|
| 分片 | **37**（`chapters/parts/`）|
| 最新提交 | `5109139`（第七项门禁 + `build.ps1` BOM；此前 `9e197cd`、`175a8d8`、`78f1c22`、`2325bbf`）|
| 线上 pre | **v0.6.0-pre**（release id=41，tag `v0.6.0-pre` @ `5109139`；附件 3970716 B，SHA-256 `C0FDD52B6B7A6740FFA3AFD125342DEE558D0C51907C5CEE67F3B4FE2EF40B08`，公开下载已回验字节一致）|
| 构建门禁 | errors / overfull>5pt / missing glyphs / undefined refs / dup labels / **dup includes** / **overlap** —— 全 0；`-Release` 下静态检查**没跑成（unavailable）判失败**（见 §2、§5 P2）|
| 日志直查 | Overfull hbox 0 / vbox 0、Float too large 0、Missing character 0、Underfull vbox 0 |
| 叠印 | 图内元素 **0 处**；粗横线 0 / 粗竖线 0 |

**源头**：《现代催化研究方法新编》上、下册扫描 PDF（附件，见 §7）。

---

## 2. 立刻能跑的命令

```powershell
# 先 cd 到仓库根（下面的路径是上一轮作者的工作副本；仓库可放在任何位置，
# tools/build.ps1 用 $PSScriptRoot 推导根目录，不写死路径）

# 全书构建 + 八项门禁（-Release 加 overfull>5pt/未定义引用/重复标签/版面重叠确认缺陷，
#   并把「静态检查没跑成」判为失败；draft 模式只拦编译错误与缺字）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release

# 单分片 / 单章
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11-c
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11

# 图内元素叠印（真实墨迹几何，非目测）；--gate 即第八项门禁，build.ps1 -Release 已调用
python tools/overlap_check.py
python tools/overlap_check.py --gate --pdf build/main.pdf --out build/overlap_all.txt

# 书签落页 / 后置页眉串章（R2-U01/U02 的程序化验收，只读；对旧 PDF 跑应复现缺陷）
python tools/pdf_probe.py --pdf build/main.pdf --out build/pdf_probe.txt

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
| 认证 | **不要把口令写进仓库**：在 Gitea 生成**受限访问令牌**，用凭据管理器或**仓库外**的 `~/.gitea-netrc`（Windows 上收紧该文件 ACL）注入，见 §8 发布流程示例。远程 URL 里**不要内嵌账户口令**；确需内嵌时必须用受限令牌，且 URL 中的 `#` 要写成 `%23`。 |

> ⚠️ **凭据纪律（R2-W01，未关闭）**：本文件此前**含明文认证信息，已移除**；但**历史提交里仍然存在**，
> 必须由账户管理者**轮换旧口令**、并决定是否清理历史之后，该项才能关闭（见
> `reviews/2026-09-30-round2/TODO.md` 的 R2-W01）。新增文档、脚本、命令示例一律**不写口令**。
>
> 另注：本地克隆的**未跟踪** `.git/config` 里若把凭据内嵌进 `remote.origin.url`（`https://` 之后、`@` 之前的那一段），
> 同样会随整机备份、截图、shell 历史外泄——接手后建议改成凭据管理器（`git config --global credential.helper manager`）
> 或 `git config --local credential.helper store --file=<仓库外路径>`，并**首先轮换口令**。

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
3. `read_image` 读图 ⚠️ **该步依赖宿主确实有视觉**；2026-09 续作会话实测**没有**（§7 方法类有
   三层证据与自测方法），那次 P1 只能推进到「OCR 文字层 + 独立复算」这一层
4. **与数值/物理一致性交叉验证**（不要只"看像不像"）——无视觉时这是唯一可用的判据

已完成示范：**#19 ATR 穿透深度** → 证实原书符号定义冲突（0.836 μm vs 物理正确值 2.005 μm），
本稿此前的修改正确。

### P2 —— 工程收尾

- ✅ `check_includes.py` **已接入 `build.ps1`** 作为第七项门禁（2026-09 完成）。
  它**静态**检查重复 `\input`/`\IfFileExists`，与编译无关，因此 draft 模式也拦
  （该缺陷会让正文重复排页，而其余六项门禁全报 0）。python 或脚本不可用时该项打印
  `skipped` 而不是静默放过。
- ✅ **第八项门禁 `overlap_check.py --gate` 已接入**（R2-W05）：只拦「两个描边图形确认相撞」，
  文字轮廓、数学上下标、合法嵌套框按候选分类报告，不按候选总数一刀切。本书实测
  `blocking=0 / candidates=99`。
- ✅ **静态检查的三种状态不再混同**（R2-W04）：`ok` / `FAIL` / `unavailable`（python 不可用、
  脚本缺失、调用异常、工具自报退出码 2）。**`-Release` 把 `unavailable` 判为失败**，
  不再出现「检查根本没跑成却打印 PASS」；draft 允许但必须打印 `skipped（原因）`。
- `chapters/parts/` **行尾风格混用**（17 CRLF-only / 19 LF-only），建议单独一次纯格式提交
- ✅ `ch11-b:6` 过期头注释**已改正**；`ch11-d:8` 复核后**本来就对**，未改
- **`\modelmark` 位置**（R2 复核：**不是缺声明，本轮不改**）：`fig:ch04b-pld`/`fig:ch04b-texture`
  的题注文字里已写「（模型计算）」并有 `\figsrc{模型计算图，非原书插图…}`；
  `fig:ch07b-co-model`/`fig:ch07c-transient` 的 `\modelmark` 在浮动体内、`\caption` 之后——
  虽不在题注内，但**读者看得到**（pdftotext 实测「［模型计算］」出现在 PDF p.159/p.170）。
  若要统一成「一律写进题注」，需重排题注并另起一轮构建
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

### R2 第二轮评审（2026-09-30）：16 项 → 15 项关闭

评审材料在 `reviews/2026-09-30-round2/`（`README.md` / `TODO.md` / `01`–`04` / `recheck_review.py` /
`verification.json`）。**逐项结论、复现命令与残余风险见 `reviews/2026-09-30-round2/VERIFICATION.md`**；
`verification.json` 是评审当时的「缺陷可复现」快照，**不是**绿色验收报告，别再拿它当成绩单。

**内容类 9 项（每项都补了可独立复算的证据）**

- `R2-C01/C02` `ch10-c.tex`：积炭速率主式补回漏掉的 $c_t$（原书 (10-135) 分子本来就含 $c_t$，
  OCR 下标行可证），附「0.5 vs 漏 $c_t$ 的 0.25」数值自检；临界粒径改 $\propto\sqrt{f}$ 缩放；
  两个基准都写 0.015、把 22.5 标为量纲不合格
- `R2-C03` `ch10-b.tex`：$j_D$ 左端补 $\rho$ 并定义之（量纲反证：$k_G$ 由 $Sh=k_Gd_p/D$ 定为 m/s，
  $G$ 为 kg·m⁻²·s⁻¹，原式左端 kg⁻¹m³ 不成立；源文 OCR 该处正有丢字符的空档）
- `R2-C04` `ch11-d.tex`：把「倒数之和」改回并联阻抗（倒数之和 = 导纳，10 Ω∥10 Ω = 5 Ω）
- `R2-C05` `ch12-b.tex`：平均周期改 $T=2\pi/\omega\approx2\pi/\omega_0$，并把「分母应补 2」
  写成**不采纳**的理由（三项独立复算都回到 $-\omega_0g/(2k)$，补 2 会使其减半）；源书同处排印
  问题记入 `sources/errata.md` 乙类 B10
- `R2-C06` `ch11-c/d.tex`：全章统一相角约定 $\varphi\equiv-\arg Z$，并明说源书图轴定义未核对
- `R2-C07` `ch01-a.tex`：BET 分开总量与单位质量量，给出双路径算例（0.1 g → 91.5 m² → 915 m²/g）
- `R2-C08` `ch03-b.tex`：DTG 改用实际质量导数 $-\dd m/\dd T$（峰值 0.4167 %/K）、横轴改 K，
  与本章 $T_p\approx673$ K 接通
- `R2-C09` `ch06-a.tex`：拉曼改 $I/I_0=(\dd\sigma/\dd\Omega)\Delta\Omega\sin^2\theta$，两端无量纲，
  可预测收集立体角加倍 ⇒ 信号加倍
- 台账 `sources/formula_verify.md` 同步（首轮「评审有误」的判定已撤销并留记录）

**导航类 2 项**

- `R2-U01/U02`：`\chapterheadstar` 原地写目录项 + `\markboth`，删掉 `main.tex` 里三处事后锚点；
  验收改由 `tools/pdf_probe.py` **程序化**完成（比目视可复现）：出厂 PDF `R2-U01 PASS（143 条不符 0）`、
  `R2-U02 PASS（命中 0）`；对 v0.6.0-pre 的旧 PDF 跑则逐条复现评审的 2 条错页 + 4 处串章页眉
- ⚠️ 踩过的坑：给 `\chapterheadstar@run` 加 `\samepage` 会让 `\interlinepenalty` **永久泄漏**
  （微测 0 → 10000，翻页不复位），页数 310 → **345**；已删，判据组合见 §7 方法类

**工程类 5 项**

- `R2-W01`：`HANDOFF.md` 三处明文凭据改为仓库外 `~/.gitea-netrc`（**仓库内部分已关闭**；
  旧口令仍留在历史提交与本机 `.git/config` 里，**须账户管理者轮换后才算关闭**）
- `R2-W02`：README 状态快照 + draft/release 两档命令 + 八项门禁表 + 「字节哈希每次都变」的说明
- `R2-W03`：`check_src.py` 三层结论（标注格式 / 目标页可达 / **内容人工核对本工具不判定**）
  + `.tex`↔台账集合差异；三个负例（页码 +10000、错原表号、未入账表）全部 exit 1
- `R2-W04`：`build.ps1` 新增 `Invoke-PyCheck` 三态 `ok/FAIL/unavailable`，`-Release` 把
  unavailable 判失败（「未检查 ≠ 通过」），draft 只打印 `skipped（原因）`
- `R2-W05`：`overlap_check.py --gate` 只拦确认相撞的图形，文字/上下标/粗条按类别报候选；
  退出码 0/1/2（2 = 没检查）；已接入 `-Release`

**必须留给下一位的三条残余风险**

1. `check_src.py` 的「目标页可达」是**二手证据**：源 PDF 不随仓库分发，判据依赖人维护的
   `sources/page_map_up.csv` / `page_map_down.csv`
2. `check_src.py` 第③层「内容人工核对」全书 **85/85 仍是「未核对页面图像」** ⇒
   **release PASS 只说明标注格式与页号自洽，不代表内容正确**
3. 重叠门禁默认只拦图形相撞（本书 `blocking=0 candidates=99`）；要把文字压文字也纳入阻断，
   须显式 `--block-text`——评审明确要求不得按候选总数一刀切

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
- **修导航这类「全局布局」缺陷，动手前先量页数与每页字数**。实例（R2-U01/U02）：为了让
  不编号章标题的锚点落在标题页，宏里加了 `\samepage`，结果 **310 → 345 页**。
  根因是 `\samepage` 的惩罚参数**永久泄漏**（微测 `build/_pen/pen.tex`：`\interlinepenalty`
  由 0 变 10000，跨段落 / `\section*` / `itemize` / 翻页都不复位）⇒ 全书段落再也不能跨页断开。
  **判据组合**：总页数 + 每页字数中位数（2039→1811）+「<800 字符页」计数（9→23）
  ——三者同向变化才说明是版面密度问题，而不是内容增减。修法：这里根本不需要 keep-together
  （`\phantomsection`/`\addcontentsline`/`\markboth` 都不产生垂直材料，锚点与标题之间无可断点），
  直接删掉 `\samepage`，页数回到 313。
- **验证探针必须先对「已知有缺陷的基线」跑一次**。`tools/pdf_probe.py`（R2-U01/U02 验收用）
  在新构建上报 PASS 不算证据——它在**发布版 310 页 PDF** 上必须复现出评审报告的那几条
  （书签 303/305 对标题 304/306；p.303/305/307/309 页眉仍印「第12 章…」），这才叫有灵敏度。
  首版探针曾因两个自身 bug 全判 FAIL：①用「去空白标题前 8 字」当键，而章标题印作
  「第1 章物理吸附…」、书签写作「1 物理吸附…」（中间夹一个「章」字）；
  ②把 `level1[-1]`（后置区块自身的「符号、缩写与索引」）当成「最后一个章」，
  于是把**正确**的页眉误报成串章。
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

### 版本发布流程（v0.6.0-pre 走的路径，已实测）

```powershell
# 0) 工作树必须干净，且发布构建从要发布的那个提交上跑
git status --short                       # 必须为空
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release
#    release 模式实测：pages 310 / errors 0 / overfull 0 / glyphs 0 / refs 0 / labels 0 / dup includes ok / PASS

# 1) 暂存成品并取哈希（写进 release notes 的「校验」段）
New-Item -ItemType Directory -Force -Path release | Out-Null
Copy-Item build\main.pdf release\catalysis-methods-essentials-vX.Y.Z-pre.pdf
(Get-FileHash release\catalysis-methods-essentials-vX.Y.Z-pre.pdf -Algorithm SHA256).Hash

# 2) 打轻量标签并推送（历史标签全是轻量标签：git cat-file -t v0.5.0-pre → commit）
git tag vX.Y.Z-pre <提交>
git push origin vX.Y.Z-pre

# 3) 建 release（用 --data-binary 送 UTF-8 JSON 文件；body 里含中文，别用命令行拼）
#     凭据：把 machine / 登录名 / 令牌 写进**仓库外**的 ~/.gitea-netrc，并收紧该文件权限（Windows 上设 ACL）
#     本文用 --netrc-file 传凭据，绝不把口令写进仓库、脚本或命令行历史
curl.exe -s --netrc-file "$HOME\.gitea-netrc" -H "Content-Type: application/json" `
  --data-binary "@build/_relpayload.json" -X POST `
  "http://zsyq.hxlab.tech:3000/api/v1/repos/yuhanxue/catalysis-methods-essentials/releases"
#    payload = {tag_name, target_commitish:"main", name, body, draft:false, prerelease:true}
#    实测 HTTP 201；返回体里取 id（v0.6.0-pre = 41）

# 4) 上传附件（PS 5.1 无 Invoke-RestMethod -Form，必须 curl.exe -F；字段名 attachment）
curl.exe -s --netrc-file "$HOME\.gitea-netrc" -F "attachment=@release/<pdf>" `
  "http://zsyq.hxlab.tech:3000/api/v1/repos/yuhanxue/catalysis-methods-essentials/releases/<id>/assets?name=<pdf>"
#    实测 HTTP 201

# 5) 回验：把附件从公开地址下载回来比哈希（不验就等于没发）
curl.exe -sL "http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/releases/download/vX.Y.Z-pre/<pdf>" -o build\_dl.pdf
(Get-FileHash build\_dl.pdf -Algorithm SHA256).Hash   # 必须 == 第 1 步
```

**易踩的坑**：① `git status` 不干净时发布的 PDF 可能来自未提交内容；② release notes 的 `SHA-256` 与 `对应提交` 两项是接手者的核验锚点，**必须实测填入**；③ 建 release 时若标签已存在，`target_commitish` 被忽略（标签指向谁就发谁）——所以先打标签再建 release；④ 附件建好后 `browser_download_url` 在部分 Gitea 版本里返回 `/attachments/<uuid>`，公开地址是 `/releases/download/<tag>/<name>`，两者都要能 200。

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
