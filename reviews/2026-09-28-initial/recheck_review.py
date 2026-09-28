"""Read-only source audit and independent counterexample calculations (stdlib only).

Run from any directory:
  python reviews/2026-09-28-initial/recheck_review.py --output path/to/result.json
The assertions validate the calculations, NOT the correctness of the textbook.
No source files or old workspace paths are modified.
"""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
import math
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def tex_without_comments(text):
    return '\n'.join(re.split(r'(?<!\\)%', line)[0] for line in text.splitlines())


def integral(f, lo=400, hi=750, n=20000):
    h = (hi-lo)/n
    return h * (sum(f(lo+i*h) for i in range(1,n)) + (f(lo)+f(hi))/2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    findings = json.loads((HERE/'findings.json').read_text(encoding='utf-8'))
    labels = collections.defaultdict(list)
    refs = set()
    figures = tables = 0
    parts = sorted((ROOT/'chapters/parts').glob('ch??-*.tex'))
    for path in sorted((ROOT/'chapters').rglob('*.tex')):
        text = tex_without_comments(path.read_text(encoding='utf-8'))
        for i,line in enumerate(text.splitlines(),1):
            for label in re.findall(r'\\label\{([^}]+)\}', line):
                labels[label].append(f'{path.relative_to(ROOT).as_posix()}:{i}')
        refs.update(re.findall(r'\\(?:ref|eqref|equref|chapref|figref|tabref|pageref)\{([^}]+)\}',text))
        figures += len(re.findall(r'\\begin\{figure\*?\}',text))
        tables += len(re.findall(r'\\begin\{(?:table\*?|longtable)\}',text))
    plan = re.findall(r'^\| (ch\d{2}-[a-z]) \|', (ROOT/'sources/assignments.md').read_text(encoding='utf-8'),re.M)
    ledger = list(csv.DictReader((ROOT/'sources/figure_table_list.csv').open(encoding='utf-8-sig')))
    duplicates = {k:v for k,v in sorted(labels.items()) if len(v)>1}
    anchor_check = []
    source_hashes = {}
    for f in findings['findings']:
        path=ROOT/f['path']
        lines=path.read_text(encoding='utf-8').splitlines()
        assert 0 < f['line'] <= len(lines), f['id']
        anchor_check.append({'id':f['id'],'path':f['path'],'line':f['line'],'line_text':lines[f['line']-1]})
        source_hashes[f['path']] = hashlib.sha256(path.read_bytes()).hexdigest()
    bjh_correct, bjh_draft = 25*math.pi, 9*math.pi
    bet = 210*6.02214076e23*.162e-18/22400
    fn_correct, fn_draft = (1/.02)*20/40, (1/.02)*40/20
    dw_amplitude = math.exp(-(math.sin(math.radians(80))/1.5406)**2)
    area = [integral(lambda t,a=a,p=p,w=w:a/(1+((t-p)/w)**4))
            for a,p,w in [(.025,550,21.4),(.05,566,22.6),(.1,583,24)]]
    tpd_b = integral(lambda t:.055/(1+((t-572)/26.8)**4))/area[1]
    atr = 10/(2*math.pi*math.sqrt(2.4**2*math.sin(math.pi/4)**2-1.5**2))
    beta_correct = math.degrees(math.acos(1/math.sqrt(3)))
    mas_actual_p2 = (3*math.cos(math.radians(35.264))**2-1)/2
    # Use exactly the rounded constants stated in the draft.
    kappa_coeff = math.sqrt(2*9.109e-31*1.602176634e-19)/1.055e-34*1e-10
    stm_pm = math.log(1.01)/2.05*100
    calculations = {
        'C01-01':{'filled_volume_per_length':bjh_correct,'draft_ring_volume_per_length':bjh_draft,'ratio':bjh_draft/bjh_correct},
        'C01-02':{'specific_area_m2_per_g':bet,'erroneous_second_division_by_0.1g':bet/.1},
        'C03-01':{'draft_positive_conversion_derivative_peak_percent_per_K':100/48,'positive_mass_loss_derivative_peak_percent_per_K':20/48},
        'C04-01':{'Q_100_Angstrom_minus2':1/4**2,'q_sin2theta_100':1.54**2/(4*4**2)},
        'C04-02':{'correct_Fn':fn_correct,'draft_Fn':fn_draft},
        'C04-03':{'draft_factor':dw_amplitude,'correct_intensity_factor':dw_amplitude**2},
        'C05-01':{'correct_volume':(100-20+100-60)/100,'draft_unnormalized':100-20+100-60},
        'C05-02':{'finite_400_750K_areas':area,'finite_area_ratios':[v/area[0] for v in area],
                   'whole_axis_area_ratios':[1,2*22.6/21.4,4*24/21.4],
                   'panel_b_area_second_over_first':tpd_b,
                   'note':'Quartic peak functions are even about their own centers; this is not an ODE solution.'},
        'C07-01':{'correct_field_depth_micrometers':atr,'using_medium_wavelength_with_extra_n1':atr/2.4},
        'C08-01':{'correct_beta_degrees':beta_correct,'P2_at_drawn_beta':mas_actual_p2},
        'C10-01':{'direct_substitution_rate':(2-.5)/3,'draft_rate':(2-.5)/2/3},
        'C11-01':{'at_equilibrium_CO10_CR1_unnormalized_i_over_FAk0':10-1,'normalized_i_over_i0':10/10-1/1,
                   'note':'The unequal concentration case is outside the intermediate equal-concentration shortcut; the report requests the missing reference-potential conversion.'},
        'C12-01':{'kappa_coefficient_Angstrom_minus1_per_sqrt_eV':kappa_coeff,'twice_kappa_coefficient':2*kappa_coeff,'kappa_at_4eV':2*kappa_coeff},
        'C12-02':{'distance_pm_for_1percent':stm_pm,'back_substitution_relative_current':math.exp(2.05*stm_pm/100)-1},
    }
    assert abs(bjh_draft/bjh_correct-.36)<1e-12
    assert fn_correct==25 and fn_draft==100
    assert 2.004<atr<2.006
    assert .49<mas_actual_p2<.51
    assert .511<kappa_coeff<.513
    assert .48<stm_pm<.49
    assert abs(math.exp(2.05*stm_pm/100)-1-.01)<1e-12
    result = {
        'review_baseline':findings['baseline'],
        'interpretation':'Counterexamples and structural findings; calculation assertions passing does not mean the textbook passes review.',
        'findings_count':len(findings['findings']),
        'priorities':dict(collections.Counter(f['priority'] for f in findings['findings'])),
        'body_parts':len(parts),'planned_parts':len(plan),
        'missing_planned_parts':[p for p in plan if not (ROOT/'chapters/parts'/f'{p}.tex').exists()],
        'duplicate_explicit_labels':duplicates,
        'unresolved_explicit_reference_candidates':sorted(refs-set(labels)),
        'reference_scan_limit':'Macro-generated labels may need the compiled .aux; candidates are not automatically errors.',
        'tex_float_inventory':{'figures':figures,'tables_including_longtable':tables},
        'figure_ledger':{'rows':len(ledger),'kinds':dict(collections.Counter(v['kind'] for v in ledger)),
                         'source_parts':len(set(v['editable_source'] for v in ledger))},
        'source_sha256':source_hashes,'anchors':anchor_check,'independent_calculations':calculations,
    }
    payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output: args.output.write_text(payload,encoding='utf-8')
    else: print(payload)


if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    main()
