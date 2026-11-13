#!/usr/bin/env python3
"""Install the complete package and skill discovery bridges in one project."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from codex_package import bridge_files, digest, discover_skills, extension_names, package_files

ROOT = Path(__file__).resolve().parent


def contained(path, root):
    path, root = Path(path), Path(root)
    path.resolve().relative_to(root.resolve())
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError('Installation path cannot contain a symlink: ' + str(candidate))
        if candidate != path and candidate.exists() and not candidate.is_dir():
            raise ValueError('Installation parent is not a directory: ' + str(candidate))
        if candidate == root:
            break
    return path


def plan(project, extensions=None, remove=False):
    project = Path(project).resolve()
    agents = contained(project / '.agents', project)
    destination = contained(agents / 'packages/codex-seo', project)
    if destination.resolve().is_relative_to(ROOT) or ROOT.is_relative_to(destination.resolve()):
        raise ValueError('Installation target must not overlap the source package')
    skills = discover_skills(ROOT, extensions)
    if extensions is not None:
        skills = {name: entry for name, entry in skills.items() if entry['extension'] in extensions}
    installed = {name: {**entry, 'path': destination / entry['path'].relative_to(ROOT)}
                 for name, entry in skills.items()}
    writes = bridge_files(destination, agents / 'skills', installed)
    for path in writes:
        contained(path, project)
    for name, entry in skills.items():
        ui = entry['path'].parent / 'agents/openai.yaml'
        if ui.is_file():
            writes[agents / 'skills' / name / 'agents/openai.yaml'] = ui.read_bytes()
    state_path = contained(agents / 'codex-seo-install.json', project)
    if state_path.exists() and not state_path.is_file():
        raise ValueError('Installation state must be a regular file')
    state_data = state_path.read_bytes() if state_path.is_file() else None
    state_checksum = digest(state_data) if state_data is not None else None
    state = json.loads(state_data) if state_data is not None else {'files': {}}
    if not isinstance(state, dict) or not isinstance(state.get('files'), dict):
        raise ValueError('Invalid installation state')
    version = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))['version']
    if remove:
        owned = {}
        for relative, checksum in state['files'].items():
            parts = Path(relative).parts
            path = contained(project / relative, agents / 'skills')
            if len(parts) < 4 or parts[:2] != ('.agents', 'skills'):
                raise ValueError('Installation state escapes the skill directory')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', parts[2]):
                raise ValueError('Invalid installed skill name')
            if parts[2] in skills and path.is_file():
                if digest(path.read_bytes()) != checksum:
                    raise ValueError('Modified installed skill is preserved: ' + str(path))
                owned[path] = checksum
        return {'project': project, 'package': destination, 'skills': skills, 'remove': owned,
                'writes': {}, 'state': state, 'state_path': state_path, 'version': version,
                'state_checksum': state_checksum}
    conflicts = [str(path) for path, data in writes.items()
                 if path.exists() and (path.is_symlink() or not path.is_file() or path.read_bytes() != data)]
    package_writes = {}
    for source in package_files(ROOT):
        target = contained(destination / source.relative_to(ROOT), project)
        data = source.read_bytes()
        if target.exists() and (target.is_symlink() or not target.is_file() or target.read_bytes() != data):
            conflicts.append(str(target))
        package_writes[target] = data
    if conflicts:
        raise ValueError('Existing files differ; choose a fresh target or review them first: ' + ', '.join(conflicts[:5]))
    return {'project': project, 'package': destination, 'skills': skills, 'remove': {},
            'writes': {**package_writes, **writes}, 'bridge_writes': writes,
            'state': state, 'state_path': state_path, 'version': version,
            'state_checksum': state_checksum}


def execute(result):
    # Recheck a reviewable plan before the first write or removal.
    for path, checksum in result['remove'].items():
        contained(path, result['project'])
        if not path.is_file() or digest(path.read_bytes()) != checksum:
            raise ValueError('Modified installed skill is preserved: ' + str(path))
    for path, data in result['writes'].items():
        contained(path, result['project'])
        if path.exists() and (not path.is_file() or path.read_bytes() != data):
            raise ValueError('Existing file changed after planning and is preserved: ' + str(path))
    state_path = contained(result['state_path'], result['project'])
    if state_path.exists() and not state_path.is_file():
        raise ValueError('Installation state must be a regular file')
    observed_state = digest(state_path.read_bytes()) if state_path.is_file() else None
    if observed_state != result['state_checksum']:
        raise ValueError('Installation state changed after planning and is preserved')
    for path in result['remove']:
        path.unlink()
        result['state']['files'].pop(path.relative_to(result['project']).as_posix(), None)
    for path, data in result['writes'].items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open('xb') as handle:
                handle.write(data)
    for path, data in result.get('bridge_writes', {}).items():
        result['state']['files'][path.relative_to(result['project']).as_posix()] = digest(data)
    result['state'].update({'package': '.agents/packages/codex-seo', 'version': result['version']})
    result['state_path'].parent.mkdir(parents=True, exist_ok=True)
    state_data = (json.dumps(result['state'], indent=2, sort_keys=True) + '\n').encode('utf-8')
    if not state_path.is_file() or state_path.read_bytes() != state_data:
        state_path.write_bytes(state_data)
    result['state_checksum'] = digest(state_data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--extension', action='append', choices=extension_names(ROOT))
    parser.add_argument('--remove', action='store_true')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--apply', action='store_true')
    modes.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = plan(args.project, set(args.extension) if args.extension else None, args.remove)
        if args.apply:
            execute(result)
        print(json.dumps({'applied': args.apply, 'action': 'remove' if args.remove else 'install',
                          'project': str(result['project']), 'package': str(result['package']),
                          'skills': sorted(result['skills']), 'files_to_write': len(result['writes']),
                          'files_to_remove': len(result['remove']),
                          'package_retained_on_remove': True}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
