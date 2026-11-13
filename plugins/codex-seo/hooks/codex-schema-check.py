#!/usr/bin/env python3
"""Read-only schema validation for Codex post-edit events or selected files.

The opt-in hook reads file paths from apply_patch headers or a file_path tool
argument. All event paths stay inside the session working directory. The
standalone command accepts explicitly selected paths. No hook is registered by
this script, and post-edit validation cannot undo an edit.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import sys

MAX_EVENT_BYTES = 2 * 1024 * 1024
MAX_FILE_BYTES = 10 * 1024 * 1024
EXTENSIONS = {'.html', '.htm', '.jsx', '.tsx', '.vue', '.svelte', '.php', '.ejs'}
PATCH_PATH = re.compile(r'^\*\*\* (?:Add File|Update File|Move to): (.+)$', re.MULTILINE)


def _validator():
    spec = importlib.util.spec_from_file_location('codex_schema_validator', Path(__file__).with_name('validate-schema.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate_jsonld


def event_paths(event: dict) -> list[Path]:
    root = Path(event.get('cwd') or os.getcwd()).resolve()
    tool = event.get('tool_input')
    if not isinstance(tool, dict):
        return []
    candidates = []
    if isinstance(tool.get('file_path'), str):
        candidates.append(tool['file_path'])
    if isinstance(tool.get('command'), str):
        candidates.extend(PATCH_PATH.findall(tool['command']))
    paths = []
    for candidate in candidates:
        if not candidate or '\0' in candidate:
            continue
        path = Path(candidate)
        if not path.is_absolute():
            path = root / path
        try:
            path = path.resolve()
            path.relative_to(root)
        except (OSError, ValueError):
            continue
        if path not in paths and path.suffix.lower() in EXTENSIONS and path.is_file():
            paths.append(path)
    return paths


def inspect_paths(paths: list[Path]) -> tuple[list[str], list[str]]:
    validate = _validator()
    critical, warnings = [], []
    for path in paths:
        if path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                warnings.append(str(path) + ': skipped because the file exceeds the 10 MiB review limit')
                continue
            content = path.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for error in validate(content, str(path)):
            bucket = critical if any(word in error.lower() for word in ('placeholder', 'deprecated', 'retired')) else warnings
            bucket.append(error)
    return critical, warnings


def main() -> int:
    try:
        if len(sys.argv) > 1:
            paths = [Path(value).expanduser().resolve() for value in sys.argv[1:]]
        else:
            raw = sys.stdin.read(MAX_EVENT_BYTES + 1)
            if len(raw.encode('utf-8')) > MAX_EVENT_BYTES:
                raise ValueError('Codex hook event exceeds the 2 MiB limit')
            event = json.loads(raw) if raw.strip() else {}
            if not isinstance(event, dict):
                raise ValueError('Codex hook event must be an object')
            paths = event_paths(event)
        critical, warnings = inspect_paths(paths)
    except (OSError, ValueError) as error:
        print(json.dumps({'systemMessage': 'Schema review could not run: ' + str(error)}))
        return 0
    messages = critical + warnings
    if not messages:
        return 0
    context = 'Schema validation findings:\n' + '\n'.join('- ' + message for message in messages)
    output = {'hookSpecificOutput': {'hookEventName': 'PostToolUse', 'additionalContext': context}}
    if critical:
        output.update({'decision': 'block', 'reason': context})
    print(json.dumps(output))
    return 2 if critical else 0


if __name__ == '__main__':
    raise SystemExit(main())
