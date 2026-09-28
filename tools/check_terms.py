# -*- coding: utf-8 -*-
r"""Terminology consistency check for Stage 4 (企划 §7：术语统一).

15 slices were written independently by different authors. Each may legitimately
choose a different rendering of the same concept. This tool does NOT decide which
form is correct — it flags that MULTIPLE competing forms coexist in the book, which
is the actual defect. The Lead then picks one canonical form per group.

Matching is longest-form-first so that e.g. "比表面积" does not also count as "比表面".
"""
import re, glob, os, io, sys
from collections import defaultdict

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
# 控制台是 GBK：中文 print 出来会被就地转码成乱码，再用 Out-File 存成 UTF-8 就永久损坏。
# 因此本脚本自己写 UTF-8 报告文件，stdout 只输出 ASCII 统计。
OUT = os.path.join(ROOT, "tools", "term_audit.txt")
_rep = io.StringIO()


def say(s=""):
    _rep.write(s + "\n")

GROUPS = {
    "X 射线与 CJK 的间距":            ["X射线", "X 射线"],
    "比表面积":                        ["比表面积", "比表面"],
    "孔径分布 / 孔尺寸分布":           ["孔尺寸分布", "孔径分布"],
    "孔容 / 孔体积":                   ["孔体积", "孔容"],
    "TOF 中文名":                      ["转换频率", "转化频率", "转换数"],
    "活性位 / 活性中心":               ["活性中心", "活性位"],
    "载体 / 担体":                     ["担体", "载体"],
    "分散度 / 分散率":                 ["分散度", "分散率"],
    "吸附等温线 / 等温式":             ["吸附等温线", "吸附等温式"],
    "化学位移 / 化学移动":             ["化学位移", "化学移动"],
    "检出限 / 检测限":                 ["检出限", "检测限"],
    "标定 / 校准":                     ["标定", "校准"],
    "原位 / 现场":                     ["原位", "现场"],
    "透射电镜全称 / 简称":             ["透射电子显微镜", "透射电镜"],
    "扫描电镜全称 / 简称":             ["扫描电子显微镜", "扫描电镜"],
    "电子能量损失谱":                  ["电子能量损失谱", "电子能量损失能谱"],
    "反应速率 / 反应速度":             ["反应速率", "反应速度"],
    "转化率 / 转变率":                 ["转化率", "转变率"],
    "选择性 / 选择率":                 ["选择性", "选择率"],
    "空速 / 空间速度":                 ["空间速度", "空速"],
    "前驱体 / 前体":                   ["前驱体", "前体"],
    "结晶度 / 晶化度":                 ["结晶度", "晶化度"],
    "质量分数 / 重量分数":             ["质量分数", "重量分数"],
    "摩尔 / 克分子":                   ["摩尔", "克分子"],
    "程序升温脱附（TPD）":             ["程序升温脱附", "程序升温脱附法"],
    "漫反射 / 扩散反射":               ["漫反射", "扩散反射"],
    "信噪比 / 信噪":                   ["信噪比", "讯噪比"],
}

FILES = sorted(glob.glob(os.path.join(ROOT, "chapters", "**", "*.tex"), recursive=True))

# 只在正文里统计，排除来源标记与注释里的原书用词
# 注意：(?m) 全局标志必须放在整个正则最前面，不能拼接在中间（Python 3.11+ 会报错）。
STRIP = re.compile(r"\\src\{[^}]*\}|\\figsrc\{[^}]*\}|\\srcnote\{.*?\}", re.S)
COMMENT = re.compile(r"(?m)(?<!\\)%.*$")


def strip_noise(raw: str) -> str:
    return COMMENT.sub(" ", STRIP.sub(" ", raw))


def count_forms(text, forms):
    """Longest-form-first, non-overlapping count."""
    ordered = sorted(forms, key=len, reverse=True)
    hits = defaultdict(int)
    where = defaultdict(list)
    i = 0
    n = len(text)
    while i < n:
        for f in ordered:
            if text.startswith(f, i):
                hits[f] += 1
                line = text.count("\n", 0, i) + 1
                if len(where[f]) < 3:
                    where[f].append(line)
                i += len(f)
                break
        else:
            i += 1
    return hits, where


results = []
per_file = defaultdict(lambda: defaultdict(int))

for path in FILES:
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    raw = io.open(path, encoding="utf-8").read()
    text = strip_noise(raw)
    for group, forms in GROUPS.items():
        hits, where = count_forms(text, forms)
        used = {f: c for f, c in hits.items() if c}
        if len(used) > 1:
            results.append((group, rel, used, where))
            for f, c in used.items():
                per_file[rel][f] += c

say(f"files scanned: {len(FILES)}")
say(f"distinct groups with competing forms: {len(set(g for g, _, _, _ in results))}")
say(f"file-group pairs affected: {len(results)}")
say()

by_group = defaultdict(list)
for group, rel, used, where in results:
    by_group[group].append((rel, used, where))

for group in GROUPS:
    if group not in by_group:
        continue
    say(f"### {group}")
    total = defaultdict(int)
    for rel, used, where in by_group[group]:
        for f, c in used.items():
            total[f] += c
    say("   全书用量: " + "  |  ".join(f"{f}={c}" for f, c in
          sorted(total.items(), key=lambda x: -x[1])))
    for rel, used, where in by_group[group]:
        detail = "; ".join(f"{f}×{c} @L{','.join(map(str, where[f]))}" for f, c in used.items())
        say(f"   - {rel}: {detail}")
    say()

io.open(OUT, "w", encoding="utf-8").write(_rep.getvalue())
print(f"files={len(FILES)} competing_groups={len(set(g for g, _, _, _ in results))} pairs={len(results)} -> tools/term_audit.txt")
