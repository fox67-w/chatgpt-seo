"""Dependency-free package discovery for the Codex execution edition."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

EXCLUDED_PARTS = {'.git', '.venv', '__pycache__', '.pytest_cache', 'node_modules',
                  '.runtime', 'dist', '.import'}
EXCLUDED_NAMES = {'runtime-state.json', '.setup.lock', '.env', '.env.local'}
EXCLUDED_ROOT_PARTS = {'reports', 'output', 'outputs', 'config', 'credentials',
                       '.config', '.cache', 'ms-playwright'}


def package_files(root):
    result = []
    for path in root.rglob('*'):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.parts[0] in EXCLUDED_ROOT_PARTS or relative.parts[0].startswith('.venv.'):
            continue
        if path.is_symlink():
            raise ValueError('Package source contains a symlink: ' + relative.as_posix())
        if path.is_file() and path.name not in EXCLUDED_NAMES and not path.name.startswith('.env.') and path.suffix not in {'.pyc', '.pyo'}:
            result.append(path)
    return sorted(result, key=lambda path: path.relative_to(root).parts)


def metadata(skill):
    text = skill.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('Invalid skill frontmatter: ' + str(skill))
    name_match = re.search(r'^name:\s*(.+)$', parts[1], re.M)
    match = re.search(r'^description:\s*(.*(?:\n(?![A-Za-z_-]+:).*)*)', parts[1], re.M)
    if not name_match or not match:
        raise ValueError('Missing skill metadata: ' + str(skill))
    name = name_match.group(1).strip().strip('"\'')
    description = ' '.join(match.group(1).strip().splitlines())
    if description.startswith('"'):
        description = json.loads(description)
    elif description.startswith("'"):
        description = description[1:-1].replace("''", "'")
    elif description.startswith(('>', '|')):
        description = description[1:].strip()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or not description:
        raise ValueError('Invalid skill identity: ' + str(skill))
    return name, description


def discover_skills(root, extensions=None):
    selected = {}
    for path in sorted((root / 'skills').glob('*/SKILL.md')):
        name, description = metadata(path)
        selected[name] = {'path': path, 'description': description, 'extension': None}
    for name in extension_names(root):
        directory = root / 'extensions' / name
        if extensions is not None and directory.name not in extensions:
            continue
        for path in sorted((directory / 'skills').glob('*/SKILL.md')):
            name, description = metadata(path)
            if name not in selected or extensions is not None:
                selected[name] = {'path': path, 'description': description, 'extension': directory.name}
    return selected


def extension_names(root):
    extensions = root / 'extensions'
    if not extensions.is_dir():
        return []
    return sorted(path.name for path in extensions.iterdir()
                  if path.is_dir() and not path.is_symlink()
                  and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.name))


def bridge_files(root, destination, skills):
    writes = {}
    for name, entry in sorted(skills.items()):
        folder = destination / name
        relative = Path(os.path.relpath(entry['path'], folder)).as_posix()
        text = ('---\nname: ' + json.dumps(name) + '\ndescription: ' +
                json.dumps(entry['description'], ensure_ascii=False) +
                '\nlicense: MIT\n---\n\n# Codex SEO workflow\n\n'
                'Read and follow the [complete workflow](' + relative + ') before acting.\n'
                'Resolve the runtime and references from that source file, preserving '
                'its package layout. Use available Codex tools and follow the evidence '
                'and authorization requirements in the complete workflow.\n')
        writes[folder / 'SKILL.md'] = text.encode('utf-8')
        ui = entry['path'].parent / 'agents/openai.yaml'
        if ui.is_file():
            writes[folder / 'agents/openai.yaml'] = ui.read_bytes()
        else:
            value = ('interface:\n  display_name: ' + json.dumps(name) +
                     '\n  short_description: ' + json.dumps(('SEO workflow: ' + name)[:64]) +
                     '\n  default_prompt: ' + json.dumps('Use $' + name + ' for this SEO task.') + '\n')
            writes[folder / 'agents/openai.yaml'] = value.encode('utf-8')
    return writes


def generate_bridges(root):
    skills = discover_skills(root)
    for path, data in bridge_files(root, root / 'codex-skills', skills).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return skills


def digest(data):
    return hashlib.sha256(data).hexdigest()
