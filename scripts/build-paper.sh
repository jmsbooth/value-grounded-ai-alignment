#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
paper_dir="$repo_root/paper"
build_dir="$paper_dir/build"
mkdir -p "$build_dir"

if command -v latexmk >/dev/null 2>&1; then
  (
    cd "$paper_dir"
    latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
  )
else
  compile_script="${LATEX_COMPILE_SCRIPT:-/Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6/scripts/compile_latex.py}"
  if [[ ! -f "$compile_script" ]]; then
    echo "latexmk is unavailable and the bundled LaTeX compile script was not found." >&2
    exit 1
  fi
  python3 "$compile_script" "$paper_dir/main.tex" --compiler tectonic --output-directory "$build_dir" --json
fi

if [[ ! -f "$build_dir/main.pdf" ]]; then
  echo "LaTeX completed without producing $build_dir/main.pdf" >&2
  exit 1
fi
cp "$build_dir/main.pdf" "$paper_dir/value-grounded-ai-alignment.pdf"
