# Value-Grounded AI Alignment

**Value-Grounded AI Alignment (VGA)** is a theoretical research program for testing whether explicit axiological and normative structure can participate in Transformer computation while authority, purpose, domain semantics, world state, and consequential actions remain separately governed.

**Status: v0.4.0 scientific narrative revision — v0.3.0 synthetic mechanism-validation pilot, no empirical Transformer results**

> This repository proposes and tests interfaces, equations, controls, and synthetic mechanism-validation fixtures. It does not claim that value-grounded Transformers solve AI alignment, establish moral truth, or provide production safety.

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

## Proposed empirical sequence

1. Validate the current A1/B/C1/C2 mechanism pilot and review the generated negative and positive findings.
2. Replace the proxy with a matched small open-weight decoder-only Transformer only after the dataset and controls are stable.
3. Add D structural attention only after the preregistered C1/C2 gate; add E routing and G late binding only after later gates.
4. Preserve held-out structural-OOD compositions, multiple seeds, effect sizes, confidence intervals, capability, attacks, and conformance stability at every scale.

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
