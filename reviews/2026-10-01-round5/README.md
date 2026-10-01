# 催化研究方法精要第五轮 reviews

日期：2026-10-01。已同步远端 main；评审基线 `69c3d182618083bb47dd7230a62fe0e5c10076a3`。
本轮新增 **6 项：1 P1、4 P2、1 P3**。只新增评审资料，不修改教材正文、生产工具和发布 PDF。

| 文件 | 内容 |
|---|---|
| [01-content.md](01-content.md) | 数值、物理解释与教学条件 |
| [02-ui-reading.md](02-ui-reading.md) | 实际 PDF 的图形、排版与阅读流程 |
| [03-workflow.md](03-workflow.md) | 验证工具、复现边界及流程设计 |
| [04-previous-round.md](04-previous-round.md) | 第四轮逐项复验及继承事项 |
| [TODO.md](TODO.md) | 按优先级排序的实施与验收清单 |
| [findings.json](findings.json) | 新问题的文件、行号、优先级索引 |
| [recheck_review.py](recheck_review.py) / [verification.json](verification.json) | 独立复算、隔离反例与运行结果 |
| [audit.json](audit.json) / [evidence](evidence/README.md) | PDF 哈希、抽样页清单与局部截图 |
| [build-summary.txt](build-summary.txt) | 本轮构建命令和日志尾部 |

## 本轮验证

- 发布构建实际完成：314 页，错误、超限 overfull、缺字、未定义引用、重复标签均为 0；重叠门禁 PASS，阻断 0、候选 91。
- 来源台账 85/85；PDF 144 个书签落页及 15 个必要入口通过；EIS 探针和 9 个自测通过；TG 654 点和 TPD 415 点再生通过。
- 独立复算 TPD 峰温与半高宽，发现单位与宽度叙述错误；自动检查通过不抵消该结果。
- 查看 37 个不同物理页的联系表，放大 p.110、186、187、273、309，确认新问题与上一轮视觉修复。

当前候选 PDF：**314 页、144 个书签**；SHA-256：
`29efd150057dab90153394d9a0e93644fe346761e9a15eaea3bfd3277b74e839`。

复现：在仓库根目录运行 `python reviews/2026-10-01-round5/recheck_review.py --out build/review-round5`。
脚本退出 0 表示取证完成，不表示本书无错误。后续源码修改后需核对基线、哈希和模型假设。

## 范围

这是当前源码和本地重建 PDF 的抽样审阅。未逐页逐式审完 314 页，未重新下载预发布资产，也未对两本原书扫描 PDF 做本轮全面图像核对。只保存必要局部截图，避免把整书图册重复加入已瘦身的仓库。

文档中的收口声明属于待核材料。新问题指本轮新确认，未必由最近一次提交引入；历史报告不改写，旧问题不重复计数。
