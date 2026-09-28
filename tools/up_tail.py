# -*- coding: utf-8 -*-
import pymupdf
ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
P = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
d = pymupdf.open(P)
out = []
for p in [537, 538, 539, 540, 541, 542]:
    t = [x.strip() for x in d[p - 1].get_text("text").splitlines() if x.strip()]
    out.append(f"--- up pdf {p} (book {p-19}) : {len(t)} lines")
    out.append("    " + " / ".join(t[:4])[:160])
open(ROOT + r"\tools\out\up_tail.txt", "w", encoding="utf-8").write("\n".join(out))
print("ok")
