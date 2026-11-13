#!/usr/bin/env bash
set -euo pipefail
# Codex extension activation is project-scoped and defaults to a dry run.
plugin_root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
if [[ -n "${CODEX_SEO_PYTHON:-}" ]]; then
    python_cmd=("${CODEX_SEO_PYTHON}")
elif command -v python3 >/dev/null 2>&1; then
    python_cmd=(python3)
elif command -v python >/dev/null 2>&1; then
    python_cmd=(python)
elif command -v py >/dev/null 2>&1; then
    python_cmd=(py -3)
else
    echo "Python 3.11 or newer is required. Set CODEX_SEO_PYTHON to its executable." >&2
    exit 2
fi
exec "${python_cmd[@]}" "${plugin_root}/install-codex.py" --extension matomo --remove "$@"
