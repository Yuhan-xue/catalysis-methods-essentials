# 三项内容级验收报告（2026-10-21）

本报告是 m00001 三项验收的收口台账：每项给出范围、方法、判决口径、当前进度、可复跑命令，
以及仍缺的部分。数字随批次变动，一律以命令输出为准，报告只记录写作时的快照。

## 0 快照

| 项 | 范围 | 进度 | 门禁 |
| --- | --- | --- | --- |
| ① 逐页内容级校对 | 340 页（v1.2.0 分页，见 §4） | **340/340**，待修正 0 | `OK pages=True` |
| ② 编号公式逐式对照原书页面图像 | 372 式 | **372/372** 终判 | `OK formulas=True` |
| ③ T2 表逐单元格核对 | 59 张 | **59/59**（余 0 张） | `OK tables=True` |

## 1 逐页内容级校对

**口径**：一页一判，三种状态——`已读`（逐字读完、无缺陷或缺陷按原书照录）、
`已读并修正`（查出并改掉）、`已读待修正`（查出但需另案处理）。每行必须写清读了什么
（图号／式号／数值清单）与证据（文本层 dump 或渲图路径），空话不计。

**方法**：先用 `tools/page_text.py <first> <last>` 取文本层逐页读（中文完整、上下标会被压平），
凡涉及版式、上下标、表格数字或图注标点，再 `tools/vbook.py <page> out.png` 渲页面图像对照。
整页图像逐张读不可行（单页 4—11 分钟且上下文过重），文本层优先是速度与稳定性的折中；
判据是「字符级差异能被文本层抓到」——错字、乱码、数值、术语都在此列。

**结果**：339 页全部入账（`sources/logs/page_p{1..4}.tsv`），状态分布
`已读 270 / 已读并修正 69 / 已读待修正 0`；`sources/logs/fixes_*.tsv` 共 90 条修正记录，
逐条记 page/file/line/old/new/reason。代表性问题（详见 `sources/content_review.md`）：
术语不统一（孔径分布→孔尺寸分布）、重字（式式/图图/表表，全库 68+2 处）、
知识性错（电子束损伤「小」→「大」、立方体四顶角→八顶角、乙烷→乙烯、15%—20%→25%—30%）、
对称性数错（二十面体 12/20/60→6/10/15）、交叉引用错（式(2-36)→式(2-21)）、
表题注与正文矛盾（表10-5 及过渡区）。

**复跑**：

```
python tools/page_text.py 61 75            # 取任意页段文本层
python tools/review_ledger.py all          # 合并 fragments → sources/content_review.md
python tools/verify_acceptance.py          # 页码门：339 页一次覆盖 + 证据字段
```

## 2 编号公式逐式复核

**口径**：372 个编号式逐式落到源书具体页与式号，判决五类——`已核对一致`（形式与符号都对上）、
`形式一致但符号不同`（源书用别的字母/记号）、`改编补充`（源书无此式，改编本为完整性补入）、
`原书自身问题`（源书印错，照录并在核对说明里写明）、`未找到`（源书中无对应式）。

**方法**：一律以源书**页面图像**为据（`tools/vpage.py up|down <pdf页> out.png --dpi 300`），
不用文本层——两册的文本层都是 OCR，指数、负号、下标会丢。页码换算：上册 书内 = PDF − 19；
下册按章加偏移（ch08 +508、ch09 +509、ch10 +511、ch11 +512、ch12 +514），每页以页眉书内页码复核。

**结果**：372/372 终判——`一致 197 / 符号不同 83 / 改编补充 74 / 原书自身问题 18`。
源书自身问题例：式(9-3b) 漏 $(\\delta E)^{1/2}$、式(9-16) 只印 $+$、式(10-63) 的 $K^0$ 印法矛盾、
式(10-127) 分母量纲不对、式(12-4) $T=1/\\omega_0$ 缺 $2\\pi$、式(11-81) 的 $0.725\\times10$ 缺指数 5。
台账：`sources/formula_crosscheck.md`（逐式表）、`sources/logs/formulas_f*.tsv`（碎片）。

**复跑**：

```
python tools/review_ledger.py formulas
python tools/verify_acceptance.py           # formulas 门：372 式终判 + src_pages 非空
```

## 3 T2 表逐单元格核对

**口径**：`sources/logs/tables_t{1,2}.tsv` 一行一表（label/verdict/src_pages/cells/mismatches/note），
逐格明细 `sources/logs/cells_<short>.tsv` 七列：`label / row / col / artifact / source / action / note`。
`action ∈ 一致 / 修正 / 差异 / 缺`；`差异` 专指「改编本自拟、源书无对应句」的格，不计 mismatch。
verdict 四类终态：`逐格一致`、`逐格修正`、`逐格差异·原书自身`、`改编补充自洽`。

**方法**：先 `page_text.py` 取改编本表页定位行栏，再 `vpage.py` 渲源书页面图像逐格读；
源书无对应表的（改编本自拟矩阵），判 `改编补充自洽` 且每一格写明「有源句／改编归纳」。

**结果**：59/59 完成，T2 余 0（分层计数以 `sources/table_status.md` 为准），逐格明细约
1100 行（各 `sources/logs/cells_*.tsv`），mismatch 1——表2-9 工业压力上限原印
`10^3—10^5 mbar`（上限只到 100 bar，与 200 bar 不符），已改为 `2×10^5 mbar`，表、
核对说明、正文三处同步。59 张表的 verdict 全部落在四类终态内（`改编补充自洽` 居多为
改编本自拟对照表或归纳栏；数值格有源句者为 `一致`），逐表 verdict 与源页见
`sources/table_status.md` 的 T1c 分层。
**剩余**：无（原余 25 张已全部并入 T1c）。表题注中原写「尚未逐页核对/待回查」的说明
已逐条改写为本轮补核结论与证据等级声明。

**复跑**：

```
python tools/review_ledger.py tables        # 合并 tables_*/cells_* → table_cells.md/.tsv
python tools/table_status.py                # 重算 T1/T1c/T2/T3/T4 分层
python tools/verify_acceptance.py           # tables 门：59 张终判 + T1c=59、T2=0
```

## 4 门禁、页码与交付差异

`tools/verify_acceptance.py` 是总闸门：页码一次覆盖且带证据、372 式终判、59 表终判、
T1c=59/T2=0、每条 fix 记录在 tex 中确有落地、`review_ledger.py all --strict` 复跑无 diff
（幂等性）。当前输出：pages/formulas/tables 三门全绿。

**340 页这件事**：交付件 `release/catalysis-methods-essentials-v1.0.0.pdf` 340 页，
v1.1.x 重建 `build/main.pdf` 为 339 页；逐页指纹比对（`build/_cmp340.txt`、`_cmp340b.txt`）表明
v1.0.0 的 p339+p340 在 v1.1.x 合并为一页（相似度 0.985），**不是丢页**。
v1.2.0 补入 5 处表引用后重建回 **340 页**（第六章末页续页 p.118 为新页），
逐页台账已按 `tools/page_align.py` 的对齐结果整体重编号。

**构建门禁**：`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1`
（Windows PowerShell 5.1 读不了 UTF-8 无 BOM 的中文脚本，必须用 PowerShell 7）。
当前：340 页、错误 0、overfull>5pt 0、缺字 0、未定义引用 0、重标号 0、PASS。

**发布验收（`-Release`）**：同一命令加 `-Release`（release 模式把 overfull/未定义引用/
重复标签/版面重叠确认缺陷一律判红），v1.2.0 在合并提交后运行：
`mode release`、340 页、错误 0、overfull>5pt 0、缺字 0、未定义引用 0、重标号 0、PASS。
即现稿已具备发布资格（交付件见 §5 末条）。

**其余检查器**（`python tools/qa_suite.py`，11 项全部 exit=0，汇总写 `build/qa_suite.txt`）：
编号连续（`check_numbers`：全由 LaTeX 计数器生成，无硬编码/重置）、目录 61 条 0 处不符
（`check_toc`）、书签 145 条 0 处不符（3 条回退匹配，`check_bookmarks`）、无重复页
（`check_duppages`：340 页均有正文，重复组 0）、页脚 bad=0（仅封面 1 页无页码，`check_folio`）、
包含检查 OK（`check_includes`）、版面重叠 PASS blocking=0（`overlap_check`）、
85 张表 `\src` 来源标注 PASS 85（`check_src`）、内容扫描仅 INFO（`content_scan`）。
其中 `check_terms` 报 8 组 21 对「竞争术语」，属术语统一清单而非缺陷，明细在 `tools/term_audit.txt`。

## 5 已完成事项与后续建议

三项验收均已达成（①340/340、②372/372、③59/59），门禁全绿。后续建议：

1. **表证据等级残余（已清零）**：曾以文字层为唯一证据的 46 格清单见 **`sources/textlayer_backfill.md`**
   （`tab:modes` 18、`tab:raman-bands-c` 18、`tab:ch07c-criteria` 8、`tab:ch07c-probe` 2）；
   现按第二条通道分档为 **30 数值双证 + 16 图像复核 + 0 仍需人工**。
   本轮用 **`tools/ocr_backfill.py`** 做了独立于内嵌文字层的第二条机器证据：把所引源页以
   300 dpi 渲成图像、用 RapidOCR 重新识别，再逐格找回数值 token。结果见 **`sources/ocr_backfill.md`**：
   30 个数值格 **全部命中**（两条独立 OCR 流程互证），并由此发现并订正一处**内容缺陷**——
   表 6-10 与正文把过氧物种谱带印成 520—550 cm⁻¹，源页图像实为 820～850 cm⁻¹
   （源文字层把 8 误识为 5；BaO2 标样 842/829/821 同带，自洽），已改 4 处并记入
   `sources/logs/fixes_t1.tsv`。剩 16 个定性格后来也逐页读图核对完毕，见
   **`sources/evidence_upgrade.md`**：15 格一致或属译名选择，1 格旧备注失实已订正
   （`tab:modes` 漫反射行原写「Kubelka—Munk 在源文字层未检索到」，而 p.427 页面图像明确印有该函数）。
   复跑 `python tools/ocr_backfill.py`（依赖 `rapidocr_onnxruntime`）。
   后续把同一方法扩成**全书普查**：**`tools/ocr_digit_audit.py`** 扫 59 个 cells 文件里的
   144 个含数值格（84 格可定位源页：上册 49、下册 35），结果 **65 全中 / 5 部分 / 14 未命中 /
   60 无源页**，19 个问题格逐条分诊（按格计：误报 4、改编补充 12、单位换算 1、舍入 2、OCR 漏识 1），
   见 **`sources/ocr_digit_audit.md`**。由此又订正两处：表 6-7 的 MoO3 谱带统一为 910/2720，
   表 2-10 的束斑球差校正器由 0.24 nm 改为 **0.20 nm**（源页印「2 Å→1.3 Å」，文字层把 2 Å
   识成「ZA」）。修正版已发 **v1.1.3**（release id=513，tag @ `78793c4`）。
2. ~~T1c 日期硬编码~~（已处理）：`tools/table_status.py` 新增 `head_date()`，日期取
   `git log -1 --format=%cs`，与 `content_review.py --date` 同口径，复跑字节一致。
3. ~~交付件（340 页）与现稿（339 页）的差异~~（已处理）：已发 **v1.1.0**（release id=490，
   tag @ `6049d99`，339 页 / 4253928 B / SHA-256 `AADE64CF…0E3C67`），双路下载 200，
   且 `tools/cmp_release_pdf.py` 判定线上件与本地构建件 **IDENTICAL CONTENT**。

## 六、制品与台账的一致性抽查（2026-10-21）

验收不能只在 `sources/` 里自洽，还要看**交付出去的那本书自己怎么说**。本节抽查做于 v1.1.3
（339 页、4254324 B、SHA-256 `8D4A8B8D…32F19`），2026-10-21 又在 v1.2.0 上复核（见本节末行）：

| 抽查点 | 制品上的原文 | 台账 | 判定 |
|---|---|---|---|
| 表账口径 | 「85 张表中 73 张已逐格核对（含 59 张原『就地说明』表的逐单元格比对）、0 张只在分片留说明、12 张为改编补充」 | `table_status.md`：T1 14 + T1c 59 = 73 逐格、T2 0、T3 12 | 一致 |
| 页数 | v1.1.3 页码至 339；v1.2.0 至 340 | 构建 339 → 340 页 | 一致 |
| 与现稿的同一性 | 末三页文字层与 `build/main.pdf` 对应页逐字相同 | — | 一致 |

一处**看似矛盾其实正确**、因此保留不改的地方：附录「逐表核对记录」里仍写
「未逐页核对：书内 p.587—588、p.594、p.596、p.599、p.601、p.605」（表 9-1 的段落）。
这是**证据深度**的说明——表 9-1 的 21 个格各自的数值都引到了可定位的源页，但没有对这六页做
整页通读——而「逐格核对」判的是**每一格的数据有无源页依据**，两者不是同一件事。把它改成
「已全部核对」反而会夸大证据，所以保留原样，并在此记明口径。

## 七、结论

三项验收的证据链从「源书页面」经「cells／pages／formulas 台账」到「sources 报告」，再到
「交付 PDF 自身的表述」，四层同口径、可复跑、可抽查。任何一处被改动，都会在
`python tools/verify_acceptance.py` 或本章的抽查点之一暴露出来。

一条命令复跑全部证据：

```
python tools/acceptance_all.py           # 台账重算 + 总闸门 + 11 项版面/引用检查
python tools/acceptance_all.py --build   # 追加重建（tools/build.ps1 -Release）
```

2026-10-21 实测输出：`ledgers exit=0 / gate exit=0 / qa_suite exit=0 → RESULT PASS`
（明细见 `build/acceptance_all.txt`）。


## 八、插图逐图核对（2026-11-03）

三项验收原本只管「字、式、表」，插图没有台账。本轮补上第四项：**57 张图逐图对照原书**。

本书插图全部是 TikZ 重画（不是扫描件），所以核对的对象不是像素，而是「重画有没有把原书那张图
说成另一回事」：坐标轴与变量、曲线形状与趋势、标注与单位、图中的数字。每张图的证据是两张渲染图——
原书页面（`python tools/vpage.py up|down <pdf页> out.png`）与成品页面（`python tools/vbook.py <页> out.png`）——
有的还叠加 OCR（下册无文字层，用 `rapidocr_onnxruntime` 重新识别）。

台账：`sources/figure_review.md`（`python tools/figure_ledger.py` 生成），逐图明细在
`sources/logs/figs_ch01.tsv` … `figs_ch12.tsv`（7 列：图号／成品页／源锚点／核对要点／判定／备注）。
四种终判与表台账同构：

| 判定 | 张数 | 含义 |
| --- | --- | --- |
| 逐图一致 | 11 | 原书有对应图，重画在结构、变量、数值上一致 |
| 逐图修正 | 14 | 发现并改正了图或题注的错误（漏画、方向反、锚点错、标注被裁） |
| 逐图差异·原书自身 | 0 | — |
| 改编补充自洽 | 32 | 原书无对应图（或只有文字），本图自绘且题注已声明，不与正文矛盾 |

代表性修正（每条都记在 `sources/logs/fixes_fig.tsv`）：

- **图 12-1／12-2 的源锚点错位**：能级-隧穿结图原注「据原书图 12-1」，而原书图 12-1 是 STM 整机结构，
  能级图实为图 12-2(e)（书内 p.889—890 / PDF 375—376）；题注已改，并经两名核对者独立读图确认。
- **图 4-1 K 吸收边方向**：重画时吸收边随能量上升的走向与原书相反，已重画三条曲线。
- **图 4-3「峰宽」标注被 x 轴裁掉**：改 `anchor=south west`、上移 0.015。
- **图 11-1 题注冒称原书图 11-2**：原书图 11-2 是电流-过电位曲线，不是界面示意图，改为「据 §11.1.5 正文绘制」。
- **图 8-x／10-x 若干**：题注「改绘」改为「按原理绘制」，并把原书实际页码写准。

复跑：`python tools/figure_ledger.py --strict`（要求 57/57 终判，否则非零退出）；
总闸门 `python tools/verify_acceptance.py` 已把该项纳入。

## 九、版面与配图质感（2026-11-03）

原稿通篇黑白：`style/preamble.tex` 只有两个灰阶。本轮建立最小配色系统，只改颜色、不改任何长度，
因此**分页不变**（重建后仍 340 页，`python tools/page_align.py build/_base339.pdf build/main.pdf`
仍报 `monotone=True`）：

- **主色** `accent` = `#1F497D`（深蓝）：节号、小节号、图题标签、语义块标目；
- **暖色** `accentwarm` = `#A04A21`：只给「易错点」类块，起警示作用；
- **墨色** `inksoft` = `#3A3F45`：方法要点、关键条件、观察等中性块；
- **浅色** `accentsoft`：交叉核对块，弱化处理。

正文实测出现 `#1F497D` 328 处、`#3A3F45` 103 处、`#A04A21` 44 处、`#ADADAD` 34 处，
说明着色确实落到 PDF 而不是只写在导言区。配色定义集中在 `style/preamble.tex` 与
`style/macros.tex` 的 `runinblk`（两参：标目文字、颜色），改一处全书生效。
