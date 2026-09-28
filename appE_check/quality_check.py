# Quality self-check for appD / appE / appF against the task brief's hard rules.
import re
import os

BASE = r"C:\Users\53150\Documents\mec\mechanics-textbook\src\appendices"
FILES = ["appD_misconceptions.tex", "appE_python.tex", "appF_reading.tex"]
ALLOWED = ({"ch:%d" % i for i in range(1, 13)}
           | {"app:%s" % c for c in "ABCDEF"}
           | {"sec:howtouse", "tab:notation"})

CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")


def strip_verbatim(text):
    return re.sub(r"\\begin\{Verbatim\}(?:\[[^\]]*\])?.*?\\end\{Verbatim\}", "", text, flags=re.S)


def strip_math(text):
    text = re.sub(r"\$[^$]*\$", "M", text)
    text = re.sub(r"\\\[.*?\\\]", " M ", text, flags=re.S)
    return text


problems = []
summary = {}

for name in FILES:
    path = os.path.join(BASE, name)
    raw = open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    summary[name] = {"lines": len(lines) - (1 if raw.endswith("\n") else 0)}

    body = strip_math(strip_verbatim(raw))
    # --- forbidden constructs ---
    for bad in (r"\usepackage", r"\newcommand", r"\newenvironment", r"\definecolor", r"\tikzset"):
        if bad in raw:
            problems.append("%s: contains %s" % (name, bad))
    # --- half-width double quotes outside verbatim ---
    hw = [i + 1 for i, ln in enumerate(strip_verbatim(raw).split("\n")) if '"' in ln]
    if hw:
        problems.append("%s: half-width double quote on lines %s" % (name, hw[:8]))
    # --- box keys ---
    keys = re.findall(r"\\begin\{(definition|theorem|corollary|lemma|example|insight|warning|history|"
                      r"review|tip|method|experiment|frontier)\}\{([^}]*)\}\{([^}]*)\}", body)
    for kind, title, key in keys:
        if not title.strip():
            problems.append("%s: empty title in %s" % (name, kind))
        if not key.strip():
            problems.append("%s: empty key in %s" % (name, kind))
        if ":" in key:
            problems.append("%s: colon in key %s" % (name, key))
    summary[name]["boxes"] = len(keys)
    summary[name]["keys"] = [k for _, _, k in keys]
    pk = re.findall(r"\\NewTColorBox|\\begin\{formulabox\}\{([^}]*)\}\{([^}]*)\}", body)
    # --- cref targets ---
    refs = set()
    for m in re.finditer(r"\\cref\{([^}]*)\}", body):
        for r in m.group(1).split(","):
            refs.add(r.strip())
    own_labels = set(re.findall(r"\\label\{([^}]*)\}", body))
    own_labels |= {"%s:%s" % (p, k) for p, k in
                   [("def", k) for k in summary[name]["keys"]]}  # placeholder, checked below
    bad_refs = sorted(r for r in refs if r not in ALLOWED and r not in own_labels)
    if bad_refs:
        problems.append("%s: refs not in allow-list: %s" % (name, bad_refs))
    summary[name]["refs"] = sorted(refs)
    # --- sentence length (CJK only) ---
    txt = body.replace("\\item", "\n\n")
    txt = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", "", txt)
    txt = txt.replace("{", "").replace("}", "")
    long_s = []
    for i, ln in enumerate(txt.split("\n")):
        if ln.strip().startswith("%"):
            continue
        for sent in re.split(r"[。！？；]", ln):
            n = len(CJK.findall(sent))
            if n > 60:
                long_s.append((i + 1, n, sent.strip()[:40]))
    if long_s:
        problems.append("%s: sentences > 60 CJK chars: %s" % (name, long_s[:6]))
    summary[name]["long_sentences"] = len(long_s)
    # --- paragraph length ---
    long_p = []
    txt_items = re.sub(r"\\item", "\n\n", txt)
    for para in re.split(r"\n\s*\n", txt_items):
        p = para.strip()
        if not p or len(CJK.findall(p)) == 0:
            continue
        if p.startswith("\\begin{longtable}") or "&" in p:
            continue
        n = len(CJK.findall(p))
        if n > 170:
            long_p.append((n, p[:40]))
    if long_p:
        problems.append("%s: paragraphs > 170 CJK chars: %s" % (name, long_p[:6]))
    summary[name]["long_paragraphs"] = len(long_p)

# --- appendix D entry count: rows inside longtable environments ---
d = open(os.path.join(BASE, FILES[0]), encoding="utf-8").read()
rows = 0
for tbl in re.findall(r"\\begin\{longtable\}.*?\\end\{longtable\}", d, flags=re.S):
    rows += len(re.findall(r"\\\\\s*$", tbl, flags=re.M))
    rows -= 2  # two header rows repeated via endfirsthead / endhead
summary["appD_entries"] = rows

# --- appendix E lab count ---
e = open(os.path.join(BASE, FILES[1]), encoding="utf-8").read()
summary["appE_lab_boxes"] = len(re.findall(r"\\begin\{lab\}", e))
summary["appE_verbatim_blocks"] = len(re.findall(r"\\begin\{Verbatim\}", e))
summary["appE_scripts"] = len(re.findall(r"\\begin\{Verbatim\}(?:\[[^\]]*\])?\n# lab", e))

print("=== summary ===")
for k, v in summary.items():
    if isinstance(v, dict):
        print("%s: lines=%d boxes=%d long_sent=%d long_para=%d" %
              (k, v["lines"], v["boxes"], v["long_sentences"], v["long_paragraphs"]))
        print("   keys: %s" % ", ".join(v["keys"]))
        print("   refs: %s" % ", ".join(v["refs"]))
    else:
        print("%s: %s" % (k, v))
print("")
print("=== problems ===")
print("\n".join(problems) if problems else "none")
