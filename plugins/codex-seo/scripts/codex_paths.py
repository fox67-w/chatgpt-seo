"""Codex-specific credential and cache locations shared by SEO helpers."""

from __future__ import annotations

import os
from pathlib import Path


def _configured(name: str, legacy: str | None = None) -> Path | None:
    value = os.environ.get(name)
    if value is None and legacy:
        value = os.environ.get(legacy)
    return Path(value).expanduser().resolve() if value else None


def config_dir() -> Path:
    override = _configured("CODEX_SEO_CONFIG_DIR", "CLAUDE_SEO_CONFIG_DIR")
    if override is not None:
        return override
    portable = _configured("CODEX_SEO_DATA_DIR")
    if portable is not None:
        return portable / "config"
    base = _configured("XDG_CONFIG_HOME") or Path.home() / ".config"
    return base / "codex-seo"


def cache_dir() -> Path:
    override = _configured("CODEX_SEO_CACHE_DIR")
    if override is not None:
        return override
    portable = _configured("CODEX_SEO_DATA_DIR")
    if portable is not None:
        return portable / "cache"
    base = _configured("XDG_CACHE_HOME") or Path.home() / ".cache"
    return base / "codex-seo"
