# VGA/VGTA Harness Validation Protocol hv-v0.5.0

Status: development validation protocol; not a confirmatory Transformer protocol.

This protocol tests whether the experimental apparatus is sufficiently
versioned, discriminating, reproducible, and independently checkable to support
future matched A1/B/C1/C2 Transformer studies. It does not test whether VGA is
better than another alignment method and it does not change the frozen
architecture or manuscript.

## Scientific rules

- Every experiment has a stable experiment ID, every execution has an immutable
  run ID, every analysis has an incrementing revision, and every report has a
  unique report ID.
- Raw artifacts are never overwritten. A changed analysis creates a new
  `analysis-rNNN` directory and identifies its predecessor and reason.
- Development runs may repair declared harness defects. Confirmatory runs fail
  closed unless the Git tree, preregistration, dataset, ontology, verifier, and
  configuration are frozen and committed.
- Synthetic labels are harness fixtures only. They are not independent human
  ground truth and cannot support population-level or moral-truth claims.
- A positive result is valid only when the relevant controls and acceptance
  checks pass. A null or negative result remains an interpretable result.
- No Transformer, C3, routing, structural attention, or late-binding expansion
  is authorized by this phase.

## Required experiments

The required experiment IDs and acceptance rules are enumerated in
`gates.yaml`. They are executed separately and aggregated by `make harness-gate`.

## Artifact compatibility

The protocol requires explicit identity for dataset, independent ground truth,
ontology, verifier, candidate schema, attack suite, metric suite, model
configuration, and analysis implementation. Analyses must reject mismatched
protocol/data combinations unless explicitly running in development mode.

## Evidence classification

Harness reports use `harness-validation` as their evidence tier and one of the
standard statuses `valid-positive`, `valid-negative`, `valid-null`,
`inconclusive`, `invalid-harness`, `invalid-implementation`, `development-only`,
or `not-run`.
