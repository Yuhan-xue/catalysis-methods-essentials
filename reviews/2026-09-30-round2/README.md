# 第二轮复审与待办（2026-09-30）

本轮按“重新同步，再写 reviews 和 todo”复审催化研究仓库。审阅基线为 `38f32fbd6abb85155d3bbc9cb55e293cc637acd4`（含新增表格来源标注与重复引入门禁）。只新增本目录，不修改正文、图源或生产工具。提交前再次同步到 `38f32fb`；它相对完整构建时的 `5109139` 只更新 HANDOFF，LaTeX、图源与工具完全一致，故 PDF 证据仍适用。

**结论：发布构建通过，但仍有 16 项可定位问题：6 项 P1、10 项 P2。** 编译成功不能证明公式、算例、来源和导航正确。优先处理积炭速率、Weisz–Prater 算例、传质因子、并联阻抗、AFM 周期与凭据暴露。

| 文件 | 用途 |
|---|---|
| [01-content-review.md](01-content-review.md) | 9 项科学内容问题，附直接代入与量纲证据 |
| [02-layout-navigation-review.md](02-layout-navigation-review.md) | 2 项导航缺陷与版式、信息密度建议 |
| [03-workflow-review.md](03-workflow-review.md) | 5 项交接与验收流程问题 |
| [04-previous-round.md](04-previous-round.md) | 对首轮 25 项的复核状态，不把“修改过”当成全面关闭 |
| [TODO.md](TODO.md) | 按优先级排列的任务与验收条件 |
| [findings.json](findings.json) | 16 项机器可读定位索引 |
| [recheck_review.py](recheck_review.py) | 数值反例与隔离工具探针 |
| [verification.json](verification.json) | 基线实测结果；缺陷复现成功不等于成书验收通过 |
| [pdf-audit.json](pdf-audit.json) | PDF 哈希、书签、视觉抽查页清单 |
| [build-release.txt](build-release.txt) | 本轮重新构建的完整摘要 |

## 实际验证与边界

- 在 `5109139` 的源码上完整运行 `tools/build.ps1 -Release`：**310 页，退出码 0**；编译错误、超宽大于 5 pt、缺字、未定义引用、重复标签均为 0，重复引入检查通过。
- 最新 PDF 有 **143 条书签**。抽看 53 页的缩略图，覆盖十二章、导读、综合应用、索引及重点算例；重点核查正文与源文件。页码均指本轮生成的 PDF 物理页。
- 阅读用户提供的下册原页面，重点核对 PDF p.403–404（书内 p.917–918）的 AFM 公式。原书本身也有周期定义问题，不能一律归咎 OCR。
- 全书重叠扫描得到跨串文字候选 86、同串 22、图形相撞 0、填充粗条 12。**这是候选统计，不是 86 项已确认叠印，也不是全书零叠印证明**；本轮不把这些数字直接列为排版缺陷。
- 新来源门禁在真实基线上检查通过；隔离注入“书页和 PDF 页同时加 10000”后仍通过，说明其 PASS 的含义需要收窄。
- 没有逐式证明全部内容，没有对全部图表逐页核对原书，没有完成印刷尺寸可读性测试，也没有进行网站应用 UI 测试：仓库产物是 LaTeX/PDF，本轮 UI 指文档阅读与查阅体验。

## 复现

```powershell
python reviews/2026-09-30-round2/recheck_review.py --out build/review-round2-probes
pwsh -NoProfile -File tools/build.ps1 -Release
```

探针依赖 PyMuPDF、fontTools、仓库工具所需依赖，以及 Windows/PowerShell。`--out` 保存隔离样例与输出；省略时使用临时目录。脚本不修改正文与已有生产检查报告。其中代数反例固定采用审阅时公式，不会自动识别未来任意公式修复；关闭问题仍须人工核对对应公式、说明、算例和 PDF。

P1 表示足以改变计算结论、方法使用或暴露访问凭据；P2 表示导航、约定或流程可靠性缺陷。建议不是已实施修复。
