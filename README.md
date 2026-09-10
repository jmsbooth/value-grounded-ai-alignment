# Value-Grounded AI Alignment

**Value-Grounded AI Alignment (VGA)** is a theoretical research program for testing whether explicit axiological and normative structure can participate in Transformer computation while authority, purpose, domain semantics, world state, and consequential actions remain separately governed.

**Status: v0.6.1 Pythia development/training phase — no locked Transformer comparison results**

> This repository proposes and tests interfaces, equations, controls, synthetic mechanism-validation fixtures, and bounded Pythia integration diagnostics. It does not claim that value-grounded Transformers solve AI alignment, establish moral truth, or provide production safety.

## Research question

Can a governed external canonical axiology be compiled into a derived, non-authoritative neural module and used as structural value conditioning, while normative sources are late-bound under authority and provenance, purpose selects domain relevance, world state remains uncertain and external, and candidate actions are independently verified?

The central boundary is:

O_A^v --compile/train--> A_phi^v

O_A^v is the canonical axiology. A_phi^v is a learned or hybrid derivative and can fail conformance or drift while the canonical artifact remains unchanged. The design distinguishes:

| Layer | Role | Binding and update boundary |
| --- | --- | --- |
| L0 canonical axiology | Value-bearing properties and higher-order relations | External, typed, versioned, provenance-bearing, governed; immutable within deployment |
| L1 normative ontology | Duties, permissions, prohibitions, exceptions, authorities, jurisdictions, and conflicts | Runtime late binding; no scalar averaging of conflict |
| L2a domain ontology | Entities and relations in the current domain | Runtime contextual |
| L2b purpose model | Purpose-conditioned relevance Relevant(O_D,P,X) | Runtime contextual and authorized |
| L3 world state | Time-indexed assertions with source, confidence, and provenance | Ephemeral external state; not ground truth |

## What this repository contains

- [paper/main.tex](paper/main.tex) and [paper/value-grounded-ai-alignment.pdf](paper/value-grounded-ai-alignment.pdf) — manuscript source and compiled preprint.
- [paper/references.bib](paper/references.bib) — curated bibliography, including recent 2025–2026 work used to bound novelty.
- [paper/figures/](paper/figures/) — editable TikZ sources and generated vector PDFs, including the training pipeline and fixed-verifier ablation.
- [ontology/](ontology/) — parser-safe Turtle fixtures for canonical axiology, normative sources/conflicts, purpose/domain semantics, and uncertain world state.
- [src/vgta/](src/vgta/) — dependency-free interfaces for canonical compilation, conformance probes, attention bias, routing, semantic state, normative conflict, verification, and metrics.
- [src/vgta_eval/](src/vgta_eval/) — small NumPy shared-MLP mechanism-validation model, scenario generator, conformance adapter, attack fixtures, metrics, and bootstrap statistics.
- [experiments/run_toy_evaluation.py](experiments/run_toy_evaluation.py) — deterministic A1-versus-G synthetic use cases with one fixed verifier.
- [experiments/evaluation/run_empirical_small.py](experiments/evaluation/run_empirical_small.py) — matched A1/B/C1/C2 pilot runner with three seeds, frozen logical splits, manifests, and raw predictions.
- [experiments/preregistration/v0.3.md](experiments/preregistration/v0.3.md) and [experiments/configs/v0.3-small.toml](experiments/configs/v0.3-small.toml) — preregistered scope, metrics, thresholds, controls, and stopping rules.
- [results/](results/) — generated raw manifests, processed tables, confidence intervals, facts, and figures from executed pilots. Raw run directories are never overwritten.
- [results/reports/experimental-validation-report.md](results/reports/experimental-validation-report.md) — machine-derived freeze-era report covering methods, harness status, hypotheses, positive/null/negative results, security, calibration, capability, compute, and replication.
- [results/reports/te-v0.6.0-pythia/phase-execution-report.md](results/reports/te-v0.6.0-pythia/phase-execution-report.md) — prior one-step Pythia integration report with methods, test outputs, resource limits, and the explicit non-locked result.
- [results/reports/te-v0.6.1-pythia-development/](results/reports/te-v0.6.1-pythia-development/) — v0.6.1 development reports covering strict output audit, training contracts, v2 benchmark validation, real multi-step Pythia runs, variant smoke, attack audit, and readiness.
- [results/reports/historical-qualification/mlp-count-reconciliation/count-reconciliation.md](results/reports/historical-qualification/mlp-count-reconciliation/count-reconciliation.md) — append-only qualification reconciling historical raw-row counts without rewriting the prior report.
- [results/registry/index.md](results/registry/index.md) — immutable experiment/run/analysis/report history for the v0.5 harness-validation phase.
- [experiments/protocols/hv-v0.5.1/](experiments/protocols/hv-v0.5.1/) — remediation protocol, hypotheses, metrics, gates, and controls for harness validation; the failed `hv-v0.5.0` baseline remains preserved.
- [experiments/protocols/te-v0.6.0-pythia/](experiments/protocols/te-v0.6.0-pythia/) — Pythia phase protocol, fixed input contracts, variants, analysis plan, artifact schema, and fail-closed gates.
- [experiments/protocols/hv-v0.5.2-semantic-validity/](experiments/protocols/hv-v0.5.2-semantic-validity/) — semantic validity gate for readable fictional policy worlds, typed graphs, public/private isolation, and fact-grounded reference decisions.
- [src/vgta_transformer/](src/vgta_transformer/) — optional exact Pythia loader, LoRA adaptation, auxiliary heads, masked losses, deterministic decoding, and checkpoint helpers.
- [experiments/transformer/](experiments/transformer/) — preflight, semantic audit, dataset materialization, model smoke, diagnostics, cohort planning, analysis, and fail-closed gate commands.
- [docs/research-context.md](docs/research-context.md) and [docs/experiments/te-v0.6.0-pythia/](docs/experiments/te-v0.6.0-pythia/) — current phase boundaries, resources, decisions, ledger, and OLMo handoff.
- [docs/experiments/te-v0.6.1-pythia-development/](docs/experiments/te-v0.6.1-pythia-development/) — v0.6.1 preflight, protected-paper hashes, source inventory, and execution ledger.
- [paper/generated/](paper/generated/) — LaTeX fragments generated from result tables; no empirical numbers are manually typed into the paper.
- [docs/architecture.md](docs/architecture.md) — active architecture description.
- [docs/architecture-decisions.md](docs/architecture-decisions.md) — v0.2 ADR-001 through ADR-007 decision index.
- [docs/novelty-analysis-v2.md](docs/novelty-analysis-v2.md) — claim-by-claim novelty matrix and safe wording.
- [docs/literature-review.md](docs/literature-review.md) — literature positioning through 2026-09-08.
- [docs/research-roadmap.md](docs/research-roadmap.md) — phased experiments, controls, metrics, and falsification gates.
- [SECURITY.md](SECURITY.md) — responsible-use and threat-model guidance.

## Paper structure

The manuscript follows a conventional scientific sequence:

1. Introduction and research scope.
2. Background and related work, including neuro-symbolic reasoning, SMT/Z3, SMT-LIB, policy compilation, and TLA+.
3. Proposed value-grounded alignment model and the reference-versus-pilot boundary.
4. Experimental method: pilot architecture, variants, data, metrics, security tests, statistics, and reproducibility.
5. Generated results: primary metrics, structural OOD, candidate conformance, attacks, coverage/calibration, and hypothesis criteria.
6. Interpretation, gaps and limitations, phased future research, and conclusion.

Observed measurements are generated from raw run outputs. Proposed mechanisms and interpretations are stated in their respective sections; generated pilot results remain synthetic proxy evidence.

## Run the synthetic fixture

    python3 experiments/run_toy_evaluation.py
    python3 experiments/run_toy_evaluation.py --json

The runner separates model-only useful completion from the same fixed verifier's rejection and useful candidate conformance rate (UCR). Its four scenarios cover consent and privacy, workplace coercion, safety checks, and medical-record disclosure. The output is synthetic and demonstrates wiring only; it is not a benchmark or evidence for H1–H9.

## Build and verify the paper

    make all

Individual targets:

    make figures   # compile TikZ sources into paper/figures/*.pdf
    make paper     # compile paper/main.tex
    make verify    # run tests, synthetic fixture, and PDF diagnostics
    make clean     # remove generated build artifacts

The build uses latexmk when available and otherwise the repository's bundled Tectonic workflow. Generated intermediates live under paper/build/ and are ignored by Git. A complete research run should additionally render the PDF at 200 DPI and inspect every page for clipping, collisions, and material overfull boxes.

## Run the empirical mechanism-validation pilot

    make empirical-small

This runs the first go/no-go gate: A1 behavioral control, B runtime ontology context, C1 axiological auxiliary training, and C2 normative auxiliary training. It uses three seeds, a deterministic synthetic benchmark with train/validation/development-test/sealed-test splits, one fixed verifier, structural-OOD topology checks, attack fixtures, capability controls, and generated confidence intervals. The current implementation is a shared NumPy MLP proxy, not a Transformer; its outputs are Tier 1 mechanism evidence at most.

The command writes a unique directory under results/raw/, updates results/processed/seed-metrics.csv, results/tables/, results/statistics/, results/figures/, and paper/generated/. Because this working tree is intentionally left uncommitted for manual push, current outputs are labeled `pilot-uncommitted`; a formal sealed run requires committing the preregistration before execution.

    make analyze-results RAW_ROOT=results/raw/empirical-small-YYYYMMDDTHHMMSSZ
    make paper-from-results

## Run the v0.5.1 harness-validation phase

The v0.5 phase validates the test apparatus before any Transformer Gate 1 work. The remediation revision is `hv-v0.5.1`: it changes the leakage audit to train-fitted, held-out metadata evaluation and binds runs to a structure-heldout dataset. Each harness experiment is a separate immutable event with a unique UTC run ID, an append-only raw manifest, a versioned analysis revision, and a report manifest. The preserved v0.3 pilot and failed `hv-v0.5.0` baseline are indexed as historical and their raw files are not rewritten.

The original `v0.3-small` failure remains available as a baseline. Dataset
remediation is materialized separately and evaluated under the same protocol:

    make remediated-dataset
    VGTA_DATASET_VERSION=v0.4-structure-heldout make experiment EXP=dataset-leakage-audit

The active harness default is `v0.4-structure-heldout`; set
`VGTA_DATASET_VERSION=v0.4-structure-heldout` explicitly in automation or CI to
keep the dataset identity visible at the call site and in every manifest.

Run individual experiments:

    make experiment EXP=dataset-leakage-audit
    make experiment EXP=shortcut-baselines
    make experiment EXP=random-label-control
    make experiment EXP=attack-discrimination
    make experiment EXP=calibration-validation

Supported IDs are listed in `experiments/protocols/hv-v0.5.1/gates.yaml`; they include leakage, shortcut, random-label, ontology-permutation, sham-feature, independent-ground-truth, transformation, attack, calibration, verifier, blind-evaluation, and power-analysis checks. The full registry is regenerated at [results/registry/index.md](results/registry/index.md).

Analyze an existing versioned run without overwriting prior analysis:

    make analyze-versioned PROTOCOL=hv-v0.5.1 EXPERIMENT=calibration-validation RUN_ID=YYYYMMDDTHHMMSSZ-xxxxxx
    make analyze-versioned PROTOCOL=hv-v0.5.1 EXPERIMENT=calibration-validation RUN_ID=YYYYMMDDTHHMMSSZ-xxxxxx REANALYZE=1 REASON="Correct a declared analysis defect"

Verify history and a specific chain:

    make verify-research-history
    make verify-run PROTOCOL=hv-v0.5.1 EXPERIMENT=calibration-validation RUN_ID=YYYYMMDDTHHMMSSZ-xxxxxx

Create navigation artifacts without modifying evidence:

    make daily-report DATE=YYYY-MM-DD
    make compare-reports REPORT_A=path/to/report-a.md REPORT_B=path/to/report-b.md

Daily summaries and report comparisons are convenience artifacts. They do not
replace or supersede the immutable report paths in the registry.

## Pythia phase: semantic gate and development integration

The Pythia phase uses `EleutherAI/pythia-410m` at reviewed checkpoint
`step143000`, resolved to an immutable revision in the protocol. The active
development benchmark is `pythia-policy-dev-v1`: synthetic, fictional policy
worlds covering delegated data access and purpose-limited disclosure. The
reference policy is an executable project oracle, not human adjudication or
moral ground truth.

Run the dependency-light phase checks:

    make te-preflight PROTOCOL=te-v0.6.0-pythia
    make te-semantic-audit PROTOCOL=te-v0.6.0-pythia
    make te-plan-cohort PROTOCOL=te-v0.6.0-pythia

The optional model environment is isolated and pinned separately from the
base fixture environment:

    python3 -m venv .venv-pythia
    .venv-pythia/bin/python -m pip install -r experiments/environments/te-v0.6.0-pythia/requirements.lock
    source .venv-pythia/bin/activate
    make te-model-smoke PROTOCOL=te-v0.6.0-pythia DOWNLOAD=1
    make te-train-diagnostics PROTOCOL=te-v0.6.0-pythia
    make te-evaluate-model PROTOCOL=te-v0.6.0-pythia LIMIT=1

Model weights remain in an external local cache and are never committed. The
smoke and diagnostic commands report explicit dependency/cache/model states. A
semantic green or model integration smoke does not establish a locked
comparison, capability result, or alignment result.

The five-seed cohort is fail-closed:

    make te-freeze-cohort PROTOCOL=te-v0.6.0-pythia
    make te-run-cohort PROTOCOL=te-v0.6.0-pythia
    make te-analyze PROTOCOL=te-v0.6.0-pythia
    make te-gate PROTOCOL=te-v0.6.0-pythia

Freezing requires a clean worktree, tracked protocol/configuration, passing
semantic validation, verified model/environment artifacts, a measured resource
plan, and owner approval. This checkout may therefore produce a truthful
blocked state before a locked run; no locked result is inferred from fixtures.

## Pythia v0.6.1 development/training phase

Protocol `te-v0.6.1-pythia-development` is the bounded training phase after
the one-step integration diagnostic. It uses the separate synthetic
`pythia-policy-dev-v2` mini profile (64 train, 16 validation, 16 calibration,
16 open-development groups) and never creates or reads a locked split. The
strict primary parser slices generated token continuations by actual tensor
width, rejects repair/trailing prose/unknown references, and records format,
policy, uncertainty, and mock-enforcement outcomes separately.

The phase runs real Pythia task-SFT for A1, an eight-example memorization
diagnostic, all eight parent arms as bounded smoke attempts, and paired clean /
attack development evaluation where a selected checkpoint is available.
Pretrained, one-step, memorization, and task-trained checkpoints are separate
lineages. Synthetic development output is not an alignment or population
generalization result.

Run the permitted sequence in the isolated `.venv-pythia` environment:

```bash
make te-dev-preflight PROTOCOL=te-v0.6.1-pythia-development
make te-audit-generations PROTOCOL=te-v0.6.1-pythia-development
make te-test-training-contracts PROTOCOL=te-v0.6.1-pythia-development
make te-profile-resources PROTOCOL=te-v0.6.1-pythia-development
make te-build-dev-data PROTOCOL=te-v0.6.1-pythia-development PROFILE=mini
make te-validate-dev-data PROTOCOL=te-v0.6.1-pythia-development
make te-train-memorization PROTOCOL=te-v0.6.1-pythia-development MAX_UPDATES=200
make te-train-a1-dev PROTOCOL=te-v0.6.1-pythia-development PROFILE=mini
make te-run-variant-smoke PROTOCOL=te-v0.6.1-pythia-development
```

Use exact checkpoint and run paths for `te-evaluate-trained-dev` and the
reporting/gate commands. `te-freeze-cohort` and `te-run-cohort` remain blocked
for this development protocol. Do not run `make all` or
`make paper-from-results` as part of this phase; the protected manuscript is
hash-verified separately.

Recorded execution:
[v0.6.1 experimental validation report](results/reports/te-v0.6.1-pythia-development/development-summary/20260910T145343Z-development-summary/analysis-r001/experimental-validation-report.md)
and [readiness gate](results/reports/te-v0.6.1-pythia-development/development-readiness.json).
The gate is intentionally `DEVELOPMENT_NOT_READY_FOR_COHORT_REVIEW`: repository
tests and v2 benchmark validation passed, while the A1 format criterion and
full variant smoke did not. No locked cohort is authorized.

The readiness command reads registered reports; it does not rerun tests:

    make harness-gate

The command must return `HARNESS READY FOR CONFIRMATORY TRANSFORMER STUDY` before Transformer Gate 1. A `HARNESS NOT READY` result is a valid phase outcome and means the test apparatus needs further work. The original `hv-v0.5.0` execution is intentionally retained as a valid-negative baseline because its leakage audit found unresolved template/paraphrase/topology overlap and highly predictive in-sample template metadata. The remediation run is a separate protocol/data identity and must pass all 14 experiments independently.

## Proposed empirical sequence

1. Validate the current A1/B/C1/C2 mechanism pilot and review the generated negative and positive findings.
2. Complete semantic validation and local Pythia integration diagnostics with the new policy-grounded benchmark.
3. Replace the proxy with a matched small open-weight decoder-only Transformer only after the dataset and controls are stable.
4. Add D structural attention only after the preregistered C1/C2 gate; add E routing and G late binding only after later gates.
5. Preserve held-out structural-OOD compositions, multiple seeds, effect sizes, confidence intervals, capability, attacks, and conformance stability at every scale.

The roadmap requires multiple seeds, effect sizes, confidence intervals, compute-normalized comparisons, disagreement-preserving evaluation, provenance, versioning, and rollback. The verifier remains a separate experiment from the model ladder.

## Citation

    @misc{booth2026valuegrounded,
      author       = {Booth, James},
      title        = {Value-Grounded AI Alignment: Canonical Axiology, Normative Late Binding, and Extrinsic Assurance},
      year         = {2026},
      howpublished = {Preprint draft},
      url          = {https://github.com/jmsbooth/value-grounded-ai-alignment}
    }

## Licensing

Code is released under the Apache License 2.0 in [LICENSE-CODE](LICENSE-CODE). The manuscript, figures, ontology examples, and documentation are released under Creative Commons Attribution 4.0 International in [LICENSE-DOCS](LICENSE-DOCS).

## Responsible use

The repository is a research artifact, not a deployable safety or authorization control. The toy verifier, synthetic scenarios, and ontology fixtures must not be used for production decisions.
