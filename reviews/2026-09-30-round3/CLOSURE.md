# 第三轮评审 · 逐 ID 关闭记录（CLOSURE）

> 本文件由执行方（deepseek-agent）在修完后写入，逐条对应 [TODO.md](TODO.md) 的十项。
> 结论口径一律是**候选完成 + 证据链 + 残余风险**，不是最终裁决；最终裁决权在评审方。

## 0. 交付元信息

| 项 | 值 |
|---|---|
| 代码起点 | `b17b1e9`（本轮评审目录提交）＋ 工作树改动；修复提交即包含本文件的那次提交 |
| 构建模式 | release（`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release`） |
| 制品 | `build/main.pdf`：**315 页 / 143 条书签 / 4 000 358 字节**，SHA-256 `F406F9AAD9E664C0D52AB0174A3CBF3B82F403956BC47D6C6E456B8EF6EA857E` |
| 制品入库 | `build/` 被 `.gitignore:4` 忽略，PDF 不入库；复现请重跑上面的构建命令 |
| 依赖 | TeX Live 2026（`C:\texlive\2026\bin\windows\latexmk.exe`）、Python 3 + PyMuPDF、qpdf（仅取证时用于读绘图算子） |
| 页数变化 | 313 → 315 页：后置索引重排 +2 页（三张长表各自回到自己的小节之后）；书签数不变（143） |
| 工具门禁 | `tools/check_src.py` → `checked 85 tables: PASS 85, REVIEW 0, FAIL 0`（exit 0）；`tools/pdf_probe.py --pdf build/main.pdf` → U01/U02/W03 全 PASS（exit 0）；`tools/fig_probe_eis.py --pdf build/main.pdf` → PASS（exit 0）；`build/r3/probe_ch90_bookmarks.py` → PASS；`build/r3/probe_lookup_tasks.py` → PASS |
| 八项发布门禁 | errors 0 / overfull>5pt 0 / missing glyphs 0 / undefined refs 0 / dup labels 0 / dup includes ok / overlap ok（blocking=0 candidates=91）/ PASS |

### ⚠️ 无视觉能力声明（必须写在最前面）

本会话的模型**没有视觉能力**（`read_image` 只返回尺寸与 sha256、不返回像素；已在 DSH 源码层确认
`textOnlyImageText()` 路径）。因此：

- `TODO.md:33` 的「**最终 PDF 放大查看**」这一步**没有做、也做不到**，不声称已做；
- 替代做法是**三层可复算探针**：矢量图层（`tools/fig_probe_eis.py` 量弧线外接框、标记到曲线距离、
  文字块与曲线相交）、文字层（`build/r3/probe_ch90_bookmarks.py`、`build/r3/probe_lookup_tasks.py`）、
  书签与页码（`tools/pdf_probe.py`）；
- **仍需要一位有视觉的人**打开 `build/main.pdf` 复核：图 11-5 两条弧的观感、面板文字遮挡、
  后置三张表的断页位置与字号。这一步是外部依赖，本记录不代为声称。

## 1. 逐 ID 关闭记录

| ID | 级别 | 结论 | 改动位置 | 证据文件 |
|---|---|---|---|---|
| R3-C02 | P1 | 候选完成 | `chapters/parts/ch11-d.tex`（函数区、面板 a、图注、反推例题） | `build/r3/R3-C02C03U01.md`、`lead_model_eis.py/.txt`、`eis_fig_before/after.*` |
| R3-C03 | P1 | 候选完成 | 同上（Warburg 归一化导纳、六点、相角） | 同上 |
| R3-C01 | P2 | 候选完成 | `chapters/parts/ch06-a.tex:177–214` | `build/r3/R3-C01.md`、`build/chk_ch06-a_36476_cb5e26.pdf` |
| R3-C04 | P2 | 候选完成（父代理独立复算） | `chapters/parts/ch03-b.tex`（7 处，+180/−31） | `build/r3/R3-C04.md`、`lead_verify_ch03b.py/.txt` |
| R3-U01 | P2 | 候选完成 | `chapters/parts/ch11-d.tex`（轴域、标注位、面板字母、删图例） | `build/r3/R3-C02C03U01.md`、`tools/fig_probe_eis.py` |
| R3-U02 | P2 | 候选完成 | `chapters/ch90-backmatter.tex`（重排为「小节标题→说明→长表」） | `build/r3/R3-U02U03.md`、`build/r3/ch90_bookmarks.txt` |
| R3-U03 | P2 | 候选完成 | 同上（缩写表拆两列 + 四处主定义纠正） | `build/r3/R3-U02U03.md`、`build/r3/backmatter_abbrev_scan.json/.txt` |
| R3-W01 | P2 | 候选完成 | `tools/check_src.py`（`scan_tex_tables` / `classify_tex_tables`） | `build/r3/R3-W.md`、`build/r3/w01_case_*_lead.txt` |
| R3-W02 | P2 | 候选完成 | `tools/check_src.py`（`parse_review` 及汇总行） | `build/r3/R3-W.md`、`build/r3/w02_case_*_lead.txt` |
| R3-W03 | P2 | 候选完成 | `tools/pdf_probe.py` + 新增 `tools/pdf_required_bookmarks.txt` | `build/r3/R3-W.md`、`build/r3/fixtures/*` |

## 2. 接受条件逐条对照

### R3-C02（P1，CPE 幂次 + 相位单位）

- `dcpu` 由 `(\z*100*dq0)^n` 改为 `100*dq0*(dwn)^n`；`dcpb` 由 `n*π/2`（弧度）改为 `n*90`（度）。
- $n=1$ 退化：$Q=C_{\mathrm{dl}}$ 时与理想 RC 最大偏差 **8.9e−16 Ω**；$\sigma=0$ 退化 **1.4e−14 Ω**。
- $n=0.85$ 弧顶 **(60.000000, 39.416822) Ω @ 3183.0988 Hz**（评审值 (60, 39.4168)、f≈3183 Hz）。
- 高频截距 10 Ω（实测 4e4 Hz 得 10.629、8e4 Hz 得 10.158，收敛到 10）/ 低频截距 110 Ω。
- 逐点与复阻抗直算对照：六个频点坐标与评审表**逐位相同**（脚本 `build/r3/lead_model_eis.py`）。
- 「24 Ω / 9 µF」反推已重写为按直径 100 Ω、弧顶高 79 Ω 与 0.63 µF（差 21% / 27%）。
- 弧被轴窗裁切一事**在图注里明写**（$f=2$ Hz–79 kHz、$Z'\le62$ Ω）。

### R3-C03（P1，Warburg 支路与量纲）

- 图源改为归一化导纳形式，等价于
  $Z=10+[\,1/(100+40(1-\mathrm{j})/\sqrt\omega)+\mathrm{j}\omega(0.5\,\mu\mathrm{F})\,]^{-1}$。
- 六频点表：0.02 Hz (222.835, 112.840)、0.1 (160.458, 50.469)、32 (112.752, 3.882)、
  3200 (59.595, 50.138)、4e4 (10.629, 7.907)、8e4 (10.158, 3.973)。
- $\sigma=0$ 退化为理想 RC（1.4e−14 Ω）；低频扩散尾方向与斜率 1.00、高频截距 10.6 Ω 写进正文。
- **画出去的坐标**就是这些函数取值：探针 P2 量到标记到曲线距离 0.03 pt / 0.01 pt
  （改前 23.61 pt，方标记完全孤立）。

### R3-C01（P2，拉曼散射功率式）

- 改用 $P_{\mathrm{sc}}=E_0(\mathrm{d}\sigma/\mathrm{d}\Omega)\Delta\Omega\sin^2\theta$、
  $E_0=P_0/A_{\mathrm{beam}}$，比例式两端都无量纲。
- 四种情形齐备：ΔΩ 加倍⇒加倍；固定 ΔΩ 距离加倍⇒不变；固定接收面积距离加倍⇒≈1/4；
  $P_{\mathrm{sc}}/(P_0\Delta\Omega)$ 与 ΔΩ 无关。
- SI 单位逐项给出；适用范围（单散射体、$N$ 个相加、不含仪器效率）写明，
  并显式说明改前式子「右端只剩面积量纲」。

### R3-C04（P2，TG/DTG）

- 明确保留**一级 Arrhenius 计算**：$E=180.000$ kJ/mol、单一 $A=2.232221\times10^{13}$（每分钟口径）、
  $T_0=300$ K，四条曲线由速率方程积分给出。
- 峰温 659.611 / 673.000 / 686.927 / 701.424 K；$\alpha(T_p)=0.610542$；峰高 0.387 / 0.372 / 0.358 / 0.344。
- Kissinger 回算 $E=180.000$ kJ/mol（父代理独立 RK4 得 180.008、$R^2=0.99999997$）；
  「峰温＝半转化温度」的表述已删除（改为「走得最快 + α(Tp)≈0.61」）。
- 导数的中心差分与坐标一致（DTG 最大偏差 1.2e−5 %/K）；峰面积 19.998 个百分点（与 β 无关）。

### R3-U01（P2，图内标注）

- 条件说明块从框外 `axis cs:1,63` 移入可见区；轴域 0–60 → 0–62（标记落框内）。
- 面板 (b) 两处被裁的说明移入框内并收窄 `text width`；45°参考线不再穿文字。
- 补面板字母 (a)/(b)；图例（文字块压弧顶）改为面板内三行标注；未用全局 `clip=false`。
- 探针 P3：10 个文字块、**0 处压曲线**、字母齐（改前 3 处相交、缺 (a)(b)）。

### R3-U02（P2，后置索引）

- 三个正式小节各自紧跟自己的长表，书签从「全部停在 p.309」变为
  **缩写 309 / 主要符号 312 / 术语索引 313**（勘误节 315）；表首页 = 书签页。
- 三张长表续页表头在真实 PDF 上逐页命中（缩写 309–311、符号 312、术语 313–314）。
- p.309 的整页空白消除（章节标题 + 小节标题 + 表首页同页）。

### R3-U03（P2，主定义位置）

- 缩写表拆成「主定义位置」+「本书应用／交叉提及」，并给出两列口径。
- FTIR → **第 7 章**（真定义在 `chapters/parts/ch07-a.tex:98`），应用列 3/10/12；
- EXAFS / XAFS / XAS → **本书未系统介绍**，应用列给出实际出现的章
  （EXAFS 2/4/9/12；XAFS 跨方法综合应用+导读；XAS 跨方法综合应用）——三者在原声明章里出现次数为 **0**。
- 符号表、术语表的表头同步改为「主定义位置」。
- 三项真实查阅任务（程序化）：FTIR→第 7 章（该章 6 页提到 FTIR）、程序升温脱附→第 5 章（p.109/110）、
  吸附量→第 1 章（7 页命中）。

### R3-W01（P2，表格全量清点）

- 现按 `table/longtable`（含 `*`）逐环境清点，登记文件 + 起始行；label 只作属性。
- 父代理独立复跑 `build/r3/w01_run_cases.py`：无 label / 非 `tab:` 前缀 / 台账缺项 / 重复标签
  **四类反例全部 exit 1**，正向对照（新表 + 台账补行）**exit 0**（PASS 86）。
- 重复标签组还触发自检 `FAIL .tex 已检查表数 84 ≠ 台账已检查行数 85`；正常态
  `checked 85 tables: PASS 85`、exit 0。
- 已知边界：清点器只认 `table/longtable*`，自定义环境（如 `sidewaystable`）仍会漏；当前 85/85 未触发。

### R3-W02（P2，人工状态枚举）

- 枚举 未核对 / 待复核 / 已核对 / 不适用；只有「已核对」且带**页面 + 核验者 + 时间 + 结论**
  四类证据才计入完成；未知取值失败关闭（记「未识别」）。
- 父代理独立复跑五组输入：空白→未核对、待复核→待复核、`已核対`→未识别、
  有效已核对→已核对（汇总 已完成 1/84）、仅「已核对」无证据→**已核对（缺证据）**（汇总 已完成 0）。
- 决策记录：台账 `review_status` 列为**人工结论**，接入硬门禁会让现网 exit 0 变成 exit 1
  （即要求人工逐表核对页面图像），超出本轮 P2 范围，故**未接线**；本轮只保证「读得准、不虚报」。

### R3-W03（P2，PDF 检查覆盖）

- 新增外部给定清单 `tools/pdf_required_bookmarks.txt`（15 条：章 + 后置区块），
  **不从未测 PDF 反推**（否则删书签会连检查项一起消失）。
- 无检查对象时报告 UNUSABLE/FAIL，**新增退出码 2**；父代理独立复跑四组夹具：
  3 页零书签 → exit **2**、书签全删 → exit **2**、删 1 条必要书签 → exit **1**
  （缺「跨方法综合应用」）、无编号章 → exit **2**、正常 `build/main.pdf` → exit **0**。
- 接线注意（写给后来者）：`tools/build.ps1` 若接入 `pdf_probe.py`，必须判 `!= 0`，不能判 `== 1`。

## 3. 未做项 / 需要评审方决策

1. **R2-W01 旧凭据轮换**：需账户管理者确认，执行方无权；本记录不含任何凭据值。
2. **继承任务**：首轮 C09-01 覆盖矩阵、首轮 C05-02 TPD 生成器逐点复验、来源内容逐表核图 —— 未动。
3. **新发现（本轮未改，需决策）**：`chapters/ch00-intro.tex:69` 与 `:115` 把 XAFS 归到第 6 章（拉曼），
   与本次 R3-U03 的「本书未系统介绍」口径冲突。该文件不在本轮写入范围，故只报不改。
4. **有视觉者复核**：见上面的无视觉声明；`build/main.pdf` 的观感复核是外部依赖。
5. **`build/r3/` 下的详细回执不入库**（`build/` 被 gitignore）：`R3-C01.md` / `R3-C02C03U01.md` /
   `R3-U02U03.md` / `R3-W.md` / `R3-C04.md` 与全部探针输出都在本机 `build/r3/`；需要入库可另行搬运。
