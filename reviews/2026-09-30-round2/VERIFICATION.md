# R2 第二轮评审 · 验证报告

> **固定提交**：`ddc8f1a`（本报告的修复与工具改动都在这个提交上；本文件随后一个 `docs` 提交入库）
> **评审基线**：`b9bdf73`（`reviews/2026-09-30-round2/` 的提交）→ `58b0440`（其后的凭据修复）
> **结论**：16 项中 **15 项关闭**；`R2-W01` 只关了仓库内部分（旧口令轮换需账户管理者）。
>
> ⚠️ **本报告不是「内容已全部正确」的证明。** 内容级逐页核对在本环境**无法执行**（会话是无视觉的
> 纯文本模型，见 §4.2）。本报告能证明的是：列出的缺陷已改、改动能被独立复算或程序化检查、
> 门禁真的在跑且失败时真的会失败。

---

## 1. 出厂制品与门禁（全部可复现）

| 项 | 值 |
|---|---|
| 制品 | `build/main.pdf`，3,987,451 字节，**313 页**，**143 条**中文书签 |
| SHA-256 | `27B726B2B41671A91151E03492B92F979ED5090FA3A66AD9C9985636FE50FF4E`（2026-09-30 02:11 构建） |
| `tools/build.ps1 -Release` | `latexmk exit 0` / pages 313 / errors 0 / overfull>5pt 0 / missing glyphs 0 / undefined refs 0 / dup labels 0 / `dup includes : ok` / **`overlap : ok`**（`overlap gate: PASS blocking=0 candidates=99`）/ **PASS** |
| `python tools/check_src.py` | `checked 85 tables: PASS 85, REVIEW 0, FAIL 0`，exit 0 |
| `python tools/pdf_probe.py` | `R2-U01 PASS`（检查 143 条，不符 0）、`R2-U02 PASS`（命中 0），exit 0 |

**页数漂移**：2026-09-30 的两次 313 页构建字节数相同（3,987,451）而 SHA-256 不同
（`08D468A1…` / `27B726B2…`）——PDF 内含 `/CreationDate` 与 `/ID`，**字节哈希每次构建都会变**，
不能用来判断内容是否变化。判据改用**文本层逐页比对**：`pdftotext -layout` 后逐页 diff，
两次构建 `pages 314 / differing_pages 0 / text_identical True`。

---

## 2. 逐项结论（16 项）

### 内容类（9 项，全部已改，均有可独立复算的证据）

| ID | 结论 | 证据 |
|---|---|---|
| R2-C01 | ✅ 积炭速率主式补回漏掉的 $c_t$ | `chapters/parts/ch10-c.tex:712-718`；原书 (10-135) 分子本来就含 $c_t$——OCR 下标行 `sources/parts/ch10-c.txt:72-74` 第 5 个 `c` 的下标为 `t` |
| R2-C02 | ✅ 临界粒径改 $\propto\sqrt{f}$ 缩放；WP 自检不再手工重乘 $\rho$，两个基准都 0.015、22.5 标为量纲不合格 | `chapters/parts/ch10-c.tex:457-459`、`:519-526`、`:720-744`（含「0.5 vs 漏 $c_t$ 的 0.25」数值自检）；`sources/formula_verify.md` |
| R2-C03 | ✅ $j_D$ 左端补 $\rho$ 并定义之 | `chapters/parts/ch10-b.tex:384` `j_D=\frac{\rho k_G}{G}Sc^{2/3}`、`:388` 补「$\rho$ 为流体密度」；量纲反证 + 用 $\rho=2$ 逐位复现评审 `chilton_colburn` 的 0.031498/0.062996 |
| R2-C04 | ✅ 「倒数之和」改回并联阻抗 | `chapters/parts/ch11-d.tex:152-163`（$Y\equiv1/Z$、总导纳是各支路之和；两个 10 Ω 并联 → 0.2 S → 5 Ω），并在 `\src` 里记下与源书措辞的差异 |
| R2-C05 | ✅ 平均周期改 $T=2\pi/\omega\approx2\pi/\omega_0$；「分母应补 2」写成**不采纳**的理由 | `chapters/parts/ch12-b.tex:326`、`:334-340`（$T=1/\omega_0$ 只覆盖 1 rad、线性力下给 $0.2727gA^2$、与 $-\omega_0g/(2k)$ 不自洽；三项独立复算都回到 $-\omega_0g/(2k)$，补 2 会使其减半）；源书同处排印问题记入 `sources/errata.md:48` 乙类 **B10** |
| R2-C06 | ✅ 全章统一相角约定 $\varphi\equiv-\arg Z$ | `chapters/parts/ch11-d.tex:88-89`（约定行）、`chapters/parts/ch11-c.tex:17`（实例节声明「本节相角一律按 $\varphi\equiv-\arg Z$」，并明说源书图 11-42/11-43 的纵轴定义未能核对） |
| R2-C07 | ✅ BET 分开总量与单位质量量，给出同材料双路径算例 | `chapters/parts/ch01-a.tex:174-223`（$S_s=V_{m,s}N_A\sigma/22400$ 与 $S_{total}=V_{m,total}N_A\sigma/22400$；0.1 g、21 mL → 91.5 m² → /0.1 g ≈ 915 m²/g） |
| R2-C08 | ✅ DTG 改用实际质量导数、横轴改 K | `chapters/parts/ch03-b.tex:191-209`（$-\dd m/\dd T=20\,\dd\alpha/\dd T$，峰值 $20/48=0.4167$ %/K；四中心 658/673/688/703 K 与本章 $T_p\approx673$ K 接通） |
| R2-C09 | ✅ 拉曼改为无量纲操作式 | `chapters/parts/ch06-a.tex:182-208`（$I/I_0=(\dd\sigma/\dd\Omega)\Delta\Omega\sin^2\theta$，两端无量纲；$\Delta\Omega$ 加倍 ⇒ $I$ 加倍） |

### 导航类（2 项）

| ID | 结论 | 证据 |
|---|---|---|
| R2-U01 | ✅ 目录项与锚点由 `\chapterheadstar` 在**落页之后**统一创建 | `style/preamble.tex:242-267`（`\needspace` → `\phantomsection` → 委托宏写 `\addcontentsline` → `\markboth`；`main.tex:43-44` 明确写「**不要**再补 `\phantomsection`/`\addcontentsline`」）；验收 `tools/pdf_probe.py`：新制品 PASS、v0.6.0-pre 旧 PDF **FAIL（2 条：303→304、305→306）** |
| R2-U02 | ✅ 非编号区块页眉不再串第 12 章 | 同上 `\markboth{#2}{}`（本书页眉只用 `\leftmark`，见 `style/preamble.tex:329-340`）；`pdf_probe`：新制品 **命中 0**、旧 PDF **命中 4 处（p.303/305/307/309）** |

### 工程类（5 项）

| ID | 结论 | 证据 |
|---|---|---|
| R2-W01 | ⚠️ **部分关闭**：`HANDOFF.md` 三处明文凭据已改为仓库外 `~/.gitea-netrc`（评审探针 `credential_rows` 由 `[67,400,407]` 变 `[]`）；**旧口令仍留在历史提交与本机 `.git/config` 中，须账户管理者轮换后才算关闭** | `58b0440`；本报告不复述旧值 |
| R2-W02 | ✅ README 与当前状态同步 | `README.md:45-58`（状态快照：时间/源码 SHA/模式/产物哈希 + 「字节哈希每次都变」的说明）、两档命令与八项门禁表 |
| R2-W03 | ✅ 来源门禁边界收紧 | 见下方三层结论；三个负例（页码 +10000 / 错原表号 / 未入账表）全部 exit 1，全库仍 `checked 85 tables: PASS 85` |
| R2-W04 | ✅ `skipped` 不再等于发布 PASS | `tools/build.ps1:23-25,90-94` `Invoke-PyCheck` 三态 `ok`/`FAIL`/`unavailable`；`-Release` 判 unavailable 失败并打印「未执行（原因）—— 未检查 ≠ 通过」，draft 只标 `skipped（原因）` |
| R2-W05 | ✅ 重叠检测接入发布验收 | `tools/overlap_check.py:401-402` `--gate` / `--block-text`；退出码 0 PASS / 1 BLOCK / 2 UNUSABLE（2 = 没检查）；只拦确认相撞的图形，文字/上下标/粗条按类别报候选 |

`R2-W03` 的细节（本工具三层结论，见 `tools/check_src.py:38-44`）：① **标注格式**（本工具判）
② **目标页可达**（本工具判：册内页数边界 + 逐页存在于 `sources/page_map_*.csv` + 原表号↔OCR 索引页
容差 `PAGE_TOL=2`）③ **内容人工核对**（**本工具不判定**，只读台账 `review_status`）。

---

## 3. 三条独立证据链

### 3.1 评审自带的探针（`recheck_review.py`，未改一行）

第三次运行（`--out build/r2/recheck3`），与前两次基线（`b9bdf73` / `58b0440`）逐叶子字段比对，
**40 个字段翻转**，其中包括全部「会翻转」的字段：

| 字段 | 改前 | 改后 |
|---|---|---|
| `credential_rows` | `[67,400,407]` | `[]` |
| `invalid_source_pages.exit_code` / summary | `0` / `PASS 2` | **`1` / `FAIL 2`** |
| `release_missing_checker.exit_code` / `prints_pass` | `0` / `true` | **`1` / `false`** |
| `overlap_gate.main_return` | `None`（命中却无退出码） | 完整结果字典（`blocking_total: 0`、`exit_code: 0`） |
| `pdf.backmatter_bookmarks[0][2]` / `[1][2]` | `303` / `305` | `307` / `309` |
| `pdf.pages` | `310` | `313` |

9 个数学参考模型字段（`coke` / `weisz_prater` / `chilton_colburn` / `parallel_impedance` /
`afm` / `eis_phase` / `bet_area` / `dtg_center` / `raman_dimensions`）保持不变——它们是
**硬编码的独立复算基线**（`recheck_review.py:23-47`），改稿不应该也不能让它们翻转；
本轮用它们做的复算见 §2 的 C02/C03/C05/C08。

### 3.2 门禁的负例（「失败时真的会失败」）

- **W03**：书页与 PDF 页同时 +10000 → `FAIL 1`、exit 1；表号改成索引里存在但页对不上的
  `表 9-33` → exit 1（「OCR 索引页 704 距引用书页 p.5 最近 699 页 > 容差 2 页」）；
  插入未入账的表 → exit 1（stderr `unregistered tables (not checked)`）；未改动的对照 ch01-a
  仍 `PASS 2`、exit 0。
- **W04**：15 次隔离构建（编译器桩，脚本与仓库版逐字节相同）覆盖四种场景 × 两模式：
  缺检查器 draft 0 / release 1；无 python draft 0 / release 1；检查器非零 draft 1 / release 1；
  正常 draft 0 / release 0；重叠阻断 release 1；不可用 release 1。
  **对照组**（git HEAD 的旧脚本）在缺检查器与无 python 时 release 都是 **exit 0**（缺陷复现）。
- **W05**：四个合成 PDF 走真实入口——无碰撞 `0`、**相交框 `1`（BLOCK）**、合法嵌套 `0`、
  数学上下标 `0`（`--block-text` 下也不按总数一刀切）；真实本书 `blocking=0 candidates=99`。

### 3.3 程序化导航验收（`tools/pdf_probe.py`，本仓库新增，只读）

同一探针跑两个 PDF 得到相反结论，说明它有灵敏度：

| 制品 | R2-U01 | R2-U02 |
|---|---|---|
| `build/main.pdf`（313 页，本次） | PASS（143 条不符 0） | PASS（命中 0，扫描自 p.307） |
| `release/catalysis-methods-essentials-v0.6.0-pre.pdf`（310 页，上一版） | **FAIL**（跨方法综合应用 303→304、符号/缩写与索引 305→306） | **FAIL**（4 处：p.303/305/307/309 页眉仍「第12 章…」） |

后置区块书签目标页（新制品）：跨方法综合应用 307、符号/缩写与索引 309、勘误与待核对状态 313。

---

## 4. 未关闭事项与待人工核对

### 4.1 `R2-W01` 的剩余动作（需账户管理者）

仓库内已看不到明文凭据，但**历史提交与本机 `.git/config` 里的旧口令仍视为已泄露**，
必须由账户管理者轮换后才能把该项判为关闭。本报告不复述旧值。

### 4.2 视觉复核缺席（`TODO.md:38` 的第 2 条只完成了一半）

`TODO.md` 的关闭条件要求「PDF 目录、书签、页眉和关键图表经过**视觉复核**」。本会话是
**无视觉的纯文本模型**（三层证据：`read_image` 只回传尺寸/字节数与 sha256、无像素；
自建盲测的随机码图答不出；`@deepseek-ai/dsh-llm/lib/types/content.js:47-50`
`textOnlyImageText(ref)` 把图片替换成文本占位）。因此：

- **书签与页眉**改用 `tools/pdf_probe.py` **程序化**验收（比目视更可复现，且已用旧 PDF
  证明能复现缺陷）——这一半可视作已替代完成；
- **目录、关键图表的可读性与 A4 实际尺寸检查**（`TODO.md:32`）**没有做**，留给有视觉的人；
- 本轮 9 项内容修复的依据是**文字层（OCR）+ 独立复算**，不是原页面图像；
  `STYLE_GUIDE.md:264` §10 第 3 条「所有公式已对照原页面图像核对」**在本会话无法执行**，
  不得声称已完成。

### 4.3 三条工具层的残余风险（接手时先读）

1. `tools/check_src.py` 的「目标页可达」是**二手证据**：源书 PDF 不随仓库分发，判据依赖
   人维护的 `sources/page_map_up.csv`（543 行）/ `page_map_down.csv`（462 行）。
2. 该工具第③层「内容人工核对」全书 **85/85 仍是「未核对页面图像」** ⇒
   **release PASS 只说明标注格式与页号自洽，不代表内容正确。**
3. `tools/overlap_check.py --gate` 默认只把「图形相撞」判为阻断（本书 `blocking=0 candidates=99`）；
   文字压文字属候选，要纳入阻断须显式 `--block-text`——这是评审明确要求的「不得按候选总数
   一刀切」，不是缺陷。

### 4.4 仍然开放的工作

- **P1 公式逐条核对**（100+ 式）只推进了少数几条；台账 `sources/formula_verify.md` 是本轮
  与首轮的汇总处。
- `TODO.md:27-33` 的 5 条设计建议（勘误索引升级、方法路径可点击、第 11 章「上一节」改显式引用、
  A4 可读性检查与压页、C05-02/C06-01/C09-01 单独复验）**本轮未做**，它们不计入缺陷数。

---

## 5. 复现命令

```powershell
# 0) 出厂构建（八项门禁；313 页 / 六项 0 / overlap PASS）
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release

# 1) 来源标注门禁（85 张表；三层结论；三个负例见 §3.2）
python tools/check_src.py

# 2) 导航程序化验收（书签落页 / 后置页眉）
python tools/pdf_probe.py --pdf build/main.pdf --out build/pdf_probe.txt

# 3) 版面重叠门禁（只读；退出码 0/1/2）
python tools/overlap_check.py --gate --pdf build/main.pdf --json build/overlap.json

# 4) 内容层漂移判据（不要比字节哈希）
pdftotext -layout build/main.pdf build/_a.txt       # 再与上一次构建的文本层逐页 diff

# 5) 评审自带探针（缺陷复现器；不是验收报告）
python reviews/2026-09-30-round2/recheck_review.py --out build/recheck
```

本轮全部改动在一个提交上：`ddc8f1a`（22 个文件，1890 insertions / 444 deletions）。
评审原始材料未改动，只增本报告。
