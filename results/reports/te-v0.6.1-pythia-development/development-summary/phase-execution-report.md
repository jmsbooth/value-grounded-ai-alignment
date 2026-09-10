# Value-Grounded AI Alignment: Pythia development report

Protocol: `te-v0.6.1-pythia-development`  
Evidence scope: bounded local development on project-authored synthetic and fictional policy worlds.  
Locked comparison: **not run and not authorized by this protocol**.

## Executive result

This phase executed the v0.6.1 development path beyond the earlier one-step
diagnostic. The real pinned Pythia-410M checkpoint was used for resource
measurement, response-contract training, task-SFT development, and the
variant smoke path. The v2 mini benchmark passed the structural and semantic
validation checks. The readiness state is `DEVELOPMENT_NOT_READY_FOR_COHORT_REVIEW`.

The result separates implementation evidence from model quality. It does not
support a claim that VGA improves alignment, discovers moral truth, or
generalizes beyond this synthetic development fixture.

## Identities and protected boundary

- Model: `EleutherAI/pythia-410m`, requested
  `step143000`, resolved
  `bba6a464f54bbf08fc174cfb351d9794d58af21d`; asset
  digest `d65a3c37a54360759a43bcb05b80df1ddbb982ed0a1d2b97bb67746d5c07a9c7`.
- Starting commit: `7aa20ea115239bab646225b63642693590ec0d4d`; branch
  `main`; development source state was
  dirty and captured by the preflight patch and untracked-source digests.
- Dataset: `pythia-policy-dev-v2`, mini profile, 64 train / 16 validation /
  16 calibration / 16 open-development groups. No locked v2 split was
  materialized, read, or scored. The existing v1 fixture and its historical
  locked files were preserved.
- Protected paper tree digest at preflight:
  `dc705ae0b8693dcb75679ad41c67a1289122f37a6c54c76743f3f6db8f99794b`.

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
| WP0 preflight | `PREFLIGHT_RECORDED` | `docs/experiments/te-v0.6.1-pythia-development/preflight.json` |
| WP1 historical output audit | `HISTORICAL_GENERATIONS_AUDITED` | 5 parent rows audited; raw strings present but token-level metadata incomplete |
| WP2 training contracts | `TRAINING_CONTRACT_VALIDATED` | 20 isolated-environment parser/training tests |
| WP3 resource profile | `RESOURCE_PROFILE_MEASURED` | `122.52551862504333` seconds; peak `2.4218` GiB RSS; checkpoint round trip `True` |
| WP4 memorization | `['A1_MEMORIZATION_CRITERION_NOT_MET', 'A1_MEMORIZATION_CRITERION_NOT_MET']` | `48` scheduled generated outputs |
| WP5 v2 benchmark | `DEVELOPMENT_BENCHMARK_VALIDATED` | `{'calibration': 16, 'open-dev': 16, 'train': 64, 'validation': 16}` rows; all semantic checks `True` |
| WP6 A1 development | `['A1_DEVELOPMENT_TRAINING_COMPLETE', 'A1_DEVELOPMENT_TRAINING_COMPLETE']` | `[24, 24]` updates; selected checkpoints recorded |
| WP7 variant smoke | `VARIANT_SMOKE_PARTIAL` | `16 / 16` child attempts |
| WP8 trained output/attacks | `TRAINED_OUTPUT_ATTACK_AUDIT_COMPLETE` | paired clean/attack output path `16` / `64` |

## Objective test output

- Historical parent generations: the five local raw strings were classified
  under the frozen two-stage taxonomy. Prompt token IDs, generated IDs, and
  effective caps were absent from the parent artifact and remain explicitly
  missing; no historical output was invented.
- Strict parser/extraction and training contract suite: `20 passed, 1 warning in 4.16s`.
- Dataset checks: `{"action_catalogue_has_five_classes": true, "calibration_and_open_dev_not_training": true, "calibration_files_present": true, "canonical_graph_reordering_invariant": true, "different_render_same_world_same_result": true, "exact_natural_duplicates_absent": true, "exact_profile_counts": true, "group_disjointness": true, "independent_domains": true, "locked_split_not_materialized": true, "majority_baseline_is_reported_not_used_for_tuning": true, "missing_evidence_is_not_negative_evidence": true, "open-dev_files_present": true, "oracle_matches_materialized_annotations": true, "private_label_isolation": true, "public_schema_and_catalogue": true, "same_template_different_facts_change_result": true, "train_files_present": true, "validation_files_present": true}`.
- Real resource profile measured five updates after two warmups, two 256-token
  generation attempts, and a checkpoint save/reload. The two generations hit
  the cap, which is retained as a stop reason rather than treated as a causal
  explanation for parser failure.

## Training and model results

### Eight-example memorization

The fixed memorization set covers both domains and all five feasible public
action classes in this v2 construction. Seeds: `[11, 23]`.
The criterion is `['A1_MEMORIZATION_CRITERION_NOT_MET', 'A1_MEMORIZATION_CRITERION_NOT_MET']`;
this is a generated-output criterion, not a loss-only result. Every attempt,
curve, checkpoint, and scheduled raw output is retained under its exact run
directory.

### Held-out A1 development

The prospective local schedule was 24 optimizer updates: three complete passes
over 64 training examples at effective batch 8, selected after the measured
resource profile. Validation selection used the lowest mean response NLL with
earlier-update tie breaking; open development was evaluated only after
selection. Per-seed strict schema rates were `[0.0, 0.0]`; end-to-end task
rates were `[0.0, 0.0]`; each denominator was 16 independent open-development
groups. `A1_FORMAT_READY` is therefore `False`.
These rates are development observations, not population estimates.

### Variant smoke

The intended eight-arm design was attempted with real model loads, fresh seed
initialization, response training, checkpoint verification/reload, and the
same eight-world open-development slice. The prospective resource amendment
selected `[4]` updates per arm/seed for engineering smoke.
`4` of `16` attempts completed; the
remaining `12` attempts failed at the MPS shared-memory
watermark before an update. Active auxiliary heads and allocated, updated
adapter/head parameter counts are stored per completed attempt. Sham labels use
fixed seed-derived training-only rotations. This is not a learning comparison
and its small smoke scores do not test H1–H10.

## Clean, attack, calibration, and capability measurements

The selected A1 checkpoint attack result is `TRAINED_OUTPUT_ATTACK_AUDIT_COMPLETE`.
Where present, attack denominators, conditional clean-correct/permitted
eligibility, format disruption, task disruption, and malformed/unassessable
outputs are stored separately in its result JSON. A zero eligible denominator
is `not_estimable`, never fabricated as zero success. Calibration and the
capability sentinel are `not_measured` in this bounded phase.

Malformed output is incomplete and does not automatically count as a prohibited
semantic action. Mock enforcement blocks malformed/unpermitted output
fail-closed; that enforcement result is not model-safety evidence.

## Resources and later-cohort estimate

Observed representative C2 profile: `122.52551862504333` seconds
including loading and checkpointing, peak process RSS `2.4218`
GiB, disk free afterward `6.409` GiB. The
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
{
  "A1_DEVELOPMENT_TRAINING_COMPLETE": true,
  "A1_FORMAT_READY": false,
  "A1_MEMORIZATION_CRITERION_MET": false,
  "AUXILIARY_BACKPROP_VALIDATED": true,
  "DEVELOPMENT_BENCHMARK_VALIDATED": true,
  "DEVELOPMENT_READY_FOR_COHORT_REVIEW": false,
  "OUTPUT_PATH_AUDITED": true,
  "RESOURCE_PLAN_MEASURED": true,
  "TRAINING_CONTRACT_VALIDATED": true,
  "VARIANT_SMOKE_COMPLETE": false
}
```

Readiness: `DEVELOPMENT_NOT_READY_FOR_COHORT_REVIEW`. Policy skill status:
`BASELINE_POLICY_SKILL_LIMITED`. Next decision: Do not request a locked cohort. Review the failed engineering/model gate, preserve all attempts, and either investigate a named defect or open a separately budgeted development attempt..

No manuscript revision, publication, OLMo run, locked 40-run launch, paid
compute, upload, or push was performed. Existing historical artifacts remain
separate and unchanged.
