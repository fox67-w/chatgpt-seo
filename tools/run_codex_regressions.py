"""Run source analysis regressions plus native Codex replacements."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parents[1]
PLUGIN = BASE / 'plugins/codex-seo'


def replacement_cases():
    record = BASE / 'tests_codex/source_contract_replacements.json'
    data = json.loads(record.read_text(encoding='utf-8'))
    cases = data['cases']
    nodes = [case['nodeid'] for case in cases]
    if len(nodes) != len(set(nodes)):
        raise ValueError('Duplicate source test replacement')
    for case in cases:
        node = case['nodeid'].split('::', 1)[0]
        if '..' in PurePosixPath(node).parts or not node.startswith('tests/'):
            raise ValueError('Invalid source test path')
        if not (PLUGIN / node).is_file() or not case.get('reason'):
            raise ValueError('Replacement must identify an existing case and reason')
        for replacement in case.get('replacement_tests', []):
            target = replacement.split('::', 1)[0]
            if not (BASE / target).is_file():
                raise ValueError('Missing native replacement test: ' + target)
        if not case.get('retain_original') and not case.get('replacement_tests'):
            raise ValueError('A replaced source contract needs native coverage')
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=BASE / 'dist/verification')
    args = parser.parse_args()
    output = args.output.resolve()
    output.relative_to(BASE)
    output.mkdir(parents=True, exist_ok=True)
    runtime = BASE / '.runtime'
    runtime.mkdir(exist_ok=True)
    # A new, checked workspace directory avoids long Windows temp paths and
    # prevents pytest from recursively resetting an unrelated existing folder.
    temporary = Path(tempfile.mkdtemp(prefix='pt-', dir=runtime)).resolve()
    temporary.relative_to(runtime.resolve())
    cases = replacement_cases()
    deselected = [case for case in cases if not case.get('retain_original')]
    command = [sys.executable, '-m', 'pytest', str(PLUGIN / 'tests'),
               str(BASE / 'tests_codex'), str(BASE / 'tests/test_codex_extensions.py'),
               str(BASE / 'tests/test_codex_workflows.py'), '--rootdir', str(BASE),
               '--basetemp', str(temporary / 'cases'), '-q', '--tb=short', '--timeout=30',
               '--junitxml', str(output / 'codex-tests.xml')]
    for case in deselected:
        command += ['--deselect', 'plugins/codex-seo/' + case['nodeid']]
    env = os.environ.copy()
    env.pop('CODEX_SEO_DATA_DIR', None)
    env.update({'PYTHONUTF8': '1', 'CODEX_SEO_CONFIG_DIR': str(temporary / 'config'),
                'CODEX_SEO_CACHE_DIR': str(temporary / 'cache')})
    (output / 'codex-test-contracts.json').write_text(json.dumps({
        'source_cases_retained_on_disk': True,
        'reviewed_replacements': deselected,
        'original_invariants_retained': [case for case in cases if case.get('retain_original')],
    }, indent=2) + '\n', encoding='utf-8', newline='\n')
    with (output / 'codex-regressions.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    lines = (output / 'codex-regressions.log').read_text(encoding='utf-8').splitlines()
    print('\n'.join(lines[-80:]))
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
