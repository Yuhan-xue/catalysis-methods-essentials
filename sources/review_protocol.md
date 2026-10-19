# 内容级验收作业规程（2026-10-19，适用于三项验收的所有执行者）

本文件是《现代催化研究方法精要》改编本三项内容级验收的统一规程。
执行者（含 Lead 与所有协作者）**先读本文件，再读自己的分组清单**。规程之外的自由发挥一律不要。

## 0. 一句话目标

把「文字层看着没问题」推进到「**亲眼看过版面图像、逐项对过源书页面图像**」，
每条结论都落在 `sources/` 台账里，并且任何人可以按台账里的命令与图像路径重跑一遍。

## 1. 铁律（违反即返工）

1. **只信页面图像。** OCR 文本只用来定位，不能当作「书里印的是什么」的证据。结论必须来自
   `tools/vbook.py` / `tools/vpage.py` 渲染出来的 PNG 经 `read_image` 看到的像素。
2. **只写自己的日志文件。** 协作者只允许写 `sources/logs/<你的组>.tsv`、
   `sources/logs/cells_<表名>.tsv`、`sources/logs/fixes_<你的组>.tsv`。
   **不得改** `chapters/`、`sources/` 下任何既有台账、`tools/`、`build/main.pdf`。
3. **不得自己修书、不得跑 `latexmk`/`build.ps1`、不得 `git`。** 发现缺陷写成修正建议行，
   Lead 统一改源码、重建、复核、提交。
4. **不恭维、不总结文风。** 只报「错字 / 乱码 / 数值 / 术语 / 编号 / 指代 / 单位量纲」这类
   内容级问题。文风偏好、排版审美不属于本次验收。
5. **看不清就说看不清。** 165 dpi 疑似的，用 300 dpi 裁切重看；仍看不清写「未看清（原因）」，
   不要猜。误判比漏判更贵——误判会让 Lead 改错书。
6. **不要开子代理**，不要并行起新会话；你的活自己干完。
7. **控制台是 GBK。** 不要 `python -c "print('中文')"`，不要在 pwsh 里输出中文；
   需要看文本就写进 UTF-8 文件再用读文件工具看。渲染命令本身只输出 ASCII 路径，安全。

## 2. 环境与命令

工作目录恒为仓库根 `C:\Users\53150\Documents\git\chemical`。

渲染**成品书**某一页（1 基页码，即 `build/main.pdf` 的页号）：

```
python tools/vbook.py 57 build/_p57_p1.png --dpi 165
python tools/vbook.py 57 build/_p57_p1.png --dpi 300 --bottom 0.55          # 只上半页（放大看）
```

渲染**源书**某页（`up`＝上册，`down`＝下册；页码是**源书 PDF 页号**，
不是书内页码；工作清单里给的是 `hint_pdf`）：

```
python tools/vpage.py up 64 build/_src_up64_p1.png --dpi 300
python tools/vpage.py up 64 build/_src_up64_p1.png --dpi 300 --top 0.05 --bottom 0.45
```

`--top/--bottom/--left/--right` 是整页宽高的分数（0..1），用于裁切放大。
成品书页码 ↔ 源书书内页：上册 `书内页 = PDF页 − 19`；下册 `书内页 = PDF页 + 507`
（以源书页眉/页脚实际印刷页码为准，务必扫一眼页眉核对，别只信算式）。

看文本（只用于定位，不作证据）：

```
python tools/page_text.py 57 build/_p57.txt      # 成品书某页文字层
```

源书 OCR 在 `sources/parts/<slice>.txt`，含 `[[UP PDF p.62 | 书内 p.43]]` 页标记，
用 grep/read 定位；`sources/page_map_up.csv`、`page_map_down.csv` 是页码映射表。

看图用 `read_image`。**第一次读图先确认能看到字**；若返回空白/糊成一团，立即报 Lead，
不要硬猜。

## 3. 三类任务的判定词表（只能从这里选）

### 3.1 逐页校对（pages）

状态列 `status` 只能是：`已读`（读过整页、无缺陷）、`已读并修正`（读到缺陷且 Lead 已改，
Lead 回填）、`已读待修正`（读到缺陷、建议已写进 fixes、等 Lead 改）。
备注必须包含：① 本页内容一句话（哪一节/哪张图表）；② 核了什么（数字复算、术语、表行数、
公式号、图注、目录页码……）；③ 如果发现缺陷：`文件:行` + 现文 → 改文 + 依据的源书页图像。
没有缺陷也要写清「未见错字、乱码、数值矛盾；核对点：……」，不允许只写「OK」。

### 3.2 逐式复核（formulas）

`verdict` 只能取：
- `已核对一致`：符号、上下标、正负号、常数、编号与源书印刷式一致（逐符号对过）。
- `已核对并修正`：原式与源书不一致，已提出修正（写进 formula fixes）。
- `形式一致但符号不同`：结构相同、符号命名/排列不同（如源书用 $k$ 本版用 $k_a$），
  且本版自带符号表/上下文自洽。备注要写清「本版 X ↔ 源书 Y」。
- `原书自身问题`：源书印刷式自相矛盾/量纲不对/编号错，本版已按上下文处理。写明源书页证据。
- `改编补充`：源书该处没有编号式，是改编本补的（常见于教学化改写）。写明「源书 p.x–y 无此式」。
- `未找到`：在源书分片范围内没找到对应式。备注写清搜过哪些源书页、用什么关键词找的。
- `未覆盖`：还没做（Lead 用，协作者不要填）。
`src_pages` 写 `up p.64` 或 `down p.258-260`；备注 1–3 句，必须并排放两侧式子
（例：`版面 r_p=r_k+t；源书书内 p.45 同式`）。

### 3.3 逐表单元格核对（tables）

`verdict` 只能取：
- `逐格一致`：源书有这张表，逐单元格比对一致。
- `逐格修正`：源书有这张表，至少一格不一致，已提修正建议。
- `逐格差异·原书自身`：源书表格内部自相矛盾/与正文矛盾，本版照录并加说明。
- `改编补充自洽`：源书无此表（改编表），逐格核过内部自洽（行列合计、单位、与正文数字一致）。
- `未找到源表`：找不到对应源表且题注未声明改编。备注写搜过的源书页。
- `未覆盖`：还没做（Lead 用）。
`cells_checked` 填实际比对的格数（行×列，合并单元格按内容块计）；`mismatches` 填不一致格数。
不一致格必须逐格写进 `sources/logs/cells_<表名>.tsv`（一行一格，含两侧原文与处置）。

## 4. 逐页校对的具体做法（pages 组）

对分到的每一页：

1. 读 `sources/parts/<slice>.txt` 里本页对应的段落（`[[...]]` 标记之间），知道这页该有什么，
   并记下可疑点候选（数字、术语、图表号）。
2. `python tools/vbook.py <page> build/_p<page>_<组>.png --dpi 165` → `read_image` 整页读。
   内容密集或字小的页用 `--dpi 300` 整页或上下半页各一张。
3. 逐项核：
   - **错字/乱码**：错别字、重复字、漏字、`�`/方框/怪符号、半角逗号句号混入中文、
     公式里不该有的中文标点。
   - **数值**：正文数字与表格/图注/公式自洽；能复算的复算（比表面积、孔径、百分数、
     单位换算、算例结果）。与源书数字不一致的，渲染源书页图像确认是哪边错。
   - **术语**：与 `sources/terminology_decisions.md` 的裁决一致；与源书术语不一致时，
     先判「本版有意统一」还是「抄错」，写清依据。
   - **编号/指代**：图号、表号、式号对不对得上实际浮动体；「上表/下图/见式」指向是否成立
     （浮动体可能落到下一页）；目录页码是否对得上正文。
   - **表格**：本页若有表，数行数列数、核表头与行标签、核每行关键数字；表是否被页面截断。
   - **公式**：本页若有编号式，核式号连续、符号与上下文一致；与源书对照属公式组深活，
     页组只需抽查编号与明显错号。
4. 写 `sources/logs/page_<组>.tsv`（制表符分隔、UTF-8、无表头行）：
   `page<TAB>status<TAB>note`
   每页一行，页码升序。备注写「图：build/_p57_p1.png；源：build/_src_up64_p1.png」。
5. 有缺陷的，另写 `sources/logs/fixes_<组>.tsv`（制表符、无表头）：
   `page<TAB>file<TAB>line<TAB>old<TAB>new<TAB>reason`
   - `file` 用仓库相对路径（如 `chapters/parts/ch01-b.tex`）；
   - `line` 用当前文件的 1 基行号，必须先用 grep 精确定位，不确定就填 0 并在 reason 里写锚句；
   - `old` 必须是从文件里**逐字复制**的原文片段（可含少量上下文，保证唯一）；
   - `new` 是替换后文本；
   - `reason` 一句话 + 源书页图像路径。改字要尽量等长，避免整书页码位移（Lead 会复核）。
6. 全部页完成后，最终消息给 Lead 一行统计 + 缺陷清单（页码、问题、是否已写 fixes）。

## 5. 逐式复核的具体做法（formulas 组）

按 `build/work_groups/formulas_<组>.tsv` 逐式（列：label num page slice line vol src_book
src_pdf hint_book hint_pdf）。

1. **先看版面**：`python tools/vbook.py <page> build/_eq_<label>.png --dpi 300 --top .1 --bottom .95`
   或按式所在行裁切；`read_image` 读出成品里印的式子与编号。
2. **再找源书页**：优先用 `hint_pdf`；没给就用 `src_pdf` 范围（如 `20-103`，是 PDF 页范围）
   按主题与式号定位。一次渲染一页可覆盖同一页上的多式，**按源书页批量做**效率最高。
   源书式号形如 (1-42)，与成品式号 (1-1) 不必相同——按内容对，别死抠号。
3. **逐符号对**：变量名、下标、上标、正负号、系数、常数、分式结构、求和/积分上下限、
   单位、式号归属。看清后再判词。
4. 写 `sources/logs/formulas_<组>.tsv`（制表符、无表头）：
   `label<TAB>verdict<TAB>src_pages<TAB>note`
   一式一行，按 label 排序。`src_pages` 精确到源书 PDF 页，备注并排放两侧式子。
5. 需修正的写 `sources/logs/formula_fixes_<组>.tsv`：
   `label<TAB>file<TAB>line<TAB>old<TAB>new<TAB>reason<TAB>src_pages`（字段格式同上节）。
6. 若一个式实在找不到源书对应式：`未找到`，备注列出搜过的 PDF 页与关键词；不要为了凑
   「已核对」硬套。

## 6. 逐表核对的具体做法（tables 组）

按 `build/work_groups/tables_<组>.tsv`（列：id num page slice line src_book hint_book hint_pdf）。

1. 读分片里该表的源码：`\begin{tabularx}` 列定义、行数、每格文本；同时 `vbook.py` 渲染
   成品该页（表跨页就渲两页），看清最终版面。
2. 源书有该表（`hint_pdf`/`src_book` 给了范围）：渲染对应源书页（跨页分成两张，必要时
   `--top/--bottom` 裁切），**逐单元格**对照：行标签、列头、每个数字、单位、表注、脚注。
   - 合并单元格按内容块计；
   - 数字精度、上标（10³、m²·g⁻¹）、负号、括号、百分号都要对；
   - 表格里的定义式/符号也要对。
3. 源书无该表（改编表）：核内部自洽——行列合计、百分比和为 100、单位一致、与正文同一
   数字一致、表注与表体一致。判 `改编补充自洽`。
4. 写 `sources/logs/tables_<组>.tsv`（制表符、无表头）：
   `label<TAB>verdict<TAB>src_pages<TAB>cells_checked<TAB>mismatches<TAB>note`
5. 不一致格写 `sources/logs/cells_<label 去掉 tab: 前缀>.tsv`（制表符、无表头）：
   `label<TAB>row<TAB>col<TAB>artifact<TAB>source<TAB>action<TAB>note`
   `action` ∈ `照源书改` / `保留本版加说明` / `待Lead裁决`。
6. 需修正的写 `sources/logs/table_fixes_<组>.tsv`，字段同 formula fixes。

## 7. 证据与可复跑

- 台账里每条备注都要能让人**按图路径重看**：成品图与源书图都写相对路径（`build/_...png`）。
- 不要删图像；图像在 `build/`（已 gitignore），台账里保留路径即可复现。
- 最终验收命令由 Lead 跑：`python tools/review_ledger.py all --strict`。
  它要求 339 页每页有「已读」行、372 个编号式每式有终判、85 张表每表有终判；缺一项就非零退出。

## 8. 交付消息格式（完成时发给 Lead）

```
组别：pages_p1
覆盖：5–88（84 页），已读 84，缺陷 3，修正建议 3
台账：sources/logs/page_p1.tsv（84 行）、fixes_p1.tsv（3 行）
缺陷：p21 …；p44 …；p73 …
未解决：无 / …
```

中途只在**被卡住**（图像通道坏、找不到源书页、需要裁决）时发消息，不要每页汇报。
