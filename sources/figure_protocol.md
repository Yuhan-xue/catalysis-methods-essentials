# 图与原书对照：作业规程

面向执行人（Lead 或协作代理）。目标只有一个：**把每一张插图逐张对着原书页面图像核一遍**，
核完的结论落到台账，使「图」这一项也具备与逐页/逐式/逐表相同的可复跑证据。

## 0. 先看清单

```bash
python tools/figure_worklist.py          # 重新生成 build/work_figures.tsv
```

`build/work_figures.tsv` 每行一张图，列：`fig_id  num  chapter  file  line  page  caption  src_hint  anchor`

- `page` 是成品 PDF 页码（`build/main.pdf`）；
- `anchor` 是题注自己声称的出处（取自题注里的 `\figsrc{...}`），**它可能是错的，正是要核的对象**；
- `src_hint` 是图前后正文里出现的「书内 p.N / PDF p.N」，只能当线索。

按章切好的小组清单在 `build/fig_groups/figs_chNN.tsv`。

## 1. 每张图的五步

1. **读题注**：`sed -n '<line-8>,<line+12>p' <file>`，看清这张图声称画什么、声称据哪张原图。
2. **渲成品页**：`python tools/vbook.py <page> build/_fig/<fig_id>_art.png --dpi 150`
3. **找原书图并渲源页**：
   - 上册（第 1—7 章）：`python tools/vpage.py up <pdf_page> build/_fig/<fig_id>_src.png --dpi 190 --top 0.1 --bottom 0.95`
   - 下册（第 8—12 章）：`python tools/vpage.py down <pdf_page> ...`
   - 书内页 → PDF 页：上册 `pdf = 书内 + 19`；下册用 `python -c "import sys;sys.path.insert(0,'tools');import pagemap_lib as p;print(p.dn_pdf(<书内页>))"`。
   - 不确定图在哪一页时，先出接触表定位：
     `python tools/vsheet.py up 36 47 build/_fig/sheet.png --cols 4 --dpi 78 --label`
4. **对着看**，逐项比：坐标轴与变量、曲线形状与趋势、标注文字与单位、图中数字、面板编号。
   必要时用 `--top/--bottom/--left/--right`（0..1）裁到图区，放大到能看清刻度。
5. **写一行台账**（见下）。

## 2. 判定口径（只有这四种算终判）

| 判定 | 含义 |
| --- | --- |
| `逐图一致` | 重画与原书图在轴/变量/趋势/标注/数字上一致；为排版做的等比例简化须写进 `checks` |
| `逐图修正` | 核出差异并已改（改 TikZ 或改题注锚点），`note` 写改了什么 |
| `逐图差异·原书自身` | 原书图自相矛盾或与正文冲突，成品照录并在图注/正文说明 |
| `改编补充自洽` | 原书没有对应图，是改编自绘；须自洽，且题注不得冒称原书图 |

非终判（会卡门）：`待核`。

## 3. 台账写法

文件：`sources/logs/figs_<章节>.tsv`（一章一个文件；已有就追加，只写表头一次）

列（制表符分隔，顺序固定）：

```
fig_id	num	art_page	src_anchor	checks	verdict	note
```

- `fig_id`：必须是 `build/work_figures.tsv` 里的 `fig_id`（如 `fig:iupac`）；
- `src_anchor`：**核实后**的源图锚点，如 `S1 图1-7 / 书内 p.20 / PDF 39`；
- `checks`：比了哪几项，一句话，分号隔开，别写「已核对」这种空话；
- `note`：判定的理由或改动；`逐图修正` 必写「改了什么」。

写完跑：

```bash
python tools/figure_ledger.py            # 合并成 sources/figure_review.md
python tools/figure_ledger.py --strict   # 还有待核就退 1
```

## 4. 发现缺陷怎么办

- **题注锚点错**（最常见：页码差 1、图号错、上下册写错）：直接改该章 tex 的 `\figsrc{...}`，
  并在台账 `note` 写「题注 p.X→p.Y」。
- **图中内容错**（轴名错、标注重叠、趋势画反、数字与原书不符）：能改就改 TikZ，改完在
  `sources/logs/fixes_fig.tsv` 追加一行（列：`page  file  line  old  new  reason`）。
- **原书自身矛盾**：不要改原书的说法，在题注或正文加一句说明，判定记 `逐图差异·原书自身`。

## 5. 纪律

- 只改自己负责的章的 tex；不跑 `latexmk`/`build.ps1`（Lead 统一重建）；不 `git add/commit/push`。
- 渲图一律放 `build/_fig/`，不要塞进仓库根目录；`build/` 不入库。
- 大图不要一次读多张；一张一张读，读完立刻写台账，避免上下文被图挤爆。
- 每张图的 `checks` 要写得让第二个人能照着复核（写页码、写数值、写你看到的轴名）。
