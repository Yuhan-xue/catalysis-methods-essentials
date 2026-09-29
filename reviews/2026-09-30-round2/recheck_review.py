"""Read-only review probes. Requires PyMuPDF and the repository's fontTools dependency.

Run: python reviews/2026-09-30-round2/recheck_review.py --out <scratch-directory>
All generated files go to --out or a temporary directory, never source/tool reports.
This reproduces observations; it is not a publication acceptance gate.
"""
from pathlib import Path
import argparse, contextlib, importlib.util, io, json, math, re, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / 'tools'))
    spec.loader.exec_module(mod)
    return mod

def run(out):
    import pymupdf
    out.mkdir(parents=True, exist_ok=True)
    facts = {'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()}
    ct, blocked, den, numerator = 2., .5, 3., 1.
    facts['coke'] = {'direct_substitution': numerator*(ct-blocked)/den,
                     'printed_factorization': (ct-blocked)/ct*numerator/den}
    rho, rm, radius, de, cb = 1500., 1e-4, 1e-3, 1e-6, 10.
    facts['weisz_prater'] = {'mass_basis': rho*rm*radius**2/(de*cb),
                             'volume_basis': (rho*rm)*radius**2/(de*cb),
                             'printed_example': (rho*rm)*rho*radius**2/(de*cb)}
    density, kg, flux, mu, diffusion, dp = 2., .01, .2, 1e-5, 1e-5, .001
    sc, sh, reynolds = mu/(density*diffusion), kg*dp/diffusion, flux*dp/mu
    facts['chilton_colburn'] = {'printed_left': kg/flux*sc**(2/3),
                                'right': sh/(reynolds*sc**(1/3)),
                                'corrected_left': density*kg/flux*sc**(2/3)}
    facts['parallel_impedance'] = {'inverse_sum_siemens': 1/10+1/10, 'impedance_ohms': 1/(1/10+1/10)}
    facts['afm'] = {'average_sin_squared_for_T_1_over_omega': .5-math.sin(2)/4,
                    'average_over_full_period': .5,
                    'linear_limit_coefficient_correct': -.5,
                    'with_proposed_extra_denominator_two': -.25}
    facts['eis_phase'] = {'capacitor_arg_degrees': -90, 'capacitor_negative_arg_degrees': 90}
    area = 210*6.02214076e23*.162e-18/22400
    facts['bet_area'] = {'specific_m2_per_g': area, 'incorrect_second_division_by_0_1_g': area/.1,
                         'total_area_of_0_1_g_then_divided_by_mass': (21*6.02214076e23*.162e-18/22400)/.1}
    facts['dtg_center'] = {'printed_positive_peak': 100/48, 'positive_mass_loss_derivative': 20/48,
                           'negative_conversion_derivative': -1/48}
    facts['raman_dimensions'] = {'manuscript_I_over_I0': 'dimensionless',
                                 'manuscript_sigma_sin2theta': 'area', 'consistent': False}

    # Change only page-pair numbers in an in-memory source view. Preserve real baseline evidence.
    src = module('check_src')
    original_show = src.git_show
    files = {str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'chapters').rglob('*.tex')}
    baseline = {p: original_show(p) for p in files}
    src.git_show = lambda p: baseline.get(p, '')
    original_read = src.read_lines
    changed = []
    def fake_read(path):
        rel = Path(path).relative_to(out/'source-probe')
        lines = original_read(str(ROOT/rel))
        if rel.name == 'ch01-a.tex':
            text = '\n'.join(lines)
            def shift(m):
                changed.append(m.group(0))
                return re.sub(r'\d+', lambda n: str(int(n.group(0))+10000), m.group(0))
            return src.PAIR_BLOCK.sub(shift, text).splitlines()
        return lines
    src.ROOT = str(out/'source-probe')
    src.read_lines = fake_read
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        code = src.main(['ch01-a'])
    facts['invalid_source_pages'] = {'exit_code': code, 'mutated_page_pairs': len(changed),
                                     'summary': captured.getvalue().strip()}

    # Exercise the real overlap checker on two intersecting (not nested) rectangles.
    scratch = out/'overlap-probe'
    (scratch/'tools').mkdir(parents=True, exist_ok=True)
    pdf = scratch/'fixture.pdf'
    doc = pymupdf.open(); page = doc.new_page()
    page.draw_rect(pymupdf.Rect(50,50,150,150), color=(0,0,0), width=1)
    page.draw_rect(pymupdf.Rect(100,100,200,200), color=(0,0,0), width=1)
    doc.save(pdf); doc.close()
    checker = module('overlap_check')
    checker.ROOT, checker.PDF, checker.OUT = str(scratch), str(pdf), str(scratch/'report.txt')
    doc = pymupdf.open(pdf)
    count = len(checker.check_graphics(doc[0])[0]); doc.close()
    with contextlib.redirect_stdout(io.StringIO()):
        result = checker.main()
    facts['overlap_gate'] = {'graphics_hits': count, 'main_return': result,
                             'entrypoint': 'main() without sys.exit / raising on hits'}

    # Copy only build.ps1 to an isolated fixture; compiler stub deliberately reports success.
    # This tests the gate's missing-checker branch, not compilation correctness.
    ps = subprocess.run(['where.exe','pwsh'], capture_output=True, text=True)
    candidates = ps.stdout.splitlines()
    bundled = Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
    pwsh = candidates[0] if candidates else str(bundled)
    build_probe = out/'release-probe'
    (build_probe/'tools').mkdir(parents=True, exist_ok=True)
    (build_probe/'build').mkdir(exist_ok=True)
    (build_probe/'tools/build.ps1').write_bytes((ROOT/'tools/build.ps1').read_bytes())
    (build_probe/'build/main.log').write_text('Output written on build/main.pdf (1 page).\n', encoding='utf-8')
    stub = build_probe/'compiler.cmd'; stub.write_text('@exit /b 0\n', encoding='ascii')
    quote = lambda p: "'"+str(p).replace("'","''")+"'"
    wrapper = build_probe/'probe.ps1'
    wrapper.write_text("function Get-Command { param($Name,$ErrorAction)\n"
                       "if ($Name -eq 'latexmk') { return [pscustomobject]@{Source="+quote(stub)+"} }\n"
                       "Microsoft.PowerShell.Core\\Get-Command $Name -ErrorAction SilentlyContinue\n}\n"
                       "& "+quote(build_probe/'tools/build.ps1')+" -Release\nexit $LASTEXITCODE\n",encoding='utf-8-sig')
    cp = subprocess.run([pwsh,'-NoProfile','-File',str(wrapper)],capture_output=True,encoding='utf-8',errors='replace')
    (build_probe/'stdout.txt').write_text(cp.stdout+cp.stderr,encoding='utf-8')
    facts['release_missing_checker'] = {'exit_code':cp.returncode, 'skipped': 'skipped' in cp.stdout,
                                        'prints_pass': 'PASS' in cp.stdout}
    pdf_path = ROOT/'build/main.pdf'
    if pdf_path.exists():
        doc = pymupdf.open(pdf_path)
        facts['pdf'] = {'pages':len(doc),'bookmarks':len(doc.get_toc()),
                        'backmatter_bookmarks':[row for row in doc.get_toc() if row[1] in ('跨方法综合应用','符号、缩写与索引')]}
        doc.close()
    # Never emit credential text. This only identifies the already-exposed authentication row.
    handoff = (ROOT/'HANDOFF.md').read_text(encoding='utf-8')
    facts['credential_rows'] = [i for i,line in enumerate(handoff.splitlines(),1)
                               if ('认证' in line and re.search(r'`[^`\s:]+:[^`\s]+`',line))
                               or re.search(r'\s-u\s+[^\s:]+:[^\s]+',line)]
    (out/'verification.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(facts,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(); parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.out:
        run(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='catalysis-review-') as temporary:
            run(Path(temporary))
