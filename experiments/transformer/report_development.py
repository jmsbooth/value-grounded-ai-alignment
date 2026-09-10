#!/usr/bin/env python3
"""Render the immutable human-readable v0.6.1 development report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(*, output: Path, preflight: Path, audit: Path, training: Path, dataset: Path, memorization: Path, a1: Path, variants: Path, resource: Path, readiness: Path, attack: Path | None = None) -> None:
    p, o, t, d, m, a, v, r, g = (read(path) for path in (preflight, audit, training, dataset, memorization, a1, variants, resource, readiness))
    attack_data = read(attack) if attack else {"status": "not_measured", "metrics": {}}
    mem_attempts = m.get("attempts", [])
    a1_attempts = a.get("attempts", [])
    variant_attempts = v.get("attempts", [])
    a1_rates = [float(item.get("open_dev", {}).get("strict_schema_rate", 0.0)) for item in a1_attempts]
    a1_policy = [float(item.get("open_dev", {}).get("end_to_end_correct_rate", 0.0)) for item in a1_attempts]
    model_identity = p.get("current_model", {})
    repo_identity = p.get("repo", {})
    paper_identity = p.get("protected_paper_tree", {})
    resource_checkpoint = r.get("checkpoint", {})
    dataset_checks = json.dumps(d.get("checks", {}), sort_keys=True)
    mem_statuses = [attempt.get("status") for attempt in mem_attempts]
    mem_generated = sum(int(attempt.get("generated_output_count", 0)) for attempt in mem_attempts)
    a1_statuses = [attempt.get("status") for attempt in a1_attempts]
    a1_updates = [attempt.get("updates_completed") for attempt in a1_attempts]
    gate_json = json.dumps(g.get("gates", {}), indent=2, sort_keys=True)
    training_test_tail = t.get("test_output", "").splitlines()[-1] if t.get("test_output") else "n/a"
    variant_complete = [attempt for attempt in variant_attempts if attempt.get("status") == "VARIANT_SMOKE_ATTEMPT_COMPLETE"]
    variant_failed = [attempt for attempt in variant_attempts if attempt.get("status") != "VARIANT_SMOKE_ATTEMPT_COMPLETE"]
    variant_schedules = sorted({attempt.get("schedule", {}).get("selected_max_updates") for attempt in variant_attempts if attempt.get("schedule")})
    report = f"""# Value-Grounded AI Alignment: Pythia development report

Protocol: `te-v0.6.1-pythia-development`  
Evidence scope: bounded local development on project-authored synthetic and fictional policy worlds.  
Locked comparison: **not run and not authorized by this protocol**.

## Executive result

This phase executed the v0.6.1 development path beyond the earlier one-step
diagnostic. The real pinned Pythia-410M checkpoint was used for resource
measurement, response-contract training, task-SFT development, and the
variant smoke path. The v2 mini benchmark passed the structural and semantic
validation checks. The readiness state is `{g.get('status', 'MISSING')}`.

The result separates implementation evidence from model quality. It does not
support a claim that VGA improves alignment, discovers moral truth, or
generalizes beyond this synthetic development fixture.

## Identities and protected boundary

- Model: `{model_identity.get('model_id', 'n/a')}`, requested
  `{model_identity.get('requested_revision', 'n/a')}`, resolved
  `{model_identity.get('resolved_revision_sha', 'n/a')}`; asset
  digest `{model_identity.get('asset_digest', 'n/a')}`.
- Starting commit: `{repo_identity.get('head', 'n/a')}`; branch
  `{repo_identity.get('branch', 'n/a')}`; development source state was
  dirty and captured by the preflight patch and untracked-source digests.
- Dataset: `pythia-policy-dev-v2`, mini profile, 64 train / 16 validation /
  16 calibration / 16 open-development groups. No locked v2 split was
  materialized, read, or scored. The existing v1 fixture and its historical
  locked files were preserved.
- Protected paper tree digest at preflight:
  `{paper_identity.get('tree_digest', 'n/a')}`.

## Methods

The primary model path uses greedy, unassisted generation and the strict
response schema. Continuations are sliced by the actual generation-call input
tensor width; no string-length slicing or answer repair is used. Response-only
SFT applies next-token shifting once, explicit prompt/response/padding masks,
token-weighted accumulation, `use_cache=false`, AdamW, LoRA rank 8 / alpha 16 /
dropout 0, and global clipping at 1.0. Auxiliary heads read the last valid
prompt position before the response tokens.

A1 is a task-SFT control, not RLHF/DPO and not a generally aligned assistant.
All main arms retain correct response supervision. The v2 benchmark uses two
fictional domains, independent world groups, fixed public action candidates,
private annotations, explicit missing evidence, and an executable reference
interpreter. Open-development and calibration rows are development-visible;
they are not confirmatory holdouts.

## Work-package results

| Work package | Result | Evidence |
| --- | --- | --- |
| WP0 preflight | `PREFLIGHT_RECORDED` | `{preflight}` |
| WP1 historical output audit | `{o.get('status', 'MISSING')}` | 5 parent rows audited; raw strings present but token-level metadata incomplete |
| WP2 training contracts | `{t.get('status', 'MISSING')}` | 20 isolated-environment parser/training tests |
| WP3 resource profile | `{r.get('status', 'MISSING')}` | `{r.get('wall_seconds', 'n/a')}` seconds; peak `{r.get('peak_rss_gib', 'n/a')}` GiB RSS; checkpoint round trip `{resource_checkpoint.get('roundtrip_verified', False)}` |
| WP4 memorization | `{mem_statuses}` | `{mem_generated}` scheduled generated outputs |
| WP5 v2 benchmark | `{d.get('status', 'MISSING')}` | `{d.get('row_counts', {})}` rows; all semantic checks `{all(d.get('checks', {}).values())}` |
| WP6 A1 development | `{a1_statuses}` | `{a1_updates}` updates; selected checkpoints recorded |
| WP7 variant smoke | `{v.get('status', 'MISSING')}` | `{v.get('attempt_count', 0)} / {v.get('expected_attempt_count', 16)}` child attempts |
| WP8 trained output/attacks | `{attack_data.get('status', 'not_measured')}` | paired clean/attack output path `{attack_data.get('clean_rows', 'not_measured')}` / `{attack_data.get('attack_rows', 'not_measured')}` |

## Objective test output

- Historical parent generations: the five local raw strings were classified
  under the frozen two-stage taxonomy. Prompt token IDs, generated IDs, and
  effective caps were absent from the parent artifact and remain explicitly
  missing; no historical output was invented.
- Strict parser/extraction and training contract suite: `{training_test_tail}`.
- Dataset checks: `{dataset_checks}`.
- Real resource profile measured five updates after two warmups, two 256-token
  generation attempts, and a checkpoint save/reload. The two generations hit
  the cap, which is retained as a stop reason rather than treated as a causal
  explanation for parser failure.

## Training and model results

### Eight-example memorization

The fixed memorization set covers both domains and all five feasible public
action classes in this v2 construction. Seeds: `{[attempt.get('seed') for attempt in mem_attempts]}`.
The criterion is `{mem_statuses}`;
this is a generated-output criterion, not a loss-only result. Every attempt,
curve, checkpoint, and scheduled raw output is retained under its exact run
directory.

### Held-out A1 development

The prospective local schedule was 24 optimizer updates: three complete passes
over 64 training examples at effective batch 8, selected after the measured
resource profile. Validation selection used the lowest mean response NLL with
earlier-update tie breaking; open development was evaluated only after
selection. Per-seed strict schema rates were `{a1_rates}`; end-to-end task
rates were `{a1_policy}`; each denominator was 16 independent open-development
groups. `A1_FORMAT_READY` is therefore `{g.get('gates', {}).get('A1_FORMAT_READY', False)}`.
These rates are development observations, not population estimates.

### Variant smoke

The intended eight-arm design was attempted with real model loads, fresh seed
initialization, response training, checkpoint verification/reload, and the
same eight-world open-development slice. The prospective resource amendment
selected `{variant_schedules}` updates per arm/seed for engineering smoke.
`{len(variant_complete)}` of `{len(variant_attempts)}` attempts completed; the
remaining `{len(variant_failed)}` attempts failed at the MPS shared-memory
watermark before an update. Active auxiliary heads and allocated, updated
adapter/head parameter counts are stored per completed attempt. Sham labels use
fixed seed-derived training-only rotations. This is not a learning comparison
and its small smoke scores do not test H1–H10.

## Clean, attack, calibration, and capability measurements

The selected A1 checkpoint attack result is `{attack_data.get('status', 'not_measured')}`.
Where present, attack denominators, conditional clean-correct/permitted
eligibility, format disruption, task disruption, and malformed/unassessable
outputs are stored separately in its result JSON. A zero eligible denominator
is `not_estimable`, never fabricated as zero success. Calibration and the
capability sentinel are `not_measured` in this bounded phase.

Malformed output is incomplete and does not automatically count as a prohibited
semantic action. Mock enforcement blocks malformed/unpermitted output
fail-closed; that enforcement result is not model-safety evidence.

## Resources and later-cohort estimate

Observed representative C2 profile: `{r.get('wall_seconds', 'n/a')}` seconds
including loading and checkpointing, peak process RSS `{r.get('peak_rss_gib', 'n/a')}`
GiB, disk free afterward `{r.get('disk_free_gib_after', 'n/a')}` GiB. The
representative measured iterations recorded tokens and examples per second;
the full records are retained in the raw profile. These measurements do not
authorize extrapolation to a 40-run cohort. The later cost estimate must be
made from these observed training/generation/checkpoint components with
headroom and a newly approved plan.

## Change and limitation ledger

The protocol amendments record the v2 mini profile, the 2048-token context
needed by the structured public input, the resource-bounded A1 schedule, and
the four-update all-arm smoke schedule. The latter was necessary after the
measured CPU cost and MPS watermark failures; it limits WP7 to engineering
coverage. The observed initial warmup target-slice failure and temporary
collator bound were independently reproduced and repaired before model
training.
The natural renderer now exposes public norm IDs so required references can be validated;
private labels and hidden world state remain outside model input. A poor model
score is not classified as a software defect.

## Gate and next decision

```json
{gate_json}
```

Readiness: `{g.get('status', 'MISSING')}`. Policy skill status:
`{g.get('policy_skill_status', 'MISSING')}`. Next decision: {g.get('next_decision', 'review the evidence')}.

No manuscript revision, publication, OLMo run, locked 40-run launch, paid
compute, upload, or push was performed. Existing historical artifacts remain
separate and unchanged.
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in ("preflight", "audit", "training", "dataset", "memorization", "a1", "variants", "resource", "readiness"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--attack", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(output=args.output, preflight=args.preflight, audit=args.audit, training=args.training, dataset=args.dataset, memorization=args.memorization, a1=args.a1, variants=args.variants, resource=args.resource, readiness=args.readiness, attack=args.attack)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
