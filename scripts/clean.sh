#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "$0")/.." && pwd)
rm -rf "$repo_root/paper/build"
rm -f "$repo_root/paper/value-grounded-ai-alignment.pdf"
find "$repo_root/paper/figures" -maxdepth 1 -type f -name '*.pdf' -delete
