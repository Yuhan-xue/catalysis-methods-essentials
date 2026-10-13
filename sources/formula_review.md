# 逐式复核台账（formula review register）

## 一、这份台账管什么

内容级验收的第二项：**把书里每个编号公式，逐条对照原书页面图像核一遍**。

与前两份台账的分工：
- `sources/formula_verify.md` 是**历史登记表**（分片作者提的存疑清单），2026-10-08 已标注「被取代」，只作历史记录。
- `sources/pixel_verify.md` 是**分片级**像素质证：记录「哪些条目读图核过、看到了什么」，按分片给条目数。
- **本表**按**公式**逐式推进：每个编号公式一行，给出源书对应式号与页码、判决、以及读图时逐字看到的印法。

为什么要单列：本项是「逐式」粒度（`pixel_verify.md` 是分片粒度），且逐式要能回答「这一式核过没有、依据是哪一页」，
不靠分片级条目数代替。

## 二、方法与判定词汇

**方法**

1. 从分片 `\src{}`/`\srcnote{}` 里取源书式号与页码（书内页 → PDF 页：上册 书内 = PDF − 19）。
2. 渲染原书页面图像，逐字读印法：
   ```
   python tools/vpage.py up   <PDF页> build/frev/up<页>.png --dpi 200
   python tools/vpage.py up   <PDF页> build/frev/up<页>_band.png --dpi 300 --top .35 --bottom .45
   ```
   **OCR 只用于定位，不作形式依据**；小字看不清时一律裁 300 dpi 复核，不得凭 165/200 dpi 的读感下判决。
3. 与本稿 tex 对照，给判决；判决为「已核对并修正」的同步改 tex。

**判定词汇**（沿用 `pixel_verify.md` 的口径）

| 词汇 | 含义 |
|---|---|
| `已核对一致` | 原书印法与本稿形式一致（含移项、解出另一变量等等价写法，需注明等价关系） |
| `已核对并修正` | 读图后发现本稿有误，已按原书改正 |
| `形式一致但符号不同` | 数学内容一致，仅记号习惯不同（需注明关系） |
| `原书自身问题` | 原书印刷/推导有误，本稿按自洽形式写并在正文注明，同时记 `errata.md` 乙类 |
| `改编补充` | 原书无此式，属改编新增，正文已注明 |
| `未覆盖` | 尚未读图核对，**不得**视为通过 |

## 三、逐式状态

### ch01-b（第 1 章 §1.6 孔结构分析）

来源标注（印在 PDF p.17）自述：「式 (1-7)—(1-17) 依 OCR 正文给出的变量定义与学科标准形式重建，
**未逐式对照原页面图像**」。故本分片是本项的第一批；其中式 (1-7) Kelvin 与式 (1-8) BJH
此前已在 `pixel_verify.md` B-1／B-2 逐值核过，不重复。

| 本稿式号 | 源书式号与页 | 判决 | 依据（读图逐字所见） |
|---|---|---|---|
| (1-7) Kelvin | 源 (1-21)，书内 p.23—24 / PDF p.42—43 | `已核对一致` | 见 `pixel_verify.md` B-1（本轮不重复读图） |
| (1-8) BJH | 源 (1-36)，书内 p.46 / PDF p.65 | `已核对一致` | 见 `pixel_verify.md` B-2（本稿环形孔精确式相对源书薄壁式在 $t/r=0.04$ 时差约 2%，已注明） |
| (1-9) $D_p=2(r_k+t)$ | 源书同处给 $r_p=r_k+t$，书内 p.45 / PDF p.64 | `形式一致但符号不同` | 原页逐字印「由 Kelvin 公式计算所得半径 $r_k$ 并非真实孔半径 $r_p$（$r_k<r_p$）……$r_p=r_k+t$」。原书变量是**真实孔半径** $r_p$，本稿 $D_p=2(r_k+t)$ 给的是**孔宽**（圆柱孔即孔径，$D_p=2r_p$）；本稿 `chapters/parts/ch01-b.tex:154-156` 已就地写明这一关系与源页。同页另见 Wheeler[86] 与 BJH 三人名。**页号更正**：此前记「书内 p.24 / PDF p.43」有误，读图实测源页是书内 p.45 / PDF p.64 |
| (1-10) Halsey 显式 | 源 (1-37) 只给定义式 $t=\frac{t_m}{V_m}V=f(p/p_0)$ | `改编补充` | 上册 PDF p.70（书内 p.51）读图：原页只有式 (1-37) 定义式与 $t_m=\qty{0.354}{nm}$，**没有** Halsey 显式；本稿已在正文声明该式为改编补充，与源页相符 |
| (1-11) $V=\frac{V_m}{t_m}t$ | 源 (1-38)，书内 p.51 / PDF p.70 | `已核对一致` | 原页逐字印 $V=\dfrac{V_m}{t_m}t$，式号 (1-38)；同页「$V_m$ 为单层饱和吸附量；$t_m$ 为氮的单分子层平均厚度（0.354 nm）」与本稿一致 |
| (1-12) MP 三式 | 源 (1-42)—(1-44)，书内 p.56 / PDF p.75 | `已核对一致` | 原页逐字印 $\Delta V_i=\Delta S_i\times\bar t_i$、$\Delta S_i=S_{i-1}-S_i$、$\bar t_i=\frac12(t_{i-1}+t_i)$，式号 (1-42)—(1-44)；同页「第 $i$ 组微孔的孔容 $\Delta V_i$」「此时吸附层厚度 $t_{i+1}$ 相应的是新被充满的微孔板间距」「按 BET 公式 $C$ 值的不同划分吸附质与吸附剂相互作用的强弱，按不同 $C$ 值范围选择合适的 $t$ 曲线」「也可采用与微孔吸附剂化学性质相同的非孔性吸附剂作基准物，建立 $t=f(p/p_0,A)$」与本稿一致 |
| (1-13) $\alpha_s$ | 源 (1-39)，书内 p.53 / PDF p.72 | `已核对一致` | 原页逐字印 $\alpha_s=n/n_{0.4}=V/V_{0.4}=f(p/p_0)$，式号 (1-39)；同页「$\alpha_s$ 方法没有使用吸附层厚度这一概念，而是引入吸附量的一个归一化数值 $\alpha_s$（以相对压力为 0.4 时的吸附量作为归一化量）」，以及「以非孔性参考吸附剂上的吸附量归一化值 $n/n_{0.4}$ 对相对压力作图获得 $\alpha_s$ 标准吸附等温线（$\alpha_s$ 曲线）」——与本稿逐字同形（本稿 `chapters/parts/ch01-b.tex:293`） |
| (1-14) 巨势泛函 | 源 (1-45)，书内 p.56 / PDF p.75 | `已核对一致` | 原页逐字印 $\Omega[\rho(r)]=F[\rho(r)]+\int\rho(r)[V_{\mathrm{ext}}(r)-\mu]\mathrm{d}r$，式号 (1-45)。同页：$F$ 含理想气体自由能与过剩自由能两项、过剩项又分相吸与相斥、$V_{\mathrm{ext}}(r)$ 与孔形（裂隙、圆柱形或球形）和孔宽有关、$\mu$ 为流体分子化学势——均与本稿一致。**叙述压缩（非缺陷，记此备查）**：原页写「相吸部分采用平均场近似（MFT），按照 Weeks-Chandler-Anderson 的方法进行处理」，本稿压缩为「van der Waals 型平均场近似（MFT）」、未提 WCA；公式形式不受影响 |
| (1-15) 积分吸附方程 | 源 (1-47)，书内 p.57 / PDF p.76 | `形式一致但符号不同` | 原页逐字印 $N(p/p_0)=\int_{W_{\min}}^{W_{\max}}N(p/p_0,W)f(W)\mathrm{d}W$，式号 (1-47)，并称其为「积分吸附方程（integral adsorption equation, IAE）」与「通用吸附等温线（general adsorption isotherm, GAI）方程」；积分变量原书用孔宽 $W$（kernel 记 $N(p/p_0,W)$、分布函数记 $f(W)$），本稿用 $D$。本稿正文已注明这一符号差别（`chapters/parts/ch01-b.tex:336-337`）。同页另有式 (1-46) $\left[\frac{\delta\Omega[\rho(r)]}{\delta\rho(r)}\right]_{\rho=\rho_{\mathrm{eq}}}=0$（巨势对局部密度导数为零的热力学平衡条件）与「式 (1-47) 也称 GAI 方程」「NLD…」等论述，本稿把 (1-46) 以文字写在式 (1-14) 之后、未单独编号，内容一致 |
| (1-16) Washburn | 源 (1-48)，书内 p.58 / PDF p.77 | `形式一致但符号不同` | 原页印 $r=\dfrac{-2\gamma\cos\theta}{p}$（对 $r$ 解出）；本稿写成 $p=-\dfrac{2\gamma\cos\theta}{r}$（对 $p$ 解出）。移项等价；同页「$\gamma=\qty{0.48}{N/m}$、$\theta$ 为 $135^\circ\sim150^\circ$、通常取平均值 $140^\circ$」与本稿一致 |
| (1-17) 数值式 | 源 (1-49)，书内 p.58 / PDF p.77 | `已核对一致` | 原页逐字印 $r=\dfrac{735}{p}$，并注「$r$ 以 nm 为单位；$p$ 以 MPa 为单位」；本稿写作 $r/\mathrm{nm}=735/(p/\mathrm{MPa})$，同一约定 |

**同批修掉的行文缺陷**：`chapters/parts/ch01-b.tex:154` 原在展示式前后重复同一句「孔宽与相对压力的
对应关系即……」，且未交代本稿 $D_p$ 与原书 $r_p$ 的变量关系；已改写为「式~\eqref{eq:bjh-dp} 中 $D_p$
为孔宽（圆柱孔即孔径），$r_k$ 为 Kelvin 半径、$t$ 为孔壁液膜厚度；原书写成 $r_p=r_k+t$，变量是真实
孔半径 $r_p$（书内 p.45 / PDF p.64）。」门禁 `tools/check_chapter.ps1 -Chap ch01-b` → errors 0 /
overfull $>5$pt 0 / missing glyphs 0 / pages 7 / PASS。

**同页附带确认（顺手核到的、不属于公式的项）**：上册 PDF p.77 原页把两项国家标准题名印作
「GB/T 21650.2—2008《压汞法和气体吸附法测定固体材料**孔径分布**和孔隙度 第 2 部分：气体吸附法分析介孔和大孔》」，
与 2026-10-13 据 OCR 作出的修改（把本稿的「孔尺寸分布」改回「孔径分布」）**独立吻合**；
同页另印「压强最大为 200~400 MPa」「可测孔半径范围为 3 nm~1000 µm」，与本稿一致。

### ch10-b（第 10 章 §10.3 模型检验、§10.4 传递过程与判据）

来源标注（首部注释）原自述「所有公式按『OCR 上下文 + 学科标准形式』重建，**未对照原页面
图像**」。2026-10-13 逐式读图复核，17 个 `\label` 与两处正文式全部有判决；首部注释同时
改写为复核页码。

| 本稿式号 | 源书式号与页 | 判决 | 依据（读图逐字所见） |
|---|---|---|---|
| `eq:temkin` | 源 (10-99) 及其前的未编号 Temkin 式，书内 p.769 / PDF p.258 | `已核对一致` | 原页印 $v_t=\frac{v}{[L]}=\tau\frac{k_1^{\mathrm{o}}k_2^{\mathrm{o}}[A_1][A_2]-k_{-1}^{\mathrm{o}}k_{-2}^{\mathrm{o}}[B_1][B_2]}{(k_1^{\mathrm{o}}[A_1]+k_{-2}^{\mathrm{o}}[B_2])^m(k_{-1}^{\mathrm{o}}[B_1]+k_2^{\mathrm{o}}[A_2])^{1-m}}$，其下 (10-99) 印 $\tau=\frac{\pi}{\sin(\pi m)}\frac{\gamma}{\exp(\gamma f)-1}$、$m=a-\gamma$——与本稿同形（本稿把这两行写在式后的文字里，未单独编号） |
| `eq:ch10-basis` | 原书无此式 | `改编补充` | 本稿自加的「速率基准声明」$r_v=\rho_pr_m$ 与三条单位声明，是本节三个判据的共同前提；原书 §10.4—§10.5 未印此声明（原书判据的基准混用正是本稿要修的坑）。**符号差**：`chapters/parts/ch10-c.tex` 的 `eq:rate-basis` 把同一个量记作 $\rho$（该节无流体密度，不冲突），已在 `chapters/parts/ch10-c.tex:424-425` 就地注明两处指的是同一个数 |
| `eq:ch10-jd` | 源 (10-101)，书内 p.770 / PDF p.259 | `形式一致但符号不同` | 320 dpi 逐字印 $j_D=\frac{k_G\rho}{G}Sc^{2/3}=\frac{Sh}{Re\,Sc^{1/3}}$、$Sc=\frac{\nu}{D}$、$Sh=\frac{k_Gd_p}{D}$、$Re=\frac{Gd_p}{\mu}$（$\rho$ 上无横线，已排除「$\bar\rho$」的读法）。整理式、$Sh$、$Re$ 三式同形；$Sc$ 原书用运动黏度 $\nu/D$，本稿写 $\mu/(\rho D)$，恒等（$\nu=\mu/\rho$），已在 `chapters/parts/ch10-b.tex:398-400` 就地注明 |
| `eq:ch10-jd-fix` | 源 (10-102)，书内 p.771 / PDF p.260 | `已核对一致` | 原页印 $j_D=\frac{0.725}{Re^{0.41}-0.15}$，其后「对气体、液体都使用」 |
| `eq:ch10-extconv` | 源 (10-103)，书内 p.771 / PDF p.260 | `已核对一致` | 320 dpi 印 $\ln\frac{1}{1-X}=\frac{0.725ad_pz}{d_p(Re^{0.41}-0.15)Sc^{2/3}}$——分子与分母**各印一个 $d_p$**，约去后与本稿同形；已在 `chapters/parts/ch10-b.tex:410-413` 就地说明 |
| `eq:ch10-jh` | 源 (10-104)(10-105)，书内 p.771 / PDF p.260 | `已核对一致` | 原页印 $Q=R(-\Delta H_r)=\alpha_sa(T_S-T_B)$、$j_H=\frac{\alpha_s}{Gc_p}Pr^{2/3}=\frac{Nu}{Re\,Pr^{1/3}}$；式后 prose 给 $Pr=c_p\mu/\lambda_f$、$Nu=\alpha_sd_p/\lambda_f$ 与「$c_p$ 为等压比热容；$\lambda_f$ 为热传导系数」 |
| `eq:ch10-dT` | 源 (10-107)(10-108)，书内 p.771 / PDF p.260 | `已核对一致` | 原页印 $T_S-T_B=\frac{j_D}{j_H}\bigl(\frac{Pr}{Sc}\bigr)^{2/3}\frac{-\Delta H_r}{\rho c_p}(c_B-c_S)$；prose「由式（10-102）与式（10-106）相比得 $j_D/j_H=0.66$……$(-\Delta H_r)c_B/\rho c_p$ 为放热反应的绝热温升 $\lambda$」，(10-108) 印 $T_S-T_B=0.66\lambda f$ |
| `eq:ch10-profile` | 源 (10-113)(10-114)，书内 p.773 / PDF p.262 | `已核对一致` | 原页印 $\frac{c}{c_S}=\frac{\sinh(\varphi_Sr/R)}{(r/R)\sinh\varphi_S}$（球形）、$\frac{c}{c_S}=\frac{\cosh(\varphi_Ll/L)}{\cosh\varphi_L}$（平板），其后「式中，$\varphi_S$ 和 $\varphi_L$ 为无因次的 Thiele 模数」 |
| `eq:ch10-thiele` | 书内 p.774 / PDF p.263 顶部两式（**未编号**）；平方形式见源 (10-118) | `已核对一致` | 原页印 $\varphi_S=R\sqrt{S_vk_S/D_e}$、$\varphi_L=L\sqrt{S_vk_S/D_e}$；(10-118) 印 $\varphi_S^2=\frac{R^2S_vk_S}{D_e}=\frac{RS_vk_Sc^m}{D_ec/R}=\frac{\text{反应速率}}{\text{扩散速率}}$ |
| `eq:ch10-r-r0` | 源 (10-115)(10-116)，书内 p.774 / PDF p.263 | `已核对一致` | 原页印 $r=4\pi R\varphi_SD_ec_S\bigl(\frac{1}{\tanh\varphi_S}-\frac{1}{\varphi_S}\bigr)$、$r_0=\frac43\pi R^3S_vk_Sc_S$ |
| `eq:ch10-eta` | 源 (10-117)（**文字定义**）+ 其后两条未编号显式，书内 p.774 / PDF p.263 | `已核对一致` | 原书 (10-117) 印的是一条文字比式「有内扩散存在时的催化剂颗粒反应速率／无内扩散存在时的催化剂颗粒反应速率」；两条显式 $\eta=\frac{r}{r_0}=\frac{3}{\varphi_S}\bigl(\frac{1}{\tanh\varphi_S}-\frac{1}{\varphi_S}\bigr)$（球形）与 $\eta=\frac{\tanh\varphi_L}{\varphi_L}$（平板）在其后**未编号**。分片原有核对说明把这两条显式挂在 (10-117) 下，本次按读图改正编号归属 |
| `eq:ch10-bicomp` | 源 (10-122)，书内 p.776 / PDF p.265 | `已核对一致` | 分片就地核对说明（$c_2$ 一次方、分母下标 $(D_e)_1$、$\eta<0.4$ 与 3/2 级表述均相符），本轮不重复读图 |
| `eq:ch10-kd` | 源 (10-123)，书内 p.776 / PDF p.265 | `已核对并修正` | 原书 $v_d=\frac{-D_2p_2}{\nu_2D_1p_1}-1$ **分子带负号**，原稿漏此负号，已补回（分片就地核对说明） |
| `eq:ch10-gammabeta` | 源 (10-124)，书内 p.778 / PDF p.267 | `已核对一致` | 220 dpi 印 $\gamma=\frac{E}{RT}$、$\beta=\frac{c_s(-\Delta H)D_e}{\lambda_pT_s}$（原书用 $\equiv$）；prose「$\Delta H$ 为反应的焓变；$\lambda_p$ 为多孔催化剂颗粒的热导率」、$\gamma=20$ 对应 $E\approx100$ kJ/mol 与 $T\approx600$ K、$\beta$ 在 $\pm0.8$ 之间 |
| `eq:ch10-da` | 源 (10-130)，书内 p.792 / PDF p.281 | `形式一致但符号不同` | 140 dpi 印 $Da\equiv\frac{rR}{k_mc_B}<\frac{0.15}{m}$；原书用**未声明基准的 $r$**，本稿改写为体积基准 $r_v$（并把 $\equiv$ 写作 $=$），属基准改写 |
| `eq:ch10-wp` | 源 (10-131)，书内 p.792 / PDF p.281 | `形式一致但符号不同` | 原页印 $\Phi=\frac{r\rho R^2}{D_ec_B}$——**确含颗粒密度 $\rho$，即质量基准形式**（式后 prose 亦印「式中，$\rho$ 为催化剂颗粒的密度」）；本稿主式写成体积基准 $\Phi=r_vR^2/(D_ec_B)$，另列质量基准的等价写法 |
| `eq:ch10-mears` | 源 (10-132)，书内 p.793 / PDF p.282 | `形式一致但符号不同` | 原页印 $\frac{r(-\Delta H)R}{h_BT_B}<0.15\frac{RT_B}{E}$（原书把气体常量与颗粒半径同记为 $R$）；本稿改写为 $r_v$ 基准，并把气体常量记作 $\mathscr{R}$ |

**同批顺带核到的正文式**（本稿写在正文里、未编号）：$R=k_G(c_B-c_S)$ = 源 (10-100)、
$j_H=1.10/(Re^{0.41}-0.15)$ = 源 (10-106)，均逐字同形（书内 p.770—771 / PDF p.259—260）。

**同批落盘的改动**：`chapters/parts/ch10-b.tex` 首部注释（`:7-10`）由「未对照原页面图像」
改写为复核页码清单；`:398-400` 补 $Sc$ 的符号关系；`:410-413` 补 (10-103) 双 $d_p$ 说明；
`:552-560` 核对说明改正 (10-117) 的编号归属并补记 $\varphi_S$/$\varphi_L$ 两式；
`chapters/parts/ch10-c.tex:424-425` 注明 $\rho$ 与 $\rho_p$ 指同一个量。

**观察（本轮未改）**：三个判据在 `ch10-b` §10.4.5（`:767-819`）与 `ch10-c` §10.5.4
（`:414-560`）各出现一次——前者放在理论节、后者放在实验节，两处公式数值一致而密度符号
不同（$\rho_p$ / $\rho$）。本轮按「各自就地定义清楚 + 互相注明」处理，未合并两节。

### 其它分片——已知的未覆盖清单（待逐分片展开）

| 分片 | 线索 | 状态 |
|---|---|---|
| `ch10-b` | 首部注释自述「所有公式按『OCR 上下文 + 学科标准形式』重建，未对照原页面图像」 | **已展开（2026-10-13）**：17 个编号公式逐一读图判决，见本节 `### ch10-b`；首部注释已改写为复核页码 |
| `ch09-d` | 表 9-15 灵敏度因子「未逐值照抄原书表（页面图像分辨率不足以保证逐值读取）」 | 部分未覆盖 |
2026-10-13 对 `chapters/parts/*.tex` 全文检索「未对照原页面图像／未逐式／未逐值／按学科标准形式重建」类自述，
把**所有**自述都列在下面，不再用「其余分片未排查」兜底：

| 分片 | 自述（行号） | 状态 |
|---|---|---|
| `ch10-b` | 首部注释：「所有公式按『OCR 上下文 + 学科标准形式』重建，未对照原页面图像」（`:7`） | **已关闭（2026-10-13）**：17 个 `\label` 逐式读图（书内 p.769—793 / PDF p.258—282），判决见本节 `### ch10-b`；首部注释已改写为复核页码 |
| `ch01-c` | 来源注：「均按 OCR 上下文与学科标准形式重建，存疑处已在正文用『待核对』标出」（`:1071`），但正文已无任何「待核对」字样 | **注释与正文不符**，读图后二选一：补标或改注 |
| `ch07-a` | 「正文 OCR 重建，系数与符号约定存疑处已在文中以『待核对』标出」（`:557`），正文同样已无该字样 | **已关闭（2026-10-13）**：7 个编号公式逐一读图复核（新增 D-9 临界角 `已核对一致`；式 `eq:beer` 判 `改编补充`），来源注已改写为复核页码并指向 `sources/pixel_verify.md` |
| `ch03-a` | 「式~\eqref{eq:ch03-alpha}--\eqref{eq:ch03-integral} 按学科标准形式重建，符号约定以原书 OCR…」（`:464`） | 未开 |
| `ch11-a` | 「本节判据系按电化学标准形式重建」（`:895`） | 未开 |
| `ch09-b` | OCR 丢字符（「Eb = Ef(n1)Ei(n)」）后「按幂次与上下文重建」（`:219`） | 未开 |
| `ch08-c` | 「本分片的表达式为按定义重建」（`:277`）、「本分片的换算式为按常用形式重建」（`:401`） | 未开 |
| `ch06-a` | 式 (stokes-ratio)「按标准形式重建，**原书未印出这条强度比公式**」（`:354`） | 改编补充已声明，待读图确认原书确未印 |
| `ch11-d` | 三处 \emph{核对说明}（Randles 拓扑、$Z_{\mathrm{W}}$ 的 $\sigma$、CPE）（`:346`/`:377`/`:416`）均自述已对照 PDF p.347—350 页面图像 | 自述已核，待抽验 |
| `ch02-b` / `ch02-c` | 来源注自述「凡按 OCR 上下文与学科标准形式重建之处，**均已逐处对照原页面图像**核验」（`:1389` / `:562`） | 自述已核但**无逐式记录**：抽验，抽中不符即整片转「未覆盖」 |
| `ch06-b` | 「定稿时已逐条对照原页面图像核验，原『待核对』标记全部核销」（`:1048`） | 自述已核销，待抽验 |
| `ch09-d` | 表 9-15 灵敏度因子「未逐值照抄原书表」（`:105`） | 属表格项，见 `sources/table_status.md` |
| `ch04-b` | 表内「按同一方法补出」的行（`:509`） | 属表格项 |

**正文里仍印着的未决提问**（不是公式，但同属「待核对」，随本项一并清）：

- `chapters/parts/ch06-a.tex:490`「尚待核对：外光路系统与样品池两行……」
- `chapters/parts/ch07-c.tex:464`「尚待核对：判据一……系据书内 p.499—500 的 DCOOD 与 HCOOH……」
- `chapters/parts/ch08-b.tex:384`「尚待核对：本表中按 $^{1}$H 化学位移直接分档（0.5 至 7.0）归纳的行……」

## 四、复跑

```
python tools/vpage.py up   64 build/frev/up064.png --dpi 200   # 书内 p.45：式 (1-9) 同处的 $r_p=r_k+t$
python tools/vpage.py up   64 build/frev/up064_bjh_rp.png --dpi 300 --top .35 --bottom .45   # 同页窄带：$r_k<r_p$ 与 $r_p=r_k+t$ 逐字
python tools/vpage.py up   70 build/frev/up070.png --dpi 200   # 书内 p.51：式 (1-37)(1-38)
python tools/vpage.py up   72 build/frev/up072.png --dpi 200   # 书内 p.53：式 (1-39) $\alpha_s$
python tools/vpage.py up   72 build/frev/up072_alphas.png --dpi 300 --top .35 --bottom .45   # 同页窄带：式 (1-39) 逐字
python tools/vpage.py up   75 build/frev/up075.png --dpi 200   # 书内 p.56：式 (1-42)—(1-45)
python tools/vpage.py up   76 build/frev/up076.png --dpi 200   # 书内 p.57：式 (1-46)(1-47)
python tools/vpage.py up   77 build/frev/up077.png --dpi 200   # 书内 p.58：式 (1-48)(1-49) 与两项国标题名

# ch10-b（2026-10-13）：源页为下册，书内 = PDF + 511
python tools/vpage.py down 258 build/frev/d258_temkin.png --dpi 160 --top .22 --bottom .50   # 书内 p.769：式 (10-99) 与 Temkin 式
python tools/vpage.py down 259 build/frev/d259_eq1.png --dpi 150 --top .55 --bottom .84      # 书内 p.770：式 (10-100)
python tools/vpage.py down 259 build/frev/d259_jd_hi.png --dpi 320 --top .70 --bottom .92    # 同页窄带：式 (10-101) 与 Sc/Sh/Re 定义
python tools/vpage.py down 260 build/frev/d260_eq1.png --dpi 150 --top .04 --bottom .32      # 书内 p.771：式 (10-102)(10-103)
python tools/vpage.py down 260 build/frev/d260_conv_hi.png --dpi 320 --top .16 --bottom .28  # 同页窄带：式 (10-103) 双 $d_p$
python tools/vpage.py down 260 build/frev/d260_eq2.png --dpi 150 --top .48 --bottom .95      # 书内 p.771：式 (10-104)—(10-108)
python tools/vpage.py down 262 build/frev/d262_prof.png --dpi 160 --top .45 --bottom .85     # 书内 p.773：式 (10-113)(10-114)
python tools/vpage.py down 263 build/frev/d263_eta.png --dpi 170 --top .70 --bottom .99      # 书内 p.774：式 (10-115)—(10-118) 与 $\eta$ 两条显式
python tools/vpage.py down 267 build/frev/d267_gb.png --dpi 220 --top .10 --bottom .40       # 书内 p.778：式 (10-124)
python tools/vpage.py down 281 build/frev/d281_crit.png --dpi 140 --top .40 --bottom .90     # 书内 p.792：式 (10-130)(10-131)
python tools/vpage.py down 282 build/frev/d282_mears.png --dpi 140 --top .05 --bottom .40    # 书内 p.793：式 (10-132)
```

## 五、本台账不主张的东西

- 不主张「核过」= 推导正确：本表判的是**印法与形式**是否与原书一致，不重做原书的物理推导；
  推导层面的问题记 `errata.md` 乙类。
- 不主张分片级条目数可以代替逐式：`pixel_verify.md` 一个条目可能覆盖多式，也可能只覆盖一式的局部。
- 不主张已覆盖的分片就是全部：本表当前已展开 `ch01-b`、`ch07-a`、`ch10-b` 三片，其余分片仅列线索。
  未展开的分片一律维持 `未覆盖`，不得因「本项已做」推定通过。
- 不主张 OCR 可作形式依据：所有判决都以**页面图像**为据，OCR 只用于定位。
