# 全书编号公式逐式复核台账（`sources/formula_crosscheck.md`）

本文件由 `tools/review_ledger.py formulas` 从磁盘可核验事实生成：
`build/work_formulas.tsv`（`tools/review_worklist.py` 生成的 372 个编号式清单，
含分片、源码行、成品页、源书页范围与提示页）＋ `sources/logs/formulas_*.tsv`
（逐式判决，附源书 PDF 页与并排式子）。生成时间 2026-10-20。

**方法**：每个式先用 `tools/vbook.py` 渲染成品页面图像，读出发行式与编号；
再用 `tools/vpage.py` 渲染源书对应页（上册 `书内页 = PDF页 − 19`，下册 `+507`，
以页眉印刷页码为准），**逐符号**对照变量、上下标、正负号、系数、常数与编号。
OCR 文本只用于定位，不作证据。判决词表与「什么算一致」见 `sources/review_protocol.md` §3.2。

| 结论 | 式数 |
| --- | --- |
| 已核对一致 | 146 |
| 已核对并修正 | 0 |
| 形式一致但符号不同 | 63 |
| 原书自身问题 | 10 |
| 改编补充 | 53 |
| 未找到 | 0 |
| 未覆盖 | 100 |
| **合计** | **372** |

> 尚有 100 式未取得终判（`未覆盖`／`未找到`），本台账**不得**用于宣称第二项验收完成。

## 一、逐式判决

### ch01-a（6/6 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:langmuir-ch01` | 1-1 | 9 | up p.1-84 | 20-103 | 形式一致但符号不同 | up p.34 | 版面 θ=V/V_m=bp/(1+bp)；源书书内 p.15 式(1-10) 印 θ=V/V_m=ap/(1+ap)，本版 b↔源书 a（吸附系数/吸附平衡常数），其余逐符号同形。 |
| `eq:langmuir-lin` | 1-2 | 9 | up p.1-84 | 35 | 形式一致但符号不同 | up p.35 | 版面 p/V=1/(V_m b)+p/V_m；源书书内 p.16 式(1-11) 印 p/V=p/V_m+1/(aV_m)，两项次序对调、a↔b，等价。 |
| `eq:bet` | 1-3 | 9 | up p.1-84 | 35 | 已核对一致 | up p.36 | 版面 V=V_m C(p/p0)/[(1-p/p0)(1+(C-1)p/p0)]；源书书内 p.17 式(1-13) 印 θ=V/V_m=Cp/[(p0-p)(1+(C-1)p/p0)]，分母乘 p0 归一后同式，解出 V 即本版式。 |
| `eq:cdef` | 1-4 | 9 | up p.1-84 | 35 | 已核对一致 | up p.36-37 | 版面 C≈exp[(E1-E_L)/(RT)]；源书书内 p.17 式(1-14) 印 C=C0exp((E1-E_L)/RT)，书内 p.18 式(1-17) 印 C=exp((E1-E_L)/RT)（正文说明 C0 可视为 1），本版取 C0=1 的化简形式。 |
| `eq:bet-lin` | 1-5 | 9 | up p.1-84 | 35 | 已核对一致 | up p.37 | 版面 (p/p0)/[V(1-p/p0)]=(C-1)/(V_m C)·p/p0+1/(V_m C)；源书书内 p.18 式(1-15) 印 p/[V(p0-p)]=(C-1)/(V_m C)×p/p0+1/(V_m C)，左端分母按 p0 归一，等价。 |
| `eq:surface` | 1-6 | 9 | up p.1-84 | 35 | 形式一致但符号不同 | up p.37 | 版面 S_s=V_{m,s}N_Aσ/22400、S_total=V_{m,total}N_Aσ/22400；源书书内 p.18 式(1-16) 印 S=(V_m/22400)N_Aσ_m（单一未带基准下标的 S），本版按单位质量/整份样品分两式并加 m,s/total 下标、σ_m 记作 σ。 |

### ch01-b（11/11 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:kelvin` | 1-7 | 11 | up p.43-60 | 62 | 形式一致但符号不同 | up p.42-43 | 版面 ln(p/p0)=-2γV_Lcosθ/(r_k RT)；源书书内 p.23 式(1-22) 印 ln(p/p0)=-(2γM)/(RTρ)·(1/r)cosθ，本版把 M/ρ 记为摩尔体积 V_L、r 记为 r_k；源书 (1-21) 是其 θ=0 特例、p.24 式(1-23)(1-24) 为半球/圆柱弯月面两式。 |
| `eq:bjh-balance` | 1-8 | 11 | up p.43-60 | 42 | 形式一致但符号不同 | up p.65 | 版面 V(x_k)=∑_{i≤k}πr_i²ℓ_i+∑_{j>k}π[r_j²-(r_j-t_k)²]ℓ_j；源书书内 p.46 式(1-36) 印 V_ads(x_k)=∑_{i=1}^{k}ΔV_i[r_i≤r_k(x_k)]+∑_{j=k+1}^{n}ΔS_j t_j[r_j≥r_k(x_k)]：两项守恒结构相同，本版把 ΔV_i 展开为 πr_i²ℓ_i、膜项写精确环形面积（源书用薄壁近似 ΔS_j t_j），厚度下标 t_k 对源书 t_j。 |
| `eq:bjh-dp` | 1-9 | 12 | up p.43-60 | 64 | 形式一致但符号不同 | up p.64 | 版面 D_p=2(r_k+t)；源书书内 p.45 正文印 r_p=r_k+t（未编号），本版给孔宽 D_p=2r_p，乘 2 的关系已在正文就地说明。 |
| `eq:halsey` | 1-10 | 12 | up p.43-60 | 70 | 改编补充 | up p.70 | 版面 t=t_m[-5/ln(p/p0)]^{1/3}；源书书内 p.51 只印式(1-37) t=(t_m/V_m)V=f(p/p0) 与 t_m=0.354 nm，全页无 Halsey 显式，本版正文已声明该式为改编补入。 |
| `eq:vt` | 1-11 | 13 | up p.43-60 | 70 | 已核对一致 | up p.70 | 版面 V=(V_m/t_m)t；源书书内 p.51 式(1-38) 印 V=(V_m/t_m)t，逐符号一致。 |
| `eq:mp-dv` | 1-12 | 13 | up p.43-60 | 75 | 已核对一致 | up p.75 | 版面 ΔV_i=ΔS_i t̄_i、ΔS_i=S_{i-1}-S_i、t̄_i=½(t_{i-1}+t_i)；源书书内 p.56 式(1-42)—(1-44) 同三式，逐符号一致（源书用 × 号、本版并列）。 |
| `eq:as` | 1-13 | 13 | up p.43-60 | 72 | 已核对一致 | up p.72 | 版面 α_s=n(p/p0)/n_{0.4}；源书书内 p.53 式(1-39) 印 α_s=n/n_{0.4}=V/V_{0.4}=f(p/p0)，本版取首末两段并把分子写成 n(p/p0)，等价。 |
| `eq:nldft-pot` | 1-14 | 14 | up p.43-60 | 72 | 形式一致但符号不同 | up p.75 | 版面 Ω[ρ(r)]=F[ρ(r)]+∫ρ(r)[V_ext(r)-μ]dr；源书书内 p.56 式(1-45) 同式，仅壁面势记 v_ext（本版 V_ext）。 |
| `eq:gae` | 1-15 | 14 | up p.43-60 | 75 | 形式一致但符号不同 | up p.76 | 版面 N(p/p0)=∫_{D_min}^{D_max}N(p/p0,D)f(D)dD；源书书内 p.57 式(1-47) 印 N(p/p0)=∫_{W_min}^{W_max}N(p/p0,W)f(W)dW，积分变量孔宽 W→D（本版正文已注明）。 |
| `eq:washburn` | 1-16 | 14 | up p.43-60 | 75 | 形式一致但符号不同 | up p.77 | 版面 p=-2γcosθ/r；源书书内 p.58 式(1-48) 印 r=-2γcosθ/p（对 r 解出），移项等价，γ=0.48 N/m、θ=135°~150° 同页一致。 |
| `eq:washburn-num` | 1-17 | 14 | up p.43-60 | 77 | 已核对一致 | up p.77 | 版面 r/nm=735/(p/MPa)；源书书内 p.58 式(1-49) 印 r=735/p 并注「r 以 nm 为单位；p 以 MPa 为单位」，同一约定。 |

### ch01-c（22/22 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch01c-dn` | 1-18 | 18 | up p.61-80 | 82 | 形式一致但符号不同 | up p.82 | 版面 D̄(n)=∫_0^∞x q(x,n)dx/∫_0^∞q(x,n)dx；源书书内 p.63 式(1-51) 印 x̄(n)=∫q(x,n)x dx/∫q(x,n)dx，本版把平均粒径记作 D̄（源书 x̄）、被积函数顺序对调，同一式。 |
| `eq:ch01c-dpq` | 1-19 | 18 | up p.61-80 | 82 | 已核对一致 | up p.82 | 版面 D̄[p,q]=[Σn_i d_i^p/Σn_i d_i^q]^{1/(p-q)}；源书书内 p.63 式(1-52) 印 D[p,q]=[Σn_i d_i^p/Σn_i d_i^q]^{1/(p-q)}，仅本版符号带平均横线，指数与上下标逐项同。 |
| `eq:ch01c-di` | 1-20 | 18 | up p.61-80 | 82 | 已核对一致 | up p.82 | 版面 d_i=√(D_i D_{i+1})；源书书内 p.63 式(1-53) 印 d_i=√(D_i×D_{i+1})，同式（乘号写成并列）。 |
| `eq:ch01c-d32a` | 1-21 | 19 | up p.61-80 | 82 | 形式一致但符号不同 | up p.82 | 版面 D[3,2]=D̄(2)、D[4,3]=D̄(3)；源书书内 p.63 在式(1-53) 后以正文印「显然，D[1,0]=x̄(0)，D[3,2]=x̄(2)，D[4,3]=x̄(3)」（未单独编号），关系相同、平均符号 x̄→D̄。 |
| `eq:ch01c-d32` | 1-22 | 19 | up p.61-80 | 82 | 形式一致但符号不同 | up p.82 | 版面 D[3,2]=Σv_i/Σ(v_i/d_i)、D[4,3]=Σw_i d_i/Σw_i=Σv_i d_i/Σv_i；源书书内 p.63 式(1-54)(1-55) 印 D[3,2]=Σs_i d_i/Σs_i、D[4,3]=Σw_i d_i/Σw_i，本版按体积分数改写 D[3,2]（球粒 s_i∝v_i/d_i，全区间等价），正文已给出等价证明。 |
| `eq:ch01c-stokes` | 1-23 | 22 | up p.61-80 | 85 | 形式一致但符号不同 | up p.87 | 版面 u=(ρ-ρ0)gd²/(18η)；源书书内 p.68 式(1-56) 印 d=[18η0 u/((ρ-ρ0)g)]^{1/2}（对 d 解出、黏度记 η0），移项等价。 |
| `eq:ch01c-dt-g` | 1-24 | 22 | up p.61-80 | 86 | 形式一致但符号不同 | up p.87 | 版面 d=[18ηH/((ρ-ρ0)gt)]^{1/2}；源书书内 p.68 式(1-57) 印 d=[18η0 H/((ρ-ρ0)gt)]^{1/2}，逐项同形，仅流体黏度记 η（源书 η0）。 |
| `eq:ch01c-centrif` | 1-25 | 22 | up p.61-80 | 86 | 形式一致但符号不同 | up p.87 | 版面 u_r=(ρ-ρ0)ω²rd²/(18η)；源书书内 p.68 式(1-58) 印 d=[18η0 u_r/((ρ-ρ0)ω²r)]^{1/2}（以 ω²r 代 g、对 d 解出、黏度记 η0），移项等价。 |
| `eq:ch01c-dt-c` | 1-26 | 22 | up p.61-80 | 86 | 形式一致但符号不同 | up p.88 | 版面 d=[18ηln(r2/r1)/((ρ-ρ0)ω²t)]^{1/2}；源书书内 p.69 式(1-59) 印 d=[18η0ln(r2/r1)/((ρ-ρ0)ω²t)]^{1/2}，逐项同形，仅流体黏度记 η（源书 η0）。 |
| `eq:ch01c-einstein` | 1-27 | 23 | up p.61-80 | 90 | 形式一致但符号不同 | up p.92 | 版面 D_d=kT/(6πηR)；源书书内 p.73 式(1-60) 印 D=kT/(6πηR)，本版扩散系数记 D_d 以避与粒径 d 混用；源书式后说明把 R 说成「颗粒粒径」，本版写水力学半径。 |
| `eq:ch01c-doppler` | 1-28 | 24 | up p.61-80 | 90 | 形式一致但符号不同 | up p.92 | 版面 Γ=(4πn/λ)²sin²(θ/2)D_d；源书书内 p.73 式(1-61) 印 Γ=((4πn/λ)sin(θ/2))²D，平方写进括号、扩散系数 D→D_d，等价。 |
| `eq:ch01c-betd` | 1-29 | 24 | up p.61-80 | 92 | 形式一致但符号不同 | up p.93 | 版面 D=6/(Sρ)；源书书内 p.74 正文印 D=φ/(Sρ)（φ 为形状因子、对球体 φ 值为 6），本版把球体的 φ=6 代入。 |
| `eq:ch01c-volapp` | 1-30 | 26 | up p.61-80 | 81 | 已核对一致 | up p.94 | 版面 V_app=V_void+V_pore+V_skel；源书书内 p.75 式(1-62) 印 V_堆积=V_隙+V_孔+V_骨架，三项与下标一一对应（中文下标译作拉丁）。 |
| `eq:ch01c-rhoskel` | 1-31 | 26 | up p.61-80 | 81 | 已核对一致 | up p.94 | 版面 ρ_skel=m/V_skel；源书书内 p.75 式(1-63) 印 ρ_骨架=m/V_骨架，仅下标为中文。 |
| `eq:ch01c-rhopart` | 1-32 | 26 | up p.61-80 | 81 | 已核对一致 | up p.95 | 版面 ρ_part=m/(V_pore+V_skel)；源书书内 p.76 式(1-64) 印 ρ_颗粒=m/V_颗粒=m/(V_骨架+V_孔)，同式（本版直接写展开式、分母次序 pore+skel）。 |
| `eq:ch01c-rhobulk` | 1-33 | 26 | up p.61-80 | 81 | 已核对一致 | up p.96 | 版面 ρ_bulk=m/V_app；源书书内 p.77 式(1-66) 印 ρ_堆积=m/V_堆积，仅下标为中文（本版用拉丁等价下标）。 |
| `eq:ch01c-order` | 1-34 | 26 | up p.61-80 | 94 | 改编补充 | up p.94-96 | 版面 ρ_skel>ρ_part>ρ_bulk；源书书内 p.75—77（PDF p.94—96）§1.2.4 全节无此不等式（正文只逐条定义三种密度），属改编本自加的自检判据。旧台账记「改编补充」，与页面图像一致。 |
| `eq:ch01c-poros` | 1-35 | 26 | up p.61-80 | 94 | 形式一致但符号不同 | up p.95 | 版面 p=V_pore/(V_pore+V_skel)=1-ρ_part/ρ_skel；源书书内 p.76 式(1-65) 印 θ=V_孔/V_颗粒=V_孔/(V_骨架+V_孔)=1-ρ_颗粒/ρ_骨架，符号 θ→p、下标译作拉丁，结构逐项同。 |
| `eq:ch01c-voidfrac` | 1-36 | 26 | up p.61-80 | 94 | 已核对一致 | up p.96 | 版面 ε=1-ρ_bulk/ρ_part；源书书内 p.77 式(1-67) 印 ε=V_隙/V_堆积=V_隙/(V_颗粒+V_隙)=1-ρ_堆积/ρ_颗粒，本版只印末段，等价。 |
| `eq:ch01c-vp` | 1-37 | 29 | up p.61-80 | 94 | 改编补充 | up p.94-97 | 版面 v_p=1/ρ_part-1/ρ_skel；源书书内 p.75—78（PDF p.94—97）无比孔容式（§1.2.4 只定义三种密度与孔隙率/空隙分数），本版由 ρ_part=m/(V_pore+V_skel)、ρ_skel=m/V_skel 直接算出，正文已注明。 |
| `eq:ch01c-crush` | 1-38 | 30 | up p.61-80 | 98 | 已核对一致 | up p.98 | 版面 P=F/A；源书书内 p.79 式(1-68) 印 P=F/A，逐符号一致；同页 F 单位 N、A 单位 mm² 与本版一致。 |
| `eq:ch01c-attrition` | 1-39 | 30 | up p.61-80 | 97 | 已核对一致 | up p.98 | 版面 A=(m0-m1)/m0×100%；源书书内 p.79 式(1-69) 印「磨耗率＝磨耗前后样品的质量差/磨耗前样品的质量×100%」（文字式），本版把磨耗率记作 A、质量差记作 m0-m1，同式（同页说明 m0、m1 为磨耗前后质量）。 |

### ch02-a（2/10 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:bragg-ch02` | 2-1 | 34 | up p.85-109 | 115 | 已核对一致 | up p.115 | 版面 nλ=2d_hkl sinθ_hkl；源书书内 p.96 式(2-6) 印 nλ=2d_hkl sinθ（同页正文把该衍射角称 θ_hkl），本体同式、本版给 θ 加 hkl 下标。 |
| `eq:d-cubic` | 2-2 | 34 | up p.85-109 | 116 | 形式一致但符号不同 | up p.116 | 版面 1/d_hkl=√(h²+k²+l²)/a；源书书内 p.97 式(2-7) 印 d_hkl=a/√(h²+k²+l²)，互为倒数（本版正文已注明等价的适用限定）。 |
| `eq:zone-law` | 2-3 | 35 | up p.85-109 | 118 | 未覆盖 | — |  |
| `eq:camlen` | 2-4 | 35 | up p.85-109 | 118 | 未覆盖 | — |  |
| `eq:weak-phase` | 2-5 | 38 | up p.85-109 | 123 | 未覆盖 | — |  |
| `eq:chi` | 2-6 | 38 | up p.85-109 | 123 | 未覆盖 | — |  |
| `eq:hrtem-contrast` | 2-7 | 38 | up p.85-109 | 124 | 未覆盖 | — |  |
| `eq:lambda-nonrel` | 2-8 | 38 | up p.85-109 | 125 | 未覆盖 | — |  |
| `eq:lambda-rel` | 2-9 | 39 | up p.85-109 | 125 | 未覆盖 | — |  |
| `eq:point-res` | 2-10 | 39 | up p.85-109 | 126 | 未覆盖 | — |  |

### ch02-b（0/11 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch02b-mag` | 2-11 | 40 |  p.— | 129 | 未覆盖 | — |  |
| `eq:ch02b-zcontrast` | 2-12 | 40 |  p.— | 131 | 未覆盖 | — |  |
| `eq:ch02b-moseley` | 2-13 | 42 |  p.— | 133 | 未覆盖 | — |  |
| `eq:ch02b-edsint` | 2-14 | 42 |  p.— | 133 | 未覆盖 | — |  |
| `eq:ch02b-cl` | 2-15 | 42 |  p.— | 135 | 未覆盖 | — |  |
| `eq:ch02b-norm` | 2-16 | 43 |  p.— | 135 | 未覆盖 | — |  |
| `eq:ch02b-kfac` | 2-17 | 43 |  p.— | 135 | 未覆盖 | — |  |
| `eq:ch02b-thickness` | 2-18 | 43 |  p.— | 137 | 未覆盖 | — |  |
| `eq:ch02b-eelsI` | 2-19 | 44 |  p.— | 137 | 未覆盖 | — |  |
| `eq:ch02b-eelsratio` | 2-20 | 44 |  p.— | 162 | 未覆盖 | — |  |
| `eq:ch02b-eelspartial` | 2-21 | 44 |  p.— | 162 | 未覆盖 | — |  |

### ch02-c（0/5 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch02c-cs` | 2-22 | 55 |  p.— | 166 | 未覆盖 | — |  |
| `eq:ch02c-envelope` | 2-23 | 56 |  p.— | 124 | 未覆盖 | — |  |
| `eq:ch02c-radon` | 2-24 | 58 |  p.— | 171 | 未覆盖 | — |  |
| `eq:ch02c-haadf` | 2-25 | 58 |  p.— | 171 | 未覆盖 | — |  |
| `eq:ch02c-holo` | 2-26 | 59 |  p.— | 173 | 未覆盖 | — |  |

### ch03-a（7/7 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch03-alpha` | 3-1 | 69 | up p.169-180 | 194 | 改编补充 | up p.194-195 | 版面 (3-1) α=(m0−mt)/(m0−m∞)；源书 §3.1（书内 p.175 / PDF p.194）只逐条定义 Δm、dm/dt、Ti、Tp，无转化率式，α 只在 §3.3 变量说明出现（书内 p.180 / PDF p.199）。图 build/_eq_p69.png / build/_src_up194_fb.png |
| `eq:ch03-dta` | 3-2 | 70 | up p.169-180 | 196 | 改编补充 | up p.195-196 | 版面 (3-2) ΔH=(K/m)∫ΔT dt；源书 §3.2.2（书内 p.176–177 / PDF p.195–196）只定义基线/峰/峰宽/峰高/峰面积/外推始点/峰温，全节无 K、m 与积分式。图 build/_eq_p70.png / build/_src_up195_fb.png |
| `eq:ch03-dsc` | 3-3 | 70 | up p.169-180 | 192 | 改编补充 | up p.197 | 版面 (3-3) ΔH=(1/m)∫[dQ/dt−(dQ/dt)base]dt；源书 §3.2.3「2. 差示扫描量热曲线」（书内 p.178 / PDF p.197）只印 dH/dt=f(T)或 f(t)，无峰面积-热焓换算式。图 build/_eq_p70.png / build/_src_up197_fb.png |
| `eq:ch03-mtdsc` | 3-4 | 71 | up p.169-180 | 197 | 形式一致但符号不同 | up p.198 | 版面 (3-4) T(t)=T0+βt+AT sin(ωt)、dQ/dt=Cp dT/dt+f(T,t)；源书书内 p.179（PDF p.198）印 dH/dt=Cp dT/dt+f(T,t)（本版 dQ/dt ↔ 源书 dH/dt）；正弦温度程序式源书未印，只有文字与图 3-8。图 build/_eq_p70.png / build/_src_up198_fb.png |
| `eq:ch03-rate` | 3-5 | 71 | up p.169-180 | 199 | 已核对一致 | up p.199 | 版面 (3-5) dα/dt=k(T)f(α) ⟺ dα/dT=(1/β)k(T)f(α)；源书书内 p.180（PDF p.199）印 dα/dT=(1/β)k(T)f(α)（未编号），本版右半逐字同形，左半为等价时间形式。图 build/_eq_p71.png / build/_src_up199_fb.png |
| `eq:ch03-arrh` | 3-6 | 71 | up p.169-180 | 199 | 改编补充 | up p.199-200 | 版面 (3-6) k(T)=A exp(−Ea/RT)；源书 §3.3（书内 p.180–181）只把 k(T) 称「速率常数的温度关系式」，未印 Arrhenius 形式。图 build/_eq_p71.png / build/_src_up199_fb.png |
| `eq:ch03-integral` | 3-7 | 71 | up p.169-180 | 199 | 改编补充 | up p.199-200 | 版面 (3-7) g(α)=∫0^α dα/f(α)=(A/β)∫0^T exp(−Ea/RT)dT；源书同节（书内 p.181 / PDF p.200）只印 Ozawa–Flynn–Wall、Kissinger、Freeman–Carroll 三式，无 g(α) 积分式。图 build/_eq_p71.png / build/_src_up200_fb.png |

### ch03-b（5/5 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch03b-tau` | 3-8 | 74 | up p.181-218 | 200-237 | 改编补充 | up p.220 | 版面 (3-8) τ≈V/Q；源书 §3.5 与 §3.5.1（书内 p.201 / PDF p.220）只定性写「分解产物直接进入红外光谱仪」，未提死体积/传输线滞后，无此式。图 build/_eq_p74.png / build/_src_up220_fb.png |
| `eq:ch03b-dT` | 3-9 | 74 | up p.181-218 | 200-237 | 改编补充 | up p.220 | 版面 (3-9) ΔT≈βτ；源书 §3.5 开篇与 §3.5.1（书内 p.201 / PDF p.220）只定性写 TG-IR 原理，未提死体积与滞后，无此式（仅图 3-31 标注升温速率 5 K/min）。图 build/_eq_p74.png / build/_src_up220_fb.png |
| `eq:ch03b-kissinger` | 3-10 | 75 | up p.181-218 | 200 | 形式一致但符号不同 | up p.200 | 版面 (3-10) d[ln(β/Tp²)]/d(1/Tp)=−E/R；源书书内 p.181（PDF p.200）印 d(ln(φ/Tp²))/d(1/Tp)=−E/R，本版 β ↔ 源书 φ（升温速率符号统一）。图 build/_eq_p75.png / build/_src_up200_fb.png |
| `eq:ch03b-dTp` | 3-11 | 75 | up p.181-218 | 200 | 改编补充 | up p.200 | 版面 (3-11) ΔTp≈(RTp²/E)ln(β2/β1)；源书书内 p.181（PDF p.200）只有三法作图步骤，无峰温对升温速率敏感度式。图 build/_eq_p75.png / build/_src_up200_fb.png |
| `eq:ch03b-dtg-area` | 3-12 | 76 | up p.181-218 | 195 | 改编补充 | up p.195 | 版面 (3-12) ∫[−d(m%)/dT]dT=20∫dα/dT dT=20 个百分点；源书第 3 章只在 §3.2.2（书内 p.176 / PDF p.195）给峰面积定义句，全章无 TG/DTG 积分恒等式。图 build/_eq_p76.png / build/_src_up195_fb.png |

### ch04-a（16/16 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:transgroup` | 4-1 | 82 | up p.219-243 | 244 | 已核对一致 | up p.242 | 版面 (4-1) T=ma+nb+pc、m,n,p=0,±1,±2,…；源书书内 p.223（PDF p.242）逐字同形（工作清单 hint_pdf 244 是对称元素表，非此式）。图 build/_eq_p82.png / build/_src_up242_fb.png |
| `eq:ka-weight` | 4-2 | 84 | up p.219-243 | 253 | 已核对一致 | up p.253 | 版面 (4-2) λ(Kα)=2/3λ(Kα1)+1/3λ(Kα2)；源书书内 p.234（PDF p.253）逐字同形，并给 I(Kα1):I(Kα2)=2:1。图 build/_eq_p84.png / build/_src_up253_fb.png |
| `eq:lambert` | 4-3 | 84 | up p.219-243 | 238-262 | 已核对一致 | up p.254 | 版面 (4-3) I=I0 e^{−μx}；源书书内 p.235（PDF p.254）印同式（未编号）。图 build/_eq_p84.png / build/_src_up254_fb.png |
| `eq:massabs` | 4-4 | 84 | up p.219-243 | 238-262 | 原书自身问题 | up p.254 | 版面 (4-4) I=I0 e^{−(μ/ρ)ρx}、μm=μ/ρ；源书书内 p.235（PDF p.254）印 I=I0 e^{(μ/ρ)ρx}=I0 e^{−μmρx}，中间式漏负号（与本页末式及 (4-3) 自相矛盾），本版按末式写正确形式。图 build/_eq_p84.png / build/_src_up254_band.png |
| `eq:massadd` | 4-5 | 84 | up p.219-243 | 238-262 | 已核对一致 | up p.255 | 版面 (4-5) μm=Σ_i wi μm,i；源书书内 p.236（PDF p.255）印 μm=Σ_{i=1}^{n} wi μmi（本版省略上下限、加逗号下标，同一式）。图 build/_eq_p84.png / build/_src_up255_fb.png |
| `eq:recipdef` | 4-6 | 85 | up p.219-243 | 255 | 已核对一致 | up p.257 | 版面 (4-6) a*·a=1、a*·b=0、a*·c=0；源书书内 p.238（PDF p.257）同式，另列出 b*、c* 两行（本版用 a→b→c 循环说明代替）。图 build/_eq_p85.png / build/_src_up257_fb.png |
| `eq:recipvec` | 4-7 | 85 | up p.219-243 | 257 | 已核对一致 | up p.257 | 版面 (4-7) a*=(b×c)/V、b*=(c×a)/V、c*=(a×b)/V；源书书内 p.238（PDF p.257）逐字同形，并给 V=a·(b×c)=b·(c×a)=c·(a×b)。图 build/_eq_p85.png / build/_src_up257_fb.png |
| `eq:laue-vec` | 4-8 | 86 | up p.219-243 | 258 | 已核对一致 | up p.259 | 版面 (4-8) (s−s0)/λ=H_hkl=ha*+kb*+lc*；源书书内 p.240（PDF p.259）印 S/λ−S0/λ=H_hkl=ha*+kb*+lc*。图 build/_eq_p86.png / build/_src_up259_fb.png |
| `eq:laue` | 4-9 | 86 | up p.219-243 | 258 | 已核对一致 | up p.260 | 版面 (4-9) a·Δs=hλ、b·Δs=kλ、c·Δs=lλ；源书书内 p.241（PDF p.260）印 a·(S−S0)=hλ、b·(S−S0)=kλ、c·(S−S0)=lλ（Δs≡s−s0）。图 build/_eq_p86.png / build/_src_up260_fb.png |
| `eq:bragg-ch04` | 4-10 | 86 | up p.219-243 | 258 | 已核对一致 | up p.263 | 版面 (4-10) 2d_hkl sinθ=nλ (n=1,2,3,…)；源书书内 p.244（PDF p.263）印 2d sinθ=nλ。图 build/_eq_p86.png / build/_src_up263_fb.png |
| `eq:cubic-d` | 4-11 | 86 | up p.219-243 | 263 | 已核对一致 | up p.263 | 版面 (4-11) 1/d_hkl²=(h²+k²+l²)/a² ⟹ d_hkl=a/√(h²+k²+l²)；源书书内 p.244（PDF p.263）立方系印 1/d²=(h²+k²+l²)/a²，本版 d 加下标 hkl 并解出 d（等价改写，源书未印后半）。图 build/_eq_p86.png / build/_src_up263_fb.png |
| `eq:cubic-sin2` | 4-12 | 86 | up p.219-243 | 263 | 改编补充 | up p.263-264 | 版面 (4-12) sin²θ=λ²(h²+k²+l²)/(4a²)；源书 §4.4.1（书内 p.244–245 / PDF p.263–264）只列立方/四方/正交/六方/单斜/三斜的 1/d² 形式，未见 sin²θ 工作公式，本式由 (4-11) 代入 Bragg 方程得出。图 build/_eq_p86.png / build/_src_up263_fb.png、build/_src_up264_fb.png |
| `eq:ewald-geom` | 4-13 | 86 | up p.219-243 | 263 | 已核对一致 | up p.259 | 版面 (4-13) OB=2(1/λ)sinθ ⟺ OB=1/d_hkl=\|H_hkl\|；源书书内 p.240（PDF p.259）印 BO=2OC=2(1/λ)sinθ，即 2(1/BO)sinθ=λ，与 2d_hkl sinθ=λ 比较得 BO=1/d_hkl=\|H\|。图 build/_eq_p86.png / build/_src_up259_fb.png |
| `eq:sf` | 4-14 | 87 | up p.219-243 | 259 | 已核对一致 | up p.268-269 | 版面 (4-14) F(hkl)=Σ_{j=1}^{N} fj exp[2πi(hxj+kyj+lzj)]=Σ fj e^{iφj}；源书书内 p.250（PDF p.269）印 F_hkl=Σ_i^n fi exp[2πi(hxi+kyi+lzi)]（i→j、n→N，同一求和）。图 build/_eq_p87.png / build/_src_up269_fb.png |
| `eq:phase` | 4-15 | 87 | up p.219-243 | 259 | 已核对一致 | up p.268 | 版面 (4-15) φj=2π(hxj+kyj+lzj)；源书书内 p.249（PDF p.268）印 φ=(Δ/λ)×2π=2π(hx+ky+lz)。图 build/_eq_p87.png / build/_src_up268_fb.png |
| `eq:intensity` | 4-16 | 87 | up p.219-243 | 268 | 已核对一致 | up p.264 | 版面 (4-16) I(hkl)∝\|F(hkl)\|²·LP·D·ΔV·j；源书书内 p.245（PDF p.264）简化式 I_hkl=K'·P·L·\|F_hkl\|²·D·ΔV·j（P、L 同量，本版按源书「合称 PL 因子」写 LP，比例号吸收 K'）。图 build/_eq_p87.png / build/_src_up264_fb.png |

### ch04-b（25/25 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch04b-bragg` | 4-17 | 89 |  p.— | 263 | 已核对一致 | up p.263 | 版面 (4-17) 2d_hkl sinθ=λ；源书书内 p.244（PDF p.263）印 2d sinθ=nλ；本版按 §4.4.1 已声明的约定把衍射级数 n 并入衍射指标（取 n=1），两式在该口径下一致。图 build/_eq_p89.png / build/_src_up263_fb.png |
| `eq:ch04b-Q` | 4-18 | 89 |  p.— | 263 | 改编补充 | up p.263-264 | 版面 (4-18) Q≡1/d_hkl²=\|H\|²；源书书内 p.244–245（PDF p.263–264）未印 Q 通式，只逐晶系给 1/d² 表达式并给 H=ha*+kb*+lc*，以 Q 标记统一是改编本的组织方式。图 build/_eq_p89.png / build/_src_up263_fb.png、build/_src_up264_fb.png |
| `eq:ch04b-triclinic` | 4-19 | 90 |  p.— | 264 | 形式一致但符号不同 | up p.264 | 版面 (4-19) Q=(1/V²)(S11h²+S22k²+S33l²+2S12hk+2S13hl+2S23kl)；源书书内 p.245（PDF p.264）三斜式印 1/d²=h²a*²+k²b*²+l²c*²+2hka*b*cosγ*+2klb*c*cosα*+2hla*c*cosβ*（倒易点阵常数），本版改用 Sij 与直接晶胞常数。图 build/_eq_p90.png / build/_src_up264_fb.png |
| `eq:ch04b-intensity` | 4-20 | 91 |  p.— | — | 已核对一致 | up p.264 | 版面 (4-20) I_hkl=K\|F_hkl\|²·P·L·j·D·ΔV、K=I0(e⁴/m²c⁴)(λ³/8πR²Vc²)；源书书内 p.245（PDF p.264）印展开式 I0(e⁴/m²c⁴)(λ³/8πR²Vc²)((1+cos²2θ)/2)(1/(sin²θcosθ))\|F\|²DΔVj 与简化式 K'·P·L·\|F\|²DΔVj，本版 K 与源书 K' 同义（角度因子与常数分列）。图 build/_eq_p91.png / build/_src_up264_fb.png |
| `eq:ch04b-PL` | 4-21 | 91 |  p.— | — | 已核对一致 | up p.264 | 版面 (4-21) P=(1+cos²2θ)/2、L=1/(2sin²θcosθ)、PL=(1+cos²2θ)/(4sin²θcosθ)；源书书内 p.245（PDF p.264）逐字同形，分母确为 4sin²θcosθ。图 build/_eq_p91.png / build/_src_up264_fb.png |
| `eq:ch04b-DW` | 4-22 | 91 |  p.— | 266 | 已核对一致 | up p.265 | 版面 (4-22) D=exp(−B sin²θ/λ²)、B=8π²U、U=⟨u²⟩；源书书内 p.246（PDF p.265）逐字同形，并注「指数中系数是 B 不是 2B」。图 build/_eq_p91.png / build/_src_up265_fb.png |
| `eq:ch04b-f` | 4-23 | 92 |  p.— | 267 | 已核对一致 | up p.267 | 版面 (4-23) f=E_a/E_e；源书书内 p.248（PDF p.267）逐字同形（E_a 为原子散射振幅、E_e 为自由电子散射振幅）。图 build/_eq_p92.png / build/_src_up267_fb.png |
| `eq:ch04b-fint` | 4-24 | 92 |  p.— | 267 | 形式一致但符号不同 | up p.267 | 版面 (4-24) f=∫_0^∞4πr²ρ(r)sin(4πr sinθ/λ)/(4πr sinθ/λ)dr；源书书内 p.248（PDF p.267）印 f=(4π/e)∫_0^∞r²ρ(r)(sin kr)/(kr)dr、k=4πsinθ/λ；源书多 1/e（其 ρ 取电子云密度），本版 ρ 取电子数密度，归一约定不同。图 build/_eq_p92.png / build/_src_up267_fb.png |
| `eq:ch04b-fpoly` | 4-25 | 94 |  p.— | 267 | 已核对一致 | up p.267 | 版面 (4-25) f=Σ_{i=1}^{4}ai exp[−bi(sinθ/λ)²]+c；源书书内 p.248（PDF p.267）印 f=Σai exp(−bi sin²θ/λ²)+c，同一式。图 build/_eq_p94.png / build/_src_up267_fb.png |
| `eq:ch04b-F` | 4-26 | 94 |  p.— | 267 | 已核对一致 | up p.269 | 版面 (4-26) F_hkl=Σ_{j=1}^{n} fj exp[2πi(hxj+kyj+lzj)]；源书书内 p.250（PDF p.269）印 F_hkl=Σ_i^n fi exp[2πi(hxi+kyi+lzi)]（i→j，同一求和）。图 build/_eq_p94.png / build/_src_up269_fb.png |
| `eq:ch04b-FT` | 4-27 | 94 |  p.— | 269 | 已核对一致 | up p.269 | 版面 (4-27) F_hkl=∫_{V_c}ρ(x,y,z)exp[2πi(hx+ky+lz)]dV；源书书内 p.250（PDF p.269）印 ∫_V ρ(x,y,z)exp[...]dV（V 即晶胞体积，本版写 V_c）。图 build/_eq_p94.png / build/_src_up269_fb.png |
| `eq:ch04b-I-extinct` | 4-28 | 94 |  p.— | 269 | 已核对一致 | up p.270 | 版面 (4-28) F_hkl=Σ_j fj exp[2πi(hxj+kyj+lzj)]{1+exp[πi(h+k+l)]}；源书书内 p.251（PDF p.270）体心格子印同式。图 build/_eq_p94.png / build/_src_up270_fb.png |
| `eq:ch04b-F-extinct` | 4-29 | 94 |  p.— | 271 | 已核对一致 | up p.270 | 版面 (4-29) F_hkl=Σ_j fj exp[2πi(hxj+kyj+lzj)]{1+e^{πi(h+k)}+e^{πi(h+l)}+e^{πi(k+l)}}；源书书内 p.251（PDF p.270）面心格子印同式。图 build/_eq_p94.png / build/_src_up270_fb.png |
| `eq:ch04b-Ii-V` | 4-30 | 96 |  p.— | 278 | 已核对一致 | up p.278 | 版面 (4-30) I_i=K_i v_i/μ_t；源书书内 p.259（PDF p.278）逐字同形（μ_t 为混体系总线吸收系数）。图 build/_eq_p96.png / build/_src_up278_fb.png |
| `eq:ch04b-Ii-w` | 4-31 | 97 |  p.— | 278 | 形式一致但符号不同 | up p.279 | 版面 (4-31) μ_m=Σ_i w_i μ_{m,i}、I_i=k_i w_i/μ_m、k_i=K_i/ρ_i；源书书内 p.260（PDF p.279）印 μ_mtρ_t=μ_t=Σv_iμ_i、I_i=K_i w_i/(ρ_i μ_mt)；本版把 K_i/ρ_i 记 k_i、μ_mt 记 μ_m（μ_m 质量加权式见书内 p.236）。图 build/_eq_p97.png / build/_src_up279_fb.png |
| `eq:ch04b-external` | 4-32 | 97 |  p.— | 278 | 已核对一致 | up p.279 | 版面 (4-32) w_i=I_i/I_i⁰；源书书内 p.260（PDF p.279）印同式（I_i⁰=(K_i/ρ_i)(1/μ_mi)）。图 build/_eq_p97.png / build/_src_up279_fb.png |
| `eq:ch04b-internal` | 4-33 | 97 |  p.— | 278 | 形式一致但符号不同 | up p.280 | 版面 (4-33) I_i/I_s=K w_i'/w_s'、w_i=w_i'/w0=w_i'/(1−w_s')；源书书内 p.261（PDF p.280）印 I_i/I_s=(K_i w_i'/ρ_i μ_mt')/(K_s w_s/ρ_s μ_mt')=K w_i'/w_s，本版给 s 相质量分数加撇并把 w_i'=w_i×w0 反解为 w_i。图 build/_eq_p97.png / build/_src_up280_fb.png |
| `eq:ch04b-RIR` | 4-34 | 97 |  p.— | 282 | 已核对一致 | up p.282 | 版面 (4-34) I_i/I_f=(K_i/K_f)(w_i/w_f)；源书书内 p.263（PDF p.282）逐字同形。图 build/_eq_p97.png / build/_src_up282_fb.png |
| `eq:ch04b-flushing` | 4-35 | 97 |  p.— | 282 | 已核对一致 | up p.282 | 版面 (4-35) w_i=(I_i/K_i)/Σ_{j=1}^{n}(I_j/K_j)；源书书内 p.263（PDF p.282）印 w_i=(K_i/I_i Σ_{j=1}^{n}I_j/K_j)^{-1}，与本版等价。图 build/_eq_p97.png / build/_src_up282_fb.png |
| `eq:ch04b-indexbase` | 4-36 | 99 |  p.— | 283 | 形式一致但符号不同 | up p.283 | 版面 (4-36) Q_hkl=f(h,k,l;a,b,c,α,β,γ)；源书书内 p.264（PDF p.283）印 d_hkl=f(h,k,l,a,b,c,α,β,γ)，本版以 Q_hkl 作自变量（源书用 d_hkl）。图 build/_eq_p99.png / build/_src_up283_fb.png |
| `eq:ch04b-cubicratio` | 4-37 | 99 |  p.— | 283 | 形式一致但符号不同 | up p.284 | 版面 (4-37) Q_i/Q_1=(h_i²+k_i²+l_i²)/(h_1²+k_1²+l_1²)；源书书内 p.265（PDF p.284）印 Q_i/Q_j=(h_i²+k_i²+l_i²)/(h_j²+k_j²+l_j²)，本版取其 j=1 的特例。图 build/_eq_p99.png / build/_src_up284_fb.png |
| `eq:ch04b-HL` | 4-38 | 100 |  p.— | 285 | 已核对一致 | up p.285 | 版面 (4-38) q_hkl≡sin²θ_hkl=(λ²/4)(h²/a²+k²/b²+l²/c²)=Ah²+Bk²+Cl²、A=λ²/4a²、B=λ²/4b²、C=λ²/4c²；源书书内 p.266（PDF p.285）逐项同形。图 build/_eq_p100.png / build/_src_up285_fb.png |
| `eq:ch04b-dicvol` | 4-39 | 101 |  p.— | 287 | 已核对一致 | up p.287 | 版面 (4-39) Q⁻(hkl)=(h²+k²+l²)/[a0+(n+1)p]²、Q⁺(hkl)=(h²+k²+l²)/[a0+np]²；源书书内 p.268（PDF p.287）逐字同形。图 build/_eq_p101.png / build/_src_up287_fb.png |
| `eq:ch04b-M20` | 4-40 | 101 |  p.— | 287 | 已核对一致 | up p.287 | 版面 (4-40) M20=Q20/(2\|ΔQ\|N20)；源书书内 p.268（PDF p.287）印 M20=Q20/(2ε̄N20)、ε̄=(1/20)Σ_{i=1}^{20}\|ΔQi\|，本版 \|ΔQ\| 即 ε̄。图 build/_eq_p101.png / build/_src_up287_fb.png |
| `eq:ch04b-FN` | 4-41 | 101 |  p.— | 287 | 已核对一致 | up p.288 | 版面 (4-41) F_N=(1/\|Δ2θ\|)(N_obs/N_poss)；源书书内 p.269（PDF p.288）印 F_N=(1/\|Δ2θ\|)(N/N_预测)，N_obs=N、N_poss=N_预测。图 build/_eq_p101.png / build/_src_up288_fb.png |

### ch04-c（24/24 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch04c-delta` | 4-42 | 103 |  p.— | 289 | 已核对一致 | up p.289 | 版面 (4-42) 2d sinθ=nλ、2d sin(θ+δ)=nλ+Δl；源书书内 p.270（PDF p.289）逐字同形。图 build/_eq_p103.png / build/_src_up289_fb.png |
| `eq:ch04c-approx` | 4-43 | 103 |  p.— | 289 | 已核对一致 | up p.290 | 版面 (4-43) (p/2)·2d[sin(θ+δ)−sinθ]=λ/2 ⟹ Dδcosθ=λ/2；源书书内 p.271（PDF p.290）分步印 (p/2)2d sin(θ+δ)=(p/2)nλ+λ/2 与 (p/2)2d sinθ=(p/2)nλ，相减即本版式（D 记 D_hkl）。图 build/_eq_p103.png / build/_src_up290_fb.png |
| `eq:ch04c-dphi` | 4-44 | 103 |  p.— | 290 | 已核对一致 | up p.291 | 版面 (4-44) Δl=2d sin(θ+δ)−nλ=2δdcosθ、Δφ=2πΔl/λ=4πdδcosθ/λ；源书书内 p.272（PDF p.291）把 Δl 定义为总光程差 2d sin(θ+δ)=nλ+2δdcosθ、Δφ₀=2πΔl/λ=2nπ+4πdδcosθ/λ，取周期后得同一 Δφ₀=4πdδcosθ/λ。图 build/_eq_p103.png / build/_src_up291_fb.png |
| `eq:ch04c-sum` | 4-45 | 103 |  p.— | 290 | 已核对一致 | up p.291-292 | 版面 (4-45) E=E0Σ_{k=0}^{p−1}e^{ikΔφ}=E0 sin(pΔφ/2)/sin(Δφ/2)·e^{i(p−1)Δφ/2}、I∝[sin(pΔφ/2)/(p sin(Δφ/2))]²；源书书内 p.272（PDF p.291）印 E=E0[sin(pΔφ0/2)/sin(Δφ0/2)]（无相位因子）、p.273（PDF p.292）印 I/Imax=sin²(Φ/2)/(Φ/2)²（小角近似），本版补相位因子并写精确归一化，小角下与源书同。图 build/_eq_p103.png / build/_src_up291_fb.png、build/_src_up292_fb.png |
| `eq:ch04c-u` | 4-46 | 103 |  p.— | 290 | 已核对一致 | up p.292 | 版面 (4-46) u=pΔφ/2=2πDδcosθ/λ=1.40 ⟹ Dδcosθ=1.40λ/2π；源书书内 p.273（PDF p.292）印 Φ=pΔφ0=4πδpd cosθ/λ=2×1.40、Φ/2=1.40（本版 u 即 Φ/2）。图 build/_eq_p103.png / build/_src_up292_fb.png |
| `eq:ch04c-scherrer` | 4-47 | 103 |  p.— | 290 | 已核对一致 | up p.292 | 版面 (4-47) β_hkl=(4×1.40/2π)(λ/(D_hkl cosθ))、D_hkl=Kλ/(β_hkl cosθ)、K=(4×1.40)/2π=0.891≈0.89；源书书内 p.273（PDF p.292）印 β_hkl=4δ 与 β_hkl=0.89λ/(D_hkl cosθ)，本版把 K=4×1.40/2π 显式写出并给反解式。图 build/_eq_p103.png / build/_src_up292_fb.png |
| `eq:ch04c-conv` | 4-48 | 104 |  p.— | 294 | 改编补充 | up p.293 | 版面 (4-48) h(x)=∫g(x')f(x−x')dx'；源书书内 p.274（PDF p.293）只用文字说「衍射谱可以看成仪器因子 g(x) 与晶粒因子 f(x) 的卷积」，未印卷积积分式。图 build/_eq_p104.png / build/_src_up293_fb.png |
| `eq:ch04c-subtract` | 4-49 | 104 |  p.— | 294 | 改编补充 | up p.293 | 版面 (4-49) Gauss 型 B²=b²+β² ⟹ β=√(B²−b²)；Lorentz 型 B=b+β ⟹ β=B−b；源书书内 p.274（PDF p.293）只说「可以忽略仪器因素，或者简单地减去仪器引起的半峰宽」，未印这两式。图 build/_eq_p104.png / build/_src_up293_fb.png |
| `eq:ch04c-doublet` | 4-50 | 105 |  p.— | 294 | 已核对一致 | up p.294 | 版面 (4-50) Δ(2θ)=2Δλ/λ·tgθ；源书书内 p.275（PDF p.294）印 Δ(2θ)=2Δλ/λ_Kα·tgθ（本版分母写 Kα 加权平均 λ）。图 build/_eq_p105.png / build/_src_up294_fb.png |
| `eq:ch04c-doubletnum` | 4-51 | 105 |  p.— | 294 | 原书自身问题 | up p.295 | 版面 (4-51) Δ(2θ)/°≈0.28 tgθ；源书书内 p.276（PDF p.295）印 Δ(2θ)=2Δλ/λ_Kα·tgθ=0.2246tgθ，按其同页自身数据复算 2×0.38/154.18=4.93×10⁻³ rad=0.2824°（即 0.28 tgθ），印刷系数 0.2246 与自身数据不符，本版按复算值写并记原书笔误。图 build/_eq_p105.png / build/_src_up295_fb.png |
| `eq:ch04c-rachinger` | 4-52 | 105 |  p.— | 294 | 已核对一致 | up p.296 | 版面 (4-52) I_i(α1)=I_i−½I_{i−3}(α1)、i=4,5,6,…；源书书内 p.277（PDF p.296）印 I_i(α1)=I_i−1/2I_{i−3}(α1) 及 I4、I5、I6 各步。图 build/_eq_p105.png / build/_src_up296_fb.png |
| `eq:ch04c-halving` | 4-53 | 106 |  p.— | 297 | 改编补充 | up p.297 | 版面 (4-53) D'=Kλ/(Bcosθ)≈Kλ/(2βcosθ)=D/2（Lorentz 型极限 B=b+β、b≈β）；源书 §4.7 末（书内 p.278 / PDF p.297）只给适宜范围 2~20 nm 与注意事项，未印此推导。图 build/_eq_p106.png / build/_src_up297_fb.png |
| `eq:ch04c-WH` | 4-54 | 106 |  p.— | 297 | 改编补充 | up p.297 | 版面 (4-54) β_hkl=Kλ/(Dcosθ)+4ε tgθ ⟺ βcosθ=Kλ/D+4ε sinθ；源书 §4.7 末尾（书内 p.278 / PDF p.297）只有一句「如果存在晶格畸变，则需要分离畸变和晶粒大小的效应」，未印 WH 关系式。图 build/_eq_p106.png / build/_src_up297_fb.png |
| `eq:ch04c-ihkl` | 4-55 | 108 |  p.— | 300 | 已核对一致 | up p.300 | 版面 (4-55) I_hkl=K·P·L·\|F_hkl\|²·D·ΔV·J；源书书内 p.281（PDF p.300）逐字同形。图 build/_eq_p108.png / build/_src_up300_fb.png |
| `eq:ch04c-rietconv` | 4-56 | 108 |  p.— | 300 | 已核对一致 | up p.300 | 版面 (4-56) Y_c,j=I_hkl⊗Ω_j；源书书内 p.281（PDF p.300）印 Y_c,j=I_hkl⊗Ω（本版给 Ω 加下标 j 与 Y_c,j 对应）。图 build/_eq_p108.png / build/_src_up300_fb.png |
| `eq:ch04c-rietveld` | 4-57 | 108 |  p.— | 300 | 形式一致但符号不同 | up p.300 | 版面 (4-57) Y_ic=A(2θi)Σ_n S_nΣ_h I_n,hklΩ_n(2θi−2θB)+Y_ib(2θi)；源书书内 p.281（PDF p.300）印 Y_i,c=A(2θi)Σ_n S_nΣ_h I_n,hklΩ_n(2θi−2θB)+Y_b(2θi)，本版按本节惯例把 Y_i,c、Y_b 写作 Y_ic、Y_ib。图 build/_eq_p108.png / build/_src_up300_fb.png |
| `eq:ch04c-rwp` | 4-58 | 111 |  p.— | 301 | 形式一致但符号不同 | up p.301 | 版面 (4-58) R_wp=[Σ_i w_i(Y_io−Y_ic)²/Σ_i w_i Y_io²]^{1/2}、w_i=1/σi²=1/Y_io；源书书内 p.282（PDF p.301）印 R_wp=[Σ_{i=1}^{n}w_i(Y_i−Y_i,c)²/Σ w_i Y_i²]^{1/2}、w_i=1/σi²、σi=√Y_i（本版 Y_i→Y_io、Y_i,c→Y_ic）。图 build/_eq_p111.png / build/_src_up301_fb.png |
| `eq:ch04c-rpexp` | 4-59 | 111 |  p.— | 301 | 形式一致但符号不同 | up p.301 | 版面 (4-59) R_p=Σ_i\|Y_io−Y_ic\|/Σ_i Y_io、R_exp=[(N−P)/Σ_i w_i Y_io²]^{1/2}；源书书内 p.282（PDF p.301）印 R_p=Σ\|Y_i−Y_i,c\|/Σ\|Y_i\|、R_exp=[(N−P)/Σ w_i Y_i²]^{1/2}（本版 Y_i→Y_io、Y_i,c→Y_ic）。图 build/_eq_p111.png / build/_src_up301_fb.png |
| `eq:ch04c-gof` | 4-60 | 111 |  p.— | 301 | 已核对一致 | up p.301 | 版面 (4-60) GOF=R_wp/R_exp=[Σ_i w_i(Y_io−Y_ic)²/(N−P)]^{1/2}、χ²=(R_wp/R_exp)²；源书书内 p.282（PDF p.301）印 GOF=R_wp/R_exp 与展开式（本版另补 χ² 等价关系，源书未印）。图 build/_eq_p111.png / build/_src_up301_fb.png |
| `eq:ch04c-sial` | 4-61 | 113 |  p.— | 305 | 已核对一致 | up p.305 | 版面 (4-61) n_Si/n_Al=(25.858−a)/(a−24.191)；源书书内 p.286（PDF p.305）逐字同形。图 build/_eq_p113.png / build/_src_up305_fb.png |
| `eq:ch04c-sialsens` | 4-62 | 113 |  p.— | 305 | 改编补充 | up p.305 | 版面 (4-62) d(Si/Al)/da=−1.667/(a−24.191)²；源书书内 p.286（PDF p.305）只给 (4-61) 与「可以通过晶胞参数变化推测硅铝比」，未作灵敏度讨论、无微分式。图 build/_eq_p113.png / build/_src_up305_fb.png |
| `eq:ch04c-rir` | 4-63 | 113 |  p.— | 305 | 已核对一致 | up p.306 | 版面 (4-63) w_M=I_M(220)/(K I_C(110)+I_M(220))×100%=I_M(220)/(0.79I_C(110)+I_M(220))×100%；源书书内 p.287（PDF p.306）印 w_M=I_M(220)/(0.79I_C(110)+I_M(220))×100%，并给 I_M/I_C=K w_M/w_C、w_M+w_C=1。图 build/_eq_p113.png / build/_src_up306_fb.png |
| `eq:ch04c-znod` | 4-64 | 114 |  p.— | 297 | 已核对一致 | up p.308 | 版面 (4-64) D_100=0.89×1.5406/(0.0026×0.9619) Å=1.3711/0.002501 Å≈548 Å≈55 nm；源书书内 p.289（PDF p.308）给 Ω(x)=1/(1+k²x²)、k²=4/β² 与 β_hkl=0.89λ/(D_hkl cosθ)，按 λ=1.5406 Å、2θ=31.7° 得 D_100=55 nm，与本节数值一致（中间量 548 Å 为本版补算）。图 build/_eq_p114.png / build/_src_up308_fb.png |
| `eq:ch04c-debye` | 4-65 | 116 |  p.— | 314 | 原书自身问题 | up p.314 | 版面 (4-65) \|F(hkl)\|²=Σ_iΣ_j f_i f_j sin(Q r_ij)/(Q r_ij)、Q=4πsinθ/λ；源书书内 p.295（PDF p.314）印 \|F(hkl)\|²=Σ_j f_j²+Σ_iΣ_{j≠i} f_i f_j*·2sin(2πr_ij)/(2πr_ij)，偏角只有 r_ij、缺 sinθ/λ 因子，量纲不成立，本版按 Q=4πsinθ/λ 写（自项 i=j 即源书 Σf_j² 项）。图 build/_eq_p116.png / build/_src_up314_fb.png |

### ch05-a（7/7 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch05-kd` | 5-1 | 118 | up p.301-319 | 322 | 改编补充 | up p.330 | 源书 (5-37) 印 N=−V_m dθ/dt=A θ^n exp[−E_d(θ)/RT]（含频率因子 A 与 E_d），未单列速率常数式；本版 k_d=A exp(−E_d/RT) 系把该因子拆出并取 E_d 为常量，属教学化改写。图 build/_m_ch05a1.png、build/_src330.png。 |
| `eq:ch05-pulse` | 5-2 | 120 | up p.301-319 | 332 | 形式一致但符号不同 | up p.332 | 本版 V_吸=V0/A0[(A0−A1)+(A0−A2)+(A0−A3)+⋯]；源书 (5-38) 印 V=V0/A0[(A0−A1)+(A0−A2)+(A0−A3)+⋯]，逐项同形，仅吸附量记号 V→V_吸。图 build/_cmp_test.png。 |
| `eq:ch05-peak` | 5-3 | 121 | up p.301-319 | 334 | 改编补充 | up p.334 | 源书 (5-52)—(5-54) 只按一级脱附印 (k_d)_M=βE_d/RT_M² 与 (k_d)_M=A exp(−E_d/RT_M)=βE_d/RT_M²；本版 n 阶通式 E_d/(RT_m²)=(A/β)nθ_m^{n−1}exp(−E_d/(RT_m)) 中的 nθ_m^{n−1} 因子为改编本所加。图 build/_m_ch05a2.png。 |
| `eq:ch05-redhead` | 5-4 | 121 | up p.301-319 | 334 | 形式一致但符号不同 | up p.334 | 本版 E_d/(RT_m²)=(A/β)exp(−E_d/(RT_m))；源书 (5-54) 印 (k_d)_M=A exp(−E_d/RT_M)=βE_d/RT_M²，移项等价，下标 M→m。图 build/_m_ch05a2.png。 |
| `eq:ch05-tpr` | 5-5 | 122 | up p.301-319 | 338 | 形式一致但符号不同 | up p.336 | 源书 (5-56) 印 dα/dt=K[G]^p[S]^q、(5-57) K=A exp(−E/RT)、(5-58) β=dT/dt；本版合并为 r=dα/dt=k f(α)、k=A exp(−E_a/RT)、β=dT/dt（K→k、E→E_a，浓度项并入 f(α)）。图 build/_m_ch05a3.png。 |
| `eq:ch05-tpr-peak` | 5-6 | 122 | up p.301-319 | 338 | 形式一致但符号不同 | up p.338 | 源书 (5-71) 印 E/RT_M²=[A[G]_M^p q[S]_M^{q−1}/β]exp(−E/RT)、(5-72) 印 2lnT_M−lnβ+p ln[G]_M+(q−1)ln[S]_M=E/RT_M+常数；本版同 (5-72)，T_M→T_m、E→E_a。图 build/_m_ch05a3.png。 |
| `eq:ch05-tpr-peak-q1` | 5-7 | 122 | up p.301-319 | 338 | 形式一致但符号不同 | up p.338 | 本版 2lnT_m−lnβ+p ln[G]_M=E_a/(RT_m)+常数；源书 (5-73) 同式，T_M→T_m、E→E_a。图 build/_m_ch05a4.png。 |

### ch05-b（3/3 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch05b-area` | 5-8 | 123 |  p.— | — | 改编补充 | up p.331-332 | 源书 p.331—332 只印脉冲标定式 (5-38) V=V0/A0[(A0−A1)+⋯] 与峰面积定性说明，无 n_des/m=(F/(k_Aβm))∫A(T)dT 积分式；本版为按定义的改写。图 build/_m_ch05a4.png。 |
| `eq:ch05b-redhead` | 5-9 | 123 |  p.— | — | 形式一致但符号不同 | up p.334 | 源书 (5-54) 印 (k_d)_M=A exp(−E_d/RT_M)=βE_d/RT_M²（本版箭头左式，A↔ν、M↔p），(5-55) 印精确式 2lnT_M−lnβ=E_d/RT_M+ln(E_d/AR)；本版右端 −3.64 为 Redhead 近似，源书无此常数。图 build/_m_ch05a5.png。 |
| `eq:ch05b-sens` | 5-10 | 123 |  p.— | — | 改编补充 | up p.334 | 源书 p.334 只印 (5-54)(5-55)，无 ∂T_p/∂lnβ 与 δE_d=RT_pδlnν 两条灵敏度式；本版由式 (5-9) 微分补出。图 build/_m_ch05a5.png。 |

### ch06-a（9/9 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:raman-shift` | 6-1 | 132 | up p.343-372 | 364 | 改编补充 | up p.365 | 源书 p.365 只用文字定义「瑞利线与斯托克斯线频率的差值称为拉曼位移」，未印 Δν̃=(ν0−νs)/c=νm/c；本版为公式化改写。图 build/_m_ch06a.png。 |
| `eq:incident-field` | 6-2 | 133 | up p.343-372 | 393 | 已核对一致 | up p.365 | 源书 p.365 原印 E=E0cos2πν0t；本版同式，仅逗号排版差异。图 build/_m_ch06a.png。 |
| `eq:induced-dipole` | 6-3 | 134 | up p.343-372 | 366 | 已核对一致 | up p.366 | 源书 p.366 原印 p=αE 与 p=αE0cos2πν0t；本版同两式，仅用粗体表张量/矢量。图 build/_m_ch06a.png。 |
| `eq:alpha-expansion` | 6-4 | 134 | up p.343-372 | 366 | 改编补充 | up p.366 | 源书 p.366 只印一阶展开 α=α0+(∂α/∂q)_0 q+⋯，q=q0cos2πνm t 仅在 prose 中给出；本版补二阶项 (1/2)(∂²α/∂q²)_0 q² 并把 q(t) 并入展示式。图 build/_m_ch06a.png。 |
| `eq:three-terms` | 6-5 | 134 | up p.343-372 | 366 | 形式一致但符号不同 | up p.366 | 源书 p.366 把三项合写为 P=α0E0cos2πν0t+(1/2)(∂α/∂q)_0 q0E0[cos2π(ν0−νm)t+cos2π(ν0+νm)t]+⋯；本版拆成 p_瑞利、p_反斯托克斯、p_斯托克斯 三行并加中文下标，P→p。图 build/_m_ch06b.png。 |
| `eq:classical-intensity` | 6-6 | 134 | up p.343-372 | 366 | 改编补充 | up p.366 | 源书 p.366 印 I=k'_ω ω_s^4 p² sin²θ（k'_ω=1/(32π²ε0c0³)）；本版改用辐照度/微分散面口径 P_sc=E0(dσ/dΩ)ΔΩ、E0=P0/A_beam，源书无此式。图 build/_m_ch06b.png。 |
| `eq:dipole-dcs` | 6-7 | 134 | up p.343-372 | 366 | 形式一致但符号不同 | up p.366 | 本版 dσ/dΩ=K sin²θ（K=(dσ/dΩ)\|θ=90°）；源书 p.366 的 I=k'_ωω_s^4p²sin²θ 与之对应，k'_ωω_s^4p²↔K、I↔dσ/dΩ，属口径改名。图 build/_m_ch06b.png。 |
| `eq:classical-intensity-ratio` | 6-8 | 134 | up p.343-372 | 366 | 改编补充 | up p.366 | 源书 p.366 无 P_sc/P0=(dσ/dΩ)(ΔΩ/A_beam)=K sin²θ ΔΩ/A_beam 这条比值式；本版为量纲自洽改写。图 build/_m_ch06b.png。 |
| `eq:stokes-ratio` | 6-9 | 135 | up p.343-372 | 367 | 改编补充 | up p.367 | 源书 p.367 只有定性句「常温下…斯托克斯线比反斯托克斯线强得多」，未印 I_as/I_s 强度比式；本版按标准形式补出（书内 p.350/PDF p.369 另给反斯托克斯强度式，非此比值）。图 build/_m_ch06c.png。 |

### ch06-b（2/2 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:resonance-cross` | 6-10 | 141 | up p.373-412 | 394 | 已核对一致 | up p.395 | 源书 p.395（书内 p.376）原印 σ∝1/(hν0−hνm)(hν0+hνm)；本版同式，仅分母加括号排版差异。图 build/_m_ch06c.png。 |
| `eq:sers-two` | 6-11 | 148 | up p.373-412 | 397 | 改编补充 | up p.397 | 源书 p.397（书内 p.378）只在 prose 中写「P=αE 中的 E 增大」「P=αE 中的 α 增大」，未印带两种机制标注的编号式；本版把 P=αE 提出并加注。图 build/_m_ch06c.png。 |

### ch07-a（7/7 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:art` | 7-1 | 162 | up p.413-447 | 436 | 已核对一致 | up p.436 | 源书 p.436（书内 p.417）原印 A+R+T=1；本版同式。图 build/_src436.png、build/_m_ch07prod1.png。 |
| `eq:beer` | 7-2 | 163 | up p.413-447 | 436 | 改编补充 | up p.436 | 源书 p.436 只印 A+R+T=1 与三项贡献说明，无 Beer–Lambert 式（全章 OCR 无「比尔/朗伯/吸光系数」）；本版 A=lg(I0/I)=εcl 为改编补充。图 build/_src436.png、build/_m_ch07prod1.png。 |
| `eq:interferogram` | 7-3 | 163 | up p.413-447 | 441 | 形式一致但符号不同 | up p.443 | 本版 I(δ)=1/2∫0∞B(ν̃)[1+cos(2πν̃δ)]dν̃；源书 p.443（书内 p.424）印 I'(δ)=∫0∞0.5I(ν)[1+cos(2πνδ)]dν，0.5 在积分号内、I(ν)→B(ν̃)、ν→ν̃，等价。图 build/_src443.png、build/_m_ch07prod1.png。 |
| `eq:km` | 7-4 | 165 | up p.413-447 | 446 | 已核对一致 | up p.446 | 源书 p.446（书内 p.427）原印 K/S=(1−R∞)²/(2R∞)；本版同式。图 build/_src446.png、build/_m_ch07prod1.png。 |
| `eq:crit` | 7-5 | 166 | up p.413-447 | 447 | 已核对一致 | up p.451 | 源书 p.451（书内 p.432）在正文内印 sinθc=n2/n1；本版单列并补 (n1>n2)，形式一致。图 build/_src451.png、build/_m_ch07prod1.png。 |
| `eq:dpen` | 7-6 | 166 | up p.413-447 | 451 | 原书自身问题 | up p.451 | 源书 p.451 印 d_p=λ1/(2πn1√(sin²θ−(n2/n1)²)) 并定义 λ1 为「反射介质中的波长」；若 λ1=λ0/n1 则分母不应再有 n1，原书符号定义自相矛盾。本版改印 d_p=λ0/(2π√(n1²sin²θ−n2²))（λ0 为真空波长），按倏逝场 1/e 定义消除该矛盾。图 build/_src451.png、build/_m_ch07prod1.png。 |
| `eq:nref` | 7-7 | 166 | up p.413-447 | 452 | 已核对一致 | up p.452 | 源书 p.452（书内 p.433）原印 N=(l/d)cotθ；本版同式。图 build/_src452_n.png、build/_m_ch07prod1.png。 |

### ch07-b（9/9 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch07b-beer` | 7-8 | 169 |  p.448-488 | 463 | 改编补充 | up p.463 | 源书 p.463（书内 p.444）只以文字说「强度定数量、定量建立在朗伯—比尔定律之上」，未印 A=εcl（全册 OCR 无「比尔/朗伯/吸光系数」）；本版式 (7-8) 为改编补充。图 build/_src463.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-co-abs` | 7-9 | 171 |  p.448-488 | 468 | 形式一致但符号不同 | up p.470 | 本版 A_CO=K_CO S_CO(Pt) x_s；源书 p.470（书内 p.451）印 A_CO=K_CO·S_CO(Pt)_s，括号外下标 s 即表面分数，本版把表面分数改写为 x_s。图 build/_src470.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-no-abs` | 7-10 | 171 |  p.448-488 | 468 | 形式一致但符号不同 | up p.470 | 本版 A_NO=K_NO S_NO(Ru)(1−x_s)；源书 p.470 印 A_NO=K_NO·S_NO(Ru)_s，本版把表面分数改写为 1−x_s（归一化写法）。图 build/_src470.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-ratio` | 7-11 | 171 |  p.448-488 | 470 | 改编补充 | up p.470 | 源书 p.470 只写 A_CO/A_NO∝Pt_b/Ru_b（对体相组成作图成直线），未印本版这条显式比值式；本版由 (7-9)(7-10) 相除得出，属改编补充。图 build/_src470.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-morse-levels` | 7-12 | 174 |  p.448-488 | 484 | 形式一致但符号不同 | up p.489 | 本版 G(v)=ωe(v+1/2)−ωe xe(v+1/2)²；源书 p.489（书内 p.470）式 (7-1) 印 W_x=W_e(n+1/2)−W_eX(n+1/2)²，W_x→G(v)、W_e→ωe、X→x_e、n→v。图 build/_src489.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-morse` | 7-13 | 174 |  p.448-488 | 489 | 形式一致但符号不同 | up p.489 | 本版 U(r)=D[e^{−β(r−re)}−1]²；源书 p.489（书内 p.470）式 (7-2) 印 U(r)=D[e^{−β(γ−γ0)}−1]²，γ→r、γ0→re（源书把 γ 称平均距离、γ0 称瞬间距离）。图 build/_src489.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-morse-params` | 7-14 | 174 |  p.448-488 | 489 | 形式一致但符号不同 | up p.489 | 本版 β=2.48×10⁷(ωe xe μ)^0.5、D=ωe/(4xe)；源书 p.489 印 β=2.48×10⁷(W_eX_eμ)^0.5、D=W_e/(4X)，W_e→ωe、X_e/X→x_e（源书 β 用 X_e、D 用 X，下标不统一，本版统一为 x_e）。图 build/_src489.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-D0` | 7-15 | 174 |  p.448-488 | 467-507 | 原书自身问题 | up p.490 | 源书 p.490（书内 p.471）式 (7-3) 印 D0=W_e/(4X)−W_e/2，同页稍后又印「又 D0=W_e/4X」（无 −W_e/2），源书自身两版并存。本版 D0=ωe²/(4ωe xe)=ωe/(4xe) 取后者（亦与本版式 7-8 的 D_eff 推导一致），未取 (7-3) 的零点能项。图 build/_src490.png、build/_src490_d0.png、build/_m_ch07prod2.png。 |
| `eq:ch07b-combination` | 7-16 | 175 |  p.448-488 | 467-507 | 形式一致但符号不同 | up p.491 | 本版 (v+δ)=v_OH+δ_OH−X12（并另列 (2v+δ)=v_OH+δ_OH−2X12）；源书 p.491（书内 p.472）式 (7-10) 印 ν^{OH}_{ν+δ}=ν^{OH}_{0→1}+δ^{OH}_{0→1}−X12、式 (7-11) 印 ν^{OH}_{2ν+δ}=ν^{OH}_{0→1}+δ^{OH}_{0→1}−2X12，逐项同形，仅记号简化。图 build/_src491_d.png、build/_m_ch07prod3.png。 |

### ch07-c（2/2 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch07c-km` | 7-18 | 179 |  p.489-518 | 512 | 改编补充 | up p.512 | 源书 p.512（书内 p.493）已转入 WO3/Al2O3 与 §7.5.4，未讨论 Kubelka–Munk 变换（源 OCR 全文无 Kubelka/Munk），无对应编号式；本版 F(R∞)=(1−R∞)²/(2R∞)=K/S 为学科标准形式补入。图 build/_src512.png、build/_m_ch07prod3.png。 |
| `eq:ch07c-isotope` | 7-19 | 183 |  p.489-518 | 518 | 改编补充 | up p.518 | 源书 p.518（书内 p.499）只印 DCOOD 同位素位移数据（ν_OH^s=2650、ν_CD^s=2200、β_CD=1029 cm⁻¹ 等），未印 ν̃=1/(2πc)√(k/μ)、μ 与 ν̃(XD)/ν̃(XH) 比式；本版按谐振近似补出。图 build/_src518.png、build/_m_ch07prod3.png。 |

### ch08-a（0/8 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:csatensor` | 8-1 | 190 | down p.525-543 | 21 | 未覆盖 | — |  |
| `eq:sigma1` | 8-2 | 191 | down p.525-543 | 21 | 未覆盖 | — |  |
| `eq:magic` | 8-3 | 191 | down p.525-543 | 21 | 未覆盖 | — |  |
| `eq:dipolar` | 8-4 | 191 | down p.525-543 | 22 | 未覆盖 | — |  |
| `eq:hh` | 8-5 | 192 | down p.525-543 | 23 | 未覆盖 | — |  |
| `eq:hhquad` | 8-6 | 192 | down p.525-543 | 22 | 未覆盖 | — |  |
| `eq:zeolite` | 8-7 | 192 | down p.525-543 | 23 | 未覆盖 | — |  |
| `eq:sial` | 8-8 | 193 | down p.525-543 | 23 | 未覆盖 | — |  |

### ch08-b（0/5 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:brunner-iso` | 8-9 | 196 | down p.540-550 | 33 | 未覆盖 | — |  |
| `eq:brunner-hb` | 8-10 | 196 | down p.540-550 | 33 | 未覆盖 | — |  |
| `eq:ernst` | 8-11 | 200 | down p.540-550 | 32-42 | 未覆盖 | — |  |
| `eq:xe-shift` | 8-12 | 201 | down p.540-550 | 38 | 未覆盖 | — |  |
| `eq:fraissard` | 8-13 | 202 | down p.540-550 | 39 | 未覆盖 | — |  |

### ch09-a（6/6 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:sampling-depth` | 9-1 | 214 | down p.567-615 | 73 | 已核对一致 | down p.582 | 版面 (9-1) $d=3\lambda\cos\theta$（build/_f4/p214.png）；源书 (9-2) 书内 p.582 / PDF p.73（build/_f4/d73.png）同式 $d=3\lambda\cos\theta$。源式号比本版大 1，因源 (9-1) 是 XPS 基本方程，编号不影响内容。 |
| `eq:imfp` | 9-2 | 214 | down p.567-615 | 73 | 原书自身问题 | down p.583 | 版面 (9-2) 三行 cases：$538E^{-2}+0.41(\delta E)^{1/2}$、$2170E^{-2}+0.72(\delta E)^{1/2}$、$49E^{-2}+0.11E^{1/2}$（build/_f4/p214.png）；源书 (9-3a—9-3c) 书内 p.583 / PDF p.74（build/_f4/d74.png）印 $\lambda^*=538E^{-2}+0.41(\delta E)^{1/2}$、$\lambda^*=2170E^{-2}+0.72(\delta E)$、$\lambda^{**}=49E^{-2}+0.11E^{1/2}$。源书无机一行漏 $1/2$ 次方，本版已按 Seah–Dench 原式改为 $(\delta E)^{1/2}$ 并在 ch09-a.tex:116-118 说明，判原书自身问题。 |
| `eq:xps` | 9-3 | 215 | down p.567-615 | 70 | 已核对一致 | down p.579 | 版面 (9-3) $E_{\mathrm k}=h\nu-E_{\mathrm B}-\phi_{\mathrm{sp}}$（build/_f4/p215.png）；源书 (9-1) 书内 p.579 / PDF p.70（build/_f4/d70.png）印 $E_k=h\nu-E_b-\Phi_{sp}$。仅下标大小写与 $\Phi/\phi$ 写法不同（源 $E_b$、$\Phi_{sp}$ ↔ 本版 $E_B$、$\phi_{sp}$），结构与各项一致。 |
| `eq:jsplit` | 9-4 | 216 | down p.567-615 | 75 | 已核对一致 | down p.584 | 版面 (9-4) $j=\|l\pm1/2\|$（build/_f4/p216.png）；源书 书内 p.584 / PDF p.75（build/_f4/d75.png）同式未编号，印 $j=\|l+m_s\|=\|l\pm1/2\|$。本版取后一等号，内容一致。 |
| `eq:bragg-ch09` | 9-5 | 217 | down p.567-615 | 79 | 已核对一致 | down p.598 | 版面 (9-5) $n\lambda=2d\sin\theta$（build/_f4/p217.png）；源书 (9-4) 书内 p.598 / PDF p.89（build/_f4/d89.png）同式 $n\lambda=2dsin\theta$，同页 0.425 nm、0.834 nm、78.5° 与 0.833 nm 数值核对。仅 sin 的排版写法不同。 |
| `eq:arxps` | 9-6 | 218 | down p.567-615 | 96 | 已核对一致 | down p.610 | 版面 (9-6) $d^{*}=d\cos\theta=3\lambda\cos\theta$（build/_f4/p218.png）；源书 (9-5) 书内 p.610 / PDF p.101（build/_f4/d101.png）同式 $d^{*}=dcos\theta=3\lambda cos\theta$。逐符号一致。 |

### ch09-b（1/1 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:eb-def` | 9-7 | 219 | down p.615-623 | 106 | 已核对一致 | down p.616 | 版面 (9-7) $E_{\mathrm B}=E_f(n-1)-E_i(n)$（build/_f4/p219.png）；源书 书内 p.616 / PDF p.107（build/_f4/d107.png）$E_b=E_f(n-1)-E_i(n)$。仅下标 $b/B$ 写法不同。 |

### ch09-c（4/4 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ups-gas` | 9-8 | 221 | down p.662-693 | 153 | 已核对一致 | down p.663 | 版面 (9-8) $E_{\mathrm K}=h\nu-I-E_{\mathrm v}-E_{\mathrm r}$（build/_f4/p221.png）；源书 (9-11) 书内 p.663 / PDF p.154（build/_f4/d154.png）同式 $E_K=h\nu-I-E_v-E_r$。逐项一致。 |
| `eq:ups-solid` | 9-9 | 221 | down p.662-693 | 160 | 已核对一致 | down p.663 | 版面 (9-9) $E_{\mathrm K}=h\nu-E_{\mathrm b}-\Phi$（build/_f4/p221.png）；源书 (9-12) 书内 p.663 / PDF p.154（build/_f4/d154.png）同式 $E_K=h\nu-E_b-\Phi$。逐项一致。 |
| `eq:aes-quant` | 9-10 | 223 | down p.662-693 | 161 | 已核对一致 | down p.683 | 版面 (9-10) $x_{\mathrm A}=\frac{I_{\mathrm A}/s_{\mathrm A}}{\sum_i I_i/s_i}$（build/_f4/p223.png）；源书 (9-15) 书内 p.683 / PDF p.174（build/_f4/d174.png）同式 $x_A=\frac{I_A/s_A}{\sum_i I_i/s_i}$。逐符号一致。 |
| `eq:iss-ch09` | 9-11 | 223 | down p.662-693 | 153 | 原书自身问题 | down p.689 | 版面 (9-11) $\frac{E_1}{E_0}=\left[\frac{\cos\theta\pm\sqrt{(m_2/m_1)^2-\sin^2\theta}}{1+m_2/m_1}\right]^{2}$（build/_f4/p223.png）；源书 (9-16) 书内 p.689 / PDF p.180（build/_f4/d180.png）分子只印 $+$ 号：$\frac{E_1}{E_0}=\left(\frac{\cos\theta+\sqrt{m_2^2/m_1^2-\sin^2\theta}}{1+m_2/m_1}\right)^2$。本版按二元碰撞通式写 $\pm$ 两个分支，keycond 说明 $\theta=90^\circ$ 取正号化简即源 (9-17) $(m_2-m_1)/(m_2+m_1)$，故判原书印刷不完整。 |

### ch09-d（6/6 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:ch09-augerparam` | 9-12 | 225 |  p.623-641 | 116 | 形式一致但符号不同 | down p.625 | 版面 (9-12) $\alpha'=E_{\mathrm K}(\text{Auger})+E_{\mathrm B}(\text{光电子})$（build/_f4/p225.png）；源书 (9-6)(9-7) 书内 p.625 / PDF p.116（build/_f4/d116.png）印 $\alpha=EK_A-EB_P$、$\alpha'=\alpha+h\nu=EK_A+EB_P$。本版 $E_{\mathrm K}(\text{Auger})\leftrightarrow$ 源 $EK_A$、$E_{\mathrm B}(\text{光电子})\leftrightarrow$ 源 $EB_P$，第二式逐项同形（源书 (9-6) 本版未列）。 |
| `eq:ch09-quant-int` | 9-13 | 225 |  p.623-641 | 121 | 形式一致但符号不同 | down p.630 | 版面 (9-13) $I_i\propto n_i\sigma_i(h\nu)\lambda_i(E_i)T(E_i)D(E_i)\cos\theta$（build/_f4/p225.png）；源书 (9-8) 书内 p.630 / PDF p.121（build/_f4/d121.png）印 $I_{ij}=KT(\mathrm{KE})L_{ij}(\gamma)\sigma_{ij}\int n_i(z)e^{-z/(\lambda(\mathrm{KE})\cos\theta)}\mathrm dz$。本版把深度积分归并为 $\lambda_i\cos\theta$ 因子、略去 $L_{ij}$、显写探测效率 $D$，属同结构的改写。 |
| `eq:ch09-rsf` | 9-14 | 226 |  p.623-641 | 121 | 改编补充 | down p.630 | 版面 (9-14) $S_i\propto\sigma_i(h\nu)\lambda_i(E_i)T(E_i)D(E_i)$（build/_f4/p225.png）；源书 §9.2.8（书内 p.630 / PDF p.121，build/_f4/d121.png）只印 (9-8) 强度式与 (9-9)(9-10) 比值式，未单列 $S_i$ 归并式，本版由 (9-8) 归并而得。 |
| `eq:ch09-atomfrac` | 9-15 | 226 |  p.623-641 | 121 | 形式一致但符号不同 | down p.633 | 版面 (9-15) $C_i=\frac{A_i/S_i}{\sum_j A_j/S_j}$（build/_f4/p226.png）；源书 (9-9) 书内 p.633 / PDF p.124（build/_f4/d124.png）印比值形式 $\frac{n_i}{n_j}=\frac{I_i/S_i}{I_j/S_j}$。本版写成归一化原子分数 $C_i$，与源式等价。 |
| `eq:ch09-shirley` | 9-16 | 227 |  p.623-641 | 125 | 改编补充 | down p.634 | 版面 (9-16) $B^{(n+1)}(x)=k\int_{x_0}^{x}\left[I(x')-B^{(n)}(x')\right]\mathrm dx'$（build/_f4/p227.png）；源书 §9.2.9 书内 p.634 / PDF p.125（build/_f4/d125.png）只以文字说明 shirley 本底「与本底以上较高动能处谱峰总面积成固定比例」，未印积分式。 |
| `eq:ch09-tougaard` | 9-17 | 227 |  p.623-641 | 125 | 改编补充 | down p.635 | 版面 (9-17) $B(E)=\int_E^{E_{\max}}\left[I(E')-B(E')\right]K(E'-E)\mathrm dE'$（build/_f4/p227.png）；源书 书内 p.634—635 / PDF p.125—126（build/_f4/d125.png、d126.png）只给 tougaard 本底的文字定义，未印卷积式。 |

### ch10-a（27/27 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:stoi` | 10-1 | 232 | down p.735-768 | 228 | 已核对一致 | down p.739 | 版面 (10-1) $\nu_1B_1+\nu_2B_2+\cdots\rightleftharpoons\nu_3B_3+\nu_4B_4+\cdots$ 或 $\sum_i\nu_iB_i=0$（build/_f4/p232.png）；源书 (10-1) 书内 p.739 / PDF p.228（build/_f4/d228.png）印 $0=\sum_i\nu_iB_i$，同页正文印 $\nu_1B_1+\nu_2B_2+\cdots\rightarrow\nu_3B_3+\nu_4B_4+\cdots$。源书把 0 写在左端、用单箭头，本版写等号右端、用可逆箭头，计量关系一致。 |
| `eq:elem` | 10-2 | 232 | down p.735-768 | 228 | 已核对一致 | down p.739 | 版面 (10-2) $\mathrm{O_2}+2*\rightleftharpoons2\,\mathrm{O}{*}$，并附「不能写作 $\tfrac12\mathrm{O_2}+2*\rightleftharpoons\mathrm{O}{*}$」（build/_f4/p232.png）；源书 书内 p.739 / PDF p.228（build/_f4/d228.png）同印 $\mathrm{O_2}+2*\rightleftharpoons2\mathrm{O}{*}$ 与不能写成 $\tfrac12\mathrm{O_2}+2*\rightleftharpoons\mathrm{O}{*}$。系数与星号写法一致。 |
| `eq:xi` | 10-3 | 232 | down p.735-768 | 225-257 | 已核对一致 | down p.740 | 版面 (10-3) $d\xi_i=\nu_i^{-1}dn_i\Longrightarrow d\xi_i/dt=\nu_i^{-1}dn_i/dt$（build/_f4/p232.png）；源书 (10-2)(10-3) 书内 p.740 / PDF p.229（build/_f4/d229.png）分别印 $d\xi_i=\nu_i^{-1}dn_i$ 与 $\frac{d\xi_i}{dt}=\nu_i^{-1}\frac{dn_i}{dt}$。逐符号一致。 |
| `eq:rate-def` | 10-4 | 233 | down p.735-768 | 225-257 | 已核对一致 | down p.740 | 版面 (10-4) $r_i=\frac1Q\frac{d\xi_i}{dt}=f(k,T,c_i)=f(k,T,p_i)$（build/_f4/p233.png）；源书 (10-4)(10-5) 书内 p.740 / PDF p.229（build/_f4/d229.png）：(10-4) 只印 $\frac1Q\frac{d\xi_i}{dt}$，(10-5) 印同一式后接 $=f(k,T,c_i)=f(k,T,p_i)$。本版把两式并成一行，内容一致。 |
| `eq:power` | 10-5 | 233 | down p.735-768 | 229 | 已核对一致 | down p.740 | 版面 (10-5) $r_i=\frac1{\nu_i}\frac{dc_i}{dt}=k\prod_i c_i^{m_i}$（build/_f4/p233.png）；源书 (10-7) 书内 p.740 / PDF p.229（build/_f4/d229.png）同式，前一条 (10-6) 另印展开式 $kc_1^{m_1}c_2^{m_2}\cdots c_n^{m_n}$。逐符号一致。 |
| `eq:arrh` | 10-6 | 233 | down p.735-768 | 229 | 已核对一致 | down p.740 | 版面 (10-6) $k=A_0\exp\left(-\frac{E}{RT}\right)$（build/_f4/p233.png）；源书 (10-8) 书内 p.740 / PDF p.229（build/_f4/d229.png）印 $k=A_0\exp(-E/RT)$。逐符号一致。 |
| `eq:eapp-def` | 10-7 | 233 | down p.735-768 | 229 | 改编补充 | down p.740 | 版面 (10-7) $E_{\mathrm{app}}\equiv-R\left.\frac{\partial\ln r}{\partial(1/T)}\right\|_{c_i\ \text{恒定}}$（build/_f4/p233.png）；源书 §10.1.3 书内 p.740 / PDF p.229（build/_f4/d229.png）只印 Arrhenius 式 (10-8) 并以文字称 $E$ 为表观活化能，未印局部斜率定义式；本版定义见 ch10-a.tex:129-133。 |
| `eq:ton` | 10-8 | 233 | down p.735-768 | 229 | 已核对一致 | down p.741 | 版面 (10-8) $\mathrm{TON}=\xi N_{\mathrm A}$（build/_f4/p233.png）；源书 (10-9) 书内 p.741 / PDF p.230（build/_f4/d230.png）同式。逐符号一致。 |
| `eq:tof` | 10-9 | 233 | down p.735-768 | 229 | 已核对一致 | down p.741 | 版面 (10-9) $\mathrm{TOF}=\frac1S\frac{d(\mathrm{TON})}{dt}$，$S=[L]A$（build/_f4/p233.png）；源书 (10-11)(10-12) 书内 p.741 / PDF p.230（build/_f4/d230.png）印 $\nu_t=\frac1S\frac{d\mathrm{TON}}{dt}$ 与 $S=[L]A$。本版把源书 $\nu_t$ 记作 TOF，右端逐项一致。 |
| `eq:coll` | 10-10 | 234 | down p.735-768 | 230 | 已核对一致 | down p.741 | 版面 (10-10) $Z=c_1c_2\sigma_{12}^2\left(\frac{8\pi RT(M_1+M_2)}{M_1M_2}\right)^{1/2}$（build/_f4/p234.png）；源书 (10-13) 书内 p.741 / PDF p.230（build/_f4/d230.png）同式。逐符号一致。 |
| `eq:tst` | 10-11 | 234 | down p.735-768 | 225-257 | 已核对一致 | down p.743 | 版面 (10-11) $A_0=\frac{k_{\mathrm B}T}{h}\exp\left(1-\Delta n+\frac{\Delta S^*}{R}\right)$（build/_f4/p234.png）；源书 (10-21) 书内 p.743 / PDF p.232（build/_f4/d232.png）同式，指数括号内 $1-\Delta n+\Delta S^*/R$ 与源书逐项一致。 |
| `eq:cstr` | 10-12 | 234 | down p.735-768 | 232 | 已核对一致 | down p.743 | 版面 (10-12) $r=\frac{n_0-n_{\mathrm f}}{V/F}=\frac{n_0-n_{\mathrm f}}{\tau}$（build/_f4/p234.png）；源书 (10-22) 书内 p.743 / PDF p.232（build/_f4/d232.png）同式。逐符号一致。 |
| `eq:pfr` | 10-13 | 234 | down p.735-768 | 232 | 已核对一致 | down p.744 | 版面 (10-13) $r=\frac{dx}{d(V/F)}$、$\frac VF=\int_0^x\frac{dx}{r}$（build/_f4/p234.png）；源书 (10-24)(10-25) 书内 p.744 / PDF p.233（build/_f4/d233.png）同两式。逐符号一致。 |
| `eq:pfr-int` | 10-14 | 235 | down p.735-768 | 233 | 已核对一致 | down p.745 | 版面 (10-14) $\frac{p}{n_{\mathrm t0}}\frac VF k=(1+\lambda)\ln\frac1{1-X}-\lambda X$，$\lambda=\omega n_{10}$、$X=x/n_{\mathrm t0}$（build/_f4/p235.png）；源书 (10-34) 书内 p.745 / PDF p.234（build/_f4/d234.png）印 $k\left(\frac{pV}{n_{t0}F}\right)=\left[(1+\lambda)\ln\frac1{1-X}-\lambda X\right]$。逐项一致（源书两侧括号位置不同）。 |
| `eq:pfr-int1` | 10-15 | 235 | down p.735-768 | 233 | 已核对一致 | down p.745 | 版面 (10-15) $k\frac{pV}{n_{\mathrm t0}F}=\ln\frac1{1-X}$ 或写作 $k\tau=\ln\frac1{1-X}$（build/_f4/p235.png）；源书 (10-35)(10-36) 书内 p.745 / PDF p.234（build/_f4/d234.png）印 $k\left(\frac{pV}{n_{t0}F}\right)=\ln\frac1{1-X}$ 与 $k\tau=\ln\frac1{1-X}$。两式合写，逐项一致。 |
| `eq:langmuir-ch10` | 10-16 | 236 | down p.735-768 | 241 | 已核对一致 | down p.752 | 版面 (10-16) $\mathrm{B}+\mathrm{L}\rightleftharpoons\mathrm{B{\cdot}L}$、$\theta=\frac{Kp}{1+Kp}$（build/_f4/p236.png）；源书 (10-58) 书内 p.752 / PDF p.241（build/_f4/d241.png）印 $\mathrm{B+L\rightleftharpoons BL}$ 与 $\theta=\frac{Kp}{1+Kp}$。源书不在中间加点，其余逐符号一致。 |
| `eq:langmuir-diss` | 10-17 | 236 | down p.735-768 | 241 | 已核对一致 | down p.752 | 版面 (10-17) $\theta=\frac{(Kp)^{1/2}}{1+(Kp)^{1/2}}$（build/_f4/p236.png）；源书 (10-59) 书内 p.752 / PDF p.241（build/_f4/d241.png）印 $\theta=\frac{\sqrt{Kp}}{1+\sqrt{Kp}}$。$(Kp)^{1/2}$ 即 $\sqrt{Kp}$，逐项一致。 |
| `eq:lh-D` | 10-18 | 237 | down p.735-768 | 243 | 改编补充 | down p.754 | 版面 (10-18) $\theta_{\mathrm v}=\frac1D$，$D=1+K_1c_1+K_2c_2+K_4c_3+K_5c_4$（build/_f4/p237.png）；源书 书内 p.754 / PDF p.243（build/_f4/d243.png）只把同一多项式写进 (10-63) 的分母平方，未单印 $\theta_v=1/D$ 与 $D$ 的定义式；本版把位平衡记账显式写成一式。 |
| `eq:lh-rds` | 10-19 | 238 | down p.735-768 | 243 | 改编补充 | down p.754 | 版面 (10-19) $r=k_3S_0^2\theta_1\theta_2-k_{-3}S_0^2\theta_3\theta_4$（build/_f4/p237.png）；源书 书内 p.754 / PDF p.243（build/_f4/d243.png）在步骤序列后只印结果 (10-63)，未印步骤 3 的速率式；本版补出这一中间式。 |
| `eq:lh` | 10-20 | 238 | down p.735-768 | 243 | 原书自身问题 | down p.754 | 版面 (10-20) $r=\frac{k_3K_1K_2S_0^2\left(c_1c_2-c_3c_4/K_0\right)}{D^2}$、$K_0=\frac{k_3K_1K_2}{k_{-3}K_4K_5}=K_{\mathrm{eq}}$（build/_f4/p238.png）；源书 (10-63) 书内 p.754 / PDF p.243（build/_f4/d243.png）主式逐项同形，但变量说明印「$K_0$ 为 $K_{\mathrm{eq}}(K_1/K_2)K_4K_5$」（build/_f4/d243_k0c.png）。由 (10-63) 令 $r=0$ 必有 $K_0=K_{\mathrm{eq}}$，源书该式仅在 $(K_1/K_2)K_4K_5=1$ 时成立，故判源书自身不自洽；本版按速率平衡写成 $k_3K_1K_2/(k_{-3}K_4K_5)$。 |
| `eq:mvk` | 10-21 | 238 | down p.735-768 | 244 | 已核对一致 | down p.756 | 版面 (10-21) $r=\frac{k_1k_2k_3c_1c_2}{k_1k_3c_1c_2+\nu_0k_2k_3c_2+k_1k_2c_1+k_1k_{-2}c_1c_3}$（build/_f4/p238.png）；源书 (10-71) 书内 p.756 / PDF p.245（build/_f4/d245.png）同式，分母四项逐项一致。 |
| `eq:lh-int` | 10-22 | 238 | down p.735-768 | 246 | 已核对一致 | down p.757 | 版面 (10-22) $\frac WF\cdot\frac{S_0K_1p}{n_{\mathrm t}}k=\ln\frac1{1-X}+K_1pX$（build/_f4/p238.png）；源书 (10-73) 书内 p.757 / PDF p.246（build/_f4/d246.png）印 $\frac WF=\left(\frac{S_0K_1p}{n_t}\right)k=\ln\frac1{1-X}+K_1pX$（三项等式链）。本版按「乘积等于右端」读，下标同样用 $n_t$，内容一致；源书链式写法本身不严格（ch10-a.tex:614-619 已说明）。 |
| `eq:eapp` | 10-23 | 239 | down p.735-768 | 245 | 改编补充 | down p.740 | 版面 (10-23) $E_{\mathrm{app}}=E_{\text{真实}}+\sum_i\nu_i\Delta H_{\mathrm{ads},i}$（build/_f4/p239.png）；源书 §10.1.3—§10.2.4（书内 p.740—757 / PDF p.229—246）未印此分解式，本版由 (10-7) 的表观活化能定义与 van't Hoff 关系推得（ch10-a.tex:628-639），属改编补充。 |
| `eq:power-rev` | 10-24 | 240 | down p.735-768 | 246 | 已核对一致 | down p.757 | 版面 (10-24) $r=k_1\prod_i c_i^{m_i}-k_{-1}\prod_i c_i^{n_i}$（build/_f4/p240.png）；源书 (10-74) 书内 p.757 / PDF p.246（build/_f4/d246.png）同式。逐符号一致。 |
| `eq:ammonia` | 10-25 | 240 | down p.735-768 | 246 | 已核对一致 | down p.757 | 版面 (10-25) $r=k_1p_{\mathrm{N_2}}p_{\mathrm{H_2}}^{3\alpha}p_{\mathrm{NH_3}}^{-2\alpha}-k_{-1}p_{\mathrm{NH_3}}^{2(1-\alpha)}p_{\mathrm{H_2}}^{-3(1-\alpha)}$（build/_f4/p240.png）；源书 (10-75) 书内 p.757 / PDF p.246（build/_f4/d246.png）同式，四个指数的系数 $3\alpha$、$-2\alpha$、$2(1-\alpha)$、$-3(1-\alpha)$ 逐一相符。 |
| `eq:ammonia-eq` | 10-26 | 240 | down p.735-768 | 246 | 改编补充 | down p.757 | 版面 (10-26) $\frac{p_{\mathrm{N_2}}p_{\mathrm{H_2}}^3}{p_{\mathrm{NH_3}}^2}=\frac{k_{-1}}{k_1}=\frac1{K_{\mathrm{eq}}}$（build/_f4/p240.png）；源书 书内 p.757 / PDF p.246（build/_f4/d246.png）只印 (10-75)，未印令 $r=0$ 的平衡式；本版据 (10-75) 自检推得，正文已注明（ch10-a.tex:724-737）。 |
| `eq:golodets` | 10-27 | 240 | down p.735-768 | 247 | 已核对一致 | down p.759 | 版面 (10-27) $m_1=\frac{K_2p_2}{K_1p_1+K_2p_2}=1-\theta_1$、$m_2=\frac{K_1p_1}{K_1p_1+K_2p_2}=\theta_1$、$m_1+m_2=1$（build/_f4/p240.png）；源书 (10-82) 书内 p.759 / PDF p.248（build/_f4/d248.png）同两式，$m_1+m_2$ 常为 1 印在其后的正文里。逐项一致。 |

### ch10-b（17/17 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:temkin` | 10-28 | 242 | down p.769-792 | 258 | 已核对一致 | down p.769 | 版面 (10-28) $v_t=\frac{v}{[L]}=\tau\frac{k_1^{\mathrm o}k_2^{\mathrm o}[A_1][A_2]-k_{-1}^{\mathrm o}k_{-2}^{\mathrm o}[B_1][B_2]}{(k_1^{\mathrm o}[A_1]+k_{-2}^{\mathrm o}[B_2])^{m}(k_{-1}^{\mathrm o}[B_1]+k_2^{\mathrm o}[A_2])^{1-m}}$（build/_f4/p246.png）；源书 书内 p.769 / PDF p.258（build/_f4/d258.png）同式，其后 (10-99) 印 $\tau=\frac{\pi}{\sin(\pi m)}\frac{\gamma}{\exp(\gamma f)-1}$、$m=a-\gamma$（本版写在式后正文）。分母两个括号的指数 $m$、$1-m$ 与各下标逐一相符。 |
| `eq:ch10-basis` | 10-29 | 246 | down p.769-792 | 259 | 改编补充 | down p.770 | 版面 (10-29) $r_v=\rho_p r_m$ 与三条单位声明（build/_f4/p246.png）；源书 §10.4.1 书内 p.770 / PDF p.259（build/_f4/d259.png）未印速率基准声明，原书判据的基准混用正是本版要修的坑；本版声明见 ch10-b.tex:372-377，并与 ch10-c.tex:418-425 的 $\rho$ 版互相注明。 |
| `eq:ch10-jd` | 10-30 | 246 | down p.769-792 | 259 | 形式一致但符号不同 | down p.770 | 版面 (10-30) $j_D=\frac{\rho k_G}{G}Sc^{2/3}=\frac{Sh}{Re\,Sc^{1/3}}$，$Sc=\frac{\mu}{\rho D}$、$Sh=\frac{k_Gd_p}{D}$、$Re=\frac{Gd_p}{\mu}$（build/_f4/p246.png）；源书 (10-101) 书内 p.770 / PDF p.259（build/_f4/d259.png）印 $j_D=\frac{k_G\rho}{G}Sc^{2/3}=\frac{Sh}{ReSc^{1/3}}$，$Sc=\frac{\nu}{D}$、$Sh=\frac{k_Gd_p}{D}$、$Re=\frac{Gd_p}{\mu}$。本版 $Sc=\mu/(\rho D)\leftrightarrow$ 源 $\nu/D$（恒等），整理式与 Sh、Re 同形。 |
| `eq:ch10-jd-fix` | 10-31 | 246 | down p.769-792 | 259 | 已核对一致 | down p.771 | 版面 (10-31) $j_D=\frac{0.725}{Re^{0.41}-0.15}$（build/_f4/p246.png）；源书 (10-102) 书内 p.771 / PDF p.260（build/_f4/d260.png）同式，其后印「对气体、液体都使用」。逐符号一致。 |
| `eq:ch10-extconv` | 10-32 | 246 | down p.769-792 | 260 | 已核对一致 | down p.771 | 版面 (10-32) $\ln\frac1{1-X}=\frac{0.725\,a\,z}{(Re^{0.41}-0.15)Sc^{2/3}}$（build/_f4/p246.png）；源书 (10-103) 书内 p.771 / PDF p.260（build/_f4/d260.png）印 $\ln\frac1{1-X}=\frac{0.725ad_pz}{d_p(Re^{0.41}-0.15)Sc^{2/3}}$，分子与分母各印一个 $d_p$、约去后同形（本版已在 ch10-b.tex:410-413 就地说明）。 |
| `eq:ch10-jh` | 10-33 | 246 | down p.769-792 | 260 | 已核对一致 | down p.771 | 版面 (10-33) $Q=R(-\Delta H_r)=\alpha_sa(T_S-T_B)$、$j_H=\frac{\alpha_s}{Gc_p}Pr^{2/3}=\frac{Nu}{Re\,Pr^{1/3}}$、$Nu=\frac{\alpha_sd_p}{\lambda_f}$（build/_f4/p246.png）；源书 (10-104)(10-105) 书内 p.771 / PDF p.260（build/_f4/d260.png）同两式，式后 prose 亦给 $Pr=c_p\mu/\lambda_f$、$Nu=\alpha_sd_p/\lambda_f$。逐项一致。 |
| `eq:ch10-dT` | 10-34 | 246 | down p.769-792 | 260 | 已核对一致 | down p.771 | 版面 (10-34) $T_S-T_B=\frac{j_D}{j_H}\left(\frac{Pr}{Sc}\right)^{2/3}\frac{-\Delta H_r}{\rho c_p}(c_B-c_S)\approx0.66\lambda f$（build/_f4/p246.png）；源书 (10-107)(10-108) 书内 p.771 / PDF p.260（build/_f4/d260.png）分别印该式与 $T_S-T_B=0.66\lambda f$。逐项一致。 |
| `eq:ch10-profile` | 10-35 | 247 | down p.769-792 | 262 | 已核对一致 | down p.773 | 版面 (10-35) $\frac{c}{c_S}=\frac{\sinh(\varphi_Sr/R)}{(r/R)\sinh\varphi_S}$（球形）、$\frac{c}{c_S}=\frac{\cosh(\varphi_Ll/L)}{\cosh\varphi_L}$（平板）（build/_f4/p247.png）；源书 (10-113)(10-114) 书内 p.773 / PDF p.262（build/_f4/d262.png）同两式，其后印「$\varphi_S$ 和 $\varphi_L$ 为无因次的 Thiele 模数」。逐项一致。 |
| `eq:ch10-thiele` | 10-36 | 247 | down p.769-792 | 263 | 已核对一致 | down p.774 | 版面 (10-36) $\varphi_S=R\sqrt{S_vk_S/D_e}$、$\varphi_L=L\sqrt{S_vk_S/D_e}$（build/_f4/p247.png）；源书 书内 p.774 / PDF p.263（build/_f4/d263.png）页顶同两式、未编号，其后 (10-118) 印 $\varphi_S^2=\frac{R^2S_vk_S}{D_e}=\frac{RS_vk_Sc^m}{D_e(c_m/R)}=\frac{\text{反应速率}}{\text{扩散速率}}$。两条显式逐项一致。 |
| `eq:ch10-r-r0` | 10-37 | 248 | down p.769-792 | 263 | 已核对一致 | down p.774 | 版面 (10-37) $r=4\pi R\varphi_SD_ec_S\left(\frac1{\tanh\varphi_S}-\frac1{\varphi_S}\right)$、$r_0=\frac43\pi R^3S_vk_Sc_S$（build/_f4/p248.png）；源书 (10-115)(10-116) 书内 p.774 / PDF p.263（build/_f4/d263.png）同两式。首因子 $4\pi R\varphi_SD_ec_S$ 逐项相符。 |
| `eq:ch10-eta` | 10-38 | 248 | down p.769-792 | 263 | 已核对一致 | down p.774 | 版面 (10-38) $\eta=\frac{r}{r_0}=\frac3{\varphi_S}\left(\frac1{\tanh\varphi_S}-\frac1{\varphi_S}\right)$（球形）、$\eta=\frac{\tanh\varphi_L}{\varphi_L}$（平板）（build/_f4/p248.png）；源书 (10-117) 书内 p.774 / PDF p.263（build/_f4/d263.png）是一条文字比式（「有内扩散存在时…／无内扩散存在时…」），两条显式印在其后未编号。本版把两条显式合为一式并编号，内容一致；编号归属本版自定。 |
| `eq:ch10-bicomp` | 10-39 | 249 | down p.769-792 | 265 | 已核对一致 | down p.776 | 版面 (10-39) $\varphi_{L,1}=L\sqrt{\frac{k_SS_vc_2}{(D_e)_1}}$（build/_f4/p249.png）；源书 (10-122) 书内 p.776 / PDF p.265（build/_f4/d265.png）印 $\varphi_{L,1}=L\sqrt{\frac{k_SS_vc_2}{(D_e)_1}}$，$c_2$ 一次方、分母下标 $(D_e)_1$，与式后「$\eta<0.4$ 时可近似为 $1/\varphi_{L,1}$、对 $\mathrm{B_2}$ 成 3/2 级」一致。 |
| `eq:ch10-kd` | 10-40 | 249 | down p.769-792 | 265 | 已核对一致 | down p.776 | 版面 (10-40) $K_d=\frac{K_1-D_1\sum_i\nu_iK_i/D_i}{1+\sum_iK_i\left(p_i+\nu_ip_1D_1/D_i\right)}$、$v_d=\frac{-D_2p_2}{\nu_2D_1p_1}-1$（build/_f4/p249.png）；源书 (10-123) 书内 p.776 / PDF p.265（build/_f4/d265.png）同两式，$v_d$ 分子确实带负号。本版现形与源书一致（旧台账所记原稿漏负号已在先前修正）。 |
| `eq:ch10-gammabeta` | 10-41 | 250 | down p.769-792 | 267 | 已核对一致 | down p.778 | 版面 (10-41) $\gamma=\frac{E}{RT}$、$\beta=\frac{c_s(-\Delta H)D_e}{\lambda_pT_s}$（build/_f4/p250.png）；源书 (10-124) 书内 p.778 / PDF p.267（build/_f4/d267.png）同两式（源书用 $\equiv$），式后「$\Delta H$ 为反应的焓变；$\lambda_p$ 为多孔催化剂颗粒的热导率」、$\gamma=20$ 对应 $E\approx100$ kJ/mol 与 $T\approx600$ K、$\beta$ 在 $\pm0.8$ 之间，均与本版一致。 |
| `eq:ch10-da` | 10-42 | 250 | down p.769-792 | 280 | 形式一致但符号不同 | down p.792 | 版面 (10-42) $Da=\frac{r_vR}{k_mc_B}<\frac{0.15}{m}$，另列质量基准 $\frac{\rho_pr_mR}{k_mc_B}$（build/_f4/p250.png）；源书 (10-130) 书内 p.792 / PDF p.281（build/_f4/d281.png）印 $Da\equiv\frac{rR}{k_mc_B}<\frac{0.15}{m}$，$r$ 未声明基准。本版改写为体积基准 $r_v$（并把 $\equiv$ 写作 $=$），属基准改写。 |
| `eq:ch10-wp` | 10-43 | 250 | down p.769-792 | 281 | 形式一致但符号不同 | down p.792 | 版面 (10-43) $\Phi\equiv\eta\varphi^2=\frac{r_vR^2}{D_ec_B}$，另列质量基准 $\frac{\rho_pr_mR^2}{D_ec_B}$（build/_f4/p250.png）；源书 (10-131) 书内 p.792 / PDF p.281（build/_f4/d281.png）印 $\Phi=\frac{r\rho R^2}{D_ec_B}$，确含颗粒密度 $\rho$（式后 prose 印「$\rho$ 为催化剂颗粒的密度」），即质量基准形式。本版主式写体积基准 $r_v$，等价写法另列。 |
| `eq:ch10-mears` | 10-44 | 250 | down p.769-792 | 280 | 形式一致但符号不同 | down p.793 | 版面 (10-44) $\frac{r_v(-\Delta H_r)R}{h_BT_B}<0.15\frac{\mathscr{R}T_B}{E}$（build/_f4/p250.png）；源书 (10-132) 书内 p.793 / PDF p.282（build/_f4/d282.png）印 $\frac{r(-\Delta H)R}{h_BT_B}<0.15\frac{RT_B}{E}$（源书把气体常量与颗粒半径同记 $R$）。本版改写为 $r_v$ 基准并把气体常量记作 $\mathscr{R}$。 |

### ch10-c（17/17 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:recycle-x` | 10-45 | 253 | down p.779-792 | 269 | 原书自身问题 | down p.781 | 版面 (10-45) $x=y_f-y_{\mathrm{in}}=\frac{y_f-y_0}{1+F_R/F_0}$（build/_f4/p253.png）；源书 (10-127) 书内 p.781 / PDF p.270（build/_f4/d270.png）印 $x=y_f-y_{\mathrm{in}}=\frac{y_f-y_0}{1+(F_R+F_0)}$，分母把无量纲 1 与流量 $F_R+F_0$ 相加、量纲不成立。本版按物料衡算写 $1+F_R/F_0$，与同页 (10-128) 的 $F_R/F_0$ 无量纲比一致。 |
| `eq:recycle-r` | 10-46 | 253 | down p.779-792 | 270 | 已核对一致 | down p.781 | 版面 (10-46) $r=\frac{dx}{dW/(F_0+F_R)}\approx\frac{y_f-y_0}{W/F_0}$（build/_f4/p253.png）；源书 (10-128) 书内 p.781 / PDF p.270（build/_f4/d270.png）印 $r=\frac{dx}{dW/(F_0+F_R)}\approx\frac{y_f-y_0}{(1+F_R/F_0)W/(F_0+F_R)}=\frac{y_f-y_0}{W/F_0}$。本版取首末两端，中间恒等变形略去，逐项一致。 |
| `eq:tri-method` | 10-47 | 256 | down p.779-792 | 274 | 已核对一致 | down p.785 | 版面 (10-47) $\frac{r_1}{r_2}=\frac{\eta_1}{\eta_2}$、$\frac{d_1}{d_2}=\frac{\phi_1}{\phi_2}$（build/_f4/p256.png）；源书 书内 p.785 / PDF p.274（build/_f4/d274.png）同两式（未编号，紧接「根据式 (10-108)～式 (10-120) 有」）。逐项一致。 |
| `eq:weisz-modulus` | 10-48 | 256 | down p.779-792 | 275 | 已核对一致 | down p.786 | 版面 (10-48) $\Phi=\eta\phi^2=\frac{d^2}{D_e}\left(-\frac1{V_p}\frac{dn}{dt}\right)\frac1{c_s}$（build/_f4/p256.png）；源书 (10-129) 书内 p.786 / PDF p.275（build/_f4/d275.png）印 $\Phi=\eta\phi^2=\frac{d^2}{D_e}\left(-\frac1{V_p}\frac{dn}{dt}\right)\frac1{c_s}$。逐符号一致（同页 $d=R$、$d=L$ 的说明亦同）。 |
| `eq:rate-basis` | 10-49 | 258 | down p.779-792 | 281 | 改编补充 | down p.792 | 版面 (10-49) $r_v=\rho r_m$ 与单位声明（build/_f4/p258.png）；源书 §10.5.4 书内 p.792 / PDF p.281（build/_f4/d281.png）无速率基准声明式，本版为三个判据统一基准而补（ch10-c.tex:414-425，并与 ch10-b 的 $\rho_p$ 版互相注明）。 |
| `eq:da` | 10-50 | 258 | down p.779-792 | 281 | 已核对一致 | down p.792 | 版面 (10-50) $Da=\frac{rR}{k_mc_B}<\frac{0.15}{m}$（build/_f4/p258.png）；源书 (10-130) 书内 p.792 / PDF p.281（build/_f4/d281.png）同式（$r$ 未加基准下标，本版此式照录）。逐符号一致。 |
| `eq:wp` | 10-51 | 258 | down p.779-792 | 281 | 形式一致但符号不同 | down p.792 | 版面 (10-51) $\Phi=\frac{r_vR^2}{D_ec_B}$（build/_f4/p258.png）；源书 (10-131) 书内 p.792 / PDF p.281（build/_f4/d281.png）印 $\Phi=\frac{r\rho R^2}{D_ec_B}$。本版 $r_v\leftrightarrow$ 源 $r\rho$（质量基准换体积基准），结构一致。 |
| `eq:mears-heat` | 10-52 | 258 | down p.779-792 | 280 | 形式一致但符号不同 | down p.793 | 版面 (10-52) $\frac{r(-\Delta H)R}{h_BT_B}<0.15\frac{\mathscr{R}T_B}{E}$（build/_f4/p258.png）；源书 (10-132) 书内 p.793 / PDF p.282（build/_f4/d282.png）印 $\frac{r(-\Delta H)R}{h_BT_B}<0.15\frac{RT_B}{E}$。本版把气体常量记作 $\mathscr{R}$、半径仍记 $R$，其余逐项一致。 |
| `eq:coke-r` | 10-53 | 261 | down p.779-792 | 282 | 已核对一致 | down p.794 | 版面 (10-53) $r=k_1K_1c_L\left(c_1-\frac{c_2}{K_{eq}}\right)$（build/_f4/p261.png）；源书 (10-133) 书内 p.794 / PDF p.283（build/_f4/d283.png）同式。逐符号一致。 |
| `eq:coke-sites` | 10-54 | 261 | down p.779-792 | 282 | 已核对一致 | down p.794 | 版面 (10-54) $c_t=c_L+c_1+c_2+c_{CL}$（build/_f4/p261.png）；源书 书内 p.794 / PDF p.283（build/_f4/d283.png）同式（未编号，紧接「则总的活性位浓度 $c_t$ 为」）。逐项一致。 |
| `eq:coke-langmuir` | 10-55 | 261 | down p.779-792 | 282 | 已核对一致 | down p.794 | 版面 (10-55) $c_t-c_{CL}=c_L(1+K_1c_1+K_2c_2)$（build/_f4/p261.png）；源书 (10-134) 书内 p.794 / PDF p.283（build/_f4/d283.png）同式。逐符号一致。 |
| `eq:coke-activity` | 10-56 | 261 | down p.779-792 | 282 | 已核对一致 | down p.794 | 版面 (10-56) $r=\frac{c_t-c_{CL}}{c_t}\cdot\frac{k_1K_1c_t(c_1-c_2/K_{eq})}{1+K_1c_1+K_2c_2}=\varphi\,r_{\text{fresh}}$，$\varphi\equiv\frac{c_t-c_{CL}}{c_t}$（build/_f4/p261.png）；源书 (10-135) 书内 p.794 / PDF p.283（build/_f4/d283.png、d283_135.png）印 $r=\frac{c_t-c_{CL}}{c_t}\frac{k_1K_1c_t(c_1-c_2/K_{eq})}{1+K_1c_1+K_2c_2}$，分子确为 $c_t$（不是 $c_L$）。逐项一致。 |
| `eq:coke-phi` | 10-57 | 261 | down p.779-792 | 284 | 已核对一致 | down p.795 | 版面 (10-57) $\varphi_1=\left(\frac{c_t-c_{CL}}{c_t}\right)^{n_1}$、$\varphi_C=\left(\frac{c_t-c_{CL}}{c_t}\right)^{n_C}$（build/_f4/p262.png）；源书 (10-136) 书内 p.795 / PDF p.284（build/_f4/d284.png）同两式。指数 $n_1$、$n_C$ 与底数逐项一致。 |
| `eq:multilayer-coke` | 10-58 | 262 | down p.779-792 | 284 | 已核对一致 | down p.795 | 版面 (10-58) $\frac{\delta c_\beta}{\delta t}=k_\beta c_\alpha p_1$（build/_f4/p262.png）；源书 书内 p.795 / PDF p.284（build/_f4/d284.png）同式（未编号，紧接 Nam–Kittrell 多层积炭假设）。本版照录 $\delta$ 写法，逐项一致。 |
| `eq:nam-kittrell` | 10-59 | 262 | down p.779-792 | 284 | 已核对一致 | down p.795 | 版面 (10-59) $c_\Sigma=q_1(1-k_t)-q_2\ln k_t$、$q_1=m_CS_0-q_2$、$q_2=\frac{k_\beta m_CS_0(1+K_1p_1+K_2p_2)}{k_\alpha K_1}$（build/_f4/p262.png）；源书 (10-137) 书内 p.795 / PDF p.284（build/_f4/d284.png）同三式。逐项一致。 |
| `eq:osc-ode` | 10-60 | 263 | down p.779-792 | 286 | 已核对一致 | down p.797 | 版面 (10-60) $dc_i/dt=F_i(c_j,p_k)$（build/_f4/p263.png）；源书 (10-138) 书内 p.797 / PDF p.286（build/_f4/d286.png）同式。逐符号一致。 |
| `eq:osc-ode-diff` | 10-61 | 263 | down p.779-792 | 286 | 已核对一致 | down p.797 | 版面 (10-61) $\partial c_i/\partial t=F_i(c_j,p_k)+D_i\frac{\partial^2c_i}{\partial r^2}$（build/_f4/p263.png）；源书 (10-139) 书内 p.797 / PDF p.286（build/_f4/d286.png）同式，式后「$D_i$ 为普适扩散系数；$r$ 为空间坐标」。逐项一致。 |

### ch11-a（6/31 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:gibbs-emf` | 11-1 | 267 | down p.807-833 | 300 | 未覆盖 | — |  |
| `eq:entropy-emf` | 11-2 | 267 | down p.807-833 | 301 | 未覆盖 | — |  |
| `eq:she` | 11-3 | 267 | down p.807-833 | 301 | 未覆盖 | — |  |
| `eq:series-rate` | 11-4 | 267 | down p.807-833 | 301 | 未覆盖 | — |  |
| `eq:nernst` | 11-5 | 267 | down p.807-833 | 302 | 未覆盖 | — |  |
| `eq:redox` | 11-6 | 268 | down p.807-833 | 303 | 未覆盖 | — |  |
| `eq:current-basic` | 11-7 | 268 | down p.807-833 | 303 | 未覆盖 | — |  |
| `eq:dg-eta` | 11-8 | 268 | down p.807-833 | 304 | 未覆盖 | — |  |
| `eq:k-eta` | 11-9 | 268 | down p.807-833 | 304 | 未覆盖 | — |  |
| `eq:bv-first` | 11-10 | 268 | down p.807-833 | 304 | 未覆盖 | — |  |
| `eq:i0` | 11-11 | 269 | down p.807-833 | 305 | 未覆盖 | — |  |
| `eq:bv` | 11-12 | 269 | down p.807-833 | 305 | 未覆盖 | — |  |
| `eq:bv-linear` | 11-13 | 269 | down p.807-833 | 305 | 未覆盖 | — |  |
| `eq:bv-cathodic` | 11-14 | 269 | down p.807-833 | 305 | 未覆盖 | — |  |
| `eq:tafel` | 11-15 | 269 | down p.807-833 | 305 | 未覆盖 | — |  |
| `eq:fick1` | 11-16 | 270 | down p.807-833 | 306 | 未覆盖 | — |  |
| `eq:diff-layer` | 11-17 | 270 | down p.807-833 | 307 | 未覆盖 | — |  |
| `eq:il` | 11-18 | 270 | down p.807-833 | 307 | 未覆盖 | — |  |
| `eq:eta1` | 11-19 | 271 | down p.807-833 | 307 | 未覆盖 | — |  |
| `eq:eta2` | 11-20 | 271 | down p.807-833 | 307 | 未覆盖 | — |  |
| `eq:eta-conc` | 11-21 | 271 | down p.807-833 | 307 | 未覆盖 | — |  |
| `eq:fick2` | 11-22 | 272 | down p.807-833 | 310 | 未覆盖 | — |  |
| `eq:cottrell` | 11-23 | 272 | down p.807-833 | 310 | 未覆盖 | — |  |
| `eq:conc-profile` | 11-24 | 272 | down p.807-833 | 311 | 未覆盖 | — |  |
| `eq:fick2-sph` | 11-25 | 272 | down p.807-833 | 312 | 未覆盖 | — |  |
| `eq:spherical` | 11-26 | 272 | down p.807-833 | 312 | 已核对一致 | down p.312 | 版面 (11-26) i_d(t)=nFAD_O C_O*[1/(πD_O t)^{1/2}+1/r0]=i_d(线性)+nFAD_O C_O*/r0；源书书内 p.824 分两式印 (11-52) i_d(t)=nFAD_O C_O*[1/(πD_O t)^{1/2}+1/r0] 与 (11-53) i_d(球形)=i_d(线性)+nFAD_O C_O*/r0，本版合为一式。图 build/_eq_p272.png / build/_src_dn312_fb.png |
| `eq:iss-ch11` | 11-27 | 273 | down p.807-833 | 313 | 已核对一致 | down p.313 | 版面 (11-27) i_ss=nFAm_0C_O*；源书书内 p.825 式 (11-55) 逐字同形（该页未定义 m_0）。图 build/_eq_p273.png / build/_src_dn313_fb.png |
| `eq:sampled-rev` | 11-28 | 273 | down p.807-833 | 313 | 已核对一致 | down p.313 | 版面 (11-28) i(t)=nFAD_O^{1/2}C_O*/(π^{1/2}t^{1/2}(1+ξθ))；源书书内 p.825 式 (11-56) 逐字同形（分母确为 1+ξθ）。图 build/_eq_p273.png / build/_src_dn313_fb.png |
| `eq:sampled-sphere-irr` | 11-29 | 273 | down p.807-833 | 313 | 已核对一致 | down p.313 | 版面 (11-29) i=nFAD_O(C_O*−θC_R*)/(r0 s)·[(δ+1)/((δ+1)/k+(1+ξ²rθ))]；源书书内 p.825 式 (11-59) 逐字同形（方括号内 (δ+1) 结构清晰可辨）。图 build/_eq_p273.png / build/_src_dn313_fb.png |
| `eq:chronocoul` | 11-30 | 273 | down p.807-833 | 314 | 已核对一致 | down p.314 | 版面 (11-30) Q_d=2nFAD_O^{1/2}C_O*t^{1/2}/π^{1/2}；源书书内 p.826 式 (11-60) 逐字同形。图 build/_eq_p273.png / build/_src_dn314_fb.png |
| `eq:chronocoul-full` | 11-31 | 274 | down p.807-833 | 314 | 形式一致但符号不同 | down p.314 | 版面 (11-31) Q=2nFAD_O^{1/2}C_O*t^{1/2}/π^{1/2}+Q_dl+nFAΓ_O；源书书内 p.826 式 (11-61) 左端印 Q_d（总电量）、末项印 nFAΓ₀（下标 0），本版左端记 Q、吸附项记 Γ_O。图 build/_eq_p274.png / build/_src_dn314_fb.png |

### ch11-b（6/29 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:chrono-bc` | 11-32 | 277 | down p.833-859 | 322 | 形式一致但符号不同 | down p.322 | 版面 (11-32) (∂c_i/∂x)_{x=0}=v_iI₀/(nFD_i)=常数；源书书内 p.834 式 (11-62) 印 ±v_iI_0/(nFD_i)（带正负号），本版取正号并声明「阴极为正」。图 build/_eq_p277.png / build/_src_dn322_fb.png |
| `eq:chrono-cixt` | 11-33 | 277 | down p.833-859 | 322 | 已核对一致 | down p.322 | 版面 (11-33) c_i(x,t)=c_i⁰+(v_iI₀/nF)[(x/D_i)erfc(x/(2√(D_it)))−(2√t/√(πD_i))exp(−x²/(4D_it))]；源书书内 p.834 式 (11-63) 逐项同形（括号内先 erfc 项、后取负的指数项）。图 build/_eq_p277.png / build/_src_dn322_fb.png |
| `eq:chrono-c0t` | 11-34 | 277 | down p.833-859 | 322 | 已核对一致 | down p.322 | 版面 (11-34) c_i(0,t)=c_i⁰−(2v_iI₀/nF)√(t/(πD_i))；源书书内 p.834 式 (11-64) 逐字同形。图 build/_eq_p277.png / build/_src_dn322_fb.png |
| `eq:sand` | 11-35 | 277 | down p.833-859 | 322 | 已核对一致 | down p.323 | 版面 (11-35) √τ=nFAc_i⁰√(πD_i)/(2v_i i) ⟺ i√τ=nFAc_i⁰√(πD_i)/(2v_i)；源书书内 p.835 正文印「若 t^{1/2}=nFc_i⁰√(πD_i)/(2v_iI₀)，则反应粒子 i 的表面浓度下降到 0」，即本版 √τ 关系的正文写法（源书以 t、I₀ 记，未单独编号；本版核对说明称原书未印，实为以正文形式印出）。图 build/_eq_p277.png / build/_src_dn323_fb.png |
| `eq:chrono-phi` | 11-36 | 277 | down p.833-859 | 323 | 形式一致但符号不同 | down p.323 | 版面 (11-36) φ(t)=φ⁰+(RT/nF)Σ_i v_i ln c_i(0,t)；源书书内 p.835 式 (11-65) 印 φ(t)=φ₀+(RT/nF)Σv_i ln c_i(0,t)，本版把 φ₀ 记作 φ⁰。图 build/_eq_p277.png / build/_src_dn323_fb.png |
| `eq:chrono-erev` | 11-37 | 277 | down p.833-859 | 324 | 形式一致但符号不同 | down p.324 | 版面 (11-37) E(t)=E_{1/2}+(RT/nF)ln((√τ−√t)/√t)、E_{1/2}=E⁰'+(RT/2nF)ln(D_R/D_O)；源书书内 p.836 式 (11-68) 印同式与 E_{1/2}=E^Θ'+(RT/nF)ln(√D_R/√D_O)，本版 E⁰'↔源书 E^Θ'，并用 (RT/2nF)ln(D_R/D_O) 的恒等写法（ln√(D_R/D_O)=½ln(D_R/D_O)）。图 build/_eq_p277.png / build/_src_dn324_fb.png |
| `eq:chrono-irr` | 11-38 | 278 | down p.833-859 | 324 | 未覆盖 | — |  |
| `eq:chrono-eta` | 11-39 | 278 | down p.833-859 | 325 | 未覆盖 | — |  |
| `eq:chrono-ic` | 11-40 | 278 | down p.833-859 | 326 | 未覆盖 | — |  |
| `eq:chrono-cd` | 11-41 | 278 | down p.833-859 | 326 | 未覆盖 | — |  |
| `eq:chrono-dp` | 11-42 | 278 | down p.833-859 | 326 | 未覆盖 | — |  |
| `eq:bulk-n` | 11-43 | 280 | down p.833-859 | 328 | 未覆盖 | — |  |
| `eq:bulk-decay` | 11-44 | 280 | down p.833-859 | 321-347 | 未覆盖 | — |  |
| `eq:strip-ip` | 11-45 | 281 | down p.833-859 | 333 | 未覆盖 | — |  |
| `eq:strip-thin` | 11-46 | 281 | down p.833-859 | 334 | 未覆盖 | — |  |
| `eq:flux` | 11-47 | 283 | down p.833-859 | 321-347 | 未覆盖 | — |  |
| `eq:conv-diff` | 11-48 | 283 | down p.833-859 | 336 | 未覆盖 | — |  |
| `eq:re` | 11-49 | 283 | down p.833-859 | 336 | 未覆盖 | — |  |
| `eq:rde-steady` | 11-50 | 284 | down p.833-859 | 337 | 未覆盖 | — |  |
| `eq:levich` | 11-51 | 284 | down p.833-859 | 337 | 未覆盖 | — |  |
| `eq:delta0` | 11-52 | 284 | down p.833-859 | 337 | 未覆盖 | — |  |
| `eq:levich-general` | 11-53 | 285 | down p.833-859 | 338 | 未覆盖 | — |  |
| `eq:kl` | 11-54 | 285 | down p.833-859 | 338 | 未覆盖 | — |  |
| `eq:rde-resistance` | 11-55 | 285 | down p.833-859 | 339 | 未覆盖 | — |  |
| `eq:ring-limit` | 11-56 | 286 | down p.833-859 | 341 | 未覆盖 | — |  |
| `eq:rrde-collection` | 11-57 | 286 | down p.833-859 | 341 | 未覆盖 | — |  |
| `eq:rrde-shield` | 11-58 | 286 | down p.833-859 | 342 | 未覆盖 | — |  |
| `eq:orr-paths` | 11-59 | 286 | down p.833-859 | 341 | 未覆盖 | — |  |
| `eq:ume` | 11-60 | 288 | down p.833-859 | 342 | 未覆盖 | — |  |

### ch11-d（1/16 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:eis-d-sine` | 11-61 | 289 | down p.855-861 | 344 | 未覆盖 | — |  |
| `eq:eis-d-phase` | 11-62 | 289 | down p.855-861 | 345 | 未覆盖 | — |  |
| `eq:eis-d-cap` | 11-63 | 289 | down p.855-861 | 343-349 | 未覆盖 | — |  |
| `eq:eis-d-capohm` | 11-64 | 289 | down p.855-861 | 346 | 未覆盖 | — |  |
| `eq:eis-d-series` | 11-65 | 289 | down p.855-861 | 346 | 未覆盖 | — |  |
| `eq:eis-d-zdef` | 11-66 | 289 | down p.855-861 | 346 | 未覆盖 | — |  |
| `eq:eis-d-zmod` | 11-67 | 289 | down p.855-861 | 346 | 未覆盖 | — |  |
| `eq:eis-d-parallel` | 11-68 | 290 | down p.855-861 | 347 | 未覆盖 | — |  |
| `eq:eis-d-cdl` | 11-69 | 292 | down p.855-861 | 348 | 未覆盖 | — |  |
| `eq:eis-d-fdiff` | 11-70 | 292 | down p.855-861 | 349 | 未覆盖 | — |  |
| `eq:eis-d-randles` | 11-71 | 293 | down p.855-861 | 350 | 未覆盖 | — |  |
| `eq:eis-d-rc` | 11-72 | 293 | down p.855-861 | 350 | 未覆盖 | — |  |
| `eq:eis-d-warburg` | 11-73 | 293 | down p.855-861 | 347 | 未覆盖 | — |  |
| `eq:eis-d-cpe` | 11-74 | 293 | down p.855-861 | 347 | 未覆盖 | — |  |
| `eq:eis-d-cpeceff` | 11-75 | 293 | down p.855-861 | 347 | 未覆盖 | — |  |
| `eq:eis-d-cpapp` | 11-76 | 293 | down p.855-861 | 348 | 改编补充 | down p.858-861 | 版面 (11-76) $C_{\mathrm p}(\omega)=\frac{\operatorname{Im}Y}{\omega}=Q\sin(n\pi/2)\omega^{n-1}$（build/_f5d/p293.png）；源书 §11.5.1 书内 p.858—861 / PDF p.346—349（build/_f5d/d346.png、d347.png、d348.png、d349.png）只列等效元件表 11-1 的 $R_\Omega$、$C_{dl}$、$R_p$、$R_{ct}$、$Z_W$、$C_c$、$L$ 七项，通查未见 CPE 或指数 $n$ 的讨论，此式在原书无可对照处（本版页面就地核对说明已写明）。 |

### ch11-c（4/4 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:dems-if` | 11-77 | 304 |  p.— | 362 | 已核对一致 | down p.874 | 版面 (11-77) $I_{\mathrm F}=\frac{dQ_{\mathrm F}}{dt}=\frac{d(zFn)}{dt}=zF\frac{dn}{dt}$（build/_f5d/p304.png）；源书 (11-126) 书内 p.874 / PDF p.362（build/_f5d/d362.png）印 $I_F=dQ_F/dt=d(zFn)/dt=zFdn/dt$。逐符号一致。 |
| `eq:dems-ni` | 11-78 | 304 |  p.— | 362 | 已核对一致 | down p.874 | 版面 (11-78) $n_{\mathrm i}=K_1K_2n$（build/_f5d/p304.png）；源书 (11-127) 书内 p.874 / PDF p.362（build/_f5d/d362.png）同式。逐符号一致。 |
| `eq:dems-qi` | 11-79 | 304 |  p.— | 362 | 已核对一致 | down p.874 | 版面 (11-79) $Q_{\mathrm i}=K_3n_{\mathrm i}$（build/_f5d/p304.png）；源书 (11-128) 书内 p.874 / PDF p.362（build/_f5d/d362.png）同式。逐符号一致。 |
| `eq:dems-ii` | 11-80 | 304 |  p.— | 362 | 已核对一致 | down p.874 | 版面 (11-80) $I_{\mathrm i}=\frac{dQ_{\mathrm i}}{dt}=K_1K_2K_3\frac{dn}{dt}=\frac{K_1K_2K_3}{zF}I_{\mathrm F}$（build/_f5d/p304.png）；源书 (11-129) 书内 p.874 / PDF p.362（build/_f5d/d362.png）同式，系数 $K_1K_2K_3/(zF)$ 逐项相符。 |

### ch12-a（5/5 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:kappa` | 12-1 | 308 | down p.885-912 | 375 | 形式一致但符号不同 | down p.891 | 版面 (12-1) $\varphi(z)=\varphi(0)e^{-\kappa z}$、$\kappa=\frac{\sqrt{2m\Phi}}{\hbar}$（build/_f5d/p308.png）；源书 书内 p.891 / PDF p.377（build/_f5d/d377.png）页顶未编号印 $\varphi(z)=\varphi(0)e^{-kz}$、$k=\frac{\sqrt{2m\phi}}{\hbar}$。本版衰减常数 $\kappa\leftrightarrow$ 源 $k$、势垒高度 $\Phi\leftrightarrow$ 源 $\phi$（源书波函数与势垒同用 $\varphi$），结构与系数一致。 |
| `eq:sumI` | 12-2 | 308 | down p.885-912 | 377 | 形式一致但符号不同 | down p.891 | 版面 (12-2) $I\propto\sum_{E_n=E_{\mathrm F}-eU}^{E_{\mathrm F}}\lvert\varphi_n(0)\rvert^{2}e^{-2\kappa W}$（build/_f5d/p308.png）；源书 书内 p.891 / PDF p.377（build/_f5d/d377.png）同式，求和上下限 $E_n=E_F-eU$ 到 $E_F$ 与源书一致，仅指数中的 $\kappa$ 源书记作 $k$。 |
| `eq:tunneling` | 12-3 | 308 | down p.885-912 | 377 | 形式一致但符号不同 | down p.891 | 版面 (12-3) $I\propto U\rho_{\mathrm s}(0,E_{\mathrm F})e^{-2\kappa W}\approx U\rho_{\mathrm s}(0,E_{\mathrm F})e^{-1.025\sqrt{\Phi}W}$（build/_f5d/p308.png）；源书 书内 p.891 / PDF p.377（build/_f5d/d377.png）印 $I\propto U\rho_s(0,E_F)e^{-2kW}\approx U\rho_s(0,E_F)e^{-1.0252\sqrt{\phi}W}$。本版 $\kappa\leftrightarrow k$、$\Phi\leftrightarrow\phi$，指数 $1.025$ 与 $2\kappa$ 的关系已在页面就地说明。 |
| `eq:wkb` | 12-4 | 309 | down p.885-912 | 378 | 已核对一致 | down p.892 | 版面 (12-4) $I\propto\int_0^{eU}\rho_{\mathrm s}(\mathbf r,E)\rho_{\mathrm t}(\mathbf r,\pm eU\mp E)T(E,eU,\mathbf r)dE$（build/_f5d/p309.png）；源书 书内 p.892 / PDF p.378（build/_f5d/d378.png）未编号印 $I=\int_0^{eU}\rho_s(r,E)\rho_t(r,\pm eU\mp E)T(E,eU,r)dE$。本版把等号写为比例号（略去常数因子），积分限与 $\pm eU\mp E$ 符号一致。 |
| `eq:dIdV` | 12-5 | 309 | down p.885-912 | 378 | 改编补充 | down p.892-893 | 版面 (12-5) $\left.\frac{dI}{dV}\right\|_{\mathbf r}\propto\rho_{\mathrm s}(\mathbf r,E_{\mathrm F}+eV)T(E_{\mathrm F},eV,\mathbf r)$（build/_f5d/p309.png）；源书 书内 p.892—893 / PDF p.378—379（build/_f5d/d378.png、d379.png）只述「归一化后的微分电导将只取决于局域态密度和隧穿电压」，未印此式，本版由 (12-4) 求导得出。 |

### ch12-b（10/10 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:lj` | 12-6 | 313 | down p.913-925 | 399 | 改编补充 | down p.914 | 版面 (12-6) $U(d)=4\varepsilon\left[\left(\frac{\sigma}{d}\right)^{12}-\left(\frac{\sigma}{d}\right)^{6}\right]$（build/_f5d/p313.png）；源书 §12.3.1 书内 p.914 / PDF p.400（build/_f5d/d400.png）只在正文提「势能曲线（Lennard-Jones 势）可以反映针尖-表面相互作用随其间距的变化特点」，未印该式；本版按标准 LJ 形式补出（ch12-b.tex:73、:691-692 已注明）。 |
| `eq:afm-driven` | 12-7 | 315 | down p.913-925 | 402 | 已核对一致 | down p.916 | 版面 (12-7) $m\frac{d^2z}{dt^2}=-kz-m\gamma\frac{dz}{dt}+F_0\cos\omega t$（build/_f5d/p315.png）；源书 (12-1) 书内 p.916 / PDF p.402（build/_f5d/d402.png）同式，四项符号与系数逐一相符。 |
| `eq:afm-q` | 12-8 | 315 | down p.913-925 | 402 | 已核对一致 | down p.916 | 版面 (12-8) $\omega_0=\sqrt{\frac km}$、$Q=\frac{\omega_0}{\gamma}$（build/_f5d/p315.png）；源书 书内 p.916 / PDF p.402（build/_f5d/d402.png）正文未编号印 $\omega_0=\sqrt{k/m}$、$Q=\omega_0/\gamma$。逐符号一致。 |
| `eq:afm-amp` | 12-9 | 315 | down p.913-925 | 402 | 已核对一致 | down p.916 | 版面 (12-9) $A(\omega)=\frac{F_0/m}{\sqrt{(\omega^2-\omega_0^2)^2+(\omega\omega_0/Q)^2}}$（build/_f5d/p315.png）；源书 书内 p.916 / PDF p.402（build/_f5d/d402.png）印 $A(\omega)=\frac{F_0/m}{[(\omega_0^2-\omega^2)^2+(\omega\omega_0/Q)^2]^{1/2}}$。平方项次序互换等价，逐项一致。 |
| `eq:afm-phase` | 12-10 | 315 | down p.913-925 | 402 | 已核对一致 | down p.916 | 版面 (12-10) $\tan\varphi=\frac{\omega\omega_0/Q}{\omega_0^2-\omega^2}$（build/_f5d/p315.png）；源书 书内 p.916 / PDF p.402（build/_f5d/d402.png）印 $\tan\phi=\frac{\omega\omega_0/Q}{\omega_0^2-\omega^2}$。仅相位角记 $\varphi$、源书 $\phi$，其余逐项一致。 |
| `eq:afm-domega-lin` | 12-11 | 316 | down p.913-925 | 403 | 已核对一致 | down p.917 | 版面 (12-11) $\Delta\omega=\omega_{\mathrm{eff}}-\omega_0\approx\omega_0\frac{k_{\mathrm{ts}}}{2k}=-\frac{\omega_0}{2k}\left.\frac{\partial F_{\mathrm{ts}}}{\partial z}\right\|_{z=0}$（build/_f5d/p316.png）；源书 (12-2) 书内 p.917 / PDF p.403（build/_f5d/d403.png）印 $\Delta\omega\approx\omega_0\frac{k_{ts}}{2k}=-\frac{\omega_0}{2k}\left.\frac{\partial F_{ts}}{\partial z}\right\|_{z=0}$。逐项一致。 |
| `eq:afm-domega-fm` | 12-12 | 316 | down p.913-925 | 403 | 已核对一致 | down p.917 | 版面 (12-12) $\Delta\omega=-\frac{\omega_0}{A^2k}\left\langle F_{\mathrm{ts}}z\right\rangle$（build/_f5d/p316.png）；源书 (12-3) 书内 p.917 / PDF p.403（build/_f5d/d403.png）同式。逐项一致。 |
| `eq:afm-fz` | 12-13 | 316 | down p.913-925 | 403 | 原书自身问题 | down p.918 | 版面 (12-13) $\left\langle F_{\mathrm{ts}}z\right\rangle\equiv\frac1T\int_0^T F_{\mathrm{ts}}(d+A\sin\omega t)A\sin\omega t\,dt$、$T=\frac{2\pi}{\omega}\approx\frac{2\pi}{\omega_0}$（build/_f5d/p316.png）；源书 (12-4) 书内 p.918 / PDF p.404（build/_f5d/d404.png）式内印裸 $T$，式后却印「振动周期 $T=1/\omega_0$」，与周期定义差 $2\pi$。本版按 $T=2\pi/\omega\approx2\pi/\omega_0$ 写出，并在 ch12-b.tex:342 记原书这一排印（分母裸 $T$、$T=1/\omega_0$）。 |
| `eq:afm-hooke` | 12-14 | 316 | down p.913-925 | 400 | 改编补充 | down p.914 | 版面 (12-14) $F=k\,\Delta z$（build/_f5d/p316.png）；源书 §12.3.2 书内 p.914 / PDF p.400（build/_f5d/d400.png）只以文字说「换算关系就是胡克定律」，未印该式；本版按胡克定律补出。 |
| `eq:tipconv` | 12-15 | 317 | down p.913-925 | 399 | 改编补充 | down p.918-919 | 版面 (12-15) $w_{\mathrm{app}}=2\sqrt{2Rr+r^2}\approx2\sqrt{2Rr}\ (r\ll R)$、$\frac{w_{\mathrm{app}}}{2r}\approx\sqrt{\frac{2R}{r}}$（build/_f5d/p317.png）；源书 §12.5.1 书内 p.918—919 / PDF p.404—405 未印针尖卷积的几何式（本版由设定「针尖末端为半径 $R$ 的球、样品为半径 $r$ 的球」自行推得，ch12-b.tex:453-464）。 |

### ch12-c（5/5 式有终判）

| 式 | 编号 | 成品页 | 源书 | 提示PDF页 | 结论 | 源书页 | 说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `eq:rayleigh` | 12-16 | 321 | down p.926-942 | 413 | 已核对一致 | down p.927 | 版面 (12-16) $\Delta x\geq\frac{0.61\,\lambda}{n\sin\theta}$（build/_f5d/p321.png）；源书 书内 p.927 / PDF p.413（build/_f5d/d413.png）正文印「两个点源之间可被清楚分辨的最小距离 $\Delta x\geq0.61\lambda/n\sin\theta$，其中 $\lambda$ 为照明光波长，$n\sin\theta$ 为数值孔径」，本版照 $0.61$ 取值写成展示式。逐项一致（ch12-c.tex:48 核对说明已记行内写法差异）。 |
| `eq:nearfield-decay` | 12-17 | 322 | down p.926-942 | 415 | 改编补充 | down p.928-929 | 版面 (12-17) $E_{\mathrm{nf}}(z)=E_{\mathrm{nf}}(0)e^{-z/\delta}$、$\delta\sim a$（build/_f5d/p322.png）；源书 书内 p.928—929 / PDF p.414—415 对近场衰减只作定性说明，未给解析式、也未定义 $\delta$（ch12-c.tex:125-132 已注明）；本版按近场衰减的通用指数形式补出并声明 $\delta\sim a$。 |
| `eq:demod` | 12-18 | 322 | down p.926-942 | 412-428 | 改编补充 | down p.936 | 版面 (12-18) $S_n=\frac{\Omega}{\pi}\int_0^{2\pi/\Omega}I(z(t))\cos(n\Omega t)\,dt$、$z(t)=\bar z+A\cos\Omega t$（build/_f5d/p322.png）；源书 §12.6.3 书内 p.936 / PDF p.422 只述「调制—解调以剔除未受调制的背景信号（直流部分）」，未印锁相解调式；本版按锁相原理补出。 |
| `eq:ters-ef` | 12-19 | 324 | down p.926-942 | 415 | 改编补充 | down p.929 | 版面 (12-19) $\mathrm{EF}\approx\left\|\frac{E_{\mathrm{loc}}(\omega_{\mathrm L})}{E_0}\right\|^2\left\|\frac{E_{\mathrm{loc}}(\omega_{\mathrm S})}{E_0}\right\|^2\approx\left\|\frac{E_{\mathrm{loc}}}{E_0}\right\|^4$（build/_f5d/p324.png）；源书 §12.6.2 书内 p.929 / PDF p.415（build/_f5d/d415.png）只作文字说「理论预测该电磁场的增强效率在 $10^3$~$10^9$」，未印增强因子式；本版按 $\|E\|^4$ 关系补出。 |
| `eq:afmir` | 12-20 | 328 | down p.926-942 | 427 | 改编补充 | down p.941 | 版面 (12-20) $A_{\mathrm{cant}}(\lambda)\propto\mu_{\mathrm{abs}}(\lambda)I(\lambda)\chi_{\mathrm{th}}$（build/_f5d/p328.png）；源书 §12.6.4 书内 p.941 / PDF p.427 只作文字说明（ch12-c.tex:625 已注明），未印该式；本版按 AFM-IR 信号与吸收系数、光强、热膨胀系数成正比的原理补出。 |

## 二、未取得终判的式（100）

| 式 | 编号 | 成品页 | 分片 | 状态 |
| --- | --- | --- | --- | --- |
| `eq:zone-law` | 2-3 | 35 | ch02-a | 未覆盖 |
| `eq:camlen` | 2-4 | 35 | ch02-a | 未覆盖 |
| `eq:weak-phase` | 2-5 | 38 | ch02-a | 未覆盖 |
| `eq:chi` | 2-6 | 38 | ch02-a | 未覆盖 |
| `eq:hrtem-contrast` | 2-7 | 38 | ch02-a | 未覆盖 |
| `eq:lambda-nonrel` | 2-8 | 38 | ch02-a | 未覆盖 |
| `eq:lambda-rel` | 2-9 | 39 | ch02-a | 未覆盖 |
| `eq:point-res` | 2-10 | 39 | ch02-a | 未覆盖 |
| `eq:ch02b-mag` | 2-11 | 40 | ch02-b | 未覆盖 |
| `eq:ch02b-zcontrast` | 2-12 | 40 | ch02-b | 未覆盖 |
| `eq:ch02b-moseley` | 2-13 | 42 | ch02-b | 未覆盖 |
| `eq:ch02b-edsint` | 2-14 | 42 | ch02-b | 未覆盖 |
| `eq:ch02b-cl` | 2-15 | 42 | ch02-b | 未覆盖 |
| `eq:ch02b-norm` | 2-16 | 43 | ch02-b | 未覆盖 |
| `eq:ch02b-kfac` | 2-17 | 43 | ch02-b | 未覆盖 |
| `eq:ch02b-thickness` | 2-18 | 43 | ch02-b | 未覆盖 |
| `eq:ch02b-eelsI` | 2-19 | 44 | ch02-b | 未覆盖 |
| `eq:ch02b-eelsratio` | 2-20 | 44 | ch02-b | 未覆盖 |
| `eq:ch02b-eelspartial` | 2-21 | 44 | ch02-b | 未覆盖 |
| `eq:ch02c-cs` | 2-22 | 55 | ch02-c | 未覆盖 |
| `eq:ch02c-envelope` | 2-23 | 56 | ch02-c | 未覆盖 |
| `eq:ch02c-radon` | 2-24 | 58 | ch02-c | 未覆盖 |
| `eq:ch02c-haadf` | 2-25 | 58 | ch02-c | 未覆盖 |
| `eq:ch02c-holo` | 2-26 | 59 | ch02-c | 未覆盖 |
| `eq:csatensor` | 8-1 | 190 | ch08-a | 未覆盖 |
| `eq:sigma1` | 8-2 | 191 | ch08-a | 未覆盖 |
| `eq:magic` | 8-3 | 191 | ch08-a | 未覆盖 |
| `eq:dipolar` | 8-4 | 191 | ch08-a | 未覆盖 |
| `eq:hh` | 8-5 | 192 | ch08-a | 未覆盖 |
| `eq:hhquad` | 8-6 | 192 | ch08-a | 未覆盖 |
| `eq:zeolite` | 8-7 | 192 | ch08-a | 未覆盖 |
| `eq:sial` | 8-8 | 193 | ch08-a | 未覆盖 |
| `eq:brunner-iso` | 8-9 | 196 | ch08-b | 未覆盖 |
| `eq:brunner-hb` | 8-10 | 196 | ch08-b | 未覆盖 |
| `eq:ernst` | 8-11 | 200 | ch08-b | 未覆盖 |
| `eq:xe-shift` | 8-12 | 201 | ch08-b | 未覆盖 |
| `eq:fraissard` | 8-13 | 202 | ch08-b | 未覆盖 |
| `eq:gibbs-emf` | 11-1 | 267 | ch11-a | 未覆盖 |
| `eq:entropy-emf` | 11-2 | 267 | ch11-a | 未覆盖 |
| `eq:she` | 11-3 | 267 | ch11-a | 未覆盖 |
| `eq:series-rate` | 11-4 | 267 | ch11-a | 未覆盖 |
| `eq:nernst` | 11-5 | 267 | ch11-a | 未覆盖 |
| `eq:redox` | 11-6 | 268 | ch11-a | 未覆盖 |
| `eq:current-basic` | 11-7 | 268 | ch11-a | 未覆盖 |
| `eq:dg-eta` | 11-8 | 268 | ch11-a | 未覆盖 |
| `eq:k-eta` | 11-9 | 268 | ch11-a | 未覆盖 |
| `eq:bv-first` | 11-10 | 268 | ch11-a | 未覆盖 |
| `eq:i0` | 11-11 | 269 | ch11-a | 未覆盖 |
| `eq:bv` | 11-12 | 269 | ch11-a | 未覆盖 |
| `eq:bv-linear` | 11-13 | 269 | ch11-a | 未覆盖 |
| `eq:bv-cathodic` | 11-14 | 269 | ch11-a | 未覆盖 |
| `eq:tafel` | 11-15 | 269 | ch11-a | 未覆盖 |
| `eq:fick1` | 11-16 | 270 | ch11-a | 未覆盖 |
| `eq:diff-layer` | 11-17 | 270 | ch11-a | 未覆盖 |
| `eq:il` | 11-18 | 270 | ch11-a | 未覆盖 |
| `eq:eta1` | 11-19 | 271 | ch11-a | 未覆盖 |
| `eq:eta2` | 11-20 | 271 | ch11-a | 未覆盖 |
| `eq:eta-conc` | 11-21 | 271 | ch11-a | 未覆盖 |
| `eq:fick2` | 11-22 | 272 | ch11-a | 未覆盖 |
| `eq:cottrell` | 11-23 | 272 | ch11-a | 未覆盖 |
| `eq:conc-profile` | 11-24 | 272 | ch11-a | 未覆盖 |
| `eq:fick2-sph` | 11-25 | 272 | ch11-a | 未覆盖 |
| `eq:chrono-irr` | 11-38 | 278 | ch11-b | 未覆盖 |
| `eq:chrono-eta` | 11-39 | 278 | ch11-b | 未覆盖 |
| `eq:chrono-ic` | 11-40 | 278 | ch11-b | 未覆盖 |
| `eq:chrono-cd` | 11-41 | 278 | ch11-b | 未覆盖 |
| `eq:chrono-dp` | 11-42 | 278 | ch11-b | 未覆盖 |
| `eq:bulk-n` | 11-43 | 280 | ch11-b | 未覆盖 |
| `eq:bulk-decay` | 11-44 | 280 | ch11-b | 未覆盖 |
| `eq:strip-ip` | 11-45 | 281 | ch11-b | 未覆盖 |
| `eq:strip-thin` | 11-46 | 281 | ch11-b | 未覆盖 |
| `eq:flux` | 11-47 | 283 | ch11-b | 未覆盖 |
| `eq:conv-diff` | 11-48 | 283 | ch11-b | 未覆盖 |
| `eq:re` | 11-49 | 283 | ch11-b | 未覆盖 |
| `eq:rde-steady` | 11-50 | 284 | ch11-b | 未覆盖 |
| `eq:levich` | 11-51 | 284 | ch11-b | 未覆盖 |
| `eq:delta0` | 11-52 | 284 | ch11-b | 未覆盖 |
| `eq:levich-general` | 11-53 | 285 | ch11-b | 未覆盖 |
| `eq:kl` | 11-54 | 285 | ch11-b | 未覆盖 |
| `eq:rde-resistance` | 11-55 | 285 | ch11-b | 未覆盖 |
| `eq:ring-limit` | 11-56 | 286 | ch11-b | 未覆盖 |
| `eq:rrde-collection` | 11-57 | 286 | ch11-b | 未覆盖 |
| `eq:rrde-shield` | 11-58 | 286 | ch11-b | 未覆盖 |
| `eq:orr-paths` | 11-59 | 286 | ch11-b | 未覆盖 |
| `eq:ume` | 11-60 | 288 | ch11-b | 未覆盖 |
| `eq:eis-d-sine` | 11-61 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-phase` | 11-62 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-cap` | 11-63 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-capohm` | 11-64 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-series` | 11-65 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-zdef` | 11-66 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-zmod` | 11-67 | 289 | ch11-d | 未覆盖 |
| `eq:eis-d-parallel` | 11-68 | 290 | ch11-d | 未覆盖 |
| `eq:eis-d-cdl` | 11-69 | 292 | ch11-d | 未覆盖 |
| `eq:eis-d-fdiff` | 11-70 | 292 | ch11-d | 未覆盖 |
| `eq:eis-d-randles` | 11-71 | 293 | ch11-d | 未覆盖 |
| `eq:eis-d-rc` | 11-72 | 293 | ch11-d | 未覆盖 |
| `eq:eis-d-warburg` | 11-73 | 293 | ch11-d | 未覆盖 |
| `eq:eis-d-cpe` | 11-74 | 293 | ch11-d | 未覆盖 |
| `eq:eis-d-cpeceff` | 11-75 | 293 | ch11-d | 未覆盖 |

## 三、本台账不主张的东西

- 不主张「式号对得上」等于「推导正确」：只核印刷形式与符号，不重做推导。
- 不主张 `形式一致但符号不同` 的式与源书等价：只主张已记录符号差异，等价性由正文符号表承担。
- 不主张 `改编补充` 的式有源书出处：这些式源书没有，判据是源书对应页范围无此式。
- 不主张未列入 372 式的行间式已核：清单只覆盖带 `\label{eq:}` 的编号式。

复跑：`python tools/review_ledger.py formulas`（判决由 `sources/logs/formulas_*.tsv` 提供）。
