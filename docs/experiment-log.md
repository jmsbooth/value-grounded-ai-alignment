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
