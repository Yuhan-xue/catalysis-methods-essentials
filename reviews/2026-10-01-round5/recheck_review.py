"""R5 independent evidence; no production edits. Exit 0 means collection completed.
Run from repo: python reviews/2026-10-01-round5/recheck_review.py --out build/review-round5
Requires numpy/scipy/PyMuPDF. Fixed model constants intentionally independent of generator.
"""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess, sys
import numpy as np
import pymupdf
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
ROOT=Path(__file__).resolve().parents[2]
BASE='69c3d182618083bb47dd7230a62fe0e5c10076a3'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/review-round5');a=ap.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    A,E,R=4.39753e10,120000.,8.314462618
    def rate(T,b,n):
        h=quad(lambda t:A/b*math.exp(-E/(R*t)),300.,T,epsabs=1e-11)[0]
        theta=math.exp(-h) if n==1 else 1/(1+h)
        return A/b*math.exp(-E/(R*T))*theta**n
    rows=[]
    for b in [5.,10.,20.]:
        legacy=brentq(lambda t:A/b*math.exp(-E/(R*t))-E/(R*t*t),400,700)
        si=brentq(lambda t:A/(b/60)*math.exp(-E/(R*t))-E/(R*t*t),400,700)
        rows.append(dict(beta_K_min=b,legacy_Tp_K=legacy,SI_Tp_K=si,shift_K=legacy-si))
    shape=[]
    for n in [1,2]:
        tp=minimize_scalar(lambda t:-rate(t,10.,n),bounds=(450,650),method='bounded').x
        pk=rate(tp,10.,n)
        left=brentq(lambda t:rate(t,10.,n)-pk/2,400,tp)
        right=brentq(lambda t:rate(t,10.,n)-pk/2,tp,800)
        shape.append(dict(order=n,Tp_K=tp,FWHM_K=right-left))
    commands=[['tools/gen_tpd_table.py','--check'],['tools/recompute_ch03b_dtg.py'],
              ['tools/pdf_probe.py','--pdf','build/main.pdf','--out',str(out/'pdf-probe.txt')],
              ['tools/fig_probe_eis.py','--pdf','build/main.pdf'],['tools/fig_probe_eis.py','--selftest'],
              ['tools/check_src.py'],['tools/check_table_content.py','--csv',str(out/'table-content.csv')]]
    cmdrows=[]
    for args in commands:
        r=subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        cmdrows.append(dict(command='python '+' '.join(args),exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
    paths=['chapters/parts/ch05-a.tex','chapters/parts/ch08-a.tex','chapters/parts/ch08-c.tex','tools/gen_tpd_table.py']
    pdf=ROOT/'build/main.pdf';doc=pymupdf.open(pdf)
    data=dict(baseline=BASE,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
              pdf=dict(pages=len(doc),bookmarks=len(doc.get_toc()),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest()),
              independent_TPD=rows,A_s_inverse_for_Tp570_at_10Kmin=(10/60)*E/(R*570**2)*math.exp(E/(R*570)),
              legacy_model_widths=shape,commands=cmdrows)
    (out/'verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k not in ['commands','source_sha256']},ensure_ascii=False,indent=2))
    print('tool exits:',[r['exit_code'] for r in cmdrows])
if __name__=='__main__':main()
