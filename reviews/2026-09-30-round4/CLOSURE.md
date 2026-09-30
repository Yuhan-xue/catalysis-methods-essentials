# 第四轮评审 · 逐 ID 关闭记录（CLOSURE）

> 由执行方在修完后写入，逐条对应 [TODO.md](TODO.md) 的 8 项 P2 与继承队列。结论口径是
> **候选完成 + 证据链 + 残余风险**，不是最终裁决；裁决权在评审方。

## 0 交付元信息

| 项 | 值 |
|---|---|
| 代码起点 | `4e1db7f`（第四轮评审目录提交） |
| 构建模式 | release（`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release`） |
| 制品 | `build/main.pdf`：**313 页 / 143 条书签 / 4 004 860 字节**，SHA-256 `327EDB67BFE8BDE570F2D145DDAC24ABE211C8BE021CE7E3EA8E0EE5D0D221B3` |
| 入库 | `build/` 被 `.gitignore` 忽略，PDF 不入库；复现请重跑上面的构建命令 |
| 页数变化 | 315 → 313 页。来源：缩写表列宽调整（中文名不再被压成窄列）与正文措辞修改，非浮动体错排（自动门禁全 0） |
| 八项发布门禁 | errors 0 / overfull>5pt 0 / missing glyphs 0 / undefined refs 0 / dup labels 0 / dup includes ok / overlap ok（blocking=0 candidates=91）/ PASS |
| 其他门禁 | `check_src.py` 85 表 PASS 85；`pdf_probe.py` U01/U02/W03 全 PASS；`fig_probe_eis.py` PASS；`recompute_ch03b_dtg.py` PASS（654 点）；`gen_tpd_table.py --check` PASS（5×83 点） |

### 无视觉能力声明（写在最前面）

本会话模型**没有视觉能力**（`read_image` 只返回尺寸与 sha256）。因此 R4-U01/U02 的
「放大图观看」没有做、也做不到；替代做法是**可复算的矢量探针 + 文字层/书签探针**，
并且 R4-W01 的修复正是把这层探针的假阴性堵上。仍建议有视觉者打开 `build/main.pdf`
复核图 11-5 与缩写表的观感（页号见下）。

## 1 新增 8 项

| ID | 结论 | 改动 | 实测证据 |
|---|---|---|---|
| R4-C01 | 候选完成 | `chapters/parts/ch06-a.tex`：删去功率式里重复的 $\sin^2\theta$，新增式 (6-x) $\mathrm{d}\sigma/\mathrm{d}\Omega=K\sin^2\theta$ 明确定义 | 用新定义 45°/90° 相对收集功率 = 0.5、30°/90° = 0.25（旧式给 0.25/0.0625）；全式只出现一次偶极角分布；量纲 $\mathrm{m^2\,sr^{-1}\times sr\times m^{-2}}$ 无量纲 |
| R4-C02 | 候选完成 | `chapters/parts/ch11-d.tex`：删去「低频极限电容」说法，新增表观并联电容式 $C_p(\omega)=Q\sin(n\pi/2)\omega^{n-1}$ | $n=1$ 退化为常数 $Q=C_{\mathrm{dl}}$；$n=0.85$ 在 1/0.01/0.0001 Hz 给出 1.63/3.25/6.49 µF（非 0.5 µF）；$C_{\mathrm{eff}}=0.5$ µF 只在峰值时间常数约定下成立 |
| R4-C03 | 候选完成 | `chapters/parts/ch11-d.tex` 读图实例推断 (4)：把「用斜率反算 σ」改为「几何斜率只作判别」，定量须用 $\omega^{-1/2}$ 坐标或复数拟合 | σ=20 与 40 的 Nyquist 几何斜率同为 1（与 σ 无关）；对 $\omega^{-1/2}$ 作图斜率分别为 20、40 $\Omega\cdot\mathrm{s^{-1/2}}$ |
| R4-C04 | 候选完成 | `chapters/parts/ch03-b.tex` pitfall：改为精确式 $h_t(\beta)=\beta h_T(\beta)$ 并给数值 | β 由 2.5→20 K·min⁻¹（8 倍），$h_T$ 0.387→0.343 %·K⁻¹、$h_t$ 0.968→6.870 %·min⁻¹，只增 7.09766 倍；与 `recheck_review.py` 独立复算一致 |
| R4-U01 | 候选完成 | `chapters/parts/ch11-d.tex` 图 11-5(a) 说明块：宽 28→24 mm、锚点 $y$ 14.5→9 Ω | 探针在**未修** PDF 上复现 1 处穿字（`理想弧顶点(60,50)` 被 2.5 pt 虚线段穿过，`build/r4/eis-pre.*`）；修后 0 处（`build/r4/eis.*`）。整页与放大观感仍建议人工复核（p.272） |
| R4-U02 | 候选完成 | `chapters/ch90-backmatter.tex`：列定义改 `p{14mm}X p{40mm}p{20mm}p{34mm}`（英文全称改可伸缩 X） | DRIFT/SSITKA 等中文名在 8pt 下按正常短语成行（PDF 文字层逐行核对，无 2—3 字窄列）；长英文名折行无 overfull；跨页续表头保留（表占 p.308—310，p.309/310 均重复表头）；14 字/行 |
| R4-W01 | 候选完成 | `tools/fig_probe_eis.py`：P3 改**路径级**分类（数据曲线 vs 轴/刻度），对数据曲线**全部短段**判交；文字改行框；新增 `--selftest` | 单元自检 9 项全 PASS（虚线被检出、实线/虚线一致、采样密度不改变结论、刻度与边框不误报、`dashes_shorter_than_old_threshold`）；对已知缺陷 PDF 阻断、修后 PASS |
| R4-W02 | 候选完成 | 新增受版本管理的 `tools/recompute_ch03b_dtg.py`（参数、采样规则、容差在文件头），`ch03-b.tex` 注释改指它 | 干净检出下 `python tools/recompute_ch03b_dtg.py` → 8 组 **654 点**全部再生，x 逐点相等、TG 最大偏差 1.02e-4 %、DTG 5.0e-6 %/K（在声明容差内）；回执见 [R4-W02-receipt.txt](R4-W02-receipt.txt) |

## 2 继承队列

| 项 | 结论 | 证据 |
|---|---|---|
| 导读两处 XAFS 归属 | 候选完成 | `chapters/ch00-intro.tex:69,115`：把 XAFS 的「（第 6 章）／（第 8 章）」改为「本书未系统介绍」，与缩写表口径一致 |
| C05-02 TPD 生成器逐点复验 | 候选完成 | `tools/gen_tpd_table.py --check`：把 `ch05-a.tex` 内嵌坐标与数值解逐点比对，5 张表 × 83 点全 PASS，worst rel 4.795e-6 |
| C09-01 覆盖矩阵 | 候选完成 | 新增 [sources/ch09_coverage_matrix.md](../../../sources/ch09_coverage_matrix.md)：分片↔原书节逐项对齐，登记重复项并去重（shake-up 机理唯一主要在 §9.4），§9.6—§9.8 明确删节并记理由；撤下 `ch09-c` 指向分片 d 的**假陈述** |
| 85 表逐表核图 | 未完成 | 需页面图像；`check_src.py` 的结构 PASS 不等于内容核对完成，本记录不代为声称 |
| 旧凭据轮换确认 | 未完成 | 需账户管理者；本记录不复述凭据、不宣称已轮换 |

## 3 复跑命令与产物

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/build.ps1 -Release
python tools/fig_probe_eis.py --selftest
python tools/fig_probe_eis.py --pdf build/main.pdf --out build/r4/eis.txt --json build/r4/eis.json
python tools/pdf_probe.py --pdf build/main.pdf --out build/r4/pdf_probe.txt --json build/r4/pdf_probe.json
python tools/check_src.py
python tools/gen_tpd_table.py --check
python tools/recompute_ch03b_dtg.py
python reviews/2026-09-30-round4/recheck_review.py --out build/review-round4
```

## 4 残余风险

- 本轮公式改动（R4-C01/C02/C03/C04）已与独立复算/doc 内数值对照，但**未逐字核对原书页面
  图像**；后续有视觉会话应按 `sources/formula_verify.md` 的口径补核。
- 图 11-5 与缩写表只做了矢量/文字层探针，**观感复核**（字体大小、断页、弧线粗细）仍依赖人工。
- §9.2.8—§9.2.10 在源切片无 OCR 文本，正文按学科标准形式重建，符号/数值存疑点见各 `\tocheck{}`。
