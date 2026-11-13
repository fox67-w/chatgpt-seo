"""Validate and reproducibly package the complete public Codex SEO port."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import re
import subprocess
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'plugins/codex-seo'
spec = importlib.util.spec_from_file_location('codex_package', ROOT / 'codex_package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def validate(check_tracked=False):
    inventory = json.loads((BASE / 'docs/claude-source-inventory.json').read_text(encoding='utf-8'))
    errors = []
    source = inventory['files']
    missing = [entry['path'] for entry in source if not (ROOT / entry['path']).is_file()]
    if missing:
        errors.append({'missing_source_files': missing})
    if check_tracked:
        try:
            tracked = set(subprocess.check_output(
                ['git', 'ls-files', '-z', '--', ROOT.relative_to(BASE).as_posix()],
                cwd=BASE).decode('utf-8').split('\0'))
            unpublished = sorted(path.relative_to(BASE).as_posix()
                                 for path in package.package_files(ROOT)
                                 if path.relative_to(BASE).as_posix() not in tracked)
            if unpublished:
                errors.append({'untracked_package_files': unpublished})
        except (OSError, subprocess.CalledProcessError, UnicodeError):
            errors.append('Could not verify Git tracked package files')
    source_skills = [entry for entry in source if re.fullmatch(r'skills/[^/]+/SKILL.md', entry['path'])]
    source_agents = [entry for entry in source if re.fullmatch(r'agents/[^/]+\.md', entry['path'])]
    extensions = sorted({Path(entry['path']).parts[1] for entry in source
                         if entry['path'].startswith('extensions/')})
    all_skills = list((ROOT / 'skills').glob('*/SKILL.md'))
    all_skills += list((ROOT / 'extensions').glob('*/skills/*/SKILL.md'))
    for skill in all_skills:
        try:
            package.metadata(skill)
        except ValueError as error:
            errors.append(str(error))
        text = skill.read_text(encoding='utf-8')
        if '$' + '{CLAUDE_PLUGIN_ROOT}' in text or '~/.claude/' in text:
            errors.append('Unresolved Claude runtime in ' + str(skill.relative_to(ROOT)))
    for path in package.package_files(ROOT):
        if path.suffix == '.py':
            try:
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            except (SyntaxError, UnicodeError) as error:
                errors.append(str(error))
    for relative in ('LICENSE', 'scripts/codex_seo.py', 'scripts/codex-seo.ps1',
                     'install-codex.py', 'plugin.json', '.codex-plugin/plugin.json'):
        if not (ROOT / relative).is_file():
            errors.append('Missing Codex execution resource: ' + relative)
    skills = package.discover_skills(ROOT)
    bridges = list((ROOT / 'codex-skills').glob('*/SKILL.md'))
    if len(bridges) != len(skills):
        errors.append('Discovery bridge count does not match unique workflows')
    for name in skills:
        bridge = ROOT / 'codex-skills' / name / 'SKILL.md'
        if not bridge.is_file():
            continue
        for target in re.findall(r'\]\(([^)]+)\)', bridge.read_text(encoding='utf-8')):
            if not (bridge.parent / target).is_file():
                errors.append('Broken discovery bridge: ' + name)
    changed = []
    for entry in source:
        path = ROOT / entry['path']
        if path.is_file():
            data = path.read_bytes()
            checksum = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            if checksum != entry['sha']:
                changed.append(entry['path'])
    return {'valid': not errors, 'errors': errors, 'upstream_commit': inventory['commit'],
            'source_files': len(source), 'missing_source_files': len(missing),
            'core_skills': len(source_skills), 'specialist_prompts': len(source_agents),
            'extension_names': extensions, 'unique_discoverable_skills': len(skills),
            'python_modules': len(list((ROOT / 'scripts').glob('*.py'))),
            'adapted_source_files': changed,
            'live_provider_validation': 'requires separately authorized accounts',
            'host_installation': 'not_verified'}


def build(output, check_tracked=False):
    result = validate(check_tracked=check_tracked)
    if not result['valid']:
        raise ValueError(json.dumps(result['errors']))
    output.mkdir(parents=True, exist_ok=True)
    archive = output / 'codex-seo-0.1.0.zip'
    entries = []
    # Stored entries avoid compression-library differences across build hosts.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as handle:
        for path in package.package_files(ROOT):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(relative, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if data.startswith(b'#!') else 0o100644) << 16
            info.compress_type = zipfile.ZIP_STORED
            handle.writestr(info, data)
            entries.append({'path': relative, 'sha256': package.digest(data), 'bytes': len(data)})
    checksum = package.digest(archive.read_bytes())
    archive.with_suffix('.sha256').write_text(checksum + '  ' + archive.name + '\n',
                                            encoding='utf-8', newline='\n')
    archive.with_suffix('.inventory.json').write_text(json.dumps(entries, indent=2) + '\n',
                                                    encoding='utf-8', newline='\n')
    return {'archive': str(archive), 'sha256': checksum, 'files': len(entries),
            'verification': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--check-tracked', action='store_true',
                        help='Require every packaged resource to be tracked by Git')
    parser.add_argument('--output', type=Path, default=BASE / 'dist/codex')
    args = parser.parse_args()
    if args.generate:
        package.generate_bridges(ROOT)
    result = (build(args.output, check_tracked=args.check_tracked) if args.build
              else validate(check_tracked=args.check_tracked))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get('valid', True) else 1)


if __name__ == '__main__':
    main()
