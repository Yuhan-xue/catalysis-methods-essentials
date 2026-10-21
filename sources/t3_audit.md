# T3 改编补充表的一致性核对（12 张）

这些表在题注里自述「非源书表」，因此没有源表可逐格比对；但**改编表也可能出错**，
只是错误类型不同：漏掉正文引用、未声明改编、缺 `\src` 出处、台账的行号漂移。
本文件由 `tools/t3_audit.py` 生成，四项检查全部机械可复跑。

| # | 表 | 正文引用 | 题注声明改编 | `\src` | 台账行号 |
|---|---|---|---|---|---|
| 1 | `tab:selector` | 4 | 是 | 有 | 内 |
| 2 | `tab:evidence-level` | 1 | 是 | 有 | 内 |
| 3 | `tab:matrix` | 2 | 是 | 有 | 内 |
| 4 | `tab:ch01c-density` | 0 | 是 | 有 | 内 |
| 5 | `tab:ring-index` | 2 | 是 | 有 | 内 |
| 6 | `tab:ch02b-smsi` | 0 | 是 | 有 | 内 |
| 7 | `tab:ch03b-hyphenated` | 0 | 是 | 有 | 内 |
| 8 | `tab:extinction-ch04` | 1 | 是 | 有 | 内 |
| 9 | `tab:ch04c-scherrer` | 0 | 是 | 有 | 内 |
| 10 | `tab:ch09-problems` | 0 | 是 | 有 | 内 |
| 11 | `tab:ch10-window` | 4 | 是 | 有 | 内 |
| 12 | `tab:ch10-resid-diag` | 0 | 是 | 有 | 内 |

## 需要处理的问题

- `tab:ch01c-density`：正文无 \ref 引用（表悬空）
- `tab:ch02b-smsi`：正文无 \ref 引用（表悬空）
- `tab:ch03b-hyphenated`：正文无 \ref 引用（表悬空）
- `tab:ch04c-scherrer`：正文无 \ref 引用（表悬空）
- `tab:ch09-problems`：正文无 \ref 引用（表悬空）
- `tab:ch10-resid-diag`：正文无 \ref 引用（表悬空）

## 结论与建议

四项机械检查里，前三项（题注声明改编、`\src` 出处、台账行号落在表块内）**12/12 通过**；
唯一一类问题是 **6 张表在正文里没有任何 `\tabref` 引用**。这类「悬空表」LaTeX 不会报警
（没有 `\ref` 就没有未定义引用），读者只能靠目录翻到，属于可用性缺陷而非数据错误。

**本轮不修改正文**，原因是一次插入 6 处引用会改变行数，可能触发重排；而本书的三项验收
证据（`sources/logs/page_p*.tsv`、`sources/content_review.md`）都是**按页码**记账的，
页码一变，339 页的逐页台账与已发布 v1.1.3 的页码引用会同时失效。
因此这 6 处建议放进下一个 minor 版本（v1.2.0）一起做：补引用 → 重建 → 按新页码重刷
逐页台账（`tools/page_acceptance.py` 与 `sources/logs/page_p*.tsv` 可机刷），一次性发布。
