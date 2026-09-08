# Empirical limitations

The current pilot has several material limitations:

- It uses generated synthetic scenarios rather than human-reviewed or
  naturally occurring data.
- The model is a small shared MLP proxy, not a Transformer and not an
  open-weight language model.
- Three seeds are the minimum repeated-run design; seed-level intervals are
  descriptive and weak for population inference.
- The labels, feature channels, and transformations are generated from the
  same controlled grammar, so benchmark regularities may be easier than real
  reasoning.
- Candidate actions are host-normalized fixtures rather than unconstrained
  language-model outputs; parser and verifier behavior therefore understate
  deployment complexity.
- The fixed verifier is intentionally weaker than a typed SMT verifier and
  cannot establish formal assurance.
- Capability tasks are narrow and cannot support broad capability-retention
  claims.
- Attack fixtures are not a real-world red-team or security evaluation.
- Ontology degradation does not yet model full temporal world-state validity,
  signed authority chains, or pluralistic human disagreement.

These limitations constrain the evidence tier to mechanism demonstration. A
negative result would still be informative because the primary contrasts and
controls are fixed before the local pilot outputs are interpreted.
