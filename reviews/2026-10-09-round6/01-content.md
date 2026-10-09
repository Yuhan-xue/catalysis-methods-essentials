# 内容评审

基线、制品与范围见 [README](README.md)。以下三项相互关联，但修复对象不同：散射定律、测量通道、分布权重。均为 **P2，待修复**。

## R6-C01：小粒子散射强度与粒径六次方的关系写反

**定位**：`chapters/parts/ch01-c.tex:382–383`，当前 PDF p.22。

正文在粒径远小于入射波长的条件下写“强度与粒径的六次方成反比”。在材料、介质、波长、入射强度、观测几何和颗粒数固定的 Rayleigh 条件下，应为单颗粒散射强度 **I ∝ d⁶**。这会直接影响读者判断少量大颗粒／团聚体为何主导散射信号。[Malvern：DLS 基础与 Rayleigh 依赖](https://www.malvernpanalytical.com/en/learn/knowledge-center/technical-notes/tn101104dynamiclightscatteringintroduction)

**独立反例**：直径从 10 nm 增至 20 nm，相同颗粒数下强度比是 64；按正文则为 1/64，两种预测相差 4096 倍。这里未固定总质量，也不把这个近似延伸到任意粒径。

**原书核对**：S1 书内 p.72／PDF p.91 的原页图像也印“反比”。因此这是应作科学勘误的原书表述，不应报成 OCR 错字，也不能以“逐字相同”关闭。图像核对与科学核验应保留两条独立结论。

**建议**：改为正比，写清 Rayleigh 及控制变量条件；附简短原书勘误说明。验收时复算 10／20 nm 比值并检查最终 PDF，不能只检查源码关键词。

## R6-C02：ELS 的迁移率／Zeta 电位不能直接唯一换算粒径

**定位**：`chapters/parts/ch01-c.tex:226`、`429–431`，PDF p.20、23。表 1-4 把电泳法列为流体动力学等效径与体积分布，正文说测电泳迁移率即可计算粒径及分布。

这里把同一仪器可能配备的两种测量通道合并了：ELS 测电泳迁移率并在电动学模型下推算 Zeta 电位；DLS 从布朗运动的相关衰减取得扩散系数，再求水动力学粒径。仪器同时报告 Zeta 和粒径，并不证明前者可直接唯一反演后者。[Malvern：ELS 测量对象](https://www.malvernpanalytical.com/en/products/technology/light-scattering/electrophoretic-light-scattering)、[电动学模型与极限条件](https://www.malvernpanalytical.com/br/learn/knowledge-center/technical-notes/tn101104zetasizernanoelectrokineticmodelling)

**独立反例**：取薄双电层 Smoluchowski 极限，μₑ=εζ/η。固定 ζ=25 mV、εᵣ=78.5、η=1 mPa·s、T=298.15 K；100 nm 和 200 nm 球形颗粒都给出 μₑ≈1.7376×10⁻⁸ m²/(V·s)，而 Stokes–Einstein 扩散系数分别为 4.3676×10⁻¹² 和 2.1838×10⁻¹² m²/s。相同迁移率对应不同尺寸，足以否定正文的无条件唯一反演。此反例不宣称所有电动学模型都完全不含尺寸。

**原书核对**：S1 书内 p.74／PDF p.93 也有由迁移率计算粒径的概括。应补充科学限定；问题不是“没有照原书写”。

**建议**：表和正文同时分开“ELS→迁移率→Zeta”与“DLS→扩散系数→粒径”；电泳行不再无条件声称给出体积分布。如果确实采用含粒径的特殊反演模型，必须列额外输入、适用范围和可辨识条件。验收应包含上述同迁移率、异尺寸反例。

## R6-C03：DLS 的体积分布需要转换，不能当作直接输出口径

**定位**：`chapters/parts/ch01-c.tex:225`、`424–426`，PDF p.20、23。

表 1-4 无限定地写“体积分布”，同时声称不引入颗粒性质参数。DLS 粒径分布的基本权重是散射强度；体积／数量口径依赖后续模型转换。把体积分布与“不需要颗粒参数”并列，会诱导读者直接比较 DLS 峰面积和 TEM 个数分布，或把强度占比当体积分数。累积量法的 z-average 和 PDI 也应与反演分布、其他平均径区分。[NIST：Dynamic light scattering distributions by any means](https://www.nist.gov/publications/dynamic-light-scattering-distributions-any-means)、[Malvern：强度至体积分布转换](https://www.malvernpanalytical.com/en/learn/knowledge-center/technical-notes/tn101104dynamiclightscatteringintroduction)

**独立反例**：相同材料、Rayleigh 条件下，等个数的 10 nm／20 nm 两群颗粒，体积权重是 1:8，强度权重是 1:64；大颗粒分别占 88.89% 与 98.46%。它们不能直接互换。该计算只检查权重语义，不模拟 DLS 多峰反演分辨率。

**原书核对**：S1 书内 p.64／PDF p.83 原表 DLS 行也列体积分布。忠实转录不免除说明仪器输出与模型转换的责任。

**建议**：表中注明“强度加权粒径分布；体积／数量分布为模型转换”，另列 z-average／PDI；把水动力学直径求解所需温度、介质黏度等输入，与体积转换所需的形状、光学性质、散射模型等假设分开。不得改成另一种绝对说法——例如所有 DLS 算法都需要输入颗粒折射率。验收包含双粒径权重算例和一个完整的输出口径标注示例。

数值记录在 [verification.json](verification.json) 的 `physics`；复现脚本为 [recheck_review.py](recheck_review.py)。正文截图见 [证据索引](evidence/README.md)。在线资料访问日期为 2026-10-09；以上计算与缺陷判断为本轮独立推导。
