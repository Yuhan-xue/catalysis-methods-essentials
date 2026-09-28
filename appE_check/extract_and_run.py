# Extract every Verbatim block from appE_python.tex and re-run the Python ones.
import os
import re
import subprocess
import sys

TEX = r"C:\Users\53150\Documents\mec\mechanics-textbook\src\appendices\appE_python.tex"
OUT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace\appE_check\extracted"
os.makedirs(OUT, exist_ok=True)

with open(TEX, encoding="utf-8") as fh:
    src = fh.read()

blocks = re.findall(r"\\begin\{Verbatim\}(?:\[[^\]]*\])?\r?\n(.*?)\\end\{Verbatim\}",
                    src, re.S)
print("found %d Verbatim blocks" % len(blocks))

env = dict(os.environ)
env["MPLBACKEND"] = "Agg"
ok = True
for i, block in enumerate(blocks):
    text = block.replace("\r\n", "\n")
    first = text.split("\n")[0].strip()
    if not first.startswith("# lab"):
        print("block %d skipped (not a lab script): %r" % (i + 1, first[:40]))
        continue
    name = first.split()[1].replace(".py", "")
    path = os.path.join(OUT, name + ".py")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text if text.endswith("\n") else text + "\n")
    proc = subprocess.run([sys.executable, path], cwd=OUT, env=env,
                          capture_output=True, text=True)
    status = "OK " if proc.returncode == 0 else "FAIL"
    if proc.returncode != 0:
        ok = False
    print("%s %-22s exit=%d  stdout_lines=%d" %
          (status, name, proc.returncode, len(proc.stdout.splitlines())))
    if proc.returncode != 0:
        print(proc.stderr[-2000:])
    else:
        for line in proc.stdout.splitlines()[:3]:
            print("      | " + line)
print("ALL PASS" if ok else "SOME FAILED")
