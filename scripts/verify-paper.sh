#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
cd "$repo_root"

PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m unittest discover -s tests -v
python3 experiments/run_toy_evaluation.py --json >/dev/null
PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" python3 experiments/evaluation/run_empirical_small.py --smoke >/dev/null

pdf="paper/value-grounded-ai-alignment.pdf"
log="paper/build/main.log"
if [[ ! -s "$pdf" ]]; then
  echo "Expected paper PDF is missing: $pdf" >&2
  exit 1
fi

if [[ -f "$log" ]] && rg -n -i 'undefined references|undefined citations|multiply defined|fatal error|^! ' "$log"; then
  echo "LaTeX verification found unresolved or fatal diagnostics." >&2
  exit 1
fi

echo "Verified Python scaffold, deterministic synthetic evaluation, and $pdf."
