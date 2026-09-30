# 现代催化研究方法精要：原理、读图与方法选择

据《现代催化研究方法新编》（上册、下册，科学出版社）浓缩编写的中文研究方法手册 ——
**LaTeX / XeLaTeX 工程**。

> **接手本项目请先读 [HANDOFF.md](HANDOFF.md)**：当前状态、能跑的命令、环境陷阱、
> 未完成事项与全部已知坑的浓缩版。写作细节见 [STYLE_GUIDE.md](STYLE_GUIDE.md) 与
> [WRITER_BRIEF.md](WRITER_BRIEF.md)。

## 一、这是什么

一套可编译的中文科技专著工程，产出可检索、含中文书签的 PDF，以及可复现的源码、图源、
来源覆盖表与质检记录。全书按「一个方法一个单元」组织，每个方法都要能回答五件事：

1. 测什么、能推断什么？2. 原理、公式与**成立条件**？3. 拿到数据/谱图/图像**怎么读**？
4. 哪些**假设与干扰**会让结论失效？5. 用哪个**互补方法**验证？

## 二、当前状态（未完成）

- 12 章全部到位；正文分片 **37 / 37**；后置索引（缩写/符号/术语/勘误）齐备。
- 最新发布 **v0.6.4-pre**：**314 页 / 144 条书签**，release 门禁全 0
  （errors / overfull>5pt / missing glyphs / undefined refs / dup labels / dup includes / overlap）。
- 逐片台账见 `sources/assignments.md`（`done` 只等于「文件存在」）；内容核验状态见
  `reviews/2026-09-30-round4/CLOSURE.md` 与 `HANDOFF.md` §1/§5。
- **仍未完成**：85 张表逐表**像素级**核图、公式逐式核对原页面图像、旧凭据轮换（后两项需人工/账户）。
- ⚠️ **字节哈希每次构建都会变**（PDF 内含 `/CreationDate` 与 `/ID`）。判断内容有没有变，
  请比**文本层逐页**、页数与书签落页（`tools/pdf_probe.py`），不要只比字节哈希。

## 三、快速开始

依赖：TeX Live 2026（XeLaTeX + `latexmk`）、Python 3（`pymupdf` / `Pillow` / `numpy` / `scipy`）、Windows PowerShell。

```powershell
# 发布验收（发布/交付前必须跑；-Release 会把「静态检查没跑成」判为失败）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release

# 单分片（作者提交前必跑）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11-d

# 关键探针（只读）
python tools/pdf_probe.py --pdf build/main.pdf          # 书签落页 / 后置页眉 / 必要书签
python tools/fig_probe_eis.py --pdf build/main.pdf      # 图 11-5 矢量层
python tools/fig_probe_eis.py --selftest                # 探针自检
python tools/check_src.py                               # 85 张表来源标注
python tools/check_table_content.py                     # 85 张表来源内容（OCR 文本层）
python tools/build_coverage_map.py                      # 原书节覆盖落点
python tools/recompute_ch03b_dtg.py                     # TG/DTG 坐标复算
python tools/gen_tpd_table.py --check                   # TPD 坐标逐点复验
```

## 四、目录结构

```
chapters/            正文分片（parts/）与装配层（chNN.tex）
style/               preamble.tex（版式/字体）、macros.tex（环境与宏）
sources/             来源建档：parts/（分片源文本）、coverage.csv、页码映射、覆盖/核对台账
tools/               构建、检查、探针脚本（.ps1 构建入口；.py 各司其职）
reviews/             历轮评审（TODO / CLOSURE / findings / 复核脚本）
main.tex             主文件    HANDOFF.md 交接    STYLE_GUIDE.md / WRITER_BRIEF.md 写作契约
```

`sources/pages/`（原书页面位图）、`sources/text/`（原书全文转储）、`build/`、`release/`
均由 `.gitignore` 排除。

## 五、版式与写作契约（摘要）

- **单栏**、A4、10 pt、`twoside`，版心 **165 mm**；`\onecolwidth`≈132 mm、`\twocolwidth`≈158 mm。
- **禁用** `figure*` / `table*`（单栏下非法）；长表用 `longtable` + 定宽 `p{}`，
  放单栏整页（`\widepageson/off`，表宽 `\textwidth`）。
- 一个分片 = 2 个 `\subsection` + 若干 `\subsubsection`，六环节各至少一处
  （`probout/principle/measure/dataflow/pitfall/crosscheck`）；至少一个读图实例，`obs` 与
  `infer` 严格分开。完整契约见 STYLE_GUIDE / WRITER_BRIEF。

## 六、来源与页码映射

- 来源两册：`S1` 上册、`S2` 下册；引用写法 `\src{S1 §x.y，书内 p.NN / PDF p.MM}`。
- 页码一律以 `sources/parts/*.txt` 的页标记 `[[UP/DOWN PDF p.n | 书内 p.m]]` 为准
  （读出的页码可用页码映射验算，但**不要**反过来用固定偏移猜页码）。
- 原书 PDF 与页面位图**不在仓库**：只保留按分片切好的源文本 `sources/parts/`（写作与核对必需）。

## 七、工具链

- 构建：`tools/build.ps1`（draft/release）、`tools/check_chapter.ps1`（单分片）。
- 门禁与检查：`check_includes.py`（重复 `\input`）、`check_src.py`（表来源）、
  `check_terms.py`（术语）、`overlap_check.py`（版面重叠，`--gate` 接入构建）。
- 内容核对（不依赖像素）：`check_table_content.py`、`build_coverage_map.py`、
  `recompute_ch03b_dtg.py`、`gen_tpd_table.py --check`。
- 阅读/导航探针：`pdf_probe.py`、`fig_probe_eis.py`。
- 其余一次性分析脚本在 `tools/` 下，按需查阅；生成的中间产物（`overlap_*.txt` 等）已不入库。

## 八、诚实纪律（本项目最重要的一条）

- 维护会话**没有视觉能力**：公式由「OCR 上下文 + 学科标准形式」重建，未核对页面图像的一律写
  `\tocheck{未对照原页面图像：…}`，**不写「已核对」**。
- 静默失效是主要风险：缺字、`\underbrace` 黑条、`\ce{Mo=O}` 双连字符、重复 `\input`
  都不报错。发布前必须让 `-Release` 门禁全绿。
- 观测可信、归因易错；校验器本身也会错。判据以命令与文件为准，不以措辞为准。

## 九、发布

流程（构建 → 打 tag → 建 release → 上传附件 → 回验哈希）见 `HANDOFF.md` §8。
releases 见 Gitea：`/yuhanxue/catalysis-methods-essentials/releases`。

## 十、版权与仓库可见性

- 本仓库据原书**浓缩编写**，是对原著的二次创作；原书文字与图像著作权属原作者与出版社。
- 仓库**不含**原书 PDF，也**不含**原书页面位图（`sources/pages/`、`sources/text/` 及历轮评审的
  页面截图均已排除）。
- `sources/parts/*.txt` 是按分片切分的**源文本摘录**，写作流程必需，故保留；**请保持本仓库私有**。
- 用于教学、个人研究与内部参考；对外分发前请自行确认授权范围。
