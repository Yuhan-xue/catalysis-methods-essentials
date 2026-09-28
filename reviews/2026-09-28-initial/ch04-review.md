# 第 4 章审阅：X 射线衍射

审阅基线：`8c34d6902555a555159eeec38b510af42976e747`；本章现有分片：`ch04-a`, `ch04-b`。

本章为重点公式与图文一致性抽查；没有列出的问题不代表已逐式证明正确。下列条目均为本次独立定位，修复状态为未处理。

## C04-01 · P1 · 正交晶系指标化的 Q 定义与系数相差 λ²/4

位置：[chapters/parts/ch04-b.tex:779](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/chapters/parts/ch04-b.tex#L779)（固定审阅提交）。

**证据与复现：** 先定义 Q=1/d²=h²/a²+k²/b²+l²/c²=Ah²+Bk²+Cl²，随后却给 A=λ²/(4a²)。后者对应的是 sin²θ 的系数，量纲也不同。a=4 Å、λ=1.54 Å、(100) 时，两写法分别为 0.0625 Å⁻² 与 0.03705625。

**影响：** 按当前线性拟合系数反推晶胞参数会得到错误比例。

**建议修改：** 选用 Q=1/d² 与 A=1/a²，或统一改为 q=sin²θ 与 A=λ²/(4a²)，同步后续算法。

**验收条件：** 给定正交晶胞模拟 3 条独立峰，再反推 a,b,c，精确恢复输入且单位自洽。

## C04-02 · P1 · Smith–Snyder Fn 指标中的峰数比写反

位置：[chapters/parts/ch04-b.tex:860](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/chapters/parts/ch04-b.tex#L860)（固定审阅提交）。

**证据与复现：** 稿件写 Fn=(1/平均|Δ2θ|)·(Nposs/Nobs)。原论文摘要明确定义为 (1/平均|Δ2θ|)·(N/Nposs)。取误差 0.02°、实测 N=20、可能 Nposs=40，正确 Fn=25，现式为 100，且可能峰越多反而得分越高。

**影响：** 会颠倒指标化结果优劣，鼓励产生过多未观测反射的候选晶胞。

**建议修改：** 按原定义恢复比值，并写清角度单位、N 与 Nposs 的统计范围。

**验收条件：** 固定实测峰及误差，增加未观测的可能峰必须降低 Fn；数值样例得到 25。

**来源/图证：** [Smith & Snyder (1979), 原论文摘要](https://doi.org/10.1107/S002188987901178X)，本次核对的是摘要中的明示定义。

## C04-03 · P1 · Debye–Waller 振幅因子被当成强度因子

位置：[chapters/parts/ch04-b.tex:114](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/chapters/parts/ch04-b.tex#L114)（固定审阅提交）。

**证据与复现：** I=K|F|²…D 中采用 D=exp[−B(sinθ/λ)²]，同时定义 B=8π²<u²>。在相同各向同性 B 的简化下，这是振幅因子，强度应为 exp[−2B(sinθ/λ)²]。取 B=1 Å²、λ=1.5406 Å、2θ=160°，两者为 0.6646 与 0.4416；绘图 caption 约 0.55 也不与所给代码相符。

**影响：** 热振动对高角峰的衰减少算一次，强度模型、图形及图注三者不一致。

**建议修改：** 说明 F 是否已含各原子的温度因子。可在原子振幅层面处理后平方；若提取共同 B 的强度乘子，则采用双倍指数，避免重复计入。

**验收条件：** B→0 时因子为 1；给定参数的强度比为约 0.4416；图源计算值、图和 caption 一致。

**来源/图证：** [Straasø 等 (2014)，式(3)](https://journals.iucr.org/s/issues/2014/01/00/gb5017/)给出强度中的 exp[−2B(sinθ/λ)²]。

## 已知未完成范围

以下为原台账已列出的计划工作，不计入本次新定位问题数：

- `ch04-c`：Scherrer、Rietveld、实例、Debye。

[返回总览](README.md) · [执行 TODO](TODO.md)
