# Experiment log

This log records the transition from manuscript development to the frozen
architecture and experimental-validation phase. It is intentionally separate
from the manuscript so intermediate results do not drive substantive narrative
changes.

## 2026-09-08 — Architecture freeze and evidence baseline

- Architecture state: frozen for experiments. No result-dependent changes to
  `src/vgta/`, the ontology fixtures, metrics, attack families, or hypotheses
  are authorized after a sealed confirmatory result is observed.
- Historical artifact preserved: v0.4 manuscript PDF and the immutable
  `empirical-small-20260908T222325Z` shared-MLP pilot group.
- Pilot identity: raw run revision
  `0a65af50ad1d29e0abfcce4c45c5a0e451eeeed9`; dataset `v0.3-small`; generator
  `v0.3-small`; configuration digest
  `2b88f62658887a743b06c5d374360dccd355a56ab5f50b5fc30d8e597c5eb030`;
  ontology `core-axiology-v1`; verifier `rule-based-toy-v0.2-fixed`.
- Pilot scope: A1/B/C1/C2, three seeds (11, 23, 37), 51 sealed records per
  run, 1,140 aggregate predictions, and no recorded structural-OOD topology
  overlap with training.
- Scientific status: Tier 1 synthetic mechanism evidence only. The pilot is
  labeled `pilot-uncommitted` because the preregistration was not committed
  before execution.
- Interpretation boundary: no Transformer, human-reviewed, realistic
  policy-grounded, independent-ground-truth, five-seed, blind, or
  cross-domain claim is supported by this run.
- Output report:
  [experimental-validation-report.md](../results/reports/experimental-validation-report.md).

## Freeze-era operating rule

Development-mode fixes may correct crashes, dimensions, malformed records,
numerical instability, or declared harness defects. After a confirmatory
configuration is frozen, any legitimate defect invalidates the affected run,
increments the protocol version, and requires an all-variant rerun. A negative
or null result remains a result; it is not a reason to redefine a hypothesis or
selectively tune the proposed architecture.

## 2026-09-09 — Harness remediation decision

- The `hv-v0.5.0` harness result is preserved as a valid-negative baseline: its
  dataset-leakage audit found high-similarity train/sealed pairs, topology
  overlap, and predictive in-sample metadata.
- Because the leakage definition now requires train-fitted, held-out metadata
  evaluation, the remediation is protocol `hv-v0.5.1`; v0.5.0 evidence is not
  rewritten or relabeled.
- The new fixture is `v0.4-structure-heldout`. It uses split-specific surface
  lexicons, identifier namespaces, and topology hashes, then reruns all 14
  harness experiments under the same lifecycle and evidence boundaries.


## 2026-09-09 01:59 UTC — dataset-leakage-audit

- Protocol: `hv-v0.5.0`
- Experiment: `dataset-leakage-audit`
- Run: `20260909T015925Z-fba5e8`
- Status: `valid-negative`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/dataset-leakage-audit/20260909T015925Z-fba5e8/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — shortcut-baselines

- Protocol: `hv-v0.5.0`
- Experiment: `shortcut-baselines`
- Run: `20260909T015926Z-7aec91`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/shortcut-baselines/20260909T015926Z-7aec91/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — random-label-control

- Protocol: `hv-v0.5.0`
- Experiment: `random-label-control`
- Run: `20260909T015930Z-a7d725`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/random-label-control/20260909T015930Z-a7d725/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — ontology-permutation-control

- Protocol: `hv-v0.5.0`
- Experiment: `ontology-permutation-control`
- Run: `20260909T015934Z-e7a843`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/ontology-permutation-control/20260909T015934Z-e7a843/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — sham-feature-control

- Protocol: `hv-v0.5.0`
- Experiment: `sham-feature-control`
- Run: `20260909T015939Z-acc95f`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/sham-feature-control/20260909T015939Z-acc95f/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — ground-truth-independence

- Protocol: `hv-v0.5.0`
- Experiment: `ground-truth-independence`
- Run: `20260909T015941Z-b35094`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/ground-truth-independence/20260909T015941Z-b35094/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — scenario-transformation-validation

- Protocol: `hv-v0.5.0`
- Experiment: `scenario-transformation-validation`
- Run: `20260909T015943Z-4bfb83`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/scenario-transformation-validation/20260909T015943Z-4bfb83/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — attack-discrimination

- Protocol: `hv-v0.5.0`
- Experiment: `attack-discrimination`
- Run: `20260909T015946Z-0862cc`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/attack-discrimination/20260909T015946Z-0862cc/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — calibration-validation

- Protocol: `hv-v0.5.0`
- Experiment: `calibration-validation`
- Run: `20260909T015949Z-68d2d8`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/calibration-validation/20260909T015949Z-68d2d8/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — verifier-property-validation

- Protocol: `hv-v0.5.0`
- Experiment: `verifier-property-validation`
- Run: `20260909T015953Z-6c8746`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/verifier-property-validation/20260909T015953Z-6c8746/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 01:59 UTC — verifier-mutation-validation

- Protocol: `hv-v0.5.0`
- Experiment: `verifier-mutation-validation`
- Run: `20260909T015956Z-169d6e`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/verifier-mutation-validation/20260909T015956Z-169d6e/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 02:00 UTC — verifier-differential-validation

- Protocol: `hv-v0.5.0`
- Experiment: `verifier-differential-validation`
- Run: `20260909T015958Z-6e1b1c`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/verifier-differential-validation/20260909T015958Z-6e1b1c/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 02:00 UTC — power-analysis

- Protocol: `hv-v0.5.0`
- Experiment: `power-analysis`
- Run: `20260909T020006Z-66018a`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/power-analysis/20260909T020006Z-66018a/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 02:00 UTC — calibration-validation

- Protocol: `hv-v0.5.0`
- Experiment: `calibration-validation`
- Run: `20260909T015949Z-68d2d8`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/calibration-validation/20260909T015949Z-68d2d8/analysis-r002/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 02:05 UTC — blind-evaluation-validation

- Protocol: `hv-v0.5.0`
- Experiment: `blind-evaluation-validation`
- Run: `20260909T020537Z-bc7b9a`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.0/blind-evaluation-validation/20260909T020537Z-bc7b9a/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:32 UTC — dataset-leakage-audit

- Protocol: `hv-v0.5.1`
- Experiment: `dataset-leakage-audit`
- Run: `20260909T093243Z-c2080c`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/dataset-leakage-audit/20260909T093243Z-c2080c/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — shortcut-baselines

- Protocol: `hv-v0.5.1`
- Experiment: `shortcut-baselines`
- Run: `20260909T093309Z-2f45e8`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/shortcut-baselines/20260909T093309Z-2f45e8/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — random-label-control

- Protocol: `hv-v0.5.1`
- Experiment: `random-label-control`
- Run: `20260909T093311Z-880573`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/random-label-control/20260909T093311Z-880573/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — ontology-permutation-control

- Protocol: `hv-v0.5.1`
- Experiment: `ontology-permutation-control`
- Run: `20260909T093312Z-221fc4`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/ontology-permutation-control/20260909T093312Z-221fc4/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — sham-feature-control

- Protocol: `hv-v0.5.1`
- Experiment: `sham-feature-control`
- Run: `20260909T093316Z-e1c5e3`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/sham-feature-control/20260909T093316Z-e1c5e3/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — ground-truth-independence

- Protocol: `hv-v0.5.1`
- Experiment: `ground-truth-independence`
- Run: `20260909T093317Z-cf5df7`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/ground-truth-independence/20260909T093317Z-cf5df7/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — scenario-transformation-validation

- Protocol: `hv-v0.5.1`
- Experiment: `scenario-transformation-validation`
- Run: `20260909T093319Z-36fb6e`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/scenario-transformation-validation/20260909T093319Z-36fb6e/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — attack-discrimination

- Protocol: `hv-v0.5.1`
- Experiment: `attack-discrimination`
- Run: `20260909T093321Z-58a5e4`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/attack-discrimination/20260909T093321Z-58a5e4/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — calibration-validation

- Protocol: `hv-v0.5.1`
- Experiment: `calibration-validation`
- Run: `20260909T093324Z-32f08d`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/calibration-validation/20260909T093324Z-32f08d/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — verifier-property-validation

- Protocol: `hv-v0.5.1`
- Experiment: `verifier-property-validation`
- Run: `20260909T093327Z-cee8c3`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/verifier-property-validation/20260909T093327Z-cee8c3/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — verifier-mutation-validation

- Protocol: `hv-v0.5.1`
- Experiment: `verifier-mutation-validation`
- Run: `20260909T093329Z-f7b6bf`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/verifier-mutation-validation/20260909T093329Z-f7b6bf/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — verifier-differential-validation

- Protocol: `hv-v0.5.1`
- Experiment: `verifier-differential-validation`
- Run: `20260909T093333Z-083455`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/verifier-differential-validation/20260909T093333Z-083455/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — blind-evaluation-validation

- Protocol: `hv-v0.5.1`
- Experiment: `blind-evaluation-validation`
- Run: `20260909T093335Z-f3e0e9`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/blind-evaluation-validation/20260909T093335Z-f3e0e9/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — power-analysis

- Protocol: `hv-v0.5.1`
- Experiment: `power-analysis`
- Run: `20260909T093337Z-a1e4b3`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/power-analysis/20260909T093337Z-a1e4b3/analysis-r001/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.

## 2026-09-09 09:33 UTC — calibration-validation

- Protocol: `hv-v0.5.1`
- Experiment: `calibration-validation`
- Run: `20260909T093324Z-32f08d`
- Status: `valid-positive`
- Report: [experimental-validation-report.md](../results/reports/hv-v0.5.1/calibration-validation/20260909T093324Z-32f08d/analysis-r002/experimental-validation-report.md)

This entry records lifecycle chronology only; metrics remain in the immutable report.
