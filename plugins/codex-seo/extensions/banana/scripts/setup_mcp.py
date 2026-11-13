#!/usr/bin/env python3
"""Print a secret-free Banana MCP configuration plan for Codex.

The host forwards GOOGLE_AI_API_KEY from its own environment. This command
never reads or writes another assistant's configuration and never connects an
account. --output creates a new TOML fragment for review; --check reports local
readiness without making network requests.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

MCP_NAME = 'nanobanana-mcp'
MCP_PACKAGE = '@ycse/nanobanana-mcp@1.1.1'


def _tools():
    path = Path(__file__).resolve().parents[2] / 'codex-extension.py'
    spec = importlib.util.spec_from_file_location('codex_extension_tools', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readiness() -> dict:
    return {'provider': 'banana', 'connected': 'not_checked', 'writes': False,
            'api_key_present': bool(os.environ.get('GOOGLE_AI_API_KEY') or os.environ.get('GOOGLE_API_KEY')),
            'npx_present': shutil.which('npx') is not None,
            'model_selected': bool(os.environ.get('NANOBANANA_MODEL')),
            'note': 'MCP can use its package default model. Direct REST calls require a selected model.'}


def check_setup() -> bool:
    report = readiness()
    print(json.dumps(report, indent=2))
    return report['api_key_present'] and report['npx_present']


def setup_mcp(api_key: str | None = None, output: Path | None = None) -> str:
    # The compatibility argument is deliberately never written or echoed.
    fragment = _tools().mcp_toml('banana')
    if output is not None:
        target = output.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(fragment)
        print(json.dumps({'created': str(target), 'connected': False}))
    else:
        print(fragment, end='')
    return fragment


def remove_mcp() -> None:
    print(json.dumps({'writes': False, 'connected': 'not_checked',
                      'instruction': 'Remove only the reviewed nanobanana-mcp entry from your intended Codex configuration.'}))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--remove', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--key', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.key is not None:
        parser.error('Pass credentials through the host environment, not --key. No key was saved.')
    if args.check:
        return 0 if check_setup() else 1
    if args.remove:
        remove_mcp()
        return 0
    try:
        setup_mcp(output=args.output)
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
