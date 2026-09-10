# Research context: Pythia development phase

Version: `te-v0.6.1-pythia-development`  
Status: multi-step Pythia development/training; not a locked comparison

- Selected model sequence: Pythia-410M now; OLMo 2 1B later under a separate
  protocol.
- The manuscript, frozen architecture, and prior MLP/harness reports remain
  unchanged. This phase reports experimental evidence separately.
- The implemented subset is task SFT plus parameter-efficient Transformer
  adaptation, auxiliary readout objectives, policy-grounded synthetic worlds,
  and an independent reference checker. It is not the complete VGTA
  architecture and does not implement custom attention, C3, routing, recursive
  ontology evolution, or solver-backed deployment.
- A green fixture gate is not semantic validation or confirmatory evidence.
- No favorable result is required to advance an implementation review. A null,
  unfavorable, blocked, or resource-limited result remains reportable.
- Every protocol, change, run group, child run, analysis, report, model asset,
  and prediction artifact receives a separate immutable identity.
- The active semantic benchmark must use readable fictional policy scenarios,
  explicit public observations, private annotations, typed graph identities,
  and an executable policy interpreter that does not use template names or
  candidate answers.
- The active host is resource constrained: development/model-smoke work is
  allowed locally, while a five-seed locked cohort requires a measured resource
  plan and owner-approved committed protocol state.
- A1 is task-SFT; all main arms share correct response supervision. The v1
  36-row benchmark is retained as a fixture, while v2 mini/standard profiles
  have separate identities and no v2 locked split in this phase.
- Pretrained, one-step diagnostic, memorization, and task-trained checkpoints
  are distinct lineages. Parser competence and policy competence are separate
  measurements. Auxiliary losses must reach shared LoRA parameters before an
  architectural claim is testable.
- A model-quality failure is not a reason to weaken controls or quietly change
  the hypothesis. Existing locked data remain untouched; OLMo and the
  manuscript remain deferred.

## Current next commands

```text
make te-dev-preflight PROTOCOL=te-v0.6.1-pythia-development
make te-audit-generations PROTOCOL=te-v0.6.1-pythia-development
make te-test-training-contracts PROTOCOL=te-v0.6.1-pythia-development
make te-profile-resources PROTOCOL=te-v0.6.1-pythia-development
make te-build-dev-data PROTOCOL=te-v0.6.1-pythia-development PROFILE=mini
make te-validate-dev-data PROTOCOL=te-v0.6.1-pythia-development
```

These commands must produce development reports even when they fail closed.
They must not invoke `make empirical-small`, `make paper-from-results`,
`te-freeze-cohort`, or `te-run-cohort`. The exact next command and blocker
derive from `results/reports/te-v0.6.1-pythia-development/development-readiness.json`.
