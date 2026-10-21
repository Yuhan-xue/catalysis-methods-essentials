# 待办：下一次 minor 版本（v1.2.0）

本文件记录**已经查清、但因为代价或范围原因没有在本版动手**的事项。每条都写了依据、代价与验证方式，
以便下次开工时不必重新研究。

## 1. 5 张悬空表补正文引用（需重排，+1 页）

| 表 | 位置 | 建议插入点 |
|---|---|---|
| `tab:ch01c-density` | `chapters/parts/ch01-c.tex:828` | 段末「…常见原因。」之后 |
| `tab:ch02b-smsi` | `chapters/parts/ch02-b.tex:1111` | 「现已按原页改正。」之后 |
| `tab:ch03b-hyphenated` | `chapters/parts/ch03-b.tex:92` | `\end{dataflow}` 之后 |
| `tab:ch04c-scherrer` | `chapters/parts/ch04-c.tex:176` | 读图实例 `\end{example}` 之后 |
| `tab:ch10-resid-diag` | `chapters/parts/ch10-b.tex:255` | 「…互补与回查）。」的 `\end{infer}` 之后 |

- **依据**：`sources/t3_audit.md`（`python tools/t3_audit.py` 可复跑）。
- **实测代价**：5 处各加一句引用后重建，**339 页 → 340 页**，门禁仍全绿。
- **为什么没做**：三项验收的证据按页记账（`sources/logs/page_p*.tsv` 339 行、`sources/content_review.md`），
  页数一变，页码引用与已发布 v1.1.3 同时失效。
- **正确顺序**：补引用 → 重建 → 用 `tools/page_acceptance.py` 重刷逐页台账（必要时重读移位页）
  → `python tools/acceptance_all.py --build` → 发布 v1.2.0。
- **已备好的草稿**：分支 `v1.2.0-prep`（提交 `e70d811`，已推送）已按上表五处插入最小引用句，
  实测 **339 → 340 页**、该分支门禁全绿；合并前仍需重刷逐页台账并重发版本。
  主线（`main`）保持 339 页 v1.1.3 不变——这是默认处置：改动可随时挑用，但不作废现有逐页证据。

## 2. 12 张 T3「改编补充」表的题注与正文交叉审查

- **已做**：四项机械检查（题注声明改编、`\src` 出处、台账行号、正文引用）12/12 通过。
- **已做**：数值回查（`tools/t3_digit_audit.py` → `sources/t3_digit_audit.md`，提交 `f5d114c`）——
  12 张表共 141 个数值 token，把各表 `\src` 指到的源页 OCR 后逐 token 回找；
  命中情况见报告表格，未命中项已按「计算/模型生成、表内编号噪声、需人工确认、无源页」分诊。
- **已澄清**：`tab:selector` 是纯定性选型矩阵，不含数据值；审计里它那 14 个「数值」全是
  `\chapref` 章号与 §1.1.2 节号，不是阈值。故这一项没有遗留问题。
- **代价**：低（不动正文），已完成一轮。

## 3. 46 格「文字层」证据的第二通道（已完成，留档备查）

已由 `tools/ocr_backfill.py`（30 个数值格，全部命中）与 `sources/evidence_upgrade.md`
（16 个定性格，逐页读图）补齐，`sources/textlayer_backfill.md` 现为 30 + 16 + 0。
若将来重跑 OCR，缓存 `build/_ocr/up_*.txt` 可复用。

## 4. 83 处「形式一致但符号不同」的符号体系归一

- **现状**：逐式记了理由（`sources/formula_crosscheck.md`），但全书尚无统一符号表。
- **代价**：中高（涉及正文改写与再核对），建议与 v1.2.0 的排版调整一起做。
