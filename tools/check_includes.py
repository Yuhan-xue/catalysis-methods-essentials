# -*- coding: utf-8 -*-
r"""检查装配器是否重复 \input / \IfFileExists 同一分片。

【为什么需要这个脚本】
2026-09-29 Lead 调 chapters/ch11.tex 的装配顺序时，插入 ch11-e 却忘了删模板原有的那一行，
导致 **ch11-e 被 \input 两次**（a→b→d→e→c→e），正文重复排了 2 页。

**当时六项门禁全部报 0，一个都没抓到**：
  errors / overfull / missing glyphs / undefined refs / dup labels —— 全 0
原因：ch11-e 内部**没有 \label**，所以「重复定义标签」不会触发；
其余五项本来就不检查「同一文件被引入几次」。

即：**重复 \input 对当时全部检查完全不可见**，只有人工比对 include 列表才能发现。
（发现方式：打印 ch11.tex 的 include 列表时肉眼看到 e 出现两次。）

本脚本把该检查自动化。建议由 tools/build.ps1 调用，作为第七项门禁。

用法：
    python tools/check_includes.py            # 正常检查，有问题 exit 1
    python tools/check_includes.py --quiet    # 只输出结论行
"""
import io
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scan():
    problems = []
    files = sorted(glob.glob(os.path.join(ROOT, "chapters", "*.tex")))
    main = os.path.join(ROOT, "main.tex")
    if os.path.exists(main):
        files.append(main)

    for f in files:
        try:
            s = io.open(f, encoding="utf-8").read()
        except Exception:
            continue
        rel = os.path.relpath(f, ROOT).replace("\\", "/")
        for pat, kind in ((r"\\input\{([^}]+)\}", "input"),
                          (r"\\IfFileExists\{([^}]+)\}", "IfFileExists")):
            found = re.findall(pat, s)
            for name in sorted(set(found)):
                n = found.count(name)
                if n > 1:
                    problems.append((rel, kind, name, n))
    return problems


def main():
    quiet = "--quiet" in sys.argv
    problems = scan()
    if problems:
        print("FAIL: 装配器重复引入分片")
        for rel, kind, name, n in problems:
            print(f"  {rel}  \\{kind}{{{name}}} 出现 {n} 次")
        print("  说明：重复 \\input 不会触发 errors/overfull/missing glyphs/"
              "undefined refs/dup labels 中的任何一项，必须在此拦截。")
        return 1
    if not quiet:
        print("include check: OK（无重复引入）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
