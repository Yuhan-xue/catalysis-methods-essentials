# 第六轮评审：科学表述、查表路径与 PDF 比对

日期：2026-10-09。评审基线：`71f5ebc5158bb87632f82c93903d7ede3afb3281`。本目录只增加评审与复现材料，不修改教材、生产工具、历史评审或发布附件。

本轮新增 **6 项 P2 问题**：3 项内容、2 项阅读设计、1 项验证流程。第五轮提出的 6 项问题在当前基线复验关闭。现有发布构建通过，并不能排除科学错误、查表语义错误或比对器漏检。

| ID | 问题 | 报告 |
| --- | --- | --- |
| R6-C01 | Rayleigh 区域的粒径六次方依赖写成反比，原书也印错 | [内容](01-content.md) |
| R6-C02 | 把电泳迁移率／Zeta 电位直接当作粒径反演依据 | [内容](01-content.md) |
| R6-C03 | DLS 分布直接标为体积分布，缺少强度权重与转换条件 | [内容](01-content.md) |
| R6-U01 | 表 9-1 的逐行核对说明先于表格出现，打断阅读路径 | [阅读设计](02-ui-reading.md) |
| R6-U02 | 拉曼反向查表的波数列混入负载百分数与相对位移 | [阅读设计](02-ui-reading.md) |
| R6-W01 | PDF 比对器把三类可见改动判为 IDENTICAL CONTENT | [验证流程](03-workflow.md) |

执行入口：[TODO](TODO.md)。历史复验：[上一轮及继承队列](04-previous-round.md)。机器可读索引：[findings.json](findings.json)。

## 验证范围

- 当前源码完整 `-Release` 构建通过：340 页、144 书签；编译错误、缺字、未定义引用、重复标签、超过 5 pt 的 overfull 均为 0；overlap 门禁为 blocking=0、candidates=109。
- 复跑 10 组现有检查，全部退出 0；另构造 1 个元数据对照和 3 个 PDF 视觉改动负例，并独立计算粒度测量反例。详见 [verification.json](verification.json)、[构建摘要](build-summary.txt)。
- 以接触表抽看 36 个不同 PDF 页面，放大查看 10 页（20、22、23、122、161、162、205、206、218、219）。原书上册 PDF 83、91、93 页另作图像核对。抽样页清单和 PDF 哈希见 [audit.json](audit.json)，可见证据见 [evidence](evidence/README.md)。
- 表格台账当前为 T1=14、T2=59、T3=12、T4=0。T2 明确不代表每格都核对；85 表来源格式检查通过也不等于内容正确。本轮不重新认证全部表格。
- 所有“PDF 页”均为本次构建的一基物理页码；S1 的“书内页”另列。没有验收全书每页／每式，没有更新 release。报告针对当前 main 源码制品，不将它等同于此前发布的 314 页附件。

本轮同步时发现远端历史已重写，评审分支直接从当前 `origin/main` 建立，未合并旧 main。问题的“新增”是首次在本轮提出，不表示都由最近提交引入。

## 重现

在仓库根目录，先用现有构建环境运行 `pwsh -NoProfile -File tools/build.ps1 -Release`，再运行：

```powershell
python reviews/2026-10-09-round6/recheck_review.py --out build/review-round6
```

需 Python、NumPy、SciPy、PyMuPDF、Pillow，以及生产工具所需的现有环境。脚本写到 `--out` 和现有工具的 `build/`，不回写教材。脚本退出 0 仅表示取证完成，必须阅读 JSON 中各命令退出码和负例结果；它不是新的发布门禁。当前归档 JSON 的工作区绝对路径已替换成 `$ROOT`／`$OUT`，结果值未改。
