#!/usr/bin/env python3
"""Inspect optional integrations and emit secret-free Codex MCP fragments.

This helper does not install packages, connect accounts, call providers, or
modify Codex settings. Review and merge emitted TOML in the intended Codex
project configuration when you choose to enable that provider.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

CATALOG_PATH = Path(__file__).with_name('codex-integrations.json')


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding='utf-8'))['providers']


def integration_plan(name: str) -> dict:
    providers = load_catalog()
    if name not in providers:
        raise ValueError('Unknown extension: ' + name)
    provider = providers[name]
    required = provider.get('required_environment', [])
    return {'extension': name, **provider,
            'environment_present': {key: bool(os.environ.get(key)) for key in required},
            'package_file_hints': {key: str((CATALOG_PATH.parent.parent / relative).resolve())
                                   for key, relative in provider.get('package_file_environment', {}).items()},
            'connected': 'not_checked', 'writes': False,
            'note': 'Environment presence is local readiness, not proof of provider authorization.'}


def mcp_toml(name: str) -> str:
    provider = load_catalog().get(name)
    if provider is None:
        raise ValueError('Unknown extension: ' + name)
    spec = provider.get('mcp')
    if spec is None:
        raise ValueError('This extension has no bundled MCP server: ' + name)
    quote = lambda value: json.dumps(value, ensure_ascii=True)
    lines = ['# Optional Codex MCP configuration. Credential values remain in the host environment.',
             '# Review this fragment before merging it into the intended Codex configuration.',
             '[mcp_servers.' + quote(spec['name']) + ']',
             'command = ' + quote(spec['command']),
             'args = ' + quote(spec['args']),
             'env_vars = ' + quote(spec.get('env_vars', []))]
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('list', 'plan', 'toml'))
    parser.add_argument('extension', nargs='?')
    parser.add_argument('--output', type=Path, help='Create a new TOML fragment file; existing files are never overwritten')
    args = parser.parse_args()
    if args.action == 'list':
        if args.output:
            parser.error('--output is supported only for toml')
        print(json.dumps(load_catalog(), indent=2))
        return 0
    if not args.extension:
        parser.error('An extension name is required')
    try:
        if args.action == 'plan':
            if args.output:
                parser.error('--output is supported only for toml')
            print(json.dumps(integration_plan(args.extension), indent=2))
        else:
            result = mcp_toml(args.extension)
            if args.output:
                target = args.output.expanduser().resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open('x', encoding='utf-8', newline='\n') as handle:
                    handle.write(result)
                print(json.dumps({'created': str(target), 'connected': False}))
            else:
                print(result, end='')
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error)}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
