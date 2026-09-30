"""R4 审阅证据：实际 TG 坐标复算、定义反例、PDF/来源旧项回归。

python reviews/2026-09-30-round4/recheck_review.py --out build/review-round4
依赖 numpy/scipy/PyMuPDF。输出是复核证据，不是全书 PASS；不修改生产源码。
数值定义固定为本轮基线，后续改稿需核对哈希及新的公式约定。
"""
from pathlib import Path
import argparse, contextlib, hashlib, importlib.util, io, json, math, re, subprocess, sys
import numpy as np
import pymupdf
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[2]
BASELINE='5cf40f70c0db2697ec60745751dd264f6cb28d82'
sys.dont_write_bytecode=True

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def numerical():
    gas,E=8.314462618,180000.
    A=5*E/(gas*673**2)*math.exp(E/(gas*673))
    def alpha(T,beta):
        h=quad(lambda t:A/beta*math.exp(-E/(gas*t)),300,T,epsabs=1e-11)[0]
        return -math.expm1(-h)
    def deriv(T,beta):
        return A/beta*math.exp(-E/(gas*T))*(1-alpha(T,beta))
    rows=[]
    for b in [2.5,5.,10.,20.]:
        tp=brentq(lambda t:A/b*math.exp(-E/(gas*t))-E/(gas*t*t),600,800)
        hp=20*deriv(tp,b)
        width=brentq(lambda t:20*deriv(t,b)-hp/2,tp,800)-brentq(lambda t:20*deriv(t,b)-hp/2,500,tp)
        rows.append(dict(beta=b,Tp=tp,alpha_peak=alpha(tp,b),peak_per_K=hp,
                         peak_per_min=b*hp,FWHM_K=width))
    tex=(ROOT/'chapters/parts/ch03-b.tex').read_text(encoding='utf-8')
    blocks=re.findall(r'\\addplot[^;]*?coordinates\s*\{(.*?)\};',tex,re.S)
    assert len(blocks)==8,'TG figure layout changed: review parser'
    coords=[]
    for i,block in enumerate(blocks):
        points=np.array([(float(a),float(b)) for a,b in re.findall(r'\(([0-9.]+),([0-9.]+)\)',block)])
        beta=[2.5,5.,10.,20.][i%4]
        expected=np.array([100-20*alpha(T,beta) if i<4 else 20*deriv(T,beta) for T in points[:,0]])
        coords.append(dict(panel='TG' if i<4 else 'DTG',beta=beta,points=len(points),
                           max_abs_error=float(max(abs(points[:,1]-expected)))))
    n=.85;R=100.;C=.5e-6;Q=C**n*R**(n-1)
    caps=[dict(f_hz=f,Cparallel_F=Q*math.sin(n*math.pi/2)*(2*math.pi*f)**(n-1)) for f in [1.,.01,.0001]]
    samples=[]
    for f in [.02,.1,32.,3200.,40000.,80000.]:
        w=2*math.pi*f;z=10+1/(1/(100+40*(1-1j)/math.sqrt(w))+1j*w*C)
        t=40/(100*math.sqrt(w));s=(1+t)**2+t*t; a=(1+t)/s;b=t/s+w*C*100
        zplot=10+100*complex(a,-b)/(a*a+b*b)
        samples.append(dict(f=f,x=z.real,minus_y=-z.imag,plot_formula_error=abs(z-zplot)))
    return dict(TG_model=dict(E=E,A_per_min=A,T0_K=300),TG_peaks=rows,TG_coordinates=coords,
      time_peak_ratio=rows[-1]['peak_per_min']/rows[0]['peak_per_min'],beta_ratio=8,
      raman_45deg=dict(correct_relative_power=.5,extra_sin2_relative_power=.25),
      cpe=dict(Q=Q,peak_convention_Ceff=C,parallel_capacitance=caps),randles=samples,
      warburg=[dict(sigma=s,nyquist_slope=1.,frequency_plot_slope=s) for s in [20.,40.]])

def tool_probes(out):
    # 复用已入库的 R3 隔离夹具，仅调用来源门禁案例；不采用其旧数值结论。
    old=module('review_r3','reviews/2026-09-30-round3/recheck_review.py')
    source=old.source_probes(out)
    src=module('source_gate','tools/check_src.py')
    evidence='; 页面=PDF p.36; 核验者=R4 fixture; 时间=2026-09-30; 结论=已核图'
    statuses={s:src.parse_review(s) for s in ['', '待复核','已核対','已核对','已核对'+evidence]}
    pdf=ROOT/'build/main.pdf'; pdf_cases={}
    for name in ['normal','no_bookmarks','missing_required']:
        with pymupdf.open(pdf) as d:
            if name=='no_bookmarks':d.set_toc([])
            if name=='missing_required':
                toc=d.get_toc();i=next(i for i,row in enumerate(toc) if row[1]=='跨方法综合应用')
                j=i+1
                while j<len(toc) and toc[j][0]>toc[i][0]:j+=1
                d.set_toc(toc[:i]+toc[j:])
            target=out/(name+'.pdf');d.save(target)
        run=subprocess.run([sys.executable,str(ROOT/'tools/pdf_probe.py'),'--pdf',str(target),
                            '--out',str(out/(name+'.txt')),'--json',str(out/(name+'.json'))],
                           capture_output=True,cwd=ROOT)
        facts=json.loads((out/(name+'.json')).read_text(encoding='utf-8'))
        pdf_cases[name]=dict(exit=run.returncode,statuses=facts['statuses'])
    # 相同真实 PDF，用生产阈值和仅用于诊断的较低阈值对照。
    eis={}
    for label,threshold in [('production',5.),('diagnostic',.01)]:
        m=module('fig_'+label,'tools/fig_probe_eis.py');m.MIN_SEG_PT=threshold
        argv=sys.argv[:];sys.argv=['probe','--pdf',str(pdf),'--out',str(out/('eis-'+label+'.txt')),
                                  '--json',str(out/('eis-'+label+'.json'))]
        try:
            with contextlib.redirect_stdout(io.StringIO()):code=m.main()
        finally:sys.argv=argv
        facts=json.loads((out/('eis-'+label+'.json')).read_text(encoding='utf-8'))
        eis[label]=dict(exit=code,threshold=threshold,P3=facts['checks']['P3_text'])
    return dict(source_old_cases=source,review_states=statuses,pdf_cases=pdf_cases,eis=eis,
                diagnostic_note='降低阈值还产生轴刻度附近候选；仅确认左图说明文字处，不能把所有候选算作缺陷。')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/review-round4');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    paths=['chapters/parts/ch03-b.tex','chapters/parts/ch06-a.tex','chapters/parts/ch11-d.tex',
           'chapters/ch90-backmatter.tex','tools/fig_probe_eis.py','tools/check_src.py','tools/pdf_probe.py']
    result=dict(baseline=BASELINE,source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                numerical=numerical(),probes=tool_probes(out),
                missing_generator=dict(path='build/r3/recompute_ch03b_dtg.py',exists=(ROOT/'build/r3/recompute_ch03b_dtg.py').exists()))
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote',out/'verification.json')
    print('TG coordinates:',sum(r['points'] for r in result['numerical']['TG_coordinates']))
    print('Time peak ratio:',result['numerical']['time_peak_ratio'])
    print('PDF cases:',result['probes']['pdf_cases'])

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
