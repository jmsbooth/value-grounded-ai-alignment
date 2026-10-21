# Scientific testing: start here

The prospective reference for new VGA/VGTA experiments is the **[Master Experimental Protocol v1.0.0](experiments/protocols/vga-master-v1.0.0/protocol.md)**.

This is a research-method protocol, not a new model result or a declaration that the existing harness satisfies every requirement.

| Reference | Purpose |
|---|---|
| [Master protocol](experiments/protocols/vga-master-v1.0.0/protocol.md) | Research question, fair controls, data boundaries, model training, evaluation, statistics, stopping, versioning and publication |
| [Execution runbook](experiments/protocols/vga-master-v1.0.0/runbook.md) | Phase-by-phase procedure, current blockers, existing commands, expected evidence and next sequence |
| [Claim register](experiments/protocols/vga-master-v1.0.0/claims.yaml) | Operational claims, controls, endpoints and scope, without rewriting historical H1-H10 |
| [Study-registration template](experiments/protocols/vga-master-v1.0.0/study-template.yaml) | Study-specific choices that must be completed, reviewed and frozen before locked execution |
| [Protocol index](experiments/protocols/README.md) | Historical protocols and their relationship to the prospective master |
| [Research context](docs/research-context.md) | Current implementation scope and unresolved work |
| [Evidence registry](results/registry/index.md) | Existing immutable experiment/report navigation |

## Operating principle

We test whether a specified implementation provides a useful benefit, not whether we can make the paper appear correct. Every main treatment must be compared with a competent baseline and meaningful supervision/information-matched controls. A bad result is retained; it is not automatically blamed on the harness. A demonstrated harness defect is qualified with a reproducer and appropriately scoped reruns.

Execution completion, measurement validity, evidence scope and scientific outcome are separate fields. One seed and one update can complete a canary, but cannot complete a sixteen- or forty-run cohort. A status string cannot replace a hash-verified result with the required scope and denominators.

The initial model sequence is Pythia-410M integration/development and locked comparison, followed by separately registered OLMo 2 1B replication if justified. Attention, MoE, coverage learning, late binding and solver-backed assurance are separate studies, not silently added treatments.

## Current boundary

At adoption baseline `07b4aaf48f82cc04c906b522d0b2f3da7f084d83`, v0.6.2 contains useful correction diagnostics, but the complete bounded retest remains outstanding and source-level issues require repair. See the runbook for the exact reviewed locations. Publishing this protocol does not repair that code, rerun models, authorize a locked cohort, or update the manuscript.

Keep the manuscript, generated manuscript assets and historical raw/reported results unchanged during correction work. New results receive new run identities; reanalysis receives a new revision. Read the selected study's resource and data-access approval before invoking model commands.
