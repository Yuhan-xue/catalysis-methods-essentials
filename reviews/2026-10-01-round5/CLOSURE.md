# 第五轮评审 · 逐 ID 关闭记录（CLOSURE）

> 由执行方在修完后写入，逐条对应 [TODO.md](TODO.md) 的 6 项（1 P1 + 4 P2 + 1 P3）与
> [04-previous-round.md](04-previous-round.md) 的继承队列。口径是**候选完成 + 证据链 +
> 残余风险**，不是最终裁决；裁决权在评审方。原始问题、截图与复算脚本（`recheck_review.py`、
> `evidence/`）一律保留，未改动。

## 0 交付元信息

| 项 | 值 |
|---|---|
| 代码起点 | `b15a479`（第五轮评审目录提交；本轮修复未改评审资料） |
| 构建模式 | release（`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release`） |
| 制品 | `build/main.pdf`：**314 页 / 144 条书签 / 4 028 589 字节**，SHA-256 `d0736a5c56e21ea026ace451323aebab5dcb2decf77b9d9a02c0f64519aa6e9d` |
| 入库 | `build/` 被 `.gitignore` 忽略；发布附件另传（见 §3） |
| 页数变化 | 314 → **314**（仅图 5-1 图例改为分栏纵排、§8.5 前加落页判断，净变化为 0 页） |
| 八项发布门禁 | errors 0 / overfull>5pt 0 / missing glyphs 0 / undefined refs 0 / dup labels 0 / dup includes ok / overlap **PASS**（blocking=0 candidates=91）/ PASS |
| 其他门禁 | `check_src` 85 表 PASS 85；`pdf_probe` R2-U01/U02 + R3-W03 全 PASS；`fig_probe_eis` PASS + selftest PASS；`check_terms` OK；`recompute_ch03b_dtg` 654 点 PASS；`check_table_content`（OCR 文本层）13 FOUND / 1 INDEX_OK / 54 NO_TABLE_NO / 17 NON_SOURCE |

### 缺陷基线复现（探针灵敏度，不许只报「修后 PASS」）

本轮新增的两个读图/排版探针先在**已知有缺陷的基线**上复现问题，再在候选 PDF 上验收。
基线用线上 **v0.6.4-pre** 附件（`6511DA75…874A`；`chapters/` 与评审基线 `69c3d18` 相同，
`081a846→69c3d18` 的差异只在 tools/docs 的删除，不涉正文），因此与评审报告描述的缺陷
同源（评审自建 PDF 的哈希 `29efd1…` 仅因 PDF 时间戳/ID 不同）：

| 探针 | v0.6.4-pre 基线 | 本候选 |
|---|---|---|
| `fig_probe_tpd.py` P1（图例分簇/配对） | **FAIL**：两图例间隙 8.06 pt；红/黑线段样本与邻面板文字成对（gap = −38.01 / −82.25 pt），行被并成 1 行 | **PASS**：间隙 82.16 pt；5 条线段全部与本行文字配对（dy ≤ 0.33 pt，gap 1.39–3.81 pt）；行距 9.21/9.21/10.11 pt |
| `fig_probe_tpd.py` P2（单倍率） | **FAIL**：检出 2 处 pgfplots 自动倍率 `⋅10` | **PASS**：0 处（倍率只在 ylabel 的 10⁻³ K⁻¹ 里） |
| `fig_probe_tpd.py` P3（刻度线性） | PASS（原有刻度本就线性） | **PASS**：y 残差 0.029 pt、x 残差 1.2e−5 pt（4+6 个刻度） |
| `fig_probe_tpd.py` P4（负号约定） | **FAIL**：ylabel 序列为 `dθ/dT / …`，无负号 | **PASS**：序列以 `−dθ/dT` 开头 |
| `check_heading_orphan.py` | **FAIL**：标题在 p.186 y=743.7，标题后同页仅 1 行（来源行） | **PASS**：标题在 p.187 y=73.6，标题后同页 53 行；上一页末条正文 y 由 759.2 → 726.0（页尾留白增加约 33 pt） |

两个探针都带 `--selftest` 合成反例（判据抓得住阈值附近的缺陷），基线复现证明灵敏度。

### 无视觉能力声明

本会话模型仍**没有视觉接入**（这一点本轮已实测，见会话记录）。R5-U01/R5-U02 的
「放大查看」验收改由**矢量层探针 + 文字层探针**完成：PDF 文字/线条是矢量对象，
100%/200% 查看只是同一几何的线性缩放，探针直接检查几何本身（分簇、配对、行距、
倍率唯一、刻度线性、标题后同页行数），结论对缩放不变。仍建议有视觉者打开
`build/main.pdf` 复核 p.110 与 p.186–188 的观感；放大图已渲染到
`build/round5-closeup/`（2×：`fig5-1_2x.png`、`p186_2x.png`、`p187_2x.png`、`p188_2x.png`）。

### 环境异常记录（与源码无关）

首次 `-Release` 构建失败（`latexmk exit 12`，`xdvipdfmx:fatal: Out of memory`，
overlap 门禁因此 UNUSABLE）。查得同机另一项目（`mechanics-textbook`）的
`reviews/2026-10-01-deep-review/verify_symbolic_all.py` 用 `glob('verify_symbolic_*.py')`
把自己也收进脚本列表，`subprocess.run([sys.executable, 自己])` 无限递归，已派生
**7472 个 python.exe**、占 17.5 GB，使页面文件耗尽。经用户确认后按根 PID 连带子树
结束 7467 个失控进程；同一份源码重新构建即通过（本 CLOSURE 的制品）。这是宿主环境
问题，不是本仓库源码/门禁问题，记录在此以免日后误判。

## 1 新增 6 项

| ID | 结论 | 改动（含位置） | 实测证据 |
|---|---|---|---|
| R5-C01 (P1) | **候选完成** | `tools/gen_tpd_table.py` 重写单位层：`beta` 一律 K/min、`A` 一律 s⁻¹（`A_PRE_S` 由解析峰温条件反解，见 L63）；积分在秒制下完成；新增 `--verify`（两种时间单位、闭式积分、解析峰温条件、守恒、欠采样）；新增 `--patch` 回写整块 tikzpicture；`chapters/parts/ch05-a.tex` 图注 `A` 改为 `7.35e8 s⁻¹ = 4.41e10 min⁻¹` 并注明标定 | `python tools/gen_tpd_table.py --verify` → 6 行全 PASS：秒/分两套独立求解 worst_rel **3.18e−11**；闭式积分 vs ODE **3.09e−10**；解析峰温条件 vs 数值峰位 **ΔTp = 2.60e−6 K**；覆盖度不增 + `∫(−dθ/dT)dT = θ₀−θ(1500)` **1.11e−15**；半高交点全部落在 2 K 加密区；图注数字与生成器一致。`--check` 5×99 点 worst_rel 4.797e−6。**未选**「只改注释说明 A 是 min⁻¹」：那虽能自洽，但会让正文/图注的 s⁻¹ 惯例与其它章节不一致；现选重标定（等效 min⁻¹ = 4.40706e10） |
| R5-C02 (P2) | **候选完成** | `chapters/parts/ch08-c.tex` L56–64：dataflow 拆成「归属分支（CP/MAS 或单脉冲，化学位移）」与「定量分支（单脉冲、积分面积、`D₁≳5T₁`、核数/标记丰度/标样响应校准）」，并链到 §8.3.3（`sec:bl-quant`）与式 (8-11)（`eq:ernst`）、§8.1.3（`sec:cp-mas`，`ch08-a.tex` L240 新增标签）；pitfall 新增第 (4) 条「把 CP/MAS 峰强当产率」（L104–107） | 独立反例 `python tools/check_cp_quant_demo.py`（新工具，示意模型 S=ηN、τ=0.1/5 ms）在 N₁=N₂=1 下：t=0.5/1/2/5/10 ms 的强度比 10.44/5.52/3.03/1.58/1.16，把强度当产率最坏 **9.44×** 偏差 → PASS；PDF 文字层 p.187「此后分两条不可相互替代的分支」、p.188 第 (4) 条均在位；`\S\ref`/`\eqref` 解析为 §8.1.3 / §8.3.3 / (8-11)，undefined refs = 0 |
| R5-C03 (P2) | **候选完成** | `ch05-a.tex`：纵轴改 `−dθ/dT`（L217）；图注「更低更窄」→「**更低更宽**——峰高比 0.681，半高全宽由 52.3 增至 73.5 K（约 1.4 倍）」（L754–755），并给负号约定与式 (5-3) 互指；生成器输出量改为正脱附速率 `−dθ/dT` | 闭式积分 + brentq（与 ODE 无关，方法与评审 `recheck_review.py` 同源）复算：n=1 Tp=570.000 K、峰高 1.7542e−2、**FWHM=52.2985 K**；n=2 Tp=568.578 K、峰高 1.1950e−2、**FWHM=73.4799 K**（比值 1.4050）。覆盖度逐点不增；正速率积分守恒 1.11e−15。`fig_probe_tpd` P4 确认 ylabel 以负号开头 |
| R5-U01 (P2) | **候选完成** | `ch05-a.tex` L216–218：`scaled x ticks=false, scaled y ticks=false`；图例改为**每个面板各一列纵排**（左 3 行、右 2 行，`legend columns=1`），不再并排一行 | `python tools/fig_probe_tpd.py --selftest` PASS；对候选 PDF：P1/P2/P3/P4 全 PASS（数值见 §0 基线表右侧）。比较：修复前左图例 `β=20` 文字（x≤302.6）与右图例红色线段（x=292.2–309.3，y=318.0）在同一水平带相交；修复后两簇最近间隙 82.16 pt |
| R5-U02 (P2) | **候选完成** | `ch08-c.tex` L7–8：在 §8.5 标题前加 `\needspace{6\baselineskip}`（只做落页判断，未用 `\samepage`、未把整节设为不可分页的大盒） | `python tools/check_heading_orphan.py --pdf build/main.pdf` PASS（p.187，标题后同页 53 行）；基线 FAIL（p.186，1 行）。release 门禁 overfull>5pt = 0（未新增 overfull），页数仍 314 |
| R5-C04 (P3) | **候选完成** | `ch08-c.tex` L114–115：`\ce{^{2}}` → `\ce{^{2}H}`，并标注「建议实验（本改编本提出、非原书已有实验）」 | PDF 文字层 p.188 依次为 `13`(7.4pt 上标) → `C`(10pt) → ` ／` → `2`(7.4pt，x=481.3) → `H`(10.0pt，x=485.0) → ` 双标记`；基线同段只有上标 `2` 而无 `H`。缺失字形门禁 = 0（H 字形真实存在） |

## 2 收口流程逐项

| 流程项 | 状态 | 证据 |
|---|---|---|
| 每项附源码 diff、复现命令、退出码 | 完成 | §1 每行的命令与数值；批量复跑见 §3 表（含退出码） |
| 先独立数值/故障反例，再跑现有门禁；记录未覆盖/跳过分支 | 完成 | 独立层：`--verify` 6 项、`fig_probe_tpd --selftest`、`check_heading_orphan` 基线复现、`check_cp_quant_demo`；门禁随后（§0 八项）。**未覆盖**：全书 314 页的像素级复核、85 表逐单元格核图、公式逐式原页核对（见 §4）；这些不用「0 mismatch」冒充已完成 |
| 同一候选 PDF 放大复核本轮截图页及相邻页，重记页数/书签/SHA-256 | 完成 | 放大图 `build/round5-closeup/`（p.110、186、187、188、273、309；2×/1.5×）；314 页 / 144 书签 / SHA-256 见 §0 |
| 逐项确认后另写 CLOSURE；不改历史 TODO | 完成 | 本文件；`TODO.md`、`01-content.md`、`02-ui-reading.md`、`findings.json`、`evidence/` 均未修改 |
| 继承队列按上一轮复验继续 | 部分 | 见 §4；抽样通过不替代全书验收 |

## 3 复跑命令与产物（本轮实测退出码）

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release      # exit 0（314 页 / 门禁全 0 / overlap PASS）
python tools/gen_tpd_table.py --check                                       # exit 0（5×99 点，worst 4.797e-6）
python tools/gen_tpd_table.py --verify                                      # exit 0（6 项独立检查）
python tools/fig_probe_tpd.py --selftest                                    # exit 0
python tools/fig_probe_tpd.py --pdf build/main.pdf --json build/tpd_fig.json --out build/tpd_fig.txt   # exit 0
python tools/check_heading_orphan.py --pdf build/main.pdf --json build/heading_orphan.json             # exit 0
python tools/check_cp_quant_demo.py                                         # exit 0（最坏偏差 9.44×）
python tools/pdf_probe.py --pdf build/main.pdf                              # exit 0（U01/U02/W03 全 PASS）
python tools/fig_probe_eis.py --pdf build/main.pdf ; python tools/fig_probe_eis.py --selftest          # exit 0 / 0
python tools/check_src.py ; python tools/check_terms.py ; python tools/check_includes.py               # exit 0 / 0 / 0
python tools/recompute_ch03b_dtg.py                                         # exit 0（654 点）
python tools/check_table_content.py --csv build/table-content.csv           # exit 0（文本层统计，不是通过率）
python tools/overlap_check.py --gate --pdf build/main.pdf                   # exit 0（blocking=0 candidates=91）
# 缺陷基线复现（v0.6.4-pre 附件）：
python tools/fig_probe_tpd.py --pdf build/_baseline_v064.pdf                # exit 1（P1/P2/P4 FAIL）
python tools/check_heading_orphan.py --pdf build/_baseline_v064.pdf          # exit 1（p.186 仅 1 行）
```

发布流程按 HANDOFF §7 执行：tag `v0.6.5-pre`（@ `c092a14`）→ 建 release（**id=52**）→ 上传附件
（asset id=70，`/attachments/2ec2b99d-19c1-47af-b0aa-724f7cfa8505`）→ 从公开下载地址回验：
`/releases/download/v0.6.5-pre/…` 与 `/attachments/…` 均 HTTP 200，下载件 SHA-256 与本地一致
（`d0736a5c…a6e9d`）。本轮 `_relpayload.json` 与回验记录在 `build/`（不入库）。

## 4 残余风险与未覆盖（继承队列）

| 项 | 状态 | 说明 |
|---|---|---|
| 85 张表**像素级**核图 | 未完成 | 本轮只做了 OCR 文本层交叉核对（54 NO_TABLE_NO 等，不是通过率）；逐单元格核图仍需图像通道/人工 |
| 公式逐式原页核对 | 部分 | 台账 `sources/formula_verify.md` 未变；本轮未新增逐式核对 |
| 原书装置数值/谱图归属逐字核对 | 未完成 | §8.5 三类装置的转速/温度/压力仍带 `\tocheck`（未对照原页面图像），本轮未移除标记 |
| 旧凭据轮换与历史清理 | **已完成**（2026-10-02） | R2-W01 关闭：两处旧口令轮换（旧 401 / 新 200）、`git filter-repo` 重写历史并强推、12 个 release 元数据同步；证据与映射见 `reviews/2026-10-02-history-cleanup/`；服务端 `git gc --prune=now` 待管理员执行（旧值已失效） |
| R5 评审自带 `recheck_review.py` 的复跑 | 说明 | 该脚本内置的是**修复前**的 A=4.39753e10 模型（用于取证）；修复后其数值是历史模型值，不能用它判修复对错。新回归夹具是 `gen_tpd_table.py --verify` 与 `fig_probe_tpd.py` |
| 全书逐页/逐式验收 | 未做 | 本轮只覆盖被指出的 6 项与相关页（p.110、p.186–188、p.273、p.309）；抽样通过不构成全书正确性证明 |
