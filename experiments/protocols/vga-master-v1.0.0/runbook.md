# Experimental runbook and phase reference

**Master:** [vga-master-v1.0.0](protocol.md)  
**Baseline inspected:** `07b4aaf48f82cc04c906b522d0b2f3da7f084d83`  
**Purpose:** operational instructions and evidence requirements; not a record of newly executed tests.

## 1. Start here on every execution

Read repository instructions, [TESTING.md](../../../TESTING.md), the [master protocol](protocol.md), the selected study registration, its resolved configurations, and the current [research context](../../../docs/research-context.md). Inspect the actual branch, commit, uncommitted work and hardware. Do not overwrite newer local work to reproduce this baseline.

Decide which activity is authorized: documentation, contract tests, model canary, bounded development, locked comparison, replication or analysis-only. A request to write this protocol does not authorize training, paid compute or release of a scientific result.

Create a preflight record with source identity, environment, protected paths, resource budget and artifact locations. Keep `paper/`, existing raw results and old reports outside the write set. Do not run `make all`, `make empirical-small`, `make paper-from-results`, or an aggregate command that regenerates frozen paper assets during experimental development.

## 2. Current state and known qualification

At the inspected baseline, the active implementation is the v0.6.2 Pythia correction. The earlier v0.6.1 source/context is historical. Existing source includes EOS supervision, a candidate evaluator separate from model claims, a variant plan and a common accumulation path. A recorded actual-Pythia diagnostic observes auxiliary-only gradients and detach/disabled-head controls.

However, the recorded correction training was a one-update/one-seed canary; only C2-SHAM was exercised in its smoke group. The recorded attack evaluation used an eight-token cap. These are not the scheduled learning comparison. This methodological document does not reclassify them or infer that EOS learning, policy accuracy, all-arm completion or model robustness was demonstrated.

The prior source review identified the following unresolved requirements. Reproduce each against the execution checkout before changing code; these are observations at a revision, not declarations that a later checkout is defective.

| Item | Inspected location | Required evidence before closing |
|---|---|---|
| Undefined `seeds` in smoke summary | `experiments/transformer/corrected_variant_smoke.py` | Full mocked command reaches final summary/receipt for selected seeds |
| Child runs reuse the parent summary/output root | same runner | Parallel/isolated child execution cannot overwrite parent or sibling evidence |
| Field-value character spans omit opening-brace offset | `src/vgta_transformer/response_contract.py` | Exact character substrings and real-tokenizer value weights, including punctuation/escaping |
| Reported total loss sums unweighted components | `src/vgta_transformer/training.py` | Logged objective equals the differentiated weighted objective on known numerical fixtures |
| Gate trusts status strings and permits pending preservation | `experiments/transformer/correction_gate.py` | Tampered/missing/foreign receipts and incomplete coverage fail; final hashes checked |
| Report selects latest matching evidence across attempts | `experiments/transformer/correction_report.py` | Explicit study inventory binds every prerequisite to compatible source/data/model/config |
| One-arm canary described as smoke complete | correction run/ledger | Selected-scope completion and full-protocol coverage reported independently |
| Quality evaluation caps shorter than required format | correction training/evaluation artifacts | Preflight proves cap can express full response; tiny caps labeled canaries |
| Some configuration fields are recorded but not enforced | training and variant runners | One resolved plan drives actual optimizer/schedule/heads/weights; unsupported fields error |

Supporting historical paths: [execution ledger](../../../docs/experiments/te-v0.6.2-pythia-correction/execution-ledger.jsonl), [training plan](../te-v0.6.2-pythia-correction/training.yaml), [variant plan](../te-v0.6.2-pythia-correction/variants.yaml), and [correction report directory](../../../results/reports/te-v0.6.2-pythia-correction/).

These corrections are prerequisites to the next retest; they do not call for another architecture redesign. Do not repeatedly write new specs instead of executing the corrected bounded schedule.

## 3. Create a study-specific registration

Copy [study-template.yaml](study-template.yaml) into a new versioned study directory. Preserve its disabled state until every study-specific field is resolved. The template is a requirements document, not a runner-supported schema until a validator/adapter explicitly implements it.

Complete the question, manuscript-claim mapping, model/tokenizer and data hashes, public input contract, acceptable-action semantics, variants, optimizer/losses, physical/effective batch, stopping rules, generation budget, endpoints, comparisons, sample size, uncertainty method, source/config receipts, custody and resource plan.

Document every null as either resolved or explicitly not applicable with a reason. Do not use defaults to hide unresolved decisions. Freeze the complete effective configuration before running a locked study. The master document sets common rules; the study profile fixes the concrete experiment.

## 4. Qualify the apparatus

Use known-answer fixtures to test the reference policy, candidate evaluator, strict parser and metrics. Require counterexamples to intentional mutations: answer leakage, target-conditioned candidates, ID-renamed graph duplicates, bad permission claims, missing consent/evidence, corrupted receipt hashes and missing cohort members.

Audit meaningful text and structured information parity. Record task vocabulary and class supports; if a label is constant, that task cannot test its claimed discrimination. Ground truth must change for relevant facts and remain stable for irrelevant naming/rendering changes. A test that only confirms function names, object shapes, strings or file existence does not close a scientific property.

Run direct pytest contract tests in an environment with the required dependencies. Inspect collection and skips; a critical test skipped for missing Torch/Transformers/PEFT is not passed. Pure tooling tests should be fast. Actual pretrained-model checks are separate, resource-budgeted executions.

## 5. Pythia implementation qualification

Execute actual-checkpoint loading and confirm revision/checksums. Audit real tokenizer EOS behavior and exact inference-prefix equality. Inspect prompt, answer and padding masks. Confirm token value spans and the weighted loss.

For each auxiliary head: response coefficient zero; head and shared-LoRA gradients measured; detached representation removes LoRA gradients; disabled heads contribute none. Set a numerical tolerance before comparing combined/isolated gradients. Keep both tiny-model and Pythia receipts, with their different scopes.

Validate microbatch/global-denominator equivalence, actual optimizer membership, update count, checkpoint/reload and resumed-next-update behavior. Parameter counts must distinguish frozen, adapter, head, optimizer-member and actually changed parameters.

Profile the longest B/C2 inputs, not just short natural-language A1 examples. Measure backward, decoding, evaluation batching, checkpointing and storage. Use safe memory settings and record backend/precision. Do not start the full schedule before estimating it from measurements.

## 6. Bounded development sequence

These are the prospective inherited correction schedules, not claims of execution:

| Step | Required execution | Interpretation |
|---|---|---|
| Memorization | Eight fixed examples; seeds 11 and 23; up to 100 updates; evaluate at 0/25/50/75/100; adequate fixed generation cap | Can the task/termination contract be learned on training examples? |
| A1 held-out development | Fresh pretrained base/adapters; 64 training groups; three passes/effective batch eight = 24 updates; two seeds; validation selects checkpoint | Can an ordinary task-SFT baseline produce assessable decisions on new development worlds? |
| All-arm smoke | Eight declared arms x seeds 11/23 x 32 updates, same grouping and adequate generation budget | Do all intended treatment/control paths execute faithfully? |
| Trained clean/attack diagnostics | Selected trained checkpoints, paired clean/transformed inputs and independent scoring | What errors and attack effects occur on open development? |
| Calibration/capability | Registered confidence-event path and frozen sentinel | Are uncertainty and unrelated capability measured rather than assumed? |

The memorization criterion inherited from v0.6.2 is at least 7/8 strict-format responses and 7/8 useful independently permitted actions at two consecutive scheduled evaluations, at least 30% NLL reduction, and EOS rate at least 7/8. It is an engineering diagnostic, not an unbiased estimate of population performance. Apply it to actual complete response generations, not teacher-forced loss alone.

Use the same eight IDs as the approved profile, covering all relevant action classes. Do not silently choose whichever eight examples the model handles best. Train A1 from a fresh base/adaptation rather than the memorization checkpoint. Keep calibration/open-development out of optimization and checkpoint selection as specified by the master.

If resources support only a one-update check, label it a canary and retain the remainder as unexecuted. A quality failure on the full declared schedule is a valid model result; a generation budget incapable of emitting the schema is an invalid quality measurement. Stop looping after the declared troubleshooting budget. Record the limitation and request a new budget/design decision if needed.

## 7. Existing commands and safe usage

The following command names exist at the baseline. Their existence is not evidence that their internals satisfy this master protocol. Correct and regression-test the identified paths before using them for readiness evidence. Inspect current `--help` and the Makefile because several `PROTOCOL=` assignments in examples are not forwarded by the underlying scripts.

```bash
# No model training or paper regeneration:
PYTHONPATH=src python -m pytest -q tests/transformer
PYTHONPATH=src python -m compileall -q src scripts experiments tests
make verify-research-history

# Real-model/resource diagnostics; run only inside the approved local budget:
make te-audit-eos
make te-test-independent-scoring
make te-test-aux-only DEVICE=cpu
make te-profile-common DEVICE=cpu

# Only after fixes, complete profile and resource review:
make te-retest-memorization CONFIG=experiments/protocols/te-v0.6.2-pythia-correction/training.yaml
make te-retest-a1 CONFIG=experiments/protocols/te-v0.6.2-pythia-correction/training.yaml
make te-corrected-variant-smoke CONFIG=experiments/protocols/te-v0.6.2-pythia-correction/variants.yaml ISOLATE=1
```

These show the historical baseline paths. A new prospective run must use its own approved resolved study configuration and explicitly record inherited versus overridden fields; do not edit the historical v0.6.2 profile in place. A one-seed or update-count override must appear in the actual plan, coverage table and scope designation.

The report/gate commands take exact artifacts (`COHORT=...`), but the existing implementation needs the receipt-verification corrections above. Do not accept their string output alone. Do not call `te-freeze-cohort` or `te-run-cohort` until owner approval and every registered locked prerequisite are verified. No command in this document is executed by publishing this file.

## 8. Locked experiment sequence

1. Finish development and record all tuning attempts, model limitations and outstanding deviations.
2. Validate analysis using synthetic known-effect/null fixtures and sample-size simulations; these are statistic tests, not model evidence.
3. Resolve the new study template, including precise claims, six-primary-comparison family or its justified replacement, five-seed plan, power/precision, budgets and custody.
4. Commit the approved registration and exact implementation/configuration. Generate or attest the untouched evaluation set under the frozen split rules; bind its manifest before evaluation.
5. Verify evidence inventory, clean source, input/label isolation, generation feasibility and resource limits. A documentation commit is not an execution approval.
6. Run all declared variants and seeds from the specified parent checkpoints. Retain interrupted/failed attempts without substituting favorable ones.
7. Seal raw predictions before joining private annotations. Generate blinded metrics and primary tables under the frozen analysis script.
8. Unblind, interpret all registered outcomes, identify scoped validity issues, and freeze the report. No result-guided repair of the confirmatory set.
9. Decide separately whether to replicate in OLMo, register an extension, stop the direction, or publish the current positive/null/adverse evidence.

## 9. Required evidence package and completion matrix

Each experiment records the scientific question, planned and actual arms/seeds/updates/groups/tokens, raw outputs, checkpoint/environment/data/config/analysis hashes, execution log, change log and report. Reanalysis receives a new revision. Daily summaries and current context are navigation, not evidence.

A phase-summary table must include all planned work, including not run, partial, invalid, and not measured. Do not hide actual update/generation budgets in a separate ledger while displaying only PASS in the report.

| Dimension | Required decision |
|---|---|
| Code fidelity | Which named contracts were reproduced, corrected and tested? |
| Execution | Exactly what was trained/evaluated and what was not? |
| Validity | Which endpoints/runs remain interpretable? |
| Scientific finding | Benefit, harm, practical equivalence, useful benefit ruled out, or uncertainty, per registered contrast |
| Scope | Synthetic/development/locked/replication; model and domain boundaries |
| Next action | Specific defect repair, remaining registered run, replication decision, or report freeze |

A protocol criterion can fail while the experiment completes successfully. Report both. Conversely, all commands can finish while the study is scientifically inconclusive or invalid.

## 10. Preserving outcomes in the paper

When a study is complete or deliberately terminated, publish the original question, why it was plausible, the implemented intervention, controls, execution, results, uncertainty, deviations and failure analysis. Do not rewrite the architecture to retrospectively fit the outcome.

If the same information in ordinary context/training performs equivalently, report that narrower result. If explicit structure increases confidence or vulnerability, report the tradeoff. If a valid implementation yields no meaningful advantage with adequate precision, that is evidence against the tested direction and may conclude the current paper. A new design inspired by it starts a new entry in the research timeline.

No probability threshold, artifact hash, number of unit tests, or declaration of neutrality guarantees an unbiased result. The purpose of this runbook is to expose the choices and preserve enough evidence for independent scrutiny and reproduction.
