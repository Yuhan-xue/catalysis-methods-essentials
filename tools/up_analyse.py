# -*- coding: utf-8 -*-
"""UP volume: parse printed TOC, detect body section anchors, derive page map."""
import os, re, csv, json, collections
import pymupdf

ROOT = r"C:\Users\53150\Documents\deepseek-harness\default-workspace"
OUT = os.path.join(ROOT, "tools", "out")
os.makedirs(OUT, exist_ok=True)
PDF_UP = r"C:\Users\53150\.dsh\attachments\v1\files\9f\9f97a9804d81e20c13ef2a42d2ed7e9964fe1bca5f3c3dba338d1b6d6f8159f7\现代催化研究方法新编 上 (辛勤，罗孟飞，徐杰 主编) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
TOC_RAW = os.path.join(ROOT, "sources", "toc", "up_toc_raw.txt")

FW = str.maketrans("０１２３４５６７８９．", "0123456789.")


def norm(s):
    return s.translate(FW).replace(" ", "").replace("\u3000", "")


# ---------- 1. parse printed TOC ----------
raw = open(TOC_RAW, encoding="utf-8").read()
toc = []          # dicts: sec,title,page,raw,src_pdf
for blk in raw.split("<<<<<")[1:]:
    hdr, _, body = blk.partition(">>>>>")
    m = re.search(r"p\.(\d+)", hdr)
    src = int(m.group(1)) if m else None
    for line in body.splitlines():
        nl = norm(line)
        if not nl or nl.startswith("目录") or nl.startswith("现代催化"):
            continue
        m2 = re.match(r"^(\d{1,2}(?:\.\d{1,2}){1,2})[\.\s、]*(.*?)[.·]{2,}\s*(.+)$", nl)
        if m2:
            toc.append({"sec": m2.group(1), "title": m2.group(2)[:60],
                        "page_raw": m2.group(3), "src_pdf": src})
        else:
            # chapter lines: 第N章 title .... page
            m3 = re.match(r"^第(\d+|[S])章(.*?)[.·]{2,}\s*(.+)$", nl)
            if m3:
                toc.append({"sec": "ch" + m3.group(1), "title": m3.group(2)[:60],
                            "page_raw": m3.group(3), "src_pdf": src})


def clean_page(p):
    """Strip OCR artifacts (leading 一/hyphen/dots) and return int or None."""
    q = p.strip()
    q = re.sub(r"^[一\-—–.·、\s]+", "", q)
    q = re.sub(r"[^0-9].*$", "", q) if re.match(r"^\d", q) else ""
    if q == "":
        return None
    v = int(q)
    return v if 0 < v < 1000 else None


for t in toc:
    t["page"] = clean_page(t["page_raw"])

with open(os.path.join(OUT, "up_toc_parsed.txt"), "w", encoding="utf-8") as f:
    for t in toc:
        f.write(f"{t['sec']:<8} page={str(t['page']):>5} raw={t['page_raw']:<10} src=toc_pdf{t['src_pdf']}  {t['title']}\n")

tocpage = {}
for t in toc:
    if t["page"] is not None and t["sec"] not in tocpage:
        tocpage[t["sec"]] = t["page"]

print("toc entries:", len(toc), "with page:", len(tocpage))
print("chapter lines:", {k: v for k, v in tocpage.items() if k.startswith("ch")})
print("toc entries missing a page number:", [t["sec"] for t in toc if t["page"] is None])

# ---------- 2. body anchors (first occurrence per sec, pdf_page >= 20) ----------
doc = pymupdf.open(PDF_UP)
pat_head = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){1,2})[　 \u3000]*([^\s\d].{0,50})$")
body = {}
for p in range(20, doc.page_count + 1):
    for line in doc[p - 1].get_text("text").splitlines():
        nl = norm(line)
        m = pat_head.match(nl)
        if m and m.group(1) in tocpage and m.group(1) not in body:
            body[m.group(1)] = (p, m.group(2)[:50])

rows = []
for sec, (p, title) in sorted(body.items(), key=lambda kv: kv[1][0]):
    tp = tocpage.get(sec)
    rows.append({"pdf_page": p, "sec": sec, "toc_page": tp if tp is not None else "",
                 "off": (p - tp) if tp is not None else "", "title": title})

with open(os.path.join(OUT, "up_anchor_off.txt"), "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"pdf={r['pdf_page']:>4} sec={r['sec']:<7} toc={str(r['toc_page']):>4} off={str(r['off']):>4}  {r['title']}\n")

hist = collections.Counter(r["off"] for r in rows if r["off"] != "")
print("offset histogram (pdf - toc_page):", dict(sorted(hist.items(), key=lambda kv: -kv[1])))
mode = hist.most_common(1)[0][0]
print("modal offset:", mode)
offrows = [r for r in rows if r["off"] != ""]
print("anchors with toc page:", len(offrows), " agreeing with mode:", sum(1 for r in offrows if r["off"] == mode))
print("disagreeing anchors:")
for r in offrows:
    if r["off"] != mode:
        print(f"   pdf={r['pdf_page']} sec={r['sec']} toc={r['toc_page']} off={r['off']} (delta {r['off']-mode:+d})  {r['title']}")

# anchors without a toc page (still placed by offset)
print("anchors without toc page (placed by modal offset):")
for r in rows:
    if r["off"] == "":
        print(f"   pdf={r['pdf_page']} sec={r['sec']}  {r['title']}")

# ---------- 3. UP running heads for chapters ----------
print("\nUP chapter-opener candidates:")
pat_ch = re.compile(r"第\s*(\d+)\s*章")
for p in range(1, 40):
    pg = doc[p - 1]
    t = " | ".join(x.strip() for x in pg.get_text("text").splitlines()[:4] if x.strip())
    print(f"  head p{p}: {t[:100]}")
for target_pdf in [p for p in range(20, doc.page_count + 1)]:
    pg = doc[target_pdf - 1]
    blocks = [b for b in pg.get_text("blocks") if b[6] == 0 and b[4].strip()]
    blocks.sort(key=lambda b: b[1])
    if not blocks:
        continue
    t0 = blocks[0][4].strip().replace("\n", " ")
    m = pat_ch.match(t0)
    if m and len(t0) < 40:
        print(f"  CH-HEAD pdf={target_pdf} -> {t0[:60]!r}")
