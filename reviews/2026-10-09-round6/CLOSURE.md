# 第六轮评审 CLOSURE（2026-10-09）

## §0 交付元信息

| 项 | 值 |
|---|---|
| 评审输入 | `reviews/2026-10-09-round6/`（`findings.json` 6 条 P2；`TODO.md` 三批 + 收口证据要求） |
| 基线提交 | `71f5ebc5158bb87632f82c93903d7ede3afb3281` |
| 修复提交 | `b3fe3d5`（评审(第六轮): 关闭 R6-C01/C02/C03/U01/U02/W01 六项并导入评审工作区） |
| 收口提交 | `v1.0.0` 标签所指提交（即本文件所在提交） |
| 发布制品 | `release/catalysis-methods-essentials-v1.0.0.pdf`（首个非 `-pre` 版本） |
| 页数 / 书签 | 340 / 145（R5 为 315 页 / 144 书签；+1 书签来自新增后置小节「表核对记录」） |
| 字节数 | 4233857 |
| SHA-256 | `A5969A1476C6C105D930E1B01B835E3097D835412B5876D6DDA598B780069C46` |

发布门禁（`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release`，日志 `build/_rel_r6b.log`）：
latexmk exit 0；pages 340；errors 0；overfull >5pt 0；missing glyphs 0；undefined refs 0；dup labels 0；
dup includes ok；overlap ok；table `\src` ok；overlap gate PASS（blocking=0，candidates=109）；总判定 **PASS**。

**提交后重建一致性**（发布制品必须出自已提交源码状态）：提交完成且工作树干净后重建，与提交前的制品
`build/_rel_pre.pdf` 做内容级比对：

```
python tools/cmp_release_pdf.py build\_rel_pre.pdf build\main.pdf
_rel_pre.pdf  pages=340 bookmarks=145 bytes=4233857
main.pdf      pages=340 bookmarks=145 bytes=4233857
ok  bookmark tree identical (145 entries)
ok  text layer (content + block geometry) identical on all 340 pages
ok  drawings (geometry + stroke/fill) identical on all 340 pages
ok  raster images (content + placement) identical on all 340 pages
RESULT: IDENTICAL CONTENT        （退出码 0）
```

字节哈希由 `23fb1068…` 变为 `A5969A14…` 属设计预期：`/ID` 与 `/CreationDate` 每次构建都变（README §一），
跨构建判等价只能用内容级比对，不能用字节哈希。

## §1 逐项关闭

### R6-C01（content）Rayleigh 区粒径依赖写反 —— 已关闭
- 位置：`chapters/parts/ch01-c.tex:382-385`（PDF p.22—23）
- 修改：把「散射光强度与粒径的六次方成**反比**」改为成**正比**，补 10 nm → 20 nm 的
  $2^{6}=64$ 倍算例，并就地记明原书此处排印为「成反比」、与 $I\propto d^{6}$ 相反，属原书笔误，本版按正比表述。
  正比表述前保留限定条件「在材料、介质、波长与颗粒个数都相同的条件下」，未写成任意粒径的普适规律。
- 数值反例（`verification.json` → `physics.rayleigh`）：等个数 10 nm 与 20 nm 颗粒，
  `equal_number_intensity_ratio = 64.0`（= 2⁶）；按原书「反比」写法应为 `inverse_claim_ratio = 0.015625`，方向相反。
- 复现：`python reviews/2026-10-09-round6/recheck_review.py --out build/review-round6` → 退出码 0，读
  `build/review-round6/verification.json` 的上述两个字段。
- 视觉复核：`python tools/vbook.py 22 build/verify/r6/p22.png --dpi 150`（同 23）；读图确认正文为
  「与粒径的六次方成正比——粒径由 10 nm 增至 20 nm，散射强度增大 2⁶ = 64 倍。原书此处排印为「成反比」…属原书笔误，本版按正比表述并在此记明」。
- 判定：TODO 验收两条（比值 64；不是普适规律）均满足。

### R6-C02（content）电泳法被当成粒径的唯一反演依据 —— 已关闭
- 位置：`chapters/parts/ch01-c.tex:226`（表 1-4「电泳法」行）+ `:440-447` 正文（PDF p.20、p.23）
- 修改：表内第二列改为「电泳迁移率 $\mu_{\mathrm{e}}$ 与 Zeta 电位 $\zeta$（**不给出粒径分布**）」；
  正文把 ELS → $\mu_{\mathrm{e}}$ → $\zeta$ 与 DLS → $D$ → $d$ 两条链路分开，补薄双电层 Smoluchowski 极限
  $\mu_{\mathrm{e}}=\varepsilon\zeta/\eta$ 与粒径无关、同 $\zeta$ 的 100 nm 与 200 nm 球给出同一 $\mu_{\mathrm{e}}$ 的反例，
  并说明仪器同时报出 Zeta 与粒径时粒径来自 DLS 通道或另行测定、$\mu_{\mathrm{e}}$ 与 $\zeta$ 反演粒径必须另加含粒径的模型并在报告中写明适用条件。
- 数值反例（`physics.smoluchowski`）：$\varepsilon_r=78.5$、$\eta=1$ mPa·s、$T=298.15$ K、$\zeta=25$ mV 时，
  100 nm 与 200 nm 的迁移率同为 `1.7376343582620002e-08` m²/(V·s)；而 Stokes–Einstein 扩散系数分别为
  `4.3676413498912424e-12` 与 `2.1838206749456212e-12` m²/s —— 迁移率本身不含粒径信息。
- 复现：同 R6-C01 的复现脚本，读 `verification.json` → `physics.smoluchowski`。
- 视觉复核：p.20 表 1-4 电泳法行、p.23 正文「其他方法」段（渲染图 `build/verify/r6/p20.png`、`p23.png`）。
- 判定：TODO 验收三条均满足。

### R6-C03（content）DLS 强度权重与体积／数量口径混用 —— 已关闭
- 位置：`chapters/parts/ch01-c.tex:225`（表 1-4「动态光散射法」行）+ `:430-433` 正文（PDF p.20、p.23）
- 修改：表内第二列标「**强度加权**粒径分布（体积／数量分布须模型换算）」；正文补「仪器默认报出的是强度加权分布，
  体积分布与数量分布都是在此基础上的模型换算，须另设颗粒形状、光学性质与散射模型假设，不能与电镜的个数分布直接比较峰位」，
  给出等个数 10 nm 与 20 nm 的算例（体积权重 1:8、强度权重 1:64，大颗粒分别占 8/9 与 64/65），
  并说明 $z$ 平均径与 PDI 是累积量分析给出的平均量与宽度指标，不等同 $D[4,3]$、$D[3,2]$，报告须注明口径。
- 数值反例（`physics.weighting`）：`volume_ratio [1, 8]`、`intensity_ratio [1, 64]`、
  `large_particle_volume_fraction 0.8888888888888888`（8/9）、`large_particle_intensity_fraction 0.9846153846153847`（64/65）。
- 复现：同 R6-C01 的复现脚本，读 `verification.json` → `physics.weighting`。
- 视觉复核：p.20 表 1-4 动态光散射行、p.23「动态光散射法」段与「两者不可混用的算例」句。
- 判定：TODO 验收三条均满足；正文与汇总表口径一致。

### R6-U01（reading）逐行核对说明先于浮动表出现 —— 已关闭
- 位置：正文侧 `chapters/parts/ch09-a.tex:431-436`；新增审计小节 `chapters/ch90-backmatter.tex:298-350`（PDF p.339）
- 修改：正文侧长逐行日志压缩为「来源入口 + 未逐页核对清单 + 指向审计记录」的短核对说明，保留
  `\src{S2 §9.2.3，书内 p.586—605 / PDF p.77—96，图 9-20、图 9-21}`（`ch09-a.tex:391`）与 `\label{tab:xpsparts}`（`:396`）；
  逐行出处、原书引文与「改编补充」判定迁入后置新小节 `\subsection{表核对记录}\label{sec:table-audit}`，
  按表 ID 检索（`\texttt{tab:xpsparts}` 条含 8 条逐行证据）。
- 视觉复核（`tools/vbook.py <页> <out.png> --dpi 150`）：
  - p.218：正文 §9.2.3 之后是约 5 行的短核对说明 + 四点必要说明，不再有逐行日志；
  - p.219：**表 9-1 位于页首**，读者在遇到任何「第 n 行」内容之前已能看到表；表后才是深度剖析、变角 XPS 等正文；
  - p.339：审计小节标题行文字层为 `12.9 表核对记录`，`\ref{sec:table-audit}` 在 p.218 解析为「表核对记录 12.9」，
    交叉引用一致（此前疑为编号缺失，经 PDF 文字层确认属读图误判）。
- 副产物：新增小节使书签数 144 → 145（`pdf_probe.py` 报 `表核对记录=339`）。
- 判定：TODO 验收三条均满足。

### R6-U02（reading）拉曼汇总表「谱带区间」列混入条件与相对位移 —— 已关闭
- 位置：`chapters/parts/ch06-c.tex:846-847`（题注列契约）、`:863`、`:865`、`:871`（PDF p.160—161）
- 修改：题注加列契约「第三列只列绝对峰位或区间（均以 cm⁻¹ 为单位）；无绝对峰位者记「---」；
  负载量、覆盖率一类条件与相对位移 $\Delta\nu$ 一律列在第四列，不参与谱峰检索」；
  三行（表面 Mo 物种 / `\ce{Mo{=}O}` 端基 / 负载 `\ce{WO_x}`）第三列改为「---（无绝对峰位）」，
  百分数与 Δν 移入第四列；50—60 cm⁻¹ 明确为**相对水合态**的位移 Δν 并给出参照态。
- 视觉复核：p.160 为题注 + 表头 + 前 4 行；p.161 续页**表头完整重复**（物种／配位 结构／谱带区间／判断依据），
  首续行「Mo=O 端基」第三列为「≈ 950；水合/脱水 900—1000」，其 Δν 说明落在第四列；
  并确认 p.162 不是该表续页（为 ch06-c 收尾与第 7 章起始），该表只跨页一次。
- 判定：TODO 验收四条（百分数入条件列、50—60 标明相对位移与参照态、按绝对波数检索不命中条件、跨页表头清楚）均满足。

### R6-W01（workflow）PDF 内容等价比对漏检三类可见改变 —— 已关闭
- 位置：`tools/cmp_release_pdf.py`（现 191 行）
- 改前：只比文本层 + 每页绘图**数量**，故 60 pt 矩形平移、同位置同尺寸位图改色、文本 y=40→220 三类可见变化均误报 `IDENTICAL CONTENT`。
- 改后：新增 `norm()`、`_round()`、`_color()`、`_rect()`、`page_signature()`，逐页比对
  ①文本块（内容 + 几何）、②矢量绘制（几何 + 描边/填充 + 线宽 + item 数）、③位图（内容 SHA-1 + 落位），
  另比页数与书签树；文档元数据（`/ID`、`/CreationDate`）**有意排除**并打印说明。退出码契约：0 相同 / 1 不同 / 2 不可用。
- 四夹具实测（`recheck_review.py`；夹具与页面图像另存 `build/review-round6/comparator-fixtures/`）：

  | 变体 | 修复前 | 修复后 | 命中检查 | 渲染字节变化 |
  |---|---|---|---|---|
  | `metadata_only`（元数据 A→B） | exit 0 | exit 0 `IDENTICAL CONTENT`（正确） | 四项全 ok | 0 |
  | `geometry_changed`（矩形平移 60 pt） | exit 0（漏检） | exit 1 `DIFFERS` | drawings 几何 `['p1 1!=1']` | 2720 |
  | `raster_changed`（位图改色） | exit 0（漏检） | exit 1 `DIFFERS` | raster images `['p1 1!=1']` | 7200 |
  | `text_moved`（文本 y 40→220） | exit 0（漏检） | exit 1 `DIFFERS` | text layer `[1]` | 4212 |

- 判定：TODO 验收（元数据对照通过；几何移动／栅格改色／文字移动不得被认证为内容相同；保留可复跑夹具与容差定义）均满足；
  本轮并已用它证明发布重建与提交前制品内容一致（§0）。

## §2 收口流程

1. 导入评审工作区：复制 `findings.json`、`TODO.md`、四份评审报告、`recheck_review.py`、`audit.json`、
   `verification.json`、`build-summary.txt` 与 `evidence/` 7 张问题页图到 `reviews/2026-10-09-round6/`。
2. 逐项修复六项，全部落盘。
3. 全量发布构建 `tools/build.ps1 -Release` → 340 页、门禁全 0、PASS（日志 `build/_rel_r6.log`）。
4. 跑本轮复现脚本 `python reviews/2026-10-09-round6/recheck_review.py --out build/review-round6` → 退出码 0，
   产出 `verification.json`（PDF 页数/书签/SHA-256、4 个源文件 SHA-256、physics 数值、comparator 四夹具、10 条命令退出码）。
5. 视觉复核：渲染并逐张读图 p.20/21/22/23、p.160/161/162/163、p.217/218/219/220、p.338/339/340（`build/verify/r6/`）。
6. 提交修复 + 评审工作区 + `.gitignore`（GraphFlow 本地产物）→ `b3fe3d5`。
7. 干净工作树重建（`build/_rel_r6b.log`，exit 0）→ 与提交前制品内容比对 `IDENTICAL CONTENT` →
   复制为 `release/catalysis-methods-essentials-v1.0.0.pdf` → 计算 SHA-256。
8. 打 tag `v1.0.0` → 推送 → 建 release → 上传附件 → 从公开地址回验（流程见 `HANDOFF.md` §7）。

## §3 复跑命令与退出码

| 命令 | 退出码 | 关键结果 |
|---|---|---|
| `pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release` | 0 | 340 页；errors/overfull>5pt/missing glyphs/undefined refs/dup labels 全 0；dup includes ok；overlap gate PASS(blocking=0, candidates=109) |
| `python reviews/2026-10-09-round6/recheck_review.py --out build/review-round6` | 0 | PDF 340 页 / 145 书签；comparator `(0,0)/(1,2720)/(1,7200)/(1,4212)`；10 条生产命令退出码全 0 |
| `python tools/cmp_release_pdf.py build\_rel_pre.pdf build\main.pdf` | 0 | `IDENTICAL CONTENT`（340 页，四类比对全一致） |
| `python tools/pdf_probe.py --pdf build/main.pdf` | 0 | 340 页 / 145 书签；R2-U01 书签落页 145 项 0 不符；R2-U02 后置页眉 0 命中；R3-W03 必要书签 15/15 |
| `python tools/fig_probe_eis.py --pdf build/main.pdf` | 0 | 图 11-5 p.297；CPE 包围盒比 0.6645（模型 0.6656）；P2/P3 PASS |
| `python tools/fig_probe_tpd.py --pdf build/main.pdf` | 0 | 图 5-1 p.121，P1—P4 PASS |
| `python tools/fig_probe_tpd.py --selftest` | 0 | PASS |
| `python tools/gen_tpd_table.py --verify` | 0 | 秒/分双解 worst_rel 3.180e-11；解析 vs 数值峰温 ΔT 2.598e-06 K；守恒 6 项 |
| `python tools/gen_tpd_table.py --check` | 0 | worst_rel 4.797e-06（rtol 1.0e-05） |
| `python tools/check_heading_orphan.py --pdf build/main.pdf` | 0 | p.204 heading_y=119.5、follow_lines=49 |
| `python tools/check_cp_quant_demo.py` | 0 | 最坏产率偏差 9.44×（真值 1.00） |
| `python tools/check_src.py` | 0 | 85 张表 PASS 85 / REVIEW 0 / FAIL 0 |
| `python tools/check_table_content.py --csv build/review-round6/table-content.csv` | 0 | 扫描 85；FOUND 14、INDEX_OK 1、NO_TABLE_NO 54、NON_SOURCE 16（**仅 OCR 文本层**） |

说明：`recheck_review.py` 退出 0 只代表取证运行完成，**不构成门禁**；其内部各命令的结果必须逐条阅读，上表即逐条读数。
第五轮回归项（TPD 单位与坐标、CP/MAS 强度≠产率、§8.5 标题不孤悬、原位 NMR 同位素归属）在本轮全部重跑并通过（见上表）。

## §4 残余风险与未覆盖

- **85 张表仍属台账级核对**：`sources/table_status.md` 现为 T1=14（逐格读图）/ T2=59（就地核对说明，标「已对照原页面图像」）/
  T3=12（自述改编补充）/ T4=0。**T2 不等于每一格都逐格比对过**；本轮新增的两张表（`tab:methods`、`tab:ch11c-insitu-methods`）同样属就地说明级。
  不得以「T4=0」或 `check_table_content.py`（OCR 文本层）代替科学核验——该脚本只覆盖转写与页码层。
- 各表就地说明中已披露的**未逐页核对**页面仍未读、未作判断（例：ch06-c 表内第 19—23、26—28 行对应的书内 p.365—372；
  ch09-a 的 p.587—588、594、596、599、601、605；ch11-c 表对应区间的若干页）。
- 全书逐式／逐页验收未做，仅抽样（p.110、p.186—188、p.273、p.309 等）；本轮新增核对说明的页面属定向复核，不等于全书复核。
- `recheck_review.py` 依赖 numpy / scipy / PyMuPDF / Pillow，且比对器依赖本机 PyMuPDF 的文本块与绘制解析结果；
  跨环境复跑时字节日志可能不同，内容级判定不受影响。
- 发布件 SHA-256 只在同一次构建内稳定；跨构建必须走 `cmp_release_pdf.py` 内容级比对（本轮已做）。
- 继承队列（未完成，非本轮范围）：原书节覆盖映射剩余 2 个未映射二级节（均为「结束语」，已记不展开）；
  服务端 `git gc --prune=now` 待管理员执行；`yuhanxue` 口令按所有者要求已恢复原值（风险自担）。
- 本轮为评审建议的收口，**发布动作按既有流程单独执行**（`HANDOFF.md` §7）；发布后的下载回验结果记于其后文档同步提交。
