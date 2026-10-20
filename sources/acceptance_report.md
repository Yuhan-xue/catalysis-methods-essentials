# 三项内容级验收报告（2026-10-21）

本报告是 m00001 三项验收的收口台账：每项给出范围、方法、判决口径、当前进度、可复跑命令，
以及仍缺的部分。数字随批次变动，一律以命令输出为准，报告只记录写作时的快照。

## 0 快照

| 项 | 范围 | 进度 | 门禁 |
| --- | --- | --- | --- |
| ① 逐页内容级校对 | 339 页（交付 v1.0.0 为 340 页，见 §4） | **339/339**，待修正 0 | `OK pages=True` |
| ② 编号公式逐式对照原书页面图像 | 372 式 | **372/372** 终判 | `OK formulas=True` |
| ③ T2 表逐单元格核对 | 59 张 | **30/59**（余 29 张） | `tables=False`（未完成即应为红） |

## 1 逐页内容级校对

**口径**：一页一判，三种状态——`已读`（逐字读完、无缺陷或缺陷按原书照录）、
`已读并修正`（查出并改掉）、`已读待修正`（查出但需另案处理）。每行必须写清读了什么
（图号／式号／数值清单）与证据（文本层 dump 或渲图路径），空话不计。

**方法**：先用 `tools/page_text.py <first> <last>` 取文本层逐页读（中文完整、上下标会被压平），
凡涉及版式、上下标、表格数字或图注标点，再 `tools/vbook.py <page> out.png` 渲页面图像对照。
整页图像逐张读不可行（单页 4—11 分钟且上下文过重），文本层优先是速度与稳定性的折中；
判据是「字符级差异能被文本层抓到」——错字、乱码、数值、术语都在此列。

**结果**：339 页全部入账（`sources/logs/page_p{1..4}.tsv`），状态分布
`已读 287 / 已读并修正 52 / 已读待修正 0`；`sources/logs/fixes_*.tsv` 共 87 条修正记录，
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

**结果**：30/59 完成（T2 余 29；分层计数以 `sources/table_status.md` 为准），fragments 合计
577 格逐格记录，mismatch 1——表2-9 工业压力上限原印 `10^3—10^5 mbar`（上限只到 100 bar，
与 200 bar 不符），已改为 `2×10^5 mbar`，表、核对说明、正文三处同步。已完成的表见
`sources/table_status.md` 的 T1c 分层（逐表 verdict 与页码），逐格明细见各
`sources/logs/cells_*.tsv`。
**剩余 29 张**：`tab:ch03b-conditions`、`tab:ch04b-Qtable`、`tab:ch04b-extinction`、
`tab:ch04b-quantmethods`、`tab:ch04b-FOM`、`tab:ch04c-boundary`、`tab:ch04c-fitmethods`、
`tab:ch04c-rfactor`、`tab:ch05-tpd`、`tab:ch05-redhead`、`tab:ch05b-tpr-shift`、
`tab:raman-ir`、`tab:fluor-suppress`、`tab:raman-parts`、`tab:insitu-window`、
`tab:raman-routes`、`tab:uv-apps`、`tab:raman-bands-c`、`tab:modes`、`tab:ch07c-probe`、
`tab:ch07c-criteria`、`tab:power-vs-hyp`、`tab:ch10-modelfam`、`tab:ch10-diffmech`、
`tab:ch10-criteria`、`tab:ch10-transient`、`tab:afm-modes`、`tab:nano-three`、`tab:nano-methods`。

**复跑**：

```
python tools/review_ledger.py tables        # 合并 tables_*/cells_* → table_cells.md/.tsv
python tools/table_status.py                # 重算 T1/T1c/T2/T3/T4 分层
python tools/verify_acceptance.py           # tables 门：59 张终判 + T1c=59、T2=0
```

## 4 门禁、页码与交付差异

`tools/verify_acceptance.py` 是总闸门：页码一次覆盖且带证据、372 式终判、59 表终判、
T1c=59/T2=0、每条 fix 记录在 tex 中确有落地、`review_ledger.py all --strict` 复跑无 diff
（幂等性）。当前输出：pages/formulas 全绿，tables 红（未完成）。

**340 vs 339**：交付件 `release/catalysis-methods-essentials-v1.0.0.pdf` 340 页，
现重建 `build/main.pdf` 339 页。两版逐页指纹比对（`build/_cmp340.txt`、`_cmp340b.txt`）表明
v1.0.0 的 p339+p340 在现稿合并为一页（相似度 0.985），**不是丢页**；m00001 所说的「340 页」
对应交付件，现稿 339 页即其全部内容。

**构建门禁**：`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1`
（Windows PowerShell 5.1 读不了 UTF-8 无 BOM 的中文脚本，必须用 PowerShell 7）。
当前：339 页、错误 0、overfull>5pt 0、缺字 0、未定义引用 0、重标号 0、PASS。

## 5 未完成与建议

1. **表 ③ 余 29 张**：每张需渲源页图像逐格读，单张 15—40 分钟量级。建议按章分批推进
   （ch04 7 张 → ch06 7 张 → ch10 5 张 → ch05 3 张 → ch07 3 张 → ch12 3 张 → ch03 1 张），
   每批跑 `review_ledger.py tables` + `git commit`。
2. **表题注的「尚未逐页核对」字样**要随逐格完成逐条删除，否则读者看到的是自认未核的说明。
3. `sources/table_status.md` 的 T1c 标题日期仍是「2026-10-19」，建议由 `table_status.py`
   用 `git log -1 --format=%cs` 生成。
