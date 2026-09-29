"""R3 独立复算与隔离反例；不修改正文、生产工具、台账或已跟踪报告。

python reviews/2026-09-30-round3/recheck_review.py --out build/review-round3
输出是审阅证据，不是全书验收。数值基线固定为 8df5e1e 的公式/参数；
源码哈希变化后必须人工复审，不能凭此脚本关闭问题。
依赖：Python、numpy、scipy、PyMuPDF；重叠对照另依赖仓库工具依赖。
"""
from pathlib import Path
import argparse, contextlib, csv, hashlib, importlib.util, io, json, math
import re, shutil, subprocess, sys, tempfile
import numpy as np
from scipy.integrate import quad
import pymupdf

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BASELINE = '8df5e1e0b9a2ccbe5ac0edf0d8d823e2fc5af114'

def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def numerical():
    R, C, n, Rs, sigma = 100., .5e-6, .85, 10., 40.
    Q = C**n * R**(n-1)
    fm = (1/(R*Q))**(1/n)/(2*math.pi)
    cpe = Rs + 1/(1/R + Q*(1j*2*math.pi*fm)**n)
    samples = []
    for f in [.02, .1, 32., 3200., 40000., 80000.]:
        w = 2*math.pi*f
        zw = sigma/math.sqrt(w)*(1-1j)
        z = Rs + 1/(1/(R+zw) + 1j*w*C)
        # 原图 dkwx / dkwy 返回 (Z', -Z'')，与下面直接复数运算对照。
        a = sigma/math.sqrt(w)
        oldx = Rs + R*(1+a)/((1+a)**2+a*a)
        oldy = R*a/((1+a)**2+a*a)
        samples.append(dict(f_hz=f, randles_x=z.real, randles_minus_y=-z.imag,
                            phi_deg=-np.angle(z,deg=True), plotted_x=oldx, plotted_minus_y=oldy))
    # 仅检验生产文本所用 Arrhenius 一级模型，不把 logistic 当物理积分器。
    E, Tp, beta, gas, T0 = 180000., 673., 5., 8.314462618, 300.
    A = beta*E/(gas*Tp*Tp)*math.exp(E/(gas*Tp))
    h, error = quad(lambda T: A/beta*math.exp(-E/(gas*T)), T0, Tp, epsabs=1e-12)
    alpha_peak = 1-math.exp(-h)
    t=np.array([658.,673.,688.,703.]); b=np.array([2.5,5.,10.,20.])
    fitted_E=-gas*np.polyfit(1/t, np.log(b/t**2), 1)[0]
    # 已修复旧项的代数对照：ct / WP / jD / AFM / BET / DTG。
    rho=1500.; rm=1e-4; rv=rho*rm; radius=1e-3; De=1e-6; cb=10.
    rho_f, k, G, dp, mu, D = 1.2, .03, .5, .001, 1.8e-5, 2e-5
    Sc=mu/(rho_f*D); Sh=k*dp/D; Re=G*dp/mu
    return {
      'cpe':dict(Q=Q, peak_f_hz=fm, peak_x=cpe.real, peak_minus_y=-cpe.imag,
                 analytical_y=R/2*math.tan(n*math.pi/4), caption_peak=[22.1,22.7,721.]),
      'randles_samples':samples,
      'raman_units':dict(lhs_power_ratio_m_exponent=0, rhs_cross_section_m_exponent=2,
                         fixed_solid_angle_distance_ratio=1., text_distance_doubling_ratio=.25),
      'thermal':dict(E_j_mol=E,Tp_K=Tp,beta_K_min=beta,T0_K=T0,A_per_min=A,
                     alpha_at_peak=alpha_peak,quadrature_error=error,
                     logistic_alpha_at_peak=.5, given_points_K=t.tolist(),
                     given_beta_K_min=b.tolist(),kissinger_fit_j_mol=fitted_E),
      'old_fixes':dict(coke_direct=(2-.5)/3,coke_factored=(2-.5)/2*(2/3),
                       WP_volume=rv*radius**2/(De*cb),WP_mass=rho*rm*radius**2/(De*cb),
                       jD_left=rho_f*k/G*Sc**(2/3), jD_right=Sh/(Re*Sc**(1/3)),
                       parallel_R1_R2=1/(1/1+1/2),AFM_sin2_mean=.5,
                       BET_specific=210/22400*6.02214076e23*.162e-18,
                       DTG_height=20/48,DTG_area=20.)}

def source_probes(out):
    m=module('r3_src','tools/check_src.py')
    real_root=str(ROOT)
    def show(path):
        p=subprocess.run(['git','show',m.BASELINE+':'+path],cwd=real_root,capture_output=True)
        return p.stdout.decode('utf-8') if p.returncode==0 else ''
    m.git_show=show
    with tempfile.TemporaryDirectory(prefix='catalysis-r3-') as temp:
        root=Path(temp); shutil.copytree(ROOT/'chapters',root/'chapters')
        (root/'sources').mkdir()
        for name in ['figure_table_list.csv','page_map_up.csv','page_map_down.csv']:
            shutil.copy2(ROOT/'sources'/name, root/'sources'/name)
        m.ROOT=str(root); m.LEDGER=str(root/'sources/figure_table_list.csv')
        def run(name):
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture),contextlib.redirect_stderr(capture):
                code=m.main([])
            report=(root/'build/check_src.txt').read_text(encoding='utf-8')
            summary=[x for x in report.splitlines() if x.startswith('checked ') or '集合差异' in x or '已核对 ' in x]
            (out/(name+'.txt')).write_text('\n'.join(summary)+'\n',encoding='utf-8')
            return dict(exit_code=code, summary=summary)
        results={'baseline':run('source-baseline')}
        target=root/'chapters/parts/ch01-a.tex'; original=target.read_text(encoding='utf-8')
        # 无来源且无标签、非 tab: 标签、标准 tab: 标签：应均可被清点。
        for name,label in [('unlabeled',''),('nonstandard_label',r'\label{review-unregistered}'),
                           ('registered_prefix_control',r'\label{tab:review-unregistered}')]:
            target.write_text(original+'\n\\begin{table}\n\\caption{Review fixture}'+label+
                              '\n\\begin{tabular}{c}X\\end{tabular}\n\\end{table}\n',encoding='utf-8')
            results[name]=run('source-'+name)
        target.write_text(original,encoding='utf-8')
        target.write_text(re.sub(r'p\.(\d+)', lambda hit: 'p.'+str(int(hit[1])+10000), original),encoding='utf-8')
        results['out_of_range_control']=run('source-out-of-range')
        target.write_text(original,encoding='utf-8')
        ledger=root/'sources/figure_table_list.csv'
        with ledger.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f); names=reader.fieldnames; rows=list(reader)
        idx=next(i for i,r in enumerate(rows) if r['kind']=='table')
        prior=rows[idx]['review_status']
        for value in ['', '待复核', '已核对页面图像']:
            rows[idx]['review_status']=value
            with ledger.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=names);writer.writeheader();writer.writerows(rows)
            results['manual_'+(value or 'empty')]=run('manual-'+(value or 'empty'))
        results['manual_original']=prior
    return results

def pdf_probes(out):
    probe=module('r3_pdf','tools/pdf_probe.py'); results={}
    for name,bookmarks in [('without_bookmarks',False),('with_bookmark_control',True)]:
        doc=pymupdf.open(); p=doc.new_page();p.insert_text((72,120),'1 Chapter Alpha')
        doc.new_page();doc.new_page()
        if bookmarks: doc.set_toc([[1,'1 Chapter Alpha',1]])
        path=out/(name+'.pdf');doc.save(path);doc.close()
        facts=probe.probe(path)
        proc=subprocess.run([sys.executable,str(ROOT/'tools/pdf_probe.py'),'--pdf',str(path),
                            '--out',str(out/(name+'.txt')),'--json',str(out/(name+'.json'))],
                            cwd=ROOT,capture_output=True)
        results[name]=dict(exit_code=proc.returncode,bookmarks_total=facts['bookmarks_total'],
                            U01_ok=facts['U01_ok'],U02_ok=facts['U02_ok'])
    # W05 修复正反对照：相撞矩形应阻断，正常矩形应通过。
    for name,cross in [('overlap_positive',True),('overlap_negative',False)]:
        doc=pymupdf.open();p=doc.new_page()
        p.draw_rect((80,100,220,240),color=(0,0,0))
        p.draw_rect((160,180,300,320) if cross else (320,180,460,320),color=(0,0,0))
        path=out/(name+'.pdf');doc.save(path);doc.close()
        proc=subprocess.run([sys.executable,str(ROOT/'tools/overlap_check.py'),'--gate','--pdf',str(path),
                             '--out',str(out/(name+'.txt')),'--json',str(out/(name+'.json'))],
                             cwd=ROOT,capture_output=True)
        facts=json.loads((out/(name+'.json')).read_text(encoding='utf-8'))
        results[name]=dict(exit_code=proc.returncode,status=facts['status'],blocking=facts['blocking_total'])
    return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/review-round3');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    paths=['chapters/parts/ch06-a.tex','chapters/parts/ch03-b.tex','chapters/parts/ch11-d.tex',
           'tools/check_src.py','tools/pdf_probe.py','tools/overlap_check.py']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    result=dict(review_baseline=BASELINE, meaning='审阅基线反例，不是全书验收或未来修复判定',
                source_sha256=hashes,numerical=numerical(),source_probes=source_probes(out),pdf_probes=pdf_probes(out))
    (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Wrote',out/'verification.json')
    print(json.dumps(dict(source={k:v.get('exit_code') for k,v in result['source_probes'].items() if isinstance(v,dict)},
                          pdf=result['pdf_probes']),ensure_ascii=False))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
