# -*- coding: utf-8 -*-
r"""Refresh the status column of sources/assignments.md from what is actually on disk.

A ledger that is maintained by hand drifts. This derives `done` from the existence
of chapters/parts/<slice>.tex (and, for the Lead-written units, from chapters/*.tex),
so "done" always means "a file exists", never "someone said so".
"""
import os, re

import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "sources", "assignments.md")
PARTS = os.path.join(ROOT, "chapters", "parts")

ROW = re.compile(r"^\|\s*(ch\d{2}-[a-e])\s*\|(.*?)\|\s*\*{0,2}(todo|done|running)\*{0,2}\s*\|(.*?)\|$")


def slice_exists(name):
    # ch01-a -> chapters/parts/ch01-a.tex
    return os.path.exists(os.path.join(PARTS, name + ".tex"))


lines = open(LEDGER, encoding="utf-8").read().splitlines()
done = todo = 0
out = []
for ln in lines:
    m = ROW.match(ln)
    if not m:
        out.append(ln)
        continue
    name, mid, _status, tail = m.groups()
    exists = slice_exists(name)
    status = "**done**" if exists else "todo"
    if exists:
        done += 1
        kb = os.path.getsize(os.path.join(PARTS, name + ".tex")) / 1024.0
        tail = re.sub(r"（.*?）", "", tail).strip() or "—"
        tail = f"{tail}  [{kb:.1f} KB on disk]"
    else:
        todo += 1
    out.append(f"| {name} |{mid}| {status} | {tail} |")

txt = "\n".join(out)
txt = re.sub(r"进度：\*\*\d+ / 34 个正文分片\*\*.*",
             f"进度：**{done} / 34 个正文分片**（状态由 tools/update_ledger.py 从磁盘刷新；"
             f"done = 文件存在），另有 3 个 Lead 亲写单元（导读、综合应用、后置）。",
             txt)
open(LEDGER, "w", encoding="utf-8").write(txt + "\n")
print(f"ledger refreshed: done={done}  todo={todo}")
