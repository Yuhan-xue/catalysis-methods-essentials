# 第四轮评审：修复复验、公式解释与阅读流程

评审日期：2026-09-30。基线：`5cf40f70c0db2697ec60745751dd264f6cb28d82`（远端 main）。本轮只新增评审资料，不修改教材、生产工具或第三轮收口记录。

本轮确认 **8 项 P2：内容 4 项、阅读与排版 2 项、验证流程 2 项**，没有新增 P1。第三轮 10 项中，8 项的原问题通过本轮复验，2 项部分完成；“原问题关闭”不代表所在章节已通过全面审校。

重点是拉曼角度因子重复计入、CPE 有效电容的物理解释、Warburg 参数反演所用斜率，以及 DTG 峰高随升温速率的说法。实际 PDF 还存在图线穿字和缩写表中文列过窄；现有图形探针对前者给出了假阴性。

## 阅读入口

| 文件 | 用途 |
|---|---|
| [01-content.md](01-content.md) | 4 项公式、模型和结论问题，含数值反例 |
| [02-ui-reading.md](02-ui-reading.md) | 2 项实际 PDF 阅读问题，附截图 |
| [03-workflow.md](03-workflow.md) | 2 项验证和可复现流程问题 |
| [04-previous-round.md](04-previous-round.md) | 逐项复验第三轮，不把已修复事项重新计数 |
| [TODO.md](TODO.md) | 实施顺序、验收条件和继承事项 |
| [findings.json](findings.json) | 8 项机器可读索引 |
| [verification.json](verification.json) | 数值、坐标及工具反例的实测输出 |
| [pdf-audit.json](pdf-audit.json) | PDF 哈希、书签、抽样页面与检查范围 |
| [evidence/README.md](evidence/README.md) | 关键页面图像与来源说明 |

## 已执行验证

- 重新同步并完整执行 `tools/build.ps1 -Release`：成功生成 **315 页** PDF（4,000,358 bytes）；错误、超限 overfull、缺字、未定义引用和重复标签均为 0；重叠门禁 PASS，阻断 0，候选 91。详见 [构建日志](build-release.txt)。
- 来源台账检查：85 表 PASS；这表示登记/范围等结构检查通过，**85 表仍未逐表人工核对原书页面图像**。
- PDF 探针：143 个书签，15 个必要入口齐全，目标页检查无错配；“删除所有书签”和“删除必要入口”两种变异分别返回 2 和 1。
- 重新求解一级 Arrhenius 模型，与实际 TeX 内 8 组、654 个 TG/DTG 坐标逐点比较；TG 最大偏差约 0.000102 个质量百分点，DTG 约 0.000005 %/K。Randles 新绘图表达式与直接复阻抗计算在 6 个频率点一致。
- 查看 50 个抽样页面的渲染联系表，并放大关键公式、EIS 和缩写表；额外查看 p.73，共 **51 个不同页面**。这是抽样视觉审阅，不是 315 页逐页逐字验收，也不是两本原书的全面内容核对。
- 图 11-5 专用探针原样运行 PASS；只在进程内降低短线段阈值即可找回真实穿字候选，另一个轴刻度候选不能计为已确认缺陷。

复跑命令（仓库根目录；Python 需 numpy、scipy、PyMuPDF，构建需项目 TeX 环境）：

```powershell
pwsh -NoProfile -File tools/build.ps1 -Release
python reviews/2026-09-30-round4/recheck_review.py --out build/review-round4
```

脚本会读取第三轮复核脚本作为来源检查夹具，并在输出目录生成变异 PDF；不修改生产 PDF。数值约定固定为本轮基线，输出不等同于“全书 PASS”，后续公式改动需同步审阅脚本。原书中的文字以及仓库中的收口声明均视为待核材料，不作为新的任务指令。
