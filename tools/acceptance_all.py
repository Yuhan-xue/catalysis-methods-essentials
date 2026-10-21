# -*- coding: utf-8 -*-
"""One command that reproduces the whole acceptance evidence chain.

    python tools/acceptance_all.py            # ledgers + gate + QA suite
    python tools/acceptance_all.py --build    # also rebuild with -Release

Steps (each must exit 0):
  1. tools/review_ledger.py all --strict   -> regenerates every ledger, byte-identical
  2. tools/verify_acceptance.py            -> pages / formulas / tables / fixes / replay
  3. tools/qa_suite.py                     -> 11 layout & cross-reference checkers
  4. tools/build.ps1 -Release (--build)    -> rebuild, release-mode gates

Output: build/acceptance_all.txt (UTF-8). Console output is ASCII only because the
Windows console here is GBK and would mangle Chinese.
"""
import argparse
import io
import os
import subprocess
import sys

PWSH = r'C:\Users\53150\AppData\Local\Microsoft\WindowsApps\pwsh.exe'
OUT = 'build/acceptance_all.txt'


def run(name, cmd, timeout=3600):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return name, 'TIMEOUT', ''
    txt = (r.stdout + r.stderr).decode('utf-8', 'replace')
    return name, 'exit=%d' % r.returncode, txt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', action='store_true', help='also rebuild with -Release')
    args = ap.parse_args()

    steps = [
        ('ledgers', [sys.executable, 'tools/review_ledger.py', 'all', '--strict']),
        ('gate', [sys.executable, 'tools/verify_acceptance.py']),
        ('qa_suite', [sys.executable, 'tools/qa_suite.py']),
    ]
    if args.build:
        steps.append(('build_release', [PWSH, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                        '-File', 'tools/build.ps1', '-Release']))

    out = io.open(OUT, 'w', encoding='utf-8', newline='\n')
    w = out.write
    w('# acceptance replay\n\n')
    failed = []
    for name, cmd in steps:
        _, status, txt = run(name, cmd)
        w('=== %-13s %s\n' % (name, status))
        tail = [ln for ln in txt.splitlines() if ln.strip()][-6:]
        for ln in tail:
            w('    ' + ln[:200] + '\n')
        w('\n')
        if status != 'exit=0':
            failed.append(name)
        print('%-13s %s' % (name, status))

    verdict = 'PASS' if not failed else 'FAIL: ' + ', '.join(failed)
    w('RESULT %s\n' % verdict)
    out.close()
    print('RESULT ' + verdict)
    print('report ' + OUT)
    return 0 if not failed else 1


if __name__ == '__main__':
    raise SystemExit(main())
