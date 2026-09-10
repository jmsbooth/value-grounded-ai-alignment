# Pythia phase execution report

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
therefore remains `SEMANTIC_DATASET_VALIDATED`.

No claim about VGA effectiveness, alignment, generalization, or human values is
supported by this report.

## Methods

- Model: `EleutherAI/pythia-410m`, requested checkpoint `step143000`, reviewed
  revision `bba6a464f54bbf08fc174cfb351d9794d58af21d`. Asset digest:
  `d65a3c37a54360759a43bcb05b80df1ddbb982ed0a1d2b97bb67746d5c07a9c7`.
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
| Dependency-light repository tests | 44 passed, 2 skipped | `make te-ci` before optional environment |
| Isolated-environment repository tests | 47 passed | `.venv-pythia` test run |
| Semantic validity | `SEMANTIC_DATASET_VALIDATED` | `semantic-audit.json` |
| Pythia model smoke | `PYTHIA_INTEGRATION_VALIDATED` | `model-smoke.json` |
| LoRA/checkpoint diagnostic | `PYTHIA_TRAINING_DIAGNOSTIC_PASSED` | `training-diagnostic.json` |
| Locked cohort freeze | `COHORT_FREEZE_BLOCKED` | `freeze-result.json` |
| Locked cohort execution | `LOCKED_RUN_NOT_STARTED` | `cohort-run-result.json` |
| Phase gate | `SEMANTIC_DATASET_VALIDATED` | `gate.json` |

Semantic checks: `facts_change_outcome=True, fixed_action_catalogue=True, graph_edge_reordering_invariant=True, public_label_isolation=True, semantic_outcomes_present=True, split_group_disjointness=True, template_permutation_invariance=True`.

## Development results

| Measurement | Result |
| --- | ---: |
| Semantic audit rows | 36 |
| Smoke input tokens | 14 |
| Smoke logits | `[1, 14, 50304]` |
| Tokenizer vocabulary | 50277 |
| Diagnostic trainable parameters | 3165203 |
| Diagnostic loss | 2.4762542247772217 |
| Diagnostic gradient norm | 11.347464561462402 |
| Frozen backbone unchanged | True |
| Checkpoint roundtrip | True |
| Development clean rows | 1 |
| Development attack rows | 4 |
| Clean parse rate | 0.0 |
| Attack parse rate | 0.0 |
| Attack safe rate under fixed expected action | 0.0 |

The zero parse rates are an observation about this tiny unadapted pretrained
development sample and its strict response contract. They are not converted
into a model-quality estimate.

## Resource and ownership boundary

The latest preflight reported 16 GiB RAM and approximately 9.121 GiB
free after the model cache and isolated environment were installed. The plan contains 40 locked child
runs (8 variants x 5 seeds), but cost is not measured and owner-approved
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
