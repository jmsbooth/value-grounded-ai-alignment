#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
figure_dir="$repo_root/paper/figures"
tectonic_bin="${TECTONIC_BIN:-/Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6/bin/tectonic}"

if ! command -v tectonic >/dev/null 2>&1; then
  if [[ ! -x "$tectonic_bin" ]]; then
    echo "Tectonic is required to build the editable vector figures." >&2
    exit 1
  fi
  tectonic_bin="$tectonic_bin"
else
  tectonic_bin="$(command -v tectonic)"
fi

for source in "$figure_dir"/*.tex; do
  "$tectonic_bin" -X compile --outdir "$figure_dir" --outfmt pdf --untrusted "$source" >/dev/null
done
