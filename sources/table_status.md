# 85 张表的核对状态台账（`sources/table_status.md`）

本文件由 `tools/table_status.py` 从磁盘可核验事实生成（脚本与输入均已入库，复跑即可重排）。
用于逐表回答一个问题：**这张表的内容到底有没有对照过原页面图像、有没有逐格比对？**
判定只认四类证据：`sources/table_pixel_verify.md` 的逐格读图段落、
`sources/table_cells.tsv` / `sources/table_cells.md` 的逐单元格核对判决、
分片文件内注明「已对照原页面图像」的就地 `\emph{核对说明}`、
以及题注/`\src` 自述「非源书表格」的改编声明。
**没有证据的表一律记「未核对页面图像」，不因结构门禁通过或 OCR 文本命中而升级。**

表总数 = 85（`env` 为 `table`/`longtable`；figure 行不计入）。

| 层级 | 含义 | 张数 |
| --- | --- | --- |
| T1 | 既有逐格读图核对（`table_pixel_verify.md` 有结论） | 14 |
| T1c | 2026-10-21 逐单元格核对（`table_cells.tsv` 有终判） | 59 |
| T2 | 仅就地核对说明，注明已对照原页面图像，未逐格比对 | 0 |
| T3 | 改编补充（自述非源书表，尚未逐格核内部自洽） | 12 |
| T4 | 未核对页面图像 | 0 |

> 口径说明：T2 只说明该分片就地留下了「已对照原页面图像」的说明，
> 不表示表内每一格都被逐格比对过；T1 与 T1c 才是逐格结论。
> T1c 的表若在 `table_cells.tsv` 里判为 `逐格修正`，说明核对后已提出修正；
> 判决词表见 `sources/review_protocol.md` §3.3。

## 一、既有逐格读图核对（14 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:physis-chemis` | `ch01-a.tex:27` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 2 | `tab:ch01c-methods` | `ch01-c.tex:193` | — | 改编补充 | sources/table_pixel_verify.md |
| 3 | `tab:extinction-ch02` | `ch02-a.tex:305` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 4 | `tab:ch03-three` | `ch03-a.tex:38` | — | 改编补充 | sources/table_pixel_verify.md |
| 5 | `tab:crystal-systems` | `ch04-a.tex:70` | — | 改编补充 | sources/table_pixel_verify.md |
| 6 | `tab:ch04b-multiplicity` | `ch04-b.tex:178` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 7 | `tab:ch04c-profile` | `ch04-c.tex:511` | — | 原书自身问题 | sources/table_pixel_verify.md |
| 8 | `tab:zeolite-ring` | `ch06-c.tex:376` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 9 | `tab:pyridine` | `ch06-c.tex:633` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 10 | `tab:ch07b-probes` | `ch07-b.tex:67` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 11 | `tab:ch07b-py` | `ch07-b.tex:716` | — | 已核对并修正 | sources/table_pixel_verify.md |
| 12 | `tab:ch07c-formate` | `ch07-c.tex:682` | 505—507 | 已核对并修正 | sources/table_pixel_verify.md |
| 13 | `tab:ch10-reactor` | `ch10-c.tex:134` | — | 改编补充 | sources/table_pixel_verify.md |
| 14 | `tab:eis-d-elements` | `ch11-d.tex:229` | 860—861 | 已核对一致 | sources/table_pixel_verify.md |

## 二、2026-10-21 逐单元格核对（59 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:isotherm-read` | `ch01-a.tex:103` | up p.39-41（书内 20—22） | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 2 | `tab:pore-class` | `ch01-b.tex:441` | up p.63-79（书内 44—60） | 改编补充自洽 | sources/table_cells.md（16 格/0 不一致） |
| 3 | `tab:ch01c-strength` | `ch01-c.tex:961` | up p.97-99（书内 78—80） | 改编补充自洽 | sources/table_cells.md（20 格/0 不一致） |
| 4 | `tab:tem-parts` | `ch02-a.tex:125` | up p.108-112（书内 89—93） | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 5 | `tab:pattern-read` | `ch02-a.tex:361` | up p.114-120（书内 95—101） | 改编补充自洽 | sources/table_cells.md（18 格/0 不一致） |
| 6 | `tab:contrast` | `ch02-a.tex:404` | up p.120-125（书内 101—106） | 改编补充自洽 | sources/table_cells.md（24 格/0 不一致） |
| 7 | `tab:ch02b-eds-eels` | `ch02-b.tex:429` | up p.132-138、p.162-165（书内 113—119、143—146） | 改编补充自洽 | sources/table_cells.md（24 格/0 不一致） |
| 8 | `tab:ch02b-bimetal` | `ch02-b.tex:985` | up p.148-149（书内 129—130） | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 9 | `tab:ch02c-pt` | `ch02-c.tex:309` | up p.155-160（书内 155—160） | 逐格修正 | sources/table_cells.md（25 格/1 不一致） |
| 10 | `tab:ch02c-newold` | `ch02-c.tex:366` | up p.147-151（书内 147—151） | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 11 | `tab:ch02c-situ` | `ch02-c.tex:385` | up p.151-160（书内 151—160） | 改编补充自洽 | sources/table_cells.md（16 格/0 不一致） |
| 12 | `tab:ch02c-gaps` | `ch02-c.tex:466` | up p.160-162（书内 160—162） | 改编补充自洽 | sources/table_cells.md（25 格/0 不一致） |
| 13 | `tab:ch03b-conditions` | `ch03-b.tex:474` | 上册 p.209—210 / PDF p.228—229 | 改编补充自洽 | sources/table_cells.md（33 格/0 不一致） |
| 14 | `tab:recip-simple` | `ch04-a.tex:343` | 上册 p.238—239 / PDF p.257—258 | 改编补充自洽 | sources/table_cells.md（15 格/0 不一致） |
| 15 | `tab:xrd-limits` | `ch04-a.tex:676` | 上册 p.221—222 / PDF p.240—241 | 改编补充自洽 | sources/table_cells.md（14 格/0 不一致） |
| 16 | `tab:ch04b-Qtable` | `ch04-b.tex:43` | 上 p.244—245 / PDF p.263—264 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 17 | `tab:ch04b-extinction` | `ch04-b.tex:424` | 上 p.250—253 / PDF p.269—272 | 改编补充自洽 | sources/table_cells.md（16 格/0 不一致） |
| 18 | `tab:ch04b-quantmethods` | `ch04-b.tex:631` | 上 p.259—263 / PDF p.278—282 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 19 | `tab:ch04b-FOM` | `ch04-b.tex:896` | 上 p.268—269 / PDF p.287—288 | 改编补充自洽 | sources/table_cells.md（6 格/0 不一致） |
| 20 | `tab:ch04c-boundary` | `ch04-c.tex:364` | 上 p.270/274/277—278 / PDF p.289/293/296—297 | 改编补充自洽 | sources/table_cells.md（10 格/0 不一致） |
| 21 | `tab:ch04c-fitmethods` | `ch04-c.tex:567` | 上 p.283—284 / PDF p.302—303 | 改编补充自洽 | sources/table_cells.md（10 格/0 不一致） |
| 22 | `tab:ch04c-rfactor` | `ch04-c.tex:632` | 上 p.282/284 / PDF p.301/303 | 改编补充自洽 | sources/table_cells.md（8 格/0 不一致） |
| 23 | `tab:ch05-tpd` | `ch05-a.tex:135` | 上册 p.311—312 / PDF p.330—331 | 改编补充自洽 | sources/table_cells.md（15 格/0 不一致） |
| 24 | `tab:ch05-redhead` | `ch05-a.tex:807` | 上册 p.313—316 / PDF p.332—335 | 改编补充自洽 | sources/table_cells.md（15 格/0 不一致） |
| 25 | `tab:ch05b-tpr-shift` | `ch05-b.tex:421` | 上册 p.327—338 / PDF p.346—357 | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 26 | `tab:raman-ir` | `ch06-a.tex:94` | 上 p.355 / p.374 / PDF p.374 / p.393 | 改编补充自洽 | sources/table_cells.md（14 格/0 不一致） |
| 27 | `tab:fluor-suppress` | `ch06-a.tex:382` | 上 p.345 / p.351 / p.374 / PDF 364 / 370 / 393 | 改编补充自洽 | sources/table_cells.md（8 格/0 不一致） |
| 28 | `tab:raman-parts` | `ch06-a.tex:428` | 上 p.351 / p.352 / p.353 / p.354 / p.355 / PDF 370—374 | 逐格修正 | sources/table_cells.md（15 格/1 不一致） |
| 29 | `tab:insitu-window` | `ch06-b.tex:111` | 上 p.353 / p.388 / p.389 / PDF 372 / 407 / 408 | 逐格修正 | sources/table_cells.md（13 格/1 不一致） |
| 30 | `tab:raman-routes` | `ch06-b.tex:346` | 上 p.374 / p.377 / p.378 / p.383 / p.384 / PDF 393 / 396 / 397 / 402 / 403 | 改编补充自洽 | sources/table_cells.md（6 格/0 不一致） |
| 31 | `tab:mo-lines` | `ch06-b.tex:469` | up p.386—387 / PDF 405—406 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 32 | `tab:uv-apps` | `ch06-b.tex:668` | 上 p.384 / p.385 / p.386 / p.390 / p.392 / p.396 / PDF 403 / 404 / 405 / 409 / 411 / 415 | 改编补充自洽 | sources/table_cells.md（10 格/0 不一致） |
| 33 | `tab:raman-bands-c` | `ch06-c.tex:833` | 上 p.356 / p.359 / p.360 / p.363 / p.364 / p.365—372 / PDF 375 / 378 / 379 / 382 / 383 / 384—391 | 改编补充自洽 | sources/table_cells.md（84 格/0 不一致） |
| 34 | `tab:modes` | `ch07-a.tex:132` | 上 p.417 / p.419 / p.427 / p.428 / p.429—431 / p.432 / p.433 / p.434 / p.437—439 / p.440—441 / PDF 436—460 | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 35 | `tab:ch07c-probe` | `ch07-c.tex:235` | 上 p.494—497 / PDF 513—516 | 改编补充自洽 | sources/table_cells.md（10 格/0 不一致） |
| 36 | `tab:ch07c-criteria` | `ch07-c.tex:399` | 上 p.498—501 / PDF 517—520 | 改编补充自洽 | sources/table_cells.md（16 格/0 不一致） |
| 37 | `tab:narrow-map` | `ch08-a.tex:41` | down p.527-531（PDF 19-23） | 改编补充自洽 | sources/table_cells.md（13 格/0 不一致） |
| 38 | `tab:nuclei` | `ch08-a.tex:314` | down p.531-539（PDF 23-31） | 改编补充自洽 | sources/table_cells.md（13 格/0 不一致） |
| 39 | `tab:probes` | `ch08-b.tex:305` | down p.542-544（PDF 34-36） | 改编补充自洽 | sources/table_cells.md（37 格/0 不一致） |
| 40 | `tab:c13-assign` | `ch08-c.tex:199` | down p.555-556（PDF 47-48） | 改编补充自洽 | sources/table_cells.md（8 格/0 不一致） |
| 41 | `tab:nuclei-coke` | `ch08-c.tex:425` | down p.555-562（PDF 47-54） | 改编补充自洽 | sources/table_cells.md（25 格/0 不一致） |
| 42 | `tab:xpsparts` | `ch09-a.tex:389` | down p.586-605（PDF 77-96） | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 43 | `tab:satellite` | `ch09-b.tex:174` | down p.619—622 / PDF 110—113 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 44 | `tab:ups-xps` | `ch09-c.tex:62` | down p.662—670 / PDF 153—161 | 改编补充自洽 | sources/table_cells.md（24 格/0 不一致） |
| 45 | `tab:surface-compare` | `ch09-c.tex:197` | down p.662-693（PDF 153-184） | 改编补充自洽 | sources/table_cells.md（30 格/0 不一致） |
| 46 | `tab:ch09-bg` | `ch09-d.tex:149` | down p.633-634（PDF 124-125） | 改编补充自洽 | sources/table_cells.md（11 格/0 不一致） |
| 47 | `tab:ch09-so` | `ch09-d.tex:190` | down p.712（PDF 203） | 改编补充自洽 | sources/table_cells.md（44 格/0 不一致） |
| 48 | `tab:power-vs-hyp` | `ch10-a.tex:765` | 下 p.754—759 / PDF 243—248 | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 49 | `tab:ch10-modelfam` | `ch10-b.tex:73` | 下 p.753—759 / PDF 242—248 | 改编补充自洽 | sources/table_cells.md（20 格/0 不一致） |
| 50 | `tab:ch10-diffmech` | `ch10-b.tex:463` | 下 p.772—775 / PDF 261—264 | 改编补充自洽 | sources/table_cells.md（24 格/0 不一致） |
| 51 | `tab:ch10-criteria` | `ch10-b.tex:877` | 下 p.790—793 / PDF 279—282 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 52 | `tab:ch10-transient` | `ch10-c.tex:976` | 下 p.788—800 / PDF 277—289 | 改编补充自洽 | sources/table_cells.md（32 格/0 不一致） |
| 53 | `tab:methods` | `ch11-a.tex:945` | down p.819—832 / PDF 307—320 | 改编补充自洽 | sources/table_cells.md（12 格/0 不一致） |
| 54 | `tab:chrono-diagnostics` | `ch11-b.tex:199` | down p.833—839 / PDF 321—327 | 改编补充自洽 | sources/table_cells.md（32 格/0 不一致） |
| 55 | `tab:bulk-vs-kinetics` | `ch11-b.tex:498` | down p.839—852 / PDF 327—340 | 改编补充自洽 | sources/table_cells.md（21 格/0 不一致） |
| 56 | `tab:ch11c-insitu-methods` | `ch11-c.tex:179` | down p.866—879 / PDF 354—367 | 改编补充自洽 | sources/table_cells.md（20 格/0 不一致） |
| 57 | `tab:afm-modes` | `ch12-b.tex:223` | 下 p.914—916 / PDF 400—402 | 改编补充自洽 | sources/table_cells.md（36 格/0 不一致） |
| 58 | `tab:nano-three` | `ch12-c.tex:657` | 下 p.929—942 / PDF 415—428 | 改编补充自洽 | sources/table_cells.md（20 格/0 不一致） |
| 59 | `tab:nano-methods` | `ch12-c.tex:700` | 下 p.926—942 / PDF 412—428 | 改编补充自洽 | sources/table_cells.md（48 格/0 不一致） |

## 四、改编补充：自述非源书表且未逐格核（12 张）

| # | 表 | 位置 | 书内页 | 结论 | 证据 |
| --- | --- | --- | --- | --- | --- |
| 1 | `tab:selector` | `chapters/ch00-intro.tex:49` | — | 改编补充 | 题注/\src 自述非源书表 |
| 2 | `tab:evidence-level` | `chapters/ch13-synthesis.tex:49` | — | 改编补充 | 题注/\src 自述非源书表 |
| 3 | `tab:matrix` | `chapters/ch13-synthesis.tex:81` | — | 改编补充 | 题注/\src 自述非源书表 |
| 4 | `tab:ch01c-density` | `ch01-c.tex:774` | — | 改编补充 | 题注/\src 自述非源书表 |
| 5 | `tab:ring-index` | `ch02-a.tex:499` | — | 改编补充 | 题注/\src 自述非源书表 |
| 6 | `tab:ch02b-smsi` | `ch02-b.tex:1042` | — | 改编补充 | 题注/\src 自述非源书表 |
| 7 | `tab:ch03b-hyphenated` | `ch03-b.tex:82` | — | 改编补充 | 题注/\src 自述非源书表 |
| 8 | `tab:extinction-ch04` | `ch04-a.tex:590` | — | 改编补充 | 题注/\src 自述非源书表 |
| 9 | `tab:ch04c-scherrer` | `ch04-c.tex:166` | — | 改编补充 | 题注/\src 自述非源书表 |
| 10 | `tab:ch09-problems` | `ch09-d.tex:292` | 705—708 | 改编补充 | 题注/\src 自述非源书表 |
| 11 | `tab:ch10-window` | `ch10-b.tex:148` | — | 改编补充 | 题注/\src 自述非源书表 |
| 12 | `tab:ch10-resid-diag` | `ch10-b.tex:232` | — | 改编补充 | 题注/\src 自述非源书表 |

## 附：本台账不主张的东西

- 不主张 T4 的表「数据错误」——只主张**尚未读图**，对错未知。
- 不主张结构门禁（`tools/check_src.py`）或 OCR 文本层命中等于内容核对。
- 不主张 T3 的改编表内容正确：没有源表可逐格比对，只能核内部自洽（核过会升到 T1c）。
- 不主张 T1c 的 `逐格一致` 超出「与原书印刷内容一致」——不重做数据解释。

