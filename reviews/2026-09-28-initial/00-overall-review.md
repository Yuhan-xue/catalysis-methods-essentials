# 总体审阅

## G-01 · P1 · 重复标签已经造成跨章误引用，综合应用索引仍为 ??

位置：[chapters/ch90-backmatter.tex:249](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/chapters/ch90-backmatter.tex#L249)（固定审阅提交）。

**证据与复现：** 源码存在 4 个重复标签名：eq:langmuir（ch01-a、ch10-a）、eq:bragg（ch02-a、ch04-a、ch09-a）、tab:extinction（ch02-a、ch04-a）、eq:iss（ch09-c、ch11-a）。本次 main.aux 中最终值分别落到 10-16、9-5、4-3、11-27；因此第 1 章的 Langmuir 引用会跳到第 10 章，ISS 引用会跳到电化学公式。后置索引两次引用不存在的 ch:13-synthesis，发布 PDF 第 168 页可见“第 ?? 章”。

**影响：** 读者按编号回查时会得到不同的公式，已经超出一般排版警告。

**建议修改：** 给全部标签加章/单元命名空间，逐个同步 ref/eqref/语义宏。为不编号的综合应用单元建立真实锚点，使用节名或页码引用，不能仅为消除警告而伪造“第 13 章”。

**验收条件：** 全量构建后重复标签和未定义引用均为 0；人工点击上述 4 组引用与综合应用索引，核对目标内容。

## G-02 · P1 · 构建退出码没有执行 README 声明的版面门禁

位置：[tools/build.ps1:57](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/tools/build.ps1#L57)（固定审阅提交）。

**证据与复现：** README 第 79—84 行声称 overfull >5 pt 会 exit 1；脚本虽统计 $ovf 和 $undef，最终失败条件只检查 latexmk、错误和缺字。本次 pwsh 运行退出 0，但统计到 3 处 >5 pt overfull（29.81882、35.96219、9.0538 pt）及 2 次未定义引用；重复标签也没有失败门禁。

**影响：** 自动化流程会把有断链和超宽的 PDF 标为成功，后续“通过验收”缺少可信基础。

**建议修改：** 区分草稿构建和发布验收；发布模式对 overfull 超阈值、未定义引用、重复标签和缺字统一失败，文档与实现保持一致。

**验收条件：** 构造各一种警告的最小样例，发布检查均非零退出；无警告样例退出 0，并保留日志。

## G-03 · P2 · 两个检查脚本仍读取旧工作区，工具链路径不具可迁移性

位置：[tools/check_chapters.py:15](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/tools/check_chapters.py#L15)（固定审阅提交）。

**证据与复现：** check_chapters.py 第 15 行、check_sources.py 第 12 行把 ROOT 写死为原作者 deepseek-harness/default-workspace；后者第 68 行还向旧工作区写 source_audit.txt。build.ps1 第 25 行写死 C:/texlive/2026，而 README 支持 TeX Live 2025+。此次为避免写入旧项目，没有执行这两个 Python 检查器。

**影响：** 换目录克隆后可能检查另一份文本或空目录，结果不能证明当前提交合格。

**建议修改：** 由 __file__ / PSScriptRoot 定位仓库；优先解析 PATH 或显式工具链参数；找不到输入时立即失败。

**验收条件：** 从含空格的全新克隆目录运行；输出写明当前 root 与 commit，所有被检查路径均在该克隆内。

## G-04 · P2 · 文件存在状态不能替代原书覆盖率，图表台账已落后

位置：[sources/assignments.md:60](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/sources/assignments.md#L60)（固定审阅提交）。

**证据与复现：** 当前计划是 34 个正文分片、已有 23 个、缺 11 个；README 仍写“约 37”。coverage.csv 只有原书目录/OCR 字段，没有目标分片、处理方式与审阅状态。figure_table_list.csv 仅 39 条记录（15 图、24 表，涉及 11 个分片），不足以登记现有 23 个分片。ch08-c 标 done 但未承担原位 NMR 专节的完整说明；ch09-d 的内容范围也与台账不同，见 C09-01。

**影响：** 12 个章标题和 169 页无法说明已经覆盖两本书的关键方法；“done”被误读时会掩盖漏项。

**建议修改：** 将存在、已写、来源核对、科学审阅、版面验收拆成状态；给每个原书二级节记录目标位置与保留/合并/删节理由；自动刷新图表清单，再人工审图。

**验收条件：** 原书二级节全部有映射或删节理由，34 片统计一致，当前图表标签与清单一一匹配；第 8、9 章的范围缺口有明确处理记录。

## G-05 · P2 · 部分浮动体页和后置标题页浪费版面

位置：[chapters/ch90-backmatter.tex:1](http://zsyq.hxlab.tech:3000/yuhanxue/catalysis-methods-essentials/src/commit/8c34d6902555a555159eeec38b510af42976e747/chapters/ch90-backmatter.tex#L1)（固定审阅提交）。

**证据与复现：** 发布 PDF 抽查发现：第 85 页仅一张表居于页中、上下大片留白；第 165 页集中出现后置材料标题，实质表格从第 166 页开始。第 68、90 页图形小而注释拥挤。第 6 页方法矩阵本次目视未见 README 所称的旧重叠，不把旧记录直接算作现存缺陷。

**影响：** 与“页面信息尽可能多”的目标不一致；但不能通过统一缩小字号来解决图内标注拥挤。

**建议修改：** 先修图的几何关系和字号，再调整浮动体尺寸、放置策略及标题与首表的分页。保留必要章间区隔，不追求无差别填满。

**验收条件：** 重渲染上述页面及前后页，无孤立标题、无碰撞/裁切；第 85、165 页的留白得到消除或写明保留理由。

[返回总览](README.md) · [执行 TODO](TODO.md)
