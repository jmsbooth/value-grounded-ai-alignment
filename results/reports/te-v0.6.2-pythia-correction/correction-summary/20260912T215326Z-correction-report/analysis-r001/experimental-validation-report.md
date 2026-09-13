# v0.6.2 Pythia correction and bounded retest report

This report is artifact-linked and conservative. It distinguishes contract validation from actual Pythia development-model evidence. The manuscript, historical predictions, reports, generated assets, and locked data remain outside this phase's write/scoring boundary.

Cohort input: `results/raw/te-v0.6.2-pythia-correction/corrected-variant-smoke/20260912T212527Z-corrected-smoke/run-summary.json`

## Work packages

| Work package | State | Evidence |
|---|---|---|
| implementation_contracts | `PASS` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` |
| eos_real_tokenizer_audit | `PASS` | `results/raw/te-v0.6.2-pythia-correction/eos-tokenizer-audit/20260912T210948Z-eos-audit/evidence-receipt.json` |
| independent_scoring | `PASS` | `results/raw/te-v0.6.2-pythia-correction/independent-scoring/20260912T210941Z-independent-score/evidence-receipt.json` |
| actual_auxiliary_isolation | `PASS` | `results/raw/te-v0.6.2-pythia-correction/auxiliary-isolation/20260912T211208Z-aux-only/evidence-receipt.json` |
| common_resource_profile | `PASS` | `results/raw/te-v0.6.2-pythia-correction/common-resource-profile/20260912T211352Z-common-resource/evidence-receipt.json` |
| corrected_model_results | `RECORDED` | `results/raw/te-v0.6.2-pythia-correction/corrected-a1-development/20260912T212156Z-a1/run-summary.json, results/raw/te-v0.6.2-pythia-correction/corrected-memorization/20260912T211909Z-memorization/run-summary.json, results/raw/te-v0.6.2-pythia-correction/corrected-variant-smoke/20260912T212527Z-corrected-smoke/run-summary.json` |
| clean_attack_evaluation | `PASS` | `results/raw/te-v0.6.2-pythia-correction/clean-attack-evaluation/20260912T214533Z-corrected-eval/evidence-receipt.json` |
| calibration | `NOT_MEASURED` | `not measured; no artifact` |
| capability_sentinel | `NOT_MEASURED` | `not measured; no artifact` |

## F01-F10 defect ledger

| ID | Correction | Test/run | Residual boundary |
|---|---|---|---|
| F01 | response_contract explicit EOS | `tests/transformer/test_response_contract.py` | real Pythia model training outcome remains development evidence only |
| F02 | exact-b-structured plus salient_values/relation_class span weights | `tests/transformer/test_variant_correction.py` | model effect not isolated by this contract test |
| F03 | applicable_norm_ids/conflict_class span weights | `tests/transformer/test_variant_correction.py` | model effect not isolated by this contract test |
| F04 | declared intended target arrays only | `tests/transformer/test_variant_correction.py` | permutation receipt requires a smoke attempt |
| F05 | auxiliary-only and detach/disabled-head diagnostics | `experiments/transformer/auxiliary_isolation_correction.py` | actual Pythia status depends on measured receipt |
| F06 | candidate-evaluator-v1 and model-claim separation | `tests/transformer/test_independent_scoring.py` | fictional project oracle is not external normative ground truth |
| F07 | one-example microbatch global denominators | `tests/transformer/test_accumulation.py` | full Pythia schedule is resource-bounded |
| F08 | parameter_accounting categories | `tests/transformer/test_parameter_accounting.py` | changed-parameter count is available after a training update |
| F09 | paper working directory and CPU workflow | `.github/workflows/paper.yml and .github/workflows/transformer-contracts.yml` | remote CI result is not available locally |
| F10 | report/gate require receipt-linked artifacts | `experiments/transformer/correction_gate.py` | no locked cohort authorization |

## Claims and handoff

Calibration and capability-sentinel results are `NOT_MEASURED` unless an artifact is listed. Clean/attack results must use independent evaluator fields and actual denominators; no literal reference score is accepted. The possible handoff remains development-only and does not authorize `te-freeze-cohort` or `te-run-cohort`.
