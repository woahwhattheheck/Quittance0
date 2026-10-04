"""Run the existing project checks, retaining every exit code and full log."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

root = Path.cwd()
out = Path(os.environ['RUNNER_TEMP']) / 'q571-validation'
out.mkdir(exist_ok=True)
checks = [
    ('frontend-lint', root / 'frontend', ['npm', 'run', 'lint']),
    ('frontend-typecheck', root / 'frontend', ['npm', 'run', 'typecheck']),
    ('frontend-tests', root / 'frontend', ['npm', 'test']),
    ('backend-typecheck', root / 'backend', ['npm', 'run', 'typecheck']),
    ('backend-contract-tests', root / 'backend', ['node', '--import', 'tsx', '--test', 'tests/invoice-contract.test.ts', 'tests/create-invoice-validation.test.ts', 'tests/shared-verification-contract.test.ts']),
    ('shared-contract-tests', root, ['node', '--test', 'tests/invoice-contract.test.mjs']),
]
receipt = {
    'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'tree_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], text=True).strip(),
    'node_version': subprocess.check_output(['node', '--version'], text=True).strip(),
    'npm_version': subprocess.check_output(['npm', '--version'], text=True).strip(),
    'checks': [],
}
for name, cwd, args in checks:
    log = out / f'{name}.log'
    timed_out = False
    with log.open('w') as stream:
        try:
            result = subprocess.run(args, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT, timeout=240)
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = 124
    text = log.read_text(errors='replace')
    summary = [line for line in text.splitlines() if re.match(r'^[ℹ#] (tests|suites|pass|fail|cancelled|skipped|todo|duration_ms)\b', line)]
    receipt['checks'].append({'name': name, 'cwd': str(cwd.relative_to(root)), 'command': args, 'exit_code': exit_code, 'timed_out': timed_out, 'summary': summary})
    print(f'::group::{name} exit={exit_code}', flush=True)
    if summary:
        print('\n'.join(summary))
    if exit_code or not summary:
        print('\n'.join(text.splitlines()[-180:]))
    print('::endgroup::', flush=True)
receipt['all_checks_passed'] = all(item['exit_code'] == 0 for item in receipt['checks'])
receipt['source_worktree_unchanged'] = not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], text=True).strip()
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('Q571_VALIDATION_RECEIPT=' + json.dumps(receipt, sort_keys=True), flush=True)
sys.exit(0 if receipt['all_checks_passed'] and receipt['source_worktree_unchanged'] else 1)
