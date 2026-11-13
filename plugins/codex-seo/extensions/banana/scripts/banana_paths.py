"""Codex-owned image output and configuration locations."""

import os
from pathlib import Path
import sys

CORE_SCRIPTS = Path(__file__).resolve().parents[3] / 'scripts'
if str(CORE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(CORE_SCRIPTS))
from codex_paths import config_dir


def output_dir() -> Path:
    value = os.environ.get('CODEX_SEO_OUTPUT_DIR') or os.environ.get('NANOBANANA_OUTPUT_DIR')
    return Path(value).expanduser().resolve() if value else Path.cwd() / 'reports' / 'images'


def banana_dir() -> Path:
    value = os.environ.get('CODEX_SEO_BANANA_HOME') or os.environ.get('BANANA_HOME')
    return Path(value).expanduser().resolve() if value else config_dir() / 'banana'
