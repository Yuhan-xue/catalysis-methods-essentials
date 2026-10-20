# 交接文档 · 《现代催化研究方法精要》

> 最后更新：2026-10-13（**逐式复核**推进并收口五片：`ch01-b` 式 (1-7)—(1-17) 共 11 式全部有判决、`ch07-a` 的
> Beer–Lambert 式判「改编补充」＋临界角式「已核对一致」、`ch10-b` 的 §10.3—§10.4 共 17 个编号公式逐一读图
> （并改正原书 (10-117) 的编号归属）、`ch01-c` 的 22 个编号公式逐一读图——查出并修正**甲类 A12**（平均粒径
> 通式原印矩次比，量纲不对且与自列的 $D[3,2]=\bar{D}(2)$ 冲突，按原书式 (1-51) 改正），并记**乙类 B12**；
> `ch03-a` 的 §3.1—§3.3 共 7 个编号公式逐一读图——5 式判「改编补充」（原书只逐条定义量、未印通式），
> 动力学方程 $\mathrm{d}\alpha/\mathrm{d}T=(1/\beta)k(T)f(\alpha)$ 逐字同形，并记**乙类 B13**（同页用 $W$ 与 $m$
> 两套质量记号、变量说明把 $\beta$ 写成「$\mathrm{d}T$ 为升温速率」）；
> 制品因 ch07-a 补入核对说明重建为 **339 页**（中后部
> 整体前移一页），逐页验收台账与内容机筛已按 339 页重算（PASS 256 / INFO 74 / WARN 9 / FLAG 0，CLEAN 331 /
> INFO 7 / WARN 1）；ch10-b 与 ch03-a 的补注只造成局部页内重排（第 246—264 页、第 69—105 页），页数与页序未再变，
> 且上一版第 104 页的空白带（158pt）随 ch03-a 重排消失，页内空白带由 10 处减为 8 处；
> 上一版 2026-10-12（内容级校对启动：机筛 13 类铺满文字层，读图 18 页，已修 7 处机筛看不见的问题——诊释→诠释、
> 上表指向、`\pedset/\supp` 重复印字、式 (1-9) 假等价、MP 量纲差 10⁴、GB/T 题名、压汞范围自校核）；
> 上一版 2026-10-11（逐页验收台账补齐三项文本层核对：书签落点 145/145、重复页 0、编号探针——340 页结构审计 + 340 页目视）；
> 上一版 2026-10-09（85 张表像素级核对收尾，`\tocheck` 全库清零）。本文是**新会话无缝接手**的浓缩版；
> 写作契约见 [STYLE_GUIDE.md](STYLE_GUIDE.md) / [WRITER_BRIEF.md](WRITER_BRIEF.md)，
> 历轮评审见 `reviews/`。

## 1 当前状态

| 项 | 值 |
|---|---|
| 成品 | 《现代催化研究方法精要：原理、读图与方法选择》 |
| 页数 | **339**（2026-10-13 为 `ch07-a` 补入核对说明后重建，中后部整体前移一页；已发布 v1.0.0 制品为 **340**，两套页码引用各自有效）。340 的来历：像素核对收尾后，2026-10-09；R5 315、R4 314、R3 315、R2 313、P0 310、基线 `74e4015` 309。相对 R5 的 +25 页全部来自 16 个批次为 85 张表就地补记的核对说明与表内修正，小字号 `\srcsize` 排版；release 门禁全 0、PASS。中途曾因 `\samepage` 惩罚参数泄漏涨到 345 页，见 §6） |
| 分片 | **37**（`chapters/parts/`） |
| 最新提交 | 见 `git log -1`（第六轮评审收口：修复 `b3fe3d5`、CLOSURE `8929cb6`（`v1.0.0` 标签所指）、合并远端评审工作区 `eaca20e`） |
| 线上正式版 | **v1.0.0**（release id=70，tag @ `8929cb6`；4233857 B，SHA-256 `A5969A14…8069C46`；340 页 / 145 书签；附件 id=105）——首个非 `-pre` 版本，`/releases/download/v1.0.0/…` 与 `/attachments/a4b543c2-9087-45ba-843b-f1c7f70686ad` 均 HTTP 200，下载件哈希与本地一致 |
| 上一版 pre | v0.6.5-pre（id=52 @ `5c1f080`；314 页 / 144 书签）、v0.6.4-pre（id=46 @ `9e6809c`）、v0.6.3-pre（id=44 @ `b457f93`） |
| 构建门禁 | errors / overfull>5pt / missing glyphs / undefined refs / dup labels / **dup includes** / **overlap** —— 全 0；`-Release` 下静态检查**没跑成（unavailable）判失败** |
| 叠印 | 图内元素确认相撞 **0**；候选 109（按类别报告，不按总数阻断） |
| 三项内容级验收（2026-10-21） | **①逐页内容级校对 339/339**（`sources/logs/page_p*.tsv`，状态：已读 287／已读并修正 52／待修正 0；`fixes_*.tsv` 87 条）＋ **②编号公式 372/372 终判**（一致 197／形式一致但符号不同 83／改编补充 74／原书自身问题 18）＋ **③T2 表逐单元格 34/59**（余 25 张，清单与逐格明细见 `sources/acceptance_report.md` 与 `sources/logs/cells_*.tsv`）。总闸门 `python tools/verify_acceptance.py`：pages/formulas 绿、tables 红（未完成就该是红）。方法、判决词表与逐项复跑命令见 **`sources/acceptance_report.md`**；表 ③ 的推进顺序与每批提交方式同该报告 §5 |
| 逐页验收 | **已建立台账**（2026-10-11）：`sources/page_acceptance.md`（2026-10-13 按 339 页制品重算） —— 339 页**逐页结构审计**（`tools/page_audit.py`：版心越界／孤悬标题／真叠印／缺字／页眉页码缺失／页尾留白／页内空白带／墨迹出界）＋ **339 页接触印相表目视复核**（`tools/pagesheet.py`：全书 17 批 × 20 页 40dpi 扫读，逐格看版面）；另两项不依赖读图的逐页核对：`tools/check_folio.py`（页脚连续无缺号、页眉 18 种无奇偶混用）、`tools/check_toc.py`（目录 61/61 页码落在标题实际页）；再加三项全书文本层核对：`tools/check_bookmarks.py`（145 个书签全部落在其标题所在页，3 条去掉前导编号后命中）、`tools/check_duppages.py`（339 页正文无空页，完全相同 0 组、近似重复 0 对）、`tools/check_numbers.py`（只认行首题注的探针；编号由 LaTeX 计数器生成、`chapters/` 无硬编码编号／无 `\tag`／无计数器重置，构造上连续，9 处 `UNSEEN` 是提取盲区不是跳号）。判定 PASS 256 / INFO 74 / WARN 9 / FLAG 0（p165 的墨迹出界按人工复核下调为 WARN，列入未关闭事项）。8 处页内空白带（25—61mm）由 `\raggedbottom`（`style/preamble.tex:388`）＋浮动体底部放置共同造成，**本轮刻意不改**：改浮动体会重排页码、作废已发布版本的页码引用。上一版的第 104 页空白带（158pt）已随 ch03-a 的页内重排消失（`gap_ct` 降到 20pt），说明它取决于浮动体落点。备注源文件 `sources/page_acceptance_notes.txt`，复跑 `python tools/page_acceptance.py`。**注意：结构审计≠内容校对**，全书版面已逐页看过，但看的是版面，不是内容 |
| 逐式复核 | **台账已建，已完成五片**（2026-10-13）：`sources/formula_review.md` —— 按公式逐条对照原书页面图像（`tools/vpage.py`；OCR 只用于定位，判决一律以图像为据，小字裁 300 dpi 复核），判决词汇沿用 `pixel_verify.md`。`ch01-b` 式 (1-7)—(1-17) 共 11 式全部有判决：式 (1-10)「改编补充」（源页只有定义式，无 Halsey 显式）、式 (1-9)(1-15)(1-16)「形式一致但符号不同」（式 (1-9) 源书用真实孔半径 $r_p$、本稿用孔宽 $D_p=2r_p$，源书内 p.45 / PDF p.64）、其余「已核对一致」（式 (1-13) 与源式 (1-39) 逐字同形，书内 p.53 / PDF p.72）。`ch07-a`：Beer–Lambert 式判「改编补充」——原书 §7.1 只印 $A+R+T=1$ 与 A/R/T 定义，随后直接进 §7.1.1，没有该式；同片临界角式判「已核对一致」（源书内 p.432 / PDF p.451 印 $\sin\theta_c=n_2/n_1$）。`ch10-b`（下册，书内 = PDF + 511）：§10.3—§10.4 的 17 个编号公式逐一读图（源书内 p.769—793 / PDF p.258—282）——已核对一致 11、形式一致但符号不同 4（`eq:ch10-jd` 的 $Sc$ 用运动黏度 $\nu/D$ 而本稿写 $\mu/(\rho D)$、三个判据式原书用未声明基准的 $r$）、已核对并修正 1（原书 $v_d$ 分子带负号）、改编补充 1（`eq:ch10-basis` 速率基准声明原书未印）；同时改正原书 (10-117) 的编号归属（该号是 $\eta$ 的**文字定义**，两条显式 $\eta$ 公式在其后未编号），并注明 `ch10-c` 的 $\rho$ 与 `ch10-b` 的 $\rho_p$ 指同一个量。`ch01-c`（§1.2.2—§1.2.5）22 个编号公式逐一读图（书内 p.63—79 / PDF p.82—98）——已核对一致 13、形式一致但符号不同 4（`eq:ch01c-stokes`/`centrif` 原书印反解形式、`eq:ch01c-betd` 原书印形状因子 $\phi$ 而本稿代入 6、`eq:ch01c-poros` 原书用 $\theta$）、改编补充 4（$D[3,2]=\bar{D}(2)$ 的关系式、体积形式 $D[3,2]$、次序不等式、比孔容式）、已核对并修正 1（`eq:ch01c-dn`，甲类 A12：本稿原把平均粒径通式印成矩次比 $\int x^{n}f/\int f$，量纲不对且与自列的 $D[3,2]=\bar{D}(2)$ 冲突，按原书式 (1-51) $\bar{x}(n)=\int q(x,n)x/\int q(x,n)$ 改正，并补一段 (1-51)—(1-53) 的对照与量纲提醒）；同片记乙类 B12（原书把 Stokes–Einstein 式里的 $R$ 印成「颗粒粒径」）。`ch03-a`（§3.1 热重、§3.2 差热与量热、§3.3 动力学）7 个编号公式逐一读图（书内 p.169—181 / PDF p.188—200）——改编补充 5（原书只逐条定义 $\Delta m$、$\mathrm{d}m/\mathrm{d}t$、$T_{\mathrm{i}}$、$T_{\mathrm{p}}$ 与 DTA 曲线要素、$\mathrm{d}H/\mathrm{d}t=f(T)$，**未印**转化率通式、DTA/DSC 换算式、Arrhenius 形式 $k(T)$ 与 $g(\alpha)$ 积分式；同页只给 Ozawa–Flynn–Wall、Kissinger、Freeman–Carroll 三法）、已核对一致 1（$\mathrm{d}\alpha/\mathrm{d}T=(1/\beta)k(T)f(\alpha)$ 右半逐字同形，书内 p.180 / PDF p.199）、形式一致但符号不同 1（`eq:ch03-mtdsc`：原书印 $\mathrm{d}H/\mathrm{d}t=C_p\,\mathrm{d}T/\mathrm{d}t+f(T,t)$，本稿记 $\mathrm{d}Q/\mathrm{d}t$）；同片把 §3.1「曲线上可直接读出的量」由三个补成四个（原书同段还定义 DTG 峰温 $T_{\mathrm{p}}$），并记乙类 B13（原书同页用 $W$ 与 $m$ 两套质量记号；§3.3 变量说明把 $\beta$ 写成「$\mathrm{d}T$ 为升温速率」）。全书 14 处自述「未对照原页面图像／按 OCR 重建」的分片已列成清单（`ch06-a`、`ch09-b`、`ch08-c`、`ch11-a`、`ch11-d` 等；`ch10-b`、`ch07-a`、`ch01-c`、`ch03-a` 已关闭），是后续批次线索 |
| 源头 | 《现代催化研究方法新编》上、下册扫描 PDF（附件，不在仓库） |
| 内容校对 | **机筛铺满 + 读图进行中**（2026-10-13 按 339 页制品重算）：`tools/content_scan.py` 逐页读 `build/main.pdf` 文字层报 13 类可疑点，339 页 CLEAN 331 / INFO 7 / WARN 1；8 个命中页（p115、p155、p235、p256、p281、p293、p322、p338）已逐条文字层判读（全是词边界巧合或数学符号）。逐页读图 **18/339 页**（第 1—17 页＋第 20 页，`tools/vbook.py` 165 dpi 整页），流程为读图 → 对照源书核数 → 改源码 → 重建 → 读图复核 → 更新台账 → 提交；已修 7 处：诊释→诠释（`errata.md` A10）、「上表」指向相反、`\pedset/\supp` 重复印字、式 (1-9) 假等价（乙类 B11）、MP 量纲差 10⁴（甲类 A11）、GB/T 21650 题名、压汞可测范围自校核。台账 `sources/content_review.md`（由 `tools/content_review.py` 从 `build/content_scan.csv` ＋ `sources/content_review_notes.txt` 生成，勿手改 md；源码基线固定在 notes 的 `baseline_commit=7cbab68`，不随提交漂移），复跑 `python tools/content_scan.py && python tools/content_review.py`。**机筛 `CLEAN` ≠ 那页没有错**：两个合法字的错别字（戌／戊、己／已、末／未、「诊释／诠释」）、数字错一位、公式推导错、图表数值与原书不符，文字层里都是「正常字符」，机筛一个都看不见 |

**R4 收口要点**（逐项证据见 `reviews/2026-09-30-round4/CLOSURE.md`）：
8 项 P2 全部处理（拉曼角度因子、CPE 有效电容、Warburg 定量、DTG 峰高、图 11-5 避线、缩写表列宽、
图形探针路径级分类、TG 生成器入库）；继承队列补写 §8.5 原位 MAS NMR、建第 8/9 章覆盖矩阵、
导读 XAFS 归属、C05-02 逐点复验、85 表 OCR 文本层核对、原书节覆盖映射。

**R5 收口要点**（逐项证据见 `reviews/2026-10-01-round5/CLOSURE.md`）：6 项全部处理
（TPD 单位自洽 + 图注重算 + 图例/倍率 + 坐标再生、§8.5 标题不孤悬、原位 NMR 归属/定量分家、²H）。
新增探针 `tools/fig_probe_tpd.py`、`tools/check_heading_orphan.py`、`tools/check_cp_quant_demo.py`；
`gen_tpd_table.py` 增 `--verify`（秒/分双解 + 闭式 + 解析峰温 + 守恒）与 `--patch`（回写整块 tikz）。

**2026-10-02 安全清理**（R2-W01）：历史明文口令已处理——`deepseek` 已轮换（旧值 API 401，新值存 `~/.netrc`）；
`yuhanxue` 的轮换已应账号所有者要求**恢复为原值**（该值曾泄露，风险由所有者承担；当前值在仓库外受限文件）。
历史已用 `git filter-repo` 清理并强推，`main`（旧 `f94789c` → 新 `00ef814`）与 `v0.6.0-pre`…`v0.6.5-pre` 六个 tag 的哈希已变，
12 个 release 元数据已同步。2026-10-02 之前的文档哈希请用 `reviews/2026-10-02-history-cleanup/commit-map.txt` 换算；
残余风险（服务端 `git gc --prune=now` 待管理员执行、其他克隆需重同步）见同目录 README。
工具侧同因：`tools/check_src.py` 的默认基线 ref 也随重写失效（`feb8739` → `74e4015`，见 `commit-map.txt` 末行），
已重新固定；并新增「ref 不可解析时立即显式报错退出 1」，不再退化成八十余条误报 FAIL。

## 2 立刻能跑的命令

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release   # 发布验收
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/check_chapter.ps1 -Chap ch11-d
python tools/check_includes.py                                           # 重复 \input（门禁）
python tools/check_src.py                                                # 85 表来源标注
python tools/check_table_content.py                                      # 85 表来源内容（OCR 文本层）
python tools/build_coverage_map.py                                       # 原书节覆盖落点
python tools/check_terms.py                                              # 术语一致性
python tools/overlap_check.py --gate --pdf build/main.pdf                # 版面重叠门禁
python tools/pdf_probe.py --pdf build/main.pdf                           # 书签落页/后置页眉/必要书签
python tools/fig_probe_eis.py --pdf build/main.pdf ; python tools/fig_probe_eis.py --selftest
python tools/fig_probe_tpd.py --pdf build/main.pdf ; python tools/fig_probe_tpd.py --selftest
python tools/check_heading_orphan.py --pdf build/main.pdf                # §8.5 标题不孤悬
python tools/check_cp_quant_demo.py                                      # CP 强度≠产率反例
python tools/recompute_ch03b_dtg.py ; python tools/gen_tpd_table.py --check
python tools/gen_tpd_table.py --verify                                   # TPD 单位/闭式/守恒
python tools/cmp_release_pdf.py build\main.pdf <线上附件.pdf>             # 内容级比对（忽略 /ID 与 /CreationDate）
```

## 3 环境事实（不要重新摸索）

| 项 | 值 |
|---|---|
| TeX | TeX Live 2026（`C:\texlive\2026\bin\windows\`，`build.ps1` 动态解析，勿硬编码）；**XeLaTeX**（ctexart + fandol），latexmk 驱动 |
| Python | 3.14，含 pymupdf / Pillow / numpy / scipy / fontTools |
| Shell | Windows PowerShell（控制台 GBK） |
| 仓库 | Gitea 私有：`http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials`（main） |
| 认证 | **不要把口令写进仓库**：用**仓库外** `~/.netrc`（收紧 ACL），git 与 curl 都读它；remote URL 不嵌凭据 |

**图像通道（2026-10-02 打通，别再把「看不到图」当既成事实）**：`read_image` 到底能不能看到像素，取决于
profile `~/.dsh/profiles/desktop/cordis.patch.yml` 里三个 provider 的 `api:` ——必须是 **`openai-completions`**。
pi-ai 的 responses 适配器把「工具结果里的图」塞进 `function_call_output.output`，本地网关
`https://api.llm.ustc.edu.cn` 会**静默丢弃**该位置的 `input_image`；completions 适配器改成把图放进一条
后随 user 消息（`Attached image(s) from tool result:`），网关正常处理。受控实测（脚本在 `build/vision_selftest/`，
`build/` 不入库）：同一张图塞 `function_call_output` → 答错、`input_tokens` 偏少（367 < 581）；放进 user
消息 → 答对。该配置**按请求热读**，改完不必重启。
**自检**：`read_image` 若只回 `Image "…" (sha256:…); request preview WxHpx.` 而看不到内容 ⇒ 通道断了，
**不要声称核对过**；通道可用时用 `python tools/vpage.py up|down <页> <out.png> [--top/--bottom/--left/--right]`
渲染**原书页面**逐式核对。

**四条会反复咬人的陷阱**：
1. **中文不要经控制台管道**：`python -c` 打印中文或 `| Out-File` 会抛 `UnicodeEncodeError` 并中断，使后续写文件**根本没执行**。一律「写脚本文件 → 结果写 UTF-8 文件 → 再读」。
2. **构建产物字节哈希每次都变**（PDF 含 `/CreationDate` 与 `/ID`）；比内容请比文本层/页数/书签。
3. **缺字静默丢**：Fandol 无字形时 TeX 不报错、字符消失——已把缺字数设为构建失败条件。
4. **临时探针脚本不要把「输出路径」放在 argv 里**：`build/_folio.py` 早先按 `argv[1]=out, argv[2]=pdf` 取参，而运行器 `build/_runutf8.py` 只把 PDF 当 `argv[1]` 传进去，结果脚本把**自己的报告**写进了 `build/main.pdf`（一个 340 页、4.2 MB 的制品被覆盖成 998 字节）。现在探针一律「只从 argv 取输入，结果走 stdout」，由 `_runutf8.py` 落盘；万一 `build/main.pdf` 再被写坏，用 `build/_dl_final.pdf`（与已发布 v1.0.0 制品同哈希 `A5969A14…069C46`）拷回即可。

## 4 版式与写作契约（摘要）

- **单栏**、A4、10 pt、`twoside`，版心 **165 mm**；`\onecolwidth`≈132 mm、`\twocolwidth`≈158 mm。
- **禁用** `figure*` / `table*`；长表用 `longtable` + 定宽 `p{}`，放单栏整页（`\widepageson/off`，表宽 `\textwidth`）。
- 一个分片 = 2 个 `\subsection` + 若干 `\subsubsection`，**六环节**各至少一处
  （`probout/principle/measure/dataflow/pitfall/crosscheck`）；至少一个读图实例，`obs` 与 `infer` 严格分开。

### 页码映射（已验证，别套固定偏移）

- **上册**：`书内 = PDF − 19`，恒定，无缺页。
- **下册**：`书内 = PDF + off`，**8 段**，段边界在 PDF 页 **18 / 19 / 60 / 225 / 226 / 297 / 372 / 373**，`off ∈ {507…514}`；**逐端点用它自己所在段的偏移**换算（曾查出 3 处误用）。
- **7 个印刷页不在 PDF 中**：526、568、734、736、808、884、886。
- **页码一律以 `sources/parts/*.txt` 的页标记 `[[UP/DOWN PDF p.n | 书内 p.m]]` 为准**（标记 = 该印刷页内容的起点），**不要用偏移反推**。下册章首页/附录首页带**假书眉**。
- 台账 `sources/figure_table_list.csv` 由 `tools/build_figlist.py` 从 .tex 派生，**不要手改**。

### 来源标注约定

- `\src{}` **写在 `\caption{}` 内部末尾**；每张图表都能追溯到原书或明确声明「非源书」。
- 三个模板：A 照原书某表（`\src{据 S1 表 6-1，书内 p.364 / PDF p.383。}`）、B 据正文归纳、C 本改编本自造（必须明说）。
- `\tocheck{}` 只写「待核对」，**不写「已核对」**；核对证据四要素（页面/核验者/时间/结论）见 `check_src.py` 口径。

## 5 未完成事项

- ✅ P0：85 张表来源标注（`check_src.py` 全 PASS）。
- ✅ 工程门禁：dup includes、overlap gate、静态检查三态、发布入口均接入 `build.ps1 -Release`。
- ✅ **公式逐式核对原页面图像**：**八个分片已逐条读图核对**（ch01-b、ch02-a、ch04-a、ch07-a、ch08-c §8.5、ch09-a、ch10-a、ch12-a），台账 `sources/pixel_verify.md`（96 张页面图像 + SHA-256 清单 `build/verify/pages_sha256.txt`）；**全库 `\tocheck` 已全部核销，`chapters/` 下出现次数为 0**（核销记录见 `chapters/ch90-backmatter.tex`）。
- ✅ **85 张表像素级核图（2026-10-09 收尾）**：OCR 文本层交叉核对见 `sources/table_content_check.md`（R5 复跑为 13 FOUND / 1 INDEX_OK / 54 NO_TABLE_NO / 17 NON_SOURCE，**不是通过率**）。**14 张有真实来源编号的表已逐格像素核对完毕**，报告 `sources/table_pixel_verify.md`（13 条记录 / 14 张表：表 1-1、1-10、2-1、3-1、4-2、4-7、4-8、6-1、6-3、7-12（两处）、7-19＋7-20、10-3、11-1；裁决分布：已核对一致 1、已核对并修正 10、改编补充 2），据此修正 11 个分片；其中「电泳法」整行缺失、表 6-1 列序错位、表 6-3 漏行、表 4-8 缺两行、表 3-1 来源标注张冠李戴等为实质错误。**其余约 71 张（54 NO_TABLE_NO + 17 NON_SOURCE，即据正文归纳或非源表）**原未做像素核对，现已于 2026-10-09 收尾：85 张表逐表就地补记核对说明（16 个批次，每批两张），逐表状态见 `sources/table_status.md` —— 14 张逐格读图 + 59 张就地说明（含「已对照原页面图像」）+ 12 张改编补充，**「未核对页面图像」一栏已清空（T4=0）**。须注意台账自身的限定：59 张「就地说明」中多数为**部分覆盖**，说明内逐条写明已读页与未逐页核对的页，**不主张每一格都比对过**；`sources/figure_table_list.csv` 的 `review_status` 列由 `tools/build_figlist.py` 无条件写「未核对页面图像」，不随读图结论改动。
- ✅ **§8.5 三类装置的转速/温度/压力**：`chapters/parts/ch08-c.tex` 的 `\tocheck` 已删（读图核对 `down042_250.png`／`down043_250.png` = 书内 p.550—551）；另把「常压下可升温到」改为原书的「正常流动压力下可升温至 423 K、转速达 3 kHz」。§8.5.2 读图实例仍未通读，见台账第五节。
- ✅ **旧凭据处理与历史清理**：R2-W01（2026-10-02）——`deepseek` 旧口令失效；`yuhanxue` 口令按所有者要求恢复原值；历史重写并强推、release 元数据同步；
  记录与映射表见 `reviews/2026-10-02-history-cleanup/`；服务端对象库彻底 prune 仍待管理员执行。
- ✅ 覆盖映射：`sources/coverage_map.md`（二级节 79/81，未映射的 2 个为「结束语」）、`ch08_coverage_note.md`、`ch09_coverage_matrix.md`。

## 6 已知坑（高频项；完整版见 STYLE_GUIDE / WRITER_BRIEF）

**静默失败类**（不报错，最难查）：

| 坑 | 表现 | 规避 |
|---|---|---|
| `\underbrace` | 本字体缺横向花括号 → 退化成粗黑条，文字层完全正常 | 全书已无；勿用 |
| `\ce{Mo=O}` | 渲染成两个连字符 | 写 `\ce{Mo{=}O}`；箭头 `<=>` 里的等号不动 |
| 缺字 | ①–⑤、Ⅰ Ⅱ Ⅲ、µ 等静默丢字 | 用字面 `°` / `µm`；缺字数已设为构建失败条件 |
| 重复 `\input` | 正文重复排页，六项门禁全报 0 | `tools/check_includes.py` |
| `\dimexpr` 派生列宽 | `Illegal unit of measure` | 用固定 mm 或纯 `X` |
| `\sloppy` | 把 `\emergencystretch` 重置为更小值 | 每个 `\sloppy` 后重设 10em |

**几何类**：`minimum width` 只是最小值；`below left=… of <父>` 定位节点角点（多子节点请写显式坐标）；
承载长文字的 node 必须给 `text width`；pgfplots 的 `width/height` 含轴标签与刻度（别再额外加）；
`\addplot {fn(\p)}` 要写 `{fn(x)}`；`legend pos=outer north east` 会把图撑出栏宽。

**方法类**：修「全局布局」前先量页数与每页字数；探针必须先在**已知有缺陷的基线**上复现缺陷才算有灵敏度；
子代理/工具的结论要独立复核（本项目多次出现「声称做了实际没做」「观测对、归因错」）；
删短语前先 grep 全书；写原子化（先落骨架再读源文件）。

**宿主环境类**：同机其它项目可能起失控进程——曾遇 `mechanics-textbook` 的
`verify_symbolic_all.py` 把 `glob('verify_symbolic_*.py')` 里的自己再当子进程运行，无限自派生
7472 个 `python.exe` 占 17.5 GB；表现为 `xdvipdfmx: Out of memory`、`latexmk exit 12`、
overlap 门禁 UNUSABLE。**先查可用内存与 python.exe 进程数再重跑构建，不要改源码**；
结束失控树要按根 PID 取其后代集合（`taskkill /T` 在数千层深的链上会超时）。

**TPD 图（图 5-1）参数纪律**：`beta` 一律 K/min、`A` 一律 s⁻¹（当前 7.35e8 s⁻¹ = 4.40706e10 min⁻¹，
由 Tp=570.000 K 解析峰温条件标定）；改参数后跑 `python tools/gen_tpd_table.py --patch` 回写整块
`tikzpicture`，再跑 `--check`、`--verify`（含图注数字一致性）与 `fig_probe_tpd.py`。
图例是**每面板一列纵排**、`scaled y ticks=false`（只保留 ylabel 的 10⁻³ K⁻¹）——别再改回并排。

## 7 发布流程（已实测）

```powershell
git status --short                       # 必须干净
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release
New-Item -ItemType Directory -Force -Path release | Out-Null
Copy-Item build\main.pdf release\catalysis-methods-essentials-vX.Y.Z-pre.pdf
(Get-FileHash release\catalysis-methods-essentials-vX.Y.Z-pre.pdf -Algorithm SHA256).Hash
git tag vX.Y.Z-pre <提交> ; git push origin vX.Y.Z-pre
# 建 release（UTF-8 JSON 用 --data-binary；curl 用 --netrc-file）
curl.exe -s --netrc-file "$HOME\.netrc" -H "Content-Type: application/json" --data-binary "@build/_relpayload.json" -X POST "http://zsyq.hxlab.tech:3000/api/v1/repos/yuhanxue/catalysis-methods-essentials/releases"
# 上传附件（PS 5.1 无 -Form，必须 curl -F；字段名 attachment）
curl.exe -s --netrc-file "$HOME\.netrc" -F "attachment=@release/<pdf>" "http://zsyq.hxlab.tech:3000/api/v1/repos/yuhanxue/catalysis-methods-essentials/releases/<id>/assets?name=<pdf>"
# 回验：从公开地址下载回来比哈希（不验等于没发）
curl.exe -sL "http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/releases/download/vX.Y.Z-pre/<pdf>" -o build\_dl.pdf
```

**易踩**：① `git status` 不干净时发布的 PDF 可能来自未提交内容；② release notes 的 SHA-256 与「对应提交」
必须实测填入；③ 先打 tag 再建 release（标签已存在时 `target_commitish` 被忽略）；④ 附件建好后
`/releases/download/<tag>/<name>` 与 `/attachments/<uuid>` 两条地址都要能 200。

## 8 接手顺序与台账索引

1. 读本文 + STYLE_GUIDE/WRITER_BRIEF；2. 跑 `build.ps1 -Release` 与 §2 探针确认基线；
3. 从 §5 未完成项中挑可做项（**先查「这件事是不是已经做完了」**）；每改一处说明改前/改后实测值。

| 文件 | 内容 |
|---|---|
| `sources/parts/*.txt` | 分片源文本（带页标记） |
| `sources/coverage.csv`、`coverage_map.md` | 原书节覆盖与引用落点 |
| `sources/page_map_{up,down}.csv`、`page_map.md` | PDF 页 ↔ 书内页映射 |
| `sources/figure_table_list.csv` | 图表来源台账（派生，勿手改） |
| `sources/formula_verify.md`、`pixel_verify.md`、`table_pixel_verify.md`、`errata.md`、`terminology_decisions.md` | 公式核对／**像素级核对台账（逐条：源页／PNG／逐字印法／判决）**／**真实来源表像素级核对台账（14 张表）**／勘误／术语裁定 |
| `sources/ch08_coverage_note.md`、`ch09_coverage_matrix.md`、`table_content_check.md` | 各章覆盖与表内容核对 |
| `sources/page_acceptance.md`、`content_review.md`、`formula_review.md` | 逐页**版面**验收（结构审计＋目视）／逐页**内容**机筛与读图进度（生成物，勿手改）／**逐式复核**（按公式逐条对照原书页面图像） |
| `sources/assignments.md` | 分片派单与「科学核验状态」 |
| `reviews/*/` | 历轮评审（TODO / CLOSURE / findings / 复核脚本） |
