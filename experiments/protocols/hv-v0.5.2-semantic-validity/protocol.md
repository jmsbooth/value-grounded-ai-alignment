# `hv-v0.5.2-semantic-validity`

Status: engineering gate for `te-v0.6.0-pythia`.

This protocol changes the operational definition of the active benchmark. It
does not rewrite thresholds or results in `hv-v0.5.0` or `hv-v0.5.1`.

## Acceptance criteria

1. Public examples are readable fictional policy worlds rather than opaque
   token templates.
2. Facts, policy rules, and typed directed graphs are explicit. Private labels,
   target actions, template identifiers, and world identifiers are excluded
   from model-visible input.
3. The public action catalogue is fixed and not target-conditioned.
4. The reference policy derives its decision from observed facts and rules;
   changing a template name cannot change a decision, while changing a
   decision-relevant fact can.
5. Train/validation/calibration/open-development/locked-engineering groups are
   disjoint by world-group identity.
6. Graph identity is invariant to identifier renaming and edge ordering, while
   topology and typed-relation changes remain detectable.
7. Any attack result in a model phase comes from an executed model on a
   transformed input, never from a hash-derived or fixture-generated outcome.

The gate emits `SEMANTIC_DATASET_VALIDATED` or `SEMANTIC_DATASET_REJECTED`.
Only the former permits Pythia development diagnostics. It is not evidence of
model capability or value alignment.

