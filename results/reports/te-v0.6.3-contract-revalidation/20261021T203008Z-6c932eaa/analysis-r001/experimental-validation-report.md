# VGA/Pythia continuation: source-contract revalidation

Study: `te-v0.6.3-contract-revalidation`  
Master protocol: `vga-master-v1.0.0`  
Run: `20261021T203008Z-6c932eaa`  
Source baseline: `e9147ac91bee999c7347cd8be2d2457d1c81beb1`  
Scope: local source-contract and numerical-fixture execution; no pretrained-model comparison.

## Result

46 targeted tests passed, with zero failures, errors or skips, after the corrections. Before correction, the fixed source-contract counterexamples produced 13 failures and one pass, and the mocked command-boundary suite produced five failures. These are software-test cases, not 46 model experiments or predictions.

The real Pythia load and cache verification were attempted and blocked: Transformers and PEFT are absent, the pinned checkpoint is not cached, and outbound DNS is unavailable in this execution container. No Pythia weights were loaded, no model-quality predictions were produced, and no training seed or locked run was substituted with a tiny model.

## Planned versus executed

| Activity | Execution | Interpretation |
|---|---|---|
| Reproduce exact value-span and weighted-loss defects | 14 tests: 13 failed, one passed before repair; all 14 passed after repair | Confirmed source defects and verified targeted correction |
| Reproduce smoke summary and child-path defects | Five mocked command tests failed before repair; all five passed after | CLI orchestration correctness under mocked training |
| Validate explicit evidence inventory | 23 fixture/tamper tests passed | Hash/context/role/assertion verification, not scientific benefit |
| Validate gate command | Four subprocess tests passed | Legacy status-only input rejected; output is exclusive and scope-limited |
| Selected-source Python compilation | Passed | Syntax only; not full-repository import/integration |
| Actual Pythia load and cache check | Blocked environment | No model experiment |
| Two-seed memorization/A1 development | Not executed | Neither success nor hypothesis failure |
| Eight-arm/two-seed smoke | Not executed with a real model | Mocked scope tests cannot satisfy model coverage |
| Locked comparison and OLMo | Not executed | Not authorized by this continuation |

## Corrections tested

1. **Exact field-value spans.** The opening brace now contributes to character offsets. Tests compare actual substrings to independently serialized values, including quotes, escapes, Unicode, empty values and arrays. Character-token weights are checked against independent key boundaries. Real-Pythia tokenizer validation remains outstanding.
2. **Weighted objective reporting.** The reported `loss` now includes the response and auxiliary coefficients used for backpropagation. Raw components and their unweighted sum remain separately available. Four algebra cases compare the logged objective and the actual optimizer update against independently calculated global denominators, including a zero response coefficient. The tested updates already matched before repair; the reproduced defect was in reporting.
3. **Smoke execution and coverage.** The undefined seed variable is resolved. Parent and isolated child runs own different directories. Existing output roots are refused. Selected canary completion is separate from the full sixteen-arm/seed and 32-update requirement. A one-update subset remains protocol-partial even when its selected execution succeeds.
4. **Evidence verification.** The gate requires an explicit inventory, an independently supplied plan hash, exact source/result/receipt/attachment hashes, producer and scope/context matches, complete required roles, and numerical assertions. It rejects missing, tampered, foreign or status-only records. Its success state is `EVIDENCE_INVENTORY_VERIFIED`, not Pythia readiness or authorization.

## Measurement boundaries

The serializer test executes actual source definitions with the annotation projection mocked to identity. The orchestration tests execute the actual `main` function with a mocked model attempt; their temporary outputs are fixtures. The numerical tests execute the actual repository loss/update functions against a small differentiable tensor expression. No fixture was relabeled as a trained language model.

The local source subset was retrieved through the GitHub connector and checked against Git blob hashes before changes. A complete checkout could not be downloaded because DNS resolution failed. Consequently, this run does not claim that the whole repository regression suite or dependency-enabled Pythia integration passes.

The execution registration and invariant expectations were recorded before repairs. Additional negative tests implement those declared contracts; they are development tests, not a preregistered model hypothesis test. The artifact inventory was assembled after execution for integrity checking and is not represented as an independently preregistered study.

## Environment

Linux x86-64; Python 3.13.5; PyTorch 2.10.0+cpu; pytest 9.0.2; 4 GiB cgroup memory limit; four CPU-equivalents quota; no GPU. Transformers/PEFT and the pinned Pythia snapshot are unavailable. This environment differs from earlier local Mac runs and is not pooled with their model evidence.

## Evidence and repository state

The machine-readable `execution-summary.json` records the counts, tested-source identities, environment blocker and limitations. Detailed case results, source manifests and original logs are retained in the accompanying evidence bundle. `preflight.json` records actual dependency/cache errors. The accompanying conversation evidence bundle retains original XML, stdout, source snapshots, analysis inventory and gate output. Repository ingestion of the complete archive/registry chain remains outstanding; the published summary must not be used as a substitute for that missing readiness requirement.

The model source corrections are proposed on a review branch. The manuscript, datasets, old protocols, and historical model results are outside the changed set. No model effectiveness, calibration, attack-robustness, or comparative VGA finding is established by this execution.

## Next execution

Run the targeted tests and then the complete dependency-enabled repository suite in the existing Pythia environment. Inspect this branch's gate `--help`: legacy `--cohort`/PASS-string reports are intentionally not accepted. The old Makefile gate wrapper and report scanner still need migration to the explicit inventory interface; do not use them to declare readiness.

Before model training, bind the resolved data/model/environment/training plan to new source and artifact receipts; verify real-tokenizer value spans and the response-feasible generation cap; profile the longest structured inputs. Then perform the already-defined two-seed memorization schedule, two-seed A1 schedule and complete eight-arm smoke. A resource-limited run remains partial; a faithful but poor model result is retained.

Expected scientific output remains the per-contrast benefit, harm, equivalence or uncertainty of the actual model study. None of those outcomes is filled in by this contract run.
