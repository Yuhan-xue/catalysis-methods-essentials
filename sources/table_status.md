# 85 张表的核对状态台账（`sources/table_status.md`）

本文件由 `build/_tbl_status.py` 从磁盘可核验事实生成（脚本与输入均为只读），
用于逐表回答一个问题：**这张表的内容到底有没有对照过原页面图像？**
判定只认三类证据：`sources/table_pixel_verify.md` 的逐格读图段落、
分片文件内注明「已对照原页面图像」的就地 `\emph{核对说明}`、
以及题注/`\src` 自述「非源书表格」的改编声明。
**没有证据的表一律记「未核对页面图像」，不因结构门禁通过或 OCR 文本命中而升级。**

表总数 = 85（`env` 为 `table`/`longtable`；figure 行不计入）。

| 层级 | 含义 | 张数 |
| --- | --- | --- |
| T1 | 已逐格读图核对（`table_pixel_verify.md` 有结论） | 14 |
| T2 | 有就地核对说明且注明已对照原页面图像 | 8 |
| T3 | 改编补充（自述非源书表，不需要源表比对） | 12 |
| T4 | 未核对页面图像 | 51 |

> 口径说明：T2 只说明该分片就地留下了「已对照原页面图像」的说明，
> 不表示表内每一格都被逐格比对过；T1 才是逐格结论。

## 一、已逐格读图核对（14 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:physis-chemis` | `ch01-a.tex:27` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 2 | `tab:ch01c-methods` | `ch01-c.tex:193` | — | 改编补充 | sources/table_pixel_verify.md |
| 3 | `tab:extinction-ch02` | `ch02-a.tex:305` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 4 | `tab:ch03-three` | `ch03-a.tex:38` | — | 改编补充 | sources/table_pixel_verify.md |
| 5 | `tab:crystal-systems` | `ch04-a.tex:70` | — | 改编补充 | sources/table_pixel_verify.md |
| 6 | `tab:ch04b-multiplicity` | `ch04-b.tex:178` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 7 | `tab:ch04c-profile` | `ch04-c.tex:511` | — | 原书自身问题 | sources/table_pixel_verify.md |
| 8 | `tab:zeolite-ring` | `ch06-c.tex:376` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 9 | `tab:pyridine` | `ch06-c.tex:633` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 10 | `tab:ch07b-probes` | `ch07-b.tex:67` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 11 | `tab:ch07b-py` | `ch07-b.tex:716` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 12 | `tab:ch07c-formate` | `ch07-c.tex:682` | 505—507 | 已核对并修正 | sources/table_pixel_verify.md |
| 13 | `tab:ch10-reactor` | `ch10-c.tex:134` | — | 改编补充 | sources/table_pixel_verify.md |
| 14 | `tab:eis-d-elements` | `ch11-d.tex:229` | 860—861 | 已核对一致 | sources/table_pixel_verify.md |

## 二、就地核对说明，已对照原页面图像（8 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:ch04b-FOM` | `ch04-b.tex:896` | 268—269 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 2 | `tab:mo-lines` | `ch06-b.tex:469` | 384—385 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 3 | `tab:uv-apps` | `ch06-b.tex:668` | 384—385 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 4 | `tab:ch07c-probe` | `ch07-c.tex:235` | 494 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 5 | `tab:ch09-bg` | `ch09-d.tex:149` | 694—733 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 6 | `tab:ch09-so` | `ch09-d.tex:190` | 694—733 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 7 | `tab:ch10-diffmech` | `ch10-b.tex:463` | 773—774 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |
| 8 | `tab:ch10-transient` | `ch10-c.tex:976` | 799 | 已核对并修正/一致（就地核对说明） | 就地核对说明（已对照原页面图像） |

<details><summary>就地核对说明摘录</summary>

- `tab:ch04b-FOM`：\emph{核对说明}：已对照原页面图像（书内 p.268—269 / PDF p.287—288）。原书印「当不能指标化 的线条少于 2，且 $M_{20}\ge 10$ 时结果基本正确。$M_{20}<6$ 时结果值得怀疑，$M_{20}<3$ 时几乎没有 意义」；本表原印 $M_{20}>10$，取的是开区间，与原书不符，已按原文改为 $\ge$（$M_{20}=10$ 恰在 判据临界处，开闭区间会改变结论）。$F_{N}$ 判据原书印「$F_{N}$ 值越大，结果越可靠。很难说 $F_{N}$ 值多大就对应正确解，但多数正确解 $F_{N}$ 值在 10 以上」，与本表一致；原书另注 Smith 建议 $N$ 取 30、不足 30 则取全部衍射线数目，该细节已补入上文原则框。 \begin{pitfall} \textbf{指标化不唯一：品质因子必须与化学约束共同判定。}当两组解的
- `tab:mo-lines`：\emph{核对说明}：已对照原页面图像（书内 p.384—385 / PDF p.403—404）。SAPO-34 的五个谱峰原书 印作 1414、1616、1628、2822 与 \qty{2974}{cm^{-1}}：\qty{1414}{cm^{-1}} 为 \ce{CH3} 的变形振 动，1616 与 \qty{1628}{cm^{-1}} 为烯烃的 C=C 伸缩振动，2822 与 \qty{2974}{cm^{-1}} 为 C—H 键 的对称与反对称伸缩振动；图 6-26 的 SAPO-34 曲线亦标注 2822 与 2974。原书归属句把后者印作 \qty{2947}{cm^{-1}}，与同页峰列表及图 6-26 标注不一致，属\textbf{原书自身问题}，本分片按峰列表 与图注取 2974。ZSM-5 与 USY 的归属亦据同页改正：ZSM-5 的 1425 与 \qty
- `tab:uv-apps`：\emph{核对说明}：本表第一行「分子筛积炭」已对照原页面图像（书内 p.384—385 / PDF p.403—404）， 原书 SAPO-34 的谱峰为 1414、1616、1628、2822 与 \qty{2974}{cm^{-1}}，ZSM-5 为 1425 与 \qty{1615}{cm^{-1}}，USY 为 \qty{1604}{cm^{-1}}（聚芳烃的 C=C 伸缩振动）；本表原印 2947 与 「C—C 伸缩」均与原文不符，已改正。其余四行（低负载量 \ce{MoO3}/$\gamma$-\ce{Al2O3}、 X 型分子筛水热合成原位、杂原子分子筛、氧化物表面相变）据 §6.4.6.2—§6.4.6.5 （书内 p.386—402 / PDF p.405—421），\textbf{尚未逐行对照原页面图像}。 
- `tab:ch07c-probe`：\emph{核对说明}：已对照原页面图像，书内 p.494 / PDF p.513（图 7-83 及正文）。 \ce{Co/Al2O3} 线式 $2057$、桥式 $1788\;\mathrm{cm^{-1}}$（草稿原记「桥式带位 未辨」，已补），共吸附后 NO 为 $1857$ 与 $1791\;\mathrm{cm^{-1}}$（草稿原误 作 $1557$，已改）；\ce{Mo/Al2O3} 单独吸附线式 $2112\;\mathrm{cm^{-1}}$， 共吸附后移至 $2097\;\mathrm{cm^{-1}}$ 且强度无明显变化，NO 为 $1790$ 与 $1701\;\mathrm{cm^{-1}}$（草稿漏 $1701$，已补）——$2112$ 与 $2097$ 并非两个 互斥的源文本值，而是同一线式带的单吸附／共吸附位置，表中已改写； \ce{Co-Mo/Al2O3}
- `tab:ch09-bg`：\emph{核对说明}：已对照原页面图像（书内 p.712 / PDF p.203）核对「S 2p」一行：源文件表 9-37（硫元素在聚合物中 S 2p 结合能值）列出 PETH、PHMS、PPS、PES、PSS 五个聚合物，$\Delta$ 依次为 1.19、1.26、1.18、1.16、1.17 eV（平均 1.19），面积比 $I(2p_{3/2})/I(2p_{1/2})$ 依次为 1.84、1.91、1.90、1.84、2.04（平均 1.91），与表中数值一致，判定为已核对一致。其余各行（P 2p、Cl 2p、Ti 2p、Cu 2p、Ni 2p、Mo 3d、Pd 3d、Pt 4f、Au 4f）的分裂值与化学位移范围按通用文献量级给出：原书（书内 p.694—733）的表格均为 C 1s、O 1s、N 1s、S 2p 等结合能统计（表 9-30—表 9-37），未给上述其他芯能级
- `tab:ch09-so`：\emph{核对说明}：已对照原页面图像（书内 p.712 / PDF p.203）核对「S 2p」一行：源文件表 9-37（硫元素在聚合物中 S 2p 结合能值）列出 PETH、PHMS、PPS、PES、PSS 五个聚合物，$\Delta$ 依次为 1.19、1.26、1.18、1.16、1.17 eV（平均 1.19），面积比 $I(2p_{3/2})/I(2p_{1/2})$ 依次为 1.84、1.91、1.90、1.84、2.04（平均 1.91），与表中数值一致，判定为已核对一致。其余各行（P 2p、Cl 2p、Ti 2p、Cu 2p、Ni 2p、Mo 3d、Pd 3d、Pt 4f、Au 4f）的分裂值与化学位移范围按通用文献量级给出：原书（书内 p.694—733）的表格均为 C 1s、O 1s、N 1s、S 2p 等结合能统计（表 9-30—表 9-37），未给上述其他芯能级
- `tab:ch10-diffmech`：\emph{核对说明}：已对照原页面图像（书内 p.773 / PDF p.263）。原书印「在常温或低表面 覆盖度下，$D_s$ 的值在 $10^{-7}\sim10^{-5}$ m/s」——区间确为 $10^{-7}$—$10^{-5}$、指数为 负，本分片转写无误；但原书所印单位 m/s 与扩散系数的量纲不符（应为 \unit{m^2.s^{-1}}）， 属\textbf{原书自身问题}，表中按原书印法转写，未擅自改单位。 \textbf{简化假定与浓度分布。}为定量解析，先考虑单一反应物并假定 \src{S2 §10.4.2，书内 p.773 / PDF p.262}：①恒温；②扩散遵从 Fick 法则，可用一个恒定的 总包有效扩散系数表征；③反应不可逆、无分子数变化、可用简单速率方程描述；④系统处于 稳态（扩散最深部浓度梯度为零）。颗粒取两种几何：半径 $R$ 的圆球，厚度 $L
- `tab:ch10-transient`：\emph{核对说明}：已对照原页面图像（书内 p.799 / PDF p.288）。原书 §10.6.4 正文写「TAP 技术 能够用于真空脉冲-应答实验、程序升温脱附/反应实验及常压稳态和瞬态实验」，\textbf{未给}升温 速率范围，也未以能力列表的形式列出；本行的分钟级时间尺度与「随温度的转化序列」等信息 表述属按常规 TPSR 实践的归纳（\textbf{改编补充}）。 \\ 积炭失活 & 分钟—小时—天 & 活性系数随积炭量的衰减规律（线性／指数／双曲线型）；三段 尺度（活性位、颗粒、反应器）的失活模型 & 初始积炭覆盖速率 $r_{s0}$ 不能直接测，只能由 $r_C$ 换算；高积炭下的孔道堵塞须另行处理 \\ 多稳态与振荡 & 秒—分（振荡周期） & 同一操作条件下的多个定态与自持振荡；表面重构、 覆盖度变化等机理线索；强制周期操作可改变时均性能 & 用出口振荡周期反推

</details>

## 三、改编补充：自述非源书表（12 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:selector` | `chapters/ch00-intro.tex:49` | — | 改编补充 | 题注/\src 自述非源书表 |
| 2 | `tab:evidence-level` | `chapters/ch13-synthesis.tex:49` | — | 改编补充 | 题注/\src 自述非源书表 |
| 3 | `tab:matrix` | `chapters/ch13-synthesis.tex:81` | — | 改编补充 | 题注/\src 自述非源书表 |
| 4 | `tab:ch01c-density` | `ch01-c.tex:774` | — | 改编补充 | 题注/\src 自述非源书表 |
| 5 | `tab:ring-index` | `ch02-a.tex:499` | — | 改编补充 | 题注/\src 自述非源书表 |
| 6 | `tab:ch02b-smsi` | `ch02-b.tex:1042` | — | 改编补充 | 题注/\src 自述非源书表 |
| 7 | `tab:ch03b-hyphenated` | `ch03-b.tex:82` | — | 改编补充 | 题注/\src 自述非源书表 |
| 8 | `tab:extinction-ch04` | `ch04-a.tex:590` | — | 改编补充 | 题注/\src 自述非源书表 |
| 9 | `tab:ch04c-scherrer` | `ch04-c.tex:166` | — | 改编补充 | 题注/\src 自述非源书表 |
| 10 | `tab:ch09-problems` | `ch09-d.tex:292` | 705—708 | 改编补充 | 题注/\src 自述非源书表 |
| 11 | `tab:ch10-window` | `ch10-b.tex:148` | — | 改编补充 | 题注/\src 自述非源书表 |
| 12 | `tab:ch10-resid-diag` | `ch10-b.tex:232` | — | 改编补充 | 题注/\src 自述非源书表 |

## 四、未核对页面图像（51 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:isotherm-read` | `ch01-a.tex:103` | — | 未核对页面图像 | — |
| 2 | `tab:pore-class` | `ch01-b.tex:441` | — | 未核对页面图像 | — |
| 3 | `tab:ch01c-strength` | `ch01-c.tex:961` | — | 未核对页面图像 | — |
| 4 | `tab:tem-parts` | `ch02-a.tex:125` | — | 未核对页面图像 | — |
| 5 | `tab:pattern-read` | `ch02-a.tex:361` | — | 未核对页面图像 | — |
| 6 | `tab:contrast` | `ch02-a.tex:404` | — | 未核对页面图像 | — |
| 7 | `tab:ch02b-eds-eels` | `ch02-b.tex:429` | — | 未核对页面图像 | — |
| 8 | `tab:ch02b-bimetal` | `ch02-b.tex:985` | — | 未核对页面图像 | — |
| 9 | `tab:ch02c-pt` | `ch02-c.tex:309` | — | 未核对页面图像 | — |
| 10 | `tab:ch02c-newold` | `ch02-c.tex:366` | — | 未核对页面图像 | — |
| 11 | `tab:ch02c-situ` | `ch02-c.tex:385` | — | 未核对页面图像 | — |
| 12 | `tab:ch02c-gaps` | `ch02-c.tex:466` | — | 未核对页面图像 | — |
| 13 | `tab:ch03b-conditions` | `ch03-b.tex:474` | — | 未核对页面图像 | — |
| 14 | `tab:recip-simple` | `ch04-a.tex:343` | — | 未核对页面图像 | — |
| 15 | `tab:xrd-limits` | `ch04-a.tex:676` | — | 未核对页面图像 | — |
| 16 | `tab:ch04b-Qtable` | `ch04-b.tex:43` | — | 未核对页面图像 | — |
| 17 | `tab:ch04b-extinction` | `ch04-b.tex:424` | — | 未核对页面图像 | — |
| 18 | `tab:ch04b-quantmethods` | `ch04-b.tex:631` | — | 未核对页面图像 | — |
| 19 | `tab:ch04c-boundary` | `ch04-c.tex:364` | — | 未核对页面图像 | — |
| 20 | `tab:ch04c-fitmethods` | `ch04-c.tex:567` | — | 未核对页面图像 | — |
| 21 | `tab:ch04c-rfactor` | `ch04-c.tex:632` | — | 未核对页面图像 | — |
| 22 | `tab:ch05-tpd` | `ch05-a.tex:135` | — | 未核对页面图像 | — |
| 23 | `tab:ch05-redhead` | `ch05-a.tex:807` | — | 未核对页面图像 | — |
| 24 | `tab:ch05b-tpr-shift` | `ch05-b.tex:421` | — | 未核对页面图像 | — |
| 25 | `tab:raman-ir` | `ch06-a.tex:94` | — | 未核对页面图像 | — |
| 26 | `tab:fluor-suppress` | `ch06-a.tex:382` | — | 未核对页面图像 | — |
| 27 | `tab:raman-parts` | `ch06-a.tex:428` | — | 未核对页面图像 | — |
| 28 | `tab:insitu-window` | `ch06-b.tex:111` | — | 未核对页面图像 | — |
| 29 | `tab:raman-routes` | `ch06-b.tex:346` | — | 未核对页面图像 | — |
| 30 | `tab:raman-bands-c` | `ch06-c.tex:833` | — | 未核对页面图像 | — |
| 31 | `tab:modes` | `ch07-a.tex:132` | — | 未核对页面图像 | — |
| 32 | `tab:ch07c-criteria` | `ch07-c.tex:399` | — | 未核对页面图像 | — |
| 33 | `tab:narrow-map` | `ch08-a.tex:41` | — | 未核对页面图像 | — |
| 34 | `tab:nuclei` | `ch08-a.tex:314` | — | 未核对页面图像 | — |
| 35 | `tab:probes` | `ch08-b.tex:305` | — | 未核对页面图像 | — |
| 36 | `tab:c13-assign` | `ch08-c.tex:199` | — | 未核对页面图像 | — |
| 37 | `tab:nuclei-coke` | `ch08-c.tex:425` | — | 未核对页面图像 | — |
| 38 | `tab:xpsparts` | `ch09-a.tex:389` | — | 未核对页面图像 | — |
| 39 | `tab:satellite` | `ch09-b.tex:174` | — | 未核对页面图像 | — |
| 40 | `tab:ups-xps` | `ch09-c.tex:62` | — | 未核对页面图像 | — |
| 41 | `tab:surface-compare` | `ch09-c.tex:197` | — | 未核对页面图像 | — |
| 42 | `tab:power-vs-hyp` | `ch10-a.tex:765` | — | 未核对页面图像 | — |
| 43 | `tab:ch10-modelfam` | `ch10-b.tex:73` | — | 未核对页面图像 | — |
| 44 | `tab:ch10-criteria` | `ch10-b.tex:877` | — | 未核对页面图像 | — |
| 45 | `tab:methods` | `ch11-a.tex:945` | — | 未核对页面图像 | — |
| 46 | `tab:chrono-diagnostics` | `ch11-b.tex:199` | — | 未核对页面图像 | — |
| 47 | `tab:bulk-vs-kinetics` | `ch11-b.tex:498` | — | 未核对页面图像 | — |
| 48 | `tab:ch11c-insitu-methods` | `ch11-c.tex:179` | — | 未核对页面图像 | — |
| 49 | `tab:afm-modes` | `ch12-b.tex:223` | — | 未核对页面图像 | — |
| 50 | `tab:nano-three` | `ch12-c.tex:657` | — | 未核对页面图像 | — |
| 51 | `tab:nano-methods` | `ch12-c.tex:700` | — | 未核对页面图像 | — |

## 附：本台账不主张的东西

- 不主张 T4 的表「数据错误」——只主张**尚未读图**，对错未知。
- 不主张结构门禁（`tools/check_src.py`）或 OCR 文本层命中等于内容核对。
- T3 的改编表仍可能抄错正文数字，只是没有「源表」可逐格比对。

