#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
min_minor=11
max_minor=14
range_text="3.${min_minor} to 3.${max_minor}"

probe_version() {
  local version
  version="$("$@" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)" || return 1
  printf '%s' "${version%$'\r'}"
}

in_range() {
  [[ "$1" =~ ^3\.([0-9]+)$ ]] || return 1
  (( BASH_REMATCH[1] >= min_minor && BASH_REMATCH[1] <= max_minor ))
}

if [[ -n "${CODEX_SEO_PYTHON:-}" ]]; then
  found="$(probe_version "${CODEX_SEO_PYTHON}" || true)"
  if in_range "${found}"; then
    exec "${CODEX_SEO_PYTHON}" "$root/install-codex.py" "$@"
  fi
  echo "CODEX_SEO_PYTHON must be Python ${range_text}. Found ${found:-no usable Python}." >&2
  exit 2
fi

seen=""
script_args=("$@")
try_python() {
  local found
  command -v "$1" >/dev/null 2>&1 || return 1
  found="$(probe_version "$@")" || return 1
  if in_range "${found}"; then
    exec "$@" "$root/install-codex.py" "${script_args[@]+"${script_args[@]}"}"
  fi
  seen="${seen}${seen:+, }${found} ($*)"
  return 1
}

try_python py -3 || true
try_python python3 || true
try_python python || true
minor=${max_minor}
while (( minor >= min_minor )); do
  try_python py "-3.${minor}" || true
  try_python "python3.${minor}" || true
  minor=$(( minor - 1 ))
done

echo "Codex SEO needs Python ${range_text}. Found: ${seen:-no Python}. Set CODEX_SEO_PYTHON to a supported interpreter." >&2
exit 2
