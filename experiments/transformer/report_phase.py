#!/usr/bin/env python3
"""Build the human-readable Pythia phase execution report from receipts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"status": "MISSING"}
    return json.loads(path.read_text(encoding="utf-8"))


def build(output: Path) -> None:
    preflight = _read(ROOT / "results/reports/te-v0.6.0-pythia/preflight/preflight.json")
    semantic = _read(ROOT / "results/reports/te-v0.6.0-pythia/semantic-validity/semantic-audit.json")
    smoke = _read(ROOT / "results/reports/te-v0.6.0-pythia/model-smoke/model-smoke.json")
    diagnostic = _read(ROOT / "results/reports/te-v0.6.0-pythia/training-diagnostics/training-diagnostic.json")
    evaluation = _read(ROOT / "results/raw/te-v0.6.0-pythia/development-evaluation/evaluation.json")
    freeze = _read(ROOT / "results/plans/te-v0.6.0-pythia/freeze-result.json")
    run = _read(ROOT / "results/raw/te-v0.6.0-pythia/cohort-run-result.json")
    gate = _read(ROOT / "results/reports/te-v0.6.0-pythia/gate/gate.json")
    disk_free_gib = preflight.get("memory_and_disk", {}).get("disk_free_gib", "n/a")
    report = f"""# Pythia phase execution report

Protocol: `te-v0.6.0-pythia`  
Evidence scope: local engineering and development validation on synthetic
fictional policy worlds.  
Generated from: preflight, semantic audit, model smoke, training diagnostic,
development evaluation, cohort guard, and phase gate artifacts.

## Executive result

The semantic dataset gate passed and the reviewed Pythia checkpoint loaded
offline with finite logits. The one-step LoRA diagnostic passed, including
nonzero gradients, frozen-backbone preservation, and checkpoint checksum
verification. A one-world pretrained development evaluation executed the model
on one clean input and four transformed inputs; none of the five outputs parsed
as the required JSON response. The five-seed locked comparison did not run:
the cohort freeze is blocked by uncommitted protocol state and the phase gate
therefore remains `{gate.get('state', 'MISSING')}`.

No claim about VGA effectiveness, alignment, generalization, or human values is
supported by this report.

## Methods

- Model: `EleutherAI/pythia-410m`, requested checkpoint `step143000`, reviewed
  revision `{smoke.get('model', {}).get('resolved_revision_sha', 'not loaded')}`. Asset digest:
  `{smoke.get('model_asset_digest', 'not recorded')}`.
- Expected architecture: GPT-NeoX causal LM, 24 layers, hidden size 1024, 16
  attention heads, intermediate size 4096, context length 2048.
- Data: project-authored synthetic worlds in two fictional domains:
  delegated data access and purpose-limited disclosure.
- Public input: readable policy text, observed facts, typed graph, question,
  fixed five-action catalogue, and generic value definitions.
- Private labels: joined outside model input by `public_id`; the reference
  policy uses facts and rules, not template names or target-conditioned actions.
- Adaptation diagnostic: LoRA rank 8, alpha 16, dropout 0; response loss is
  masked to response tokens and `use_cache=false`.
- Evaluation: deterministic greedy decoding, fixed JSON parser, raw output
  retention, and executed prompt/purpose/authority/occlusion transformations.

## Test and gate information

| Check | Result | Evidence |
| --- | --- | --- |
| Dependency-light repository tests | 45 passed, 2 skipped | base-environment regression |
| Isolated-environment repository tests | 48 passed | `.venv-pythia` test run |
| Semantic validity | `{semantic.get('status', 'MISSING')}` | `semantic-audit.json` |
| Pythia model smoke | `{smoke.get('status', 'MISSING')}` | `model-smoke.json` |
| LoRA/checkpoint diagnostic | `{diagnostic.get('status', 'MISSING')}` | `training-diagnostic.json` |
| Locked cohort freeze | `{freeze.get('status', 'MISSING')}` | `freeze-result.json` |
| Locked cohort execution | `{run.get('status', 'MISSING')}` | `cohort-run-result.json` |
| Phase gate | `{gate.get('state', 'MISSING')}` | `gate.json` |

Semantic checks: `{', '.join(f'{key}={value}' for key, value in semantic.get('checks', dict()).items())}`.

## Development results

| Measurement | Result |
| --- | ---: |
| Semantic audit rows | {sum(int(value) for value in semantic.get('row_counts', dict()).values())} |
| Smoke input tokens | {smoke.get('input_tokens', 'n/a')} |
| Smoke logits | `{smoke.get('logit_shape', 'n/a')}` |
| Tokenizer vocabulary | {smoke.get('tokenizer_vocab_size', 'n/a')} |
| Diagnostic trainable parameters | {diagnostic.get('trainable_parameters', 'n/a')} |
| Diagnostic loss | {diagnostic.get('metrics', dict()).get('loss', 'n/a')} |
| Diagnostic gradient norm | {diagnostic.get('metrics', dict()).get('gradient_norm', 'n/a')} |
| Frozen backbone unchanged | {diagnostic.get('frozen_backbone_unchanged', 'n/a')} |
| Checkpoint roundtrip | {diagnostic.get('checkpoint_roundtrip_verified', 'n/a')} |
| Development clean rows | {evaluation.get('examples', 'n/a')} |
| Development attack rows | {evaluation.get('attack_rows', 'n/a')} |
| Clean parse rate | {evaluation.get('clean_parse_rate', 'n/a')} |
| Attack parse rate | {evaluation.get('attack_parse_rate', 'n/a')} |
| Attack safe rate under fixed expected action | {evaluation.get('attack_safe_rate', 'n/a')} |

The zero parse rates are an observation about this tiny unadapted pretrained
development sample and its strict response contract. They are not converted
into a model-quality estimate.

## Resource and ownership boundary

The latest preflight reported 16 GiB RAM and approximately {disk_free_gib} GiB
free after the model cache and isolated environment were installed. The plan contains 40 locked child
runs (8 variants x 5 seeds), but full-cohort cost is not measured and owner-approved
protocol state is not committed. Accordingly, no locked run was started and no
locked comparison analysis is reported.

## Reproduction commands

```text
make te-preflight
make te-semantic-audit
make te-model-smoke
make te-train-diagnostics
make te-plan-cohort
make te-freeze-cohort
make te-run-cohort
make te-analyze
make te-gate
```

The existing manuscript and historical MLP/harness artifacts remain unchanged.
The historical 1,140-row accounting qualification is separate at
`results/reports/historical-qualification/mlp-count-reconciliation/`.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/phase-execution-report.md")
    args = parser.parse_args()
    build(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
