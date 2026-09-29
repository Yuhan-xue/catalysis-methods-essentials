# 第三轮 reviews 与 TODO（2026-09-30）

本轮从远端 `main` 同步至 **`8df5e1e0b9a2ccbe5ac0edf0d8d823e2fc5af114`**，复审 R2 修复及其相邻公式、绘图、导航和检查工具。只增加本目录，不修改教材、图源、生产工具或旧轮报告。

**确认 10 项问题：2 项 P1、8 项 P2。** 重点是 EIS 图 11-5 的 CPE、Warburg 曲线并未实现正文公式，以及拉曼“量纲检查”仍然不成立。R2 的 16 项中，13 项指定问题已修复，2 项部分关闭，1 项重开；详见逐项复核表。这不是对全书内容正确性的认证。

| 文件 | 用途 |
|---|---|
| [01-content-review.md](01-content-review.md) | 4 项内容/模型问题，附代数推导、数值反例与 PDF 页码 |
| [02-layout-navigation-review.md](02-layout-navigation-review.md) | 3 项图内标注、索引查阅流程问题及信息密度建议 |
| [03-workflow-review.md](03-workflow-review.md) | 3 项检查工具的假通过情形，附正反对照 |
| [04-previous-round.md](04-previous-round.md) | R2 全部 16 项的独立复核状态与历史遗留 |
| [TODO.md](TODO.md) | 修复顺序、依赖与可执行验收条件 |
| [findings.json](findings.json) | 10 项机器可读定位与任务索引 |
| [recheck_review.py](recheck_review.py) | 数值复算和隔离工具探针 |
| [verification.json](verification.json) | 本轮实测输出；反例复现不是成书 PASS |
| [pdf-audit.json](pdf-audit.json) | PDF 哈希、143 条书签、54 页视觉抽查清单 |
| [evidence/README.md](evidence/README.md) | 关键页面截图与阅读说明 |
| [build-release.txt](build-release.txt) | 完整发布构建摘要 |

## 本轮实际验证

- `tools/build.ps1 -Release` 完整构建：**313 页、退出码 0**；编译错误、缺字、未定义引用、重复标签、超宽 >5 pt 均为 0；重复引入通过；重叠门禁 `PASS blocking=0 candidates=99`。
- `check_src.py`：85 张登记表格 PASS。当前台账为已核对 0、未核对 85；本轮发现的是工具对新增表格与未知状态的处理缺陷，未声称当前 85 张表已有伪造人工核验记录。
- `pdf_probe.py`：143 条书签目标检查通过；后置页眉串章命中 0。另用隔离 PDF 验证无书签输入仍错误返回 PASS。
- 缩略图抽查 51 页，另外精看 p.123、270、271，共 **54 个不同页面**；重点放大 p.72、122–123、270–273、307、309。页码均为本轮 PDF 物理页。书签实际落页、图内标注、曲线外形和索引表位置均与源文件对照。
- 直接用正文等效电路做复数运算；积分一级 Arrhenius 模型；用 XeLaTeX 最小样例确认 PGF 默认三角函数角度单位。来源与 PDF 工具探针均在隔离文件上运行，含应阻断和应通过的对照。

## 复现与边界

```powershell
python reviews/2026-09-30-round3/recheck_review.py --out build/review-round3
pwsh -NoProfile -File tools/build.ps1 -Release
python tools/check_src.py
python tools/pdf_probe.py --out build/pdf_probe_r3.txt --json build/pdf_probe_r3.json
```

脚本依赖 numpy、scipy、PyMuPDF 与重叠检查所需依赖。数值部分固定采用本轮基线参数，输出带源码 SHA-256；将来正文变更后仍须人工复核公式和图，不能只重跑脚本就关闭问题。完整构建已经通过，无需为本轮纯评审文档重复构建。

未逐式证明全书，未重新逐页核对两册原书，未验证全部 99 个重叠候选，未做 A4 实物打印或手机端阅读测试，未审计所有辅助工具。UI 指 LaTeX/PDF 阅读界面与查阅流程，未声称测试了独立网站应用。图 11-5 的确认缺陷来自实际渲染，不由候选计数推断。旧口令轮换及历史来源覆盖待办继续保留，不重复算作本轮新增问题。

P1：会使计算、读图或方法判定产生实质错误，应优先处理。P2：约定、查阅体验或验收可信度问题。建议均尚未实施。
