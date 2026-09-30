# 证据说明

全部页面图像由本轮 Release `build/main.pdf` 渲染，PDF 页码采用 1-based。没有修改或重画教材图像。

- `eis-panel-a.png`：p.273 左图局部，约 300 dpi，确认虚线穿字。
- `p273.png`：图 11-5 全页，保留图注和周围空间。
- `p309.png` / `p310.png`：缩写表前两页，确认中文列过窄。
- `p122.png`：拉曼公式及其微分截面定义。
- `p71.png` / `p72.png`：DTG 峰高文字与相邻新图。
- `eis-production.json`：生产图形探针的完整实测输出，包含曲线边界和弧顶检查；PASS 不覆盖已确认的穿字漏检。
- `pdf-probe.json`：正常 PDF 的完整探针结果。

哈希和完整抽样页号见 [pdf-audit.json](../pdf-audit.json)。低阈值诊断及变异案例摘要见 [verification.json](../verification.json)，变异 PDF 不入库，可由复核脚本重新生成。
