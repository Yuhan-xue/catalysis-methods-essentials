# 分片派单台账（assignments）

**为什么需要这张表**：本项目实际发生过**重复派单**——同一分片 `ch02-a` 被派给两个作者，
两人并发写同一文件。后到者（95a27314）做对了：它检测到并发写入、**拒绝覆盖**，
改为做独立技术审查，结果抓出 4 个实质错误（密排六方消光规则写反、Ewald 球球心错误、
χ 符号约定与 Scherzer 欠焦不自洽、100 kV 波长数值与所给非相对论公式不自洽）。
但这是运气好，不是流程好。**派单前先查这张表。**

## 并发写入纪律（三条，都踩过）

1. **一个分片同一时刻只能有一个作者。** 派单前查本表。
2. **Lead 不要改正在被写的分片。** 我曾改 `ch02-a.tex` 而作者仍在写，
   改动被覆盖。要改先确认 mtime 已静止。
3. **编译期间不要改 `style/`。** 我在 12:02:27 写 `preamble.tex`，
   与某作者的编译（12:02:26 读取）相撞，导致对方报 `! Missing \endcsname inserted`
   且无 PDF。那是我的责任，不是章的问题。

## 台账（状态：todo / running / done）

| 分片 | 内容 | 状态 | 作者/备注 |
|---|---|---|---|
| ch01-a | 物理吸附、BET、比表面积 | **done** | Lead 亲写；BET 三式已用页面图像核对  [14.2 KB on disk]  [14.2 KB on disk]  [14.2 KB on disk]  [14.2 KB on disk]  [14.2 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.6 KB on disk]  [14.4 KB on disk] |
| ch01-b | 孔容与孔尺寸分布 | **done** | —  [38.6 KB on disk]  [38.8 KB on disk]  [38.8 KB on disk]  [38.8 KB on disk]  [38.8 KB on disk]  [38.8 KB on disk]  [40.6 KB on disk]  [40.6 KB on disk]  [40.6 KB on disk]  [40.6 KB on disk]  [41.6 KB on disk]  [41.6 KB on disk]  [41.6 KB on disk] |
| ch01-c | 颗粒度、密度、机械强度 | **done** | —  [79.3 KB on disk]  [79.3 KB on disk]  [79.3 KB on disk] |
| ch02-a | TEM 原理、衍射与成像 | **done** | 6 页；经 Lead 修正 4 处  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [45.1 KB on disk]  [45.6 KB on disk]  [45.6 KB on disk]  [47.4 KB on disk]  [47.4 KB on disk]  [47.4 KB on disk]  [47.4 KB on disk]  [49.7 KB on disk]  [49.7 KB on disk]  [49.7 KB on disk] |
| ch02-b | STEM、分析电镜、辐射损伤、催化应用 | **done** | —  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk]  [90.8 KB on disk] |
| ch02-c | 新型电镜（球差/三维/全息/环境 TEM）、局限 | **done** | —  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk]  [70.5 KB on disk] |
| ch03-a | 热分析分类、TG/DTA/DSC、动力学简介 | **done** | 曾因 groupplot declare function 作用域报错，已修  [34.1 KB on disk]  [34.1 KB on disk]  [34.1 KB on disk]  [34.1 KB on disk]  [34.1 KB on disk]  [34.5 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk]  [34.8 KB on disk] |
| ch03-b | 热分析应用、联用技术、实验技巧 | **done** | —  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk]  [38.7 KB on disk] |
| ch04-a | 晶体学基础、X 射线性质、衍射几何 | **done** | 5 页 / 11762 字 / 3 图 5 表  [43.8 KB on disk]  [43.8 KB on disk]  [43.8 KB on disk]  [43.8 KB on disk]  [44.5 KB on disk]  [44.5 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [44.7 KB on disk]  [45.4 KB on disk]  [45.4 KB on disk]  [45.4 KB on disk] |
| ch04-b | 衍射、物相鉴定与定量、指标化 | **done** | —  [64.7 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk]  [66.8 KB on disk] |
| ch04-c | Scherrer、Rietveld、实例、Debye | **done** | —  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk]  [77.5 KB on disk] |
| ch05-a | 化学吸附原理、三种等温式、TPD 理论 | **done** | —  [22.6 KB on disk]  [22.6 KB on disk]  [22.6 KB on disk]  [22.6 KB on disk]  [23.0 KB on disk]  [23.0 KB on disk]  [23.7 KB on disk]  [23.7 KB on disk]  [35.5 KB on disk]  [35.5 KB on disk]  [36.3 KB on disk]  [36.3 KB on disk]  [36.3 KB on disk]  [36.3 KB on disk]  [36.3 KB on disk] |
| ch05-b | TPD/TPR/TPO/TPSR 应用实例 | **done** | —  [50.3 KB on disk]  [50.3 KB on disk]  [50.3 KB on disk]  [50.3 KB on disk]  [50.3 KB on disk]  [50.9 KB on disk]  [50.9 KB on disk]  [50.9 KB on disk]  [50.9 KB on disk]  [50.9 KB on disk] |
| ch06-a | 拉曼原理、实验技术、荧光 | **done** | 图注 node 未设 text width 曾致超版心 66 pt，已修  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [29.2 KB on disk]  [28.8 KB on disk] |
| ch06-b | 拉曼催化应用、紫外拉曼、SERS、共焦 | **done** | —  [80.0 KB on disk]  [80.0 KB on disk]  [80.0 KB on disk]  [80.0 KB on disk]  [80.0 KB on disk]  [80.0 KB on disk] |
| ch07-a | 原位红外原理与七种测量模式 | **done** | 5 页  [36.6 KB on disk]  [36.6 KB on disk]  [36.6 KB on disk]  [36.6 KB on disk]  [36.6 KB on disk]  [37.1 KB on disk]  [38.2 KB on disk]  [38.2 KB on disk]  [38.2 KB on disk]  [38.2 KB on disk]  [38.2 KB on disk]  [38.2 KB on disk]  [38.6 KB on disk]  [38.6 KB on disk]  [38.6 KB on disk] |
| ch07-b | 探针分子、金属与氧化物催化剂表征 | **done** | —  [62.7 KB on disk]  [62.7 KB on disk]  [62.7 KB on disk]  [62.7 KB on disk]  [63.7 KB on disk]  [63.7 KB on disk]  [63.7 KB on disk] |
| ch07-c | 硫化物催化剂、反应机理 | **done** | —  [57.1 KB on disk]  [58.8 KB on disk]  [58.8 KB on disk] |
| ch08-a | MAS/CP-MAS、分子筛结构 | **done** | 曾派两次失败，未产出  [33.7 KB on disk]  [33.7 KB on disk]  [34.2 KB on disk]  [34.2 KB on disk]  [34.2 KB on disk]  [34.2 KB on disk]  [34.2 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk]  [35.6 KB on disk] |
| ch08-b | 酸性研究、吸附分子 | **done** | —  [47.9 KB on disk]  [48.1 KB on disk]  [48.1 KB on disk]  [48.1 KB on disk]  [48.1 KB on disk]  [48.1 KB on disk]  [48.1 KB on disk]  [48.6 KB on disk]  [48.6 KB on disk]  [48.6 KB on disk] |
| ch08-c | 原位 MAS NMR、积炭 | **done** | —  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk]  [42.7 KB on disk] |
| ch09-a | 表面、XPS 原理与仪器、实验方式 | **done** | 57.8 KB  [41.8 KB on disk]  [41.8 KB on disk]  [41.8 KB on disk]  [41.8 KB on disk]  [41.8 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk]  [42.3 KB on disk] |
| ch09-b | XPS 化学位移、伴峰、定量、后处理、常见问题 | **done** | —  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk]  [12.8 KB on disk] |
| ch09-c | UPS、AES、ISS | **done** | Lead 亲写；ISS 式已用 θ=90° 极限自检  [13.4 KB on disk]  [13.4 KB on disk]  [13.4 KB on disk]  [13.4 KB on disk]  [13.4 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk]  [13.7 KB on disk] |
| ch09-d | 表面分析应用、表面分析与催化、XPS 技术进展 | **done** | —  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk]  [37.9 KB on disk] |
| ch10-a | 动力学概念、速率方程 | **done** | —  [54.0 KB on disk]  [54.1 KB on disk]  [54.1 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk]  [54.9 KB on disk] |
| ch10-b | 模型建立与检验、传递过程 | **done** | —  [60.4 KB on disk]  [60.4 KB on disk] |
| ch10-c | 测定方法与实验装置、非稳态动力学 | **done** | —  [70.0 KB on disk]  [70.0 KB on disk]  [70.0 KB on disk]  [76.6 KB on disk]  [76.6 KB on disk]  [76.6 KB on disk]  [76.6 KB on disk]  [76.6 KB on disk]  [77.7 KB on disk]  [77.7 KB on disk] |
| ch11-a | 电化学原理、控制电势方法 | **done** | —  [54.2 KB on disk]  [58.5 KB on disk]  [58.5 KB on disk]  [58.5 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.3 KB on disk]  [62.4 KB on disk] |
| ch11-b | 控制电流、整体电解、流体动力学 | **done** | —  [0.1 KB on disk]  [70.1 KB on disk]  [70.1 KB on disk]  [70.1 KB on disk]  [70.4 KB on disk] |
| ch11-c | 阻抗、现场谱学 | **done** | —  [48.2 KB on disk]  [48.2 KB on disk]  [48.2 KB on disk]  [48.2 KB on disk]  [36.6 KB on disk] |
| ch12-a | STM 原理与应用 | **done** | —  [49.2 KB on disk]  [40.8 KB on disk]  [39.5 KB on disk]  [39.5 KB on disk]  [39.8 KB on disk]  [40.0 KB on disk]  [40.0 KB on disk]  [40.0 KB on disk]  [40.0 KB on disk]  [40.0 KB on disk]  [40.0 KB on disk]  [40.7 KB on disk]  [40.7 KB on disk]  [40.7 KB on disk] |
| ch12-b | AFM 原理、模型、应用 | **done** | —  [48.3 KB on disk]  [48.3 KB on disk]  [48.3 KB on disk]  [48.3 KB on disk]  [48.3 KB on disk]  [48.3 KB on disk]  [48.3 KB on disk] |
| ch12-c | 近场光学、TERS、Nano-FTIR | **done** | —  [66.2 KB on disk]  [66.2 KB on disk]  [66.2 KB on disk]  [66.2 KB on disk]  [66.2 KB on disk] |
| — | ch00-intro 导读与方法选择矩阵 | **done** | Lead 亲写 |
| — | ch13-synthesis 跨方法综合应用 | **done** | Lead 亲写 |
| — | ch90-backmatter 缩写/符号/索引 | **done** | Lead 亲写；长表置于单栏整页 |

进度：**34 / 34 个正文分片**（状态由 tools/update_ledger.py 从磁盘刷新；done = 文件存在），另有 3 个 Lead 亲写单元（导读、综合应用、后置）。\n\n## 科学核验状态（与「文件存在」分开）\n\n上表的 done 只表示**分片文件存在、能通过编译与结构门禁**，不等于该片内容已按原书逐页核对。R3/R4 之后的内容核验状态：\n\n- **ch05-a（TPD 图源）**：生成器逐点复验通过（`python tools/gen_tpd_table.py --check`，5×83 点）。\n- **ch08-c（§8.5 原位 MAS NMR）**：已按原书 §8.5 补写；映射与边界见 `sources/ch08_coverage_note.md`；来源为 OCR 文字层，未逐字核对页面图像。\n- **ch09-a/b/c/d（第 9 章）**：覆盖矩阵见 `sources/ch09_coverage_matrix.md`；§9.6—§9.8 记为删节（未系统展开）。\n- **全书 85 张表**：结构/页码门禁通过；已加 OCR 文本层交叉核对（`python tools/check_table_content.py`：13 FOUND / 1 INDEX_OK / 54 无原书表号 / 17 非源书 / 0 MISS），**像素级逐表核图进行中**：14 张已逐格对照原书原页面图像、42 张已就地留有「已对照原页面图像」核对说明、12 张为改编补充、17 张尚未核对页面图像（逐表状态见 `sources/table_status.md`）；OCR 交叉核对详见 `sources/table_content_check.md`。
- **原书节覆盖**：机器初筛见 `sources/coverage_map.md`（二级节 79/81 有落点，未映射的 2 个均为「结束语」，已记不展开）；说明见 `sources/coverage_map_notes.md`。\n- **其余分片**：只做过编译与结构门禁、局部公式复算；**未做逐页核图**。\n
