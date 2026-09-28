# -*- coding: utf-8 -*-
r"""G-03: 把工具里写死的仓库根路径改成由 __file__ 推导。

问题（评审指出）：48 个 Python 工具把 ROOT 写死为原作者的工作区路径。
换目录克隆后运行，脚本会去检查**另一份**代码或空目录，输出却看起来正常——
这是典型的静默错误：结果不能证明当前提交合格。

做法：把
    ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
换成自包含的推导（不依赖该文件是否已 import os）：
    import os as _os
    ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
"""
import io, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = re.compile(r'^ROOT\s*=\s*r?["\']C:\\Users\\53150\\Documents\\deepseek-harness\\default-workspace["\']\s*$',
                 re.M)
NEW = ('import os as _os\n'
       'ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))')

changed = []
for p in sorted(glob.glob(os.path.join(HERE, "*.py"))):
    txt = io.open(p, encoding="utf-8").read()
    new, n = OLD.subn(NEW, txt)
    if n:
        io.open(p, "w", encoding="utf-8").write(new)
        changed.append(f"  {os.path.basename(p)}")

print(f"改了 {len(changed)} 个 Python 工具：")
print("\n".join(changed))

# 复核
left = []
for p in sorted(glob.glob(os.path.join(HERE, "*.py"))):
    if "deepseek-harness" in io.open(p, encoding="utf-8").read():
        left.append(os.path.basename(p))
print(f"\n仍含旧路径的文件：{left if left else '（无）'}")
