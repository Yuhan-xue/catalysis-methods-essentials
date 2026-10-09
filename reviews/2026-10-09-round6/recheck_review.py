"""Round 6 evidence collection, not a release gate. Never edits production inputs.
python reviews/2026-10-09-round6/recheck_review.py --out build/review-round6
Needs numpy, scipy, PyMuPDF (production probes), Pillow.
"""
from pathlib import Path
import argparse, hashlib, io, json, math, subprocess, sys
import pymupdf
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
BASE='71f5ebc5158bb87632f82c93903d7ede3afb3281'

def run(args):
    r=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    return dict(command='python '+' '.join(map(str,args)),exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)

def make_pdf(path,rect,image_color=(200,30,30),text_xy=(40,40),metadata='A'):
    doc=pymupdf.open();p=doc.new_page(width=320,height=240)
    p.insert_text(text_xy,'Model curve and micrograph',fontsize=11)
    p.draw_rect(pymupdf.Rect(rect),color=(0,0,1),width=2)
    raw=io.BytesIO();Image.new('RGB',(50,50),image_color).save(raw,format='PNG')
    p.insert_image(pymupdf.Rect(220,100,280,160),stream=raw.getvalue())
    doc.set_toc([[1,'Chapter',1]]);doc.set_metadata({'title':metadata});doc.save(path);doc.close()

def comparator_probe(out):
    folder=out/'comparator-fixtures';folder.mkdir(exist_ok=True)
    base=folder/'base.pdf';make_pdf(base,(40,80,160,130))
    variants={'metadata_only':((40,80,160,130),(200,30,30),(40,40),'B'),
              'geometry_changed':((40,140,160,190),(200,30,30),(40,40),'A'),
              'raster_changed':((40,80,160,130),(30,200,30),(40,40),'A'),
              'text_moved':((40,80,160,130),(200,30,30),(40,220),'A')}
    a=pymupdf.open(base);ap=a[0].get_pixmap().samples;results={}
    for name,(rect,color,xy,metadata) in variants.items():
        target=folder/(name+'.pdf');make_pdf(target,rect,color,xy,metadata)
        result=run(['tools/cmp_release_pdf.py',base,target])
        b=pymupdf.open(target);bp=b[0].get_pixmap().samples
        result['rendered_bytes_changed']=sum(x!=y for x,y in zip(ap,bp))
        result['raster_sha256']=hashlib.sha256(bp).hexdigest();b.close()
        results[name]=result
    a.close();return results

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'build/review-round6');args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    commands=[['tools/gen_tpd_table.py','--verify'],['tools/gen_tpd_table.py','--check'],
              ['tools/fig_probe_tpd.py','--pdf','build/main.pdf'],['tools/fig_probe_tpd.py','--selftest'],
              ['tools/check_heading_orphan.py','--pdf','build/main.pdf'],['tools/check_cp_quant_demo.py'],
              ['tools/pdf_probe.py','--pdf','build/main.pdf'],['tools/fig_probe_eis.py','--pdf','build/main.pdf'],
              ['tools/check_src.py'],['tools/check_table_content.py','--csv',out/'table-content.csv']]
    eps=78.5*8.8541878128e-12;eta=1e-3;zeta=.025;temp=298.15;k=1.380649e-23
    sizes=[100e-9,200e-9]
    physics={'rayleigh':dict(diameters_nm=[10,20],equal_number_intensity_ratio=2**6,inverse_claim_ratio=2**-6),
             'weighting':dict(diameters_nm=[10,20],equal_number_ratio=[1,1],volume_ratio=[1,8],intensity_ratio=[1,64],
                              large_particle_volume_fraction=8/9,large_particle_intensity_fraction=64/65),
             'smoluchowski':dict(assumptions='thin double layer, same zeta=25 mV, epsilon_r=78.5, eta=1 mPa s, T=298.15 K',
                                diameter_nm=[d*1e9 for d in sizes],mobility_m2_V_s=[eps*zeta/eta]*2,
                                diffusion_m2_s=[k*temp/(3*math.pi*eta*d) for d in sizes])}
    pdf=ROOT/'build/main.pdf';doc=pymupdf.open(pdf)
    paths=['chapters/parts/ch01-c.tex','chapters/parts/ch09-a.tex','tools/cmp_release_pdf.py','sources/table_status.md']
    data=dict(baseline=BASE,pdf=dict(pages=len(doc),bookmarks=len(doc.get_toc()),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest()),
              source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},physics=physics,
              comparator=comparator_probe(out),commands=[run(c) for c in commands])
    doc.close();(out/'verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('pdf:',data['pdf']);print('comparator:',{k:(v['exit_code'],v['rendered_bytes_changed']) for k,v in data['comparator'].items()})
    print('production exits:',[r['exit_code'] for r in data['commands']])
if __name__=='__main__':main()
