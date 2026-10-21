# Experimental protocol index

## Prospective reference

**[vga-master-v1.0.0/protocol.md](vga-master-v1.0.0/protocol.md)** is the canonical research-method reference for newly registered studies. It consolidates test phases, information/supervision parity, controls, independent evaluation, statistical decisions, change control and evidence history.

Its companion [runbook](vga-master-v1.0.0/runbook.md) explains execution; the [claim register](vga-master-v1.0.0/claims.yaml) identifies operational tests; the [study template](vga-master-v1.0.0/study-template.yaml) must be completed for a particular experiment. No template or master-document publication constitutes model execution or owner authorization to launch a locked study.

A study adopts an exact master version and a complete approved profile. If prose, YAML and code disagree, stop and reconcile the plan before evaluation. Do not silently choose the interpretation that produces the best result.

## Existing protocols and preservation

| Protocol | Recorded role |
|---|---|
| [v0.3 pilot registration](../preregistration/v0.3.md) | Historical shared-MLP design; execution/registration limitations remain recorded |
| [hv-v0.5.0](hv-v0.5.0/protocol.md) | Initial harness checks and rejected leakage fixture |
| [hv-v0.5.1](hv-v0.5.1/protocol.md) | Revised fixture/binding checks; their original passing statuses do not imply full semantic validity |
| [hv-v0.5.2-semantic-validity](hv-v0.5.2-semantic-validity/protocol.md) | Public/private and fact-grounded semantic benchmark contracts |
| [te-v0.6.0-pythia](te-v0.6.0-pythia/protocol.md) | Initial actual-checkpoint integration and one-step development work |
| [te-v0.6.1-pythia-development](te-v0.6.1-pythia-development/protocol.md) | Multi-step baseline development and incomplete variant execution |
| [te-v0.6.2-pythia-correction](te-v0.6.2-pythia-correction/protocol.md) | EOS, control, scoring, gradient and resource corrections with canary-level recorded retests |

The roles above are navigation descriptions, not rewritten historical findings. Exact results and qualifications reside in each versioned report and source review. Preserve old protocol bytes and historical artifacts. New methodology is prospective; already inspected results do not become preregistered when a document is later committed.

## New study registration

Create a new directory with a unique study/version ID and copy the master study template. Resolve the manuscript mapping, actual implementation, model/data hashes, full arm/seed/update plan, budgets, evaluation rules, endpoints, power/precision, analysis, custody and approval. Freeze it before locked outputs become available. Any remaining required null is a blocker, not permission for an agent to improvise.

The template is a registration contract; current runners need an explicit validator/adapter before it is executable. Do not imply that publishing YAML implements enforcement.

For repository-wide entry and current status, read [TESTING.md](../../TESTING.md) and [research context](../../docs/research-context.md).
