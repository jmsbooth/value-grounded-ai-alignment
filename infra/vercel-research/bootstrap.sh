#!/usr/bin/env bash
# Run inside a Vercel sandbox. Does not provision resources or launch training.
set -euo pipefail
KIT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=${VGA_ROOT:-/vercel}
REV=${VGA_SOURCE_REVISION:-41d01730ca98430d282a06f089b0617d6351ab6b}
REPO="$ROOT/value-grounded-ai-alignment"
ENV="$ROOT/vga-env"
[[ "$REV" =~ ^[0-9a-f]{40}$ ]] || { echo 'An immutable source SHA is required' >&2; exit 2; }
command -v uv >/dev/null
command -v git >/dev/null
if [ ! -d "$REPO/.git" ]; then
  [ ! -e "$REPO" ] || { echo 'Refusing to overwrite existing non-git source directory' >&2; exit 2; }
  GIT_LFS_SKIP_SMUDGE=1 git clone --no-checkout --filter=blob:none https://github.com/jmsbooth/value-grounded-ai-alignment.git "$REPO"
  git -C "$REPO" fetch --depth 1 origin "$REV"
  git -C "$REPO" checkout --detach "$REV"
fi
[ "$(git -C "$REPO" rev-parse HEAD)" = "$REV" ] || { echo 'Existing checkout differs from requested SHA; do not reset it automatically' >&2; exit 2; }
git -C "$REPO" diff --quiet
git -C "$REPO" diff --cached --quiet
if [ ! -x "$ENV/bin/python" ]; then
  uv venv --python 3.13.16 "$ENV"
fi
"$ENV/bin/python" -c 'import platform; assert platform.python_version() == "3.13.16", "Unexpected Python runtime"'
uv pip sync --python "$ENV/bin/python" --index https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match "$KIT/requirements.lock"
export HF_HOME="$ROOT/vga-model-cache"
export HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1 TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
PYTHONPATH="$REPO/src" "$ENV/bin/python" "$KIT/prepare.py" --root "$ROOT" --source-revision "$REV" --download
printf '\nEnvironment ready. For future commands: source %s/vga-activate.sh\n' "$ROOT"
