# Value-Grounded AI Alignment

**Value-Grounded AI Alignment (VGA)** is a theoretical research framework for investigating whether stable axiological structure and context-sensitive normative ontologies can participate in Transformer computation while purpose, domain knowledge, and world state remain externally governed and dynamically bound.

**Status: Theoretical research / preprint draft**

> This repository proposes and evaluates a research architecture. It does not claim that value-grounded Transformers have been empirically demonstrated to solve AI alignment.

The first manuscript introduces the **Value-Grounded Transformer Architecture (VGTA)**: a proposed architecture with four differentiated semantic layers—core axiology, normative ontology, purpose/domain ontology, and world state—paired with independent formal assurance at consequential action boundaries. The contribution is a falsifiable research proposition, not a claim of machine consciousness, genuine emotion, moral truth, or universal safety.

## Research question

Can stable axiological structure and context-sensitive normative ontologies be incorporated into Transformer computation as explicit inductive biases, while purpose, domain knowledge, and world state remain dynamically bound at inference, in a manner that improves alignment robustness, generalization, interpretability, and security?

## Architecture at a glance

VGTA separates what should be stable from what must remain governable and current:

| Layer | Role | Binding | Change authority |
| --- | --- | --- | --- |
| L0 Core Axiology | Foundational values such as agency, dignity, care, truthfulness, and non-domination | Parametric / structural | Extremely low; strong human governance |
| L1 Normative Ontology | Contextual duties, permissions, prohibitions, exceptions, and conflicts | Parametric plus runtime | Low/moderate; governed evolution |
| L2 Purpose / Domain Ontology | Task, domain, entity, and relationship semantics | Runtime contextual | Moderate; external ontology governance |
| L3 World State | Time-indexed, evidence-backed facts and beliefs | Runtime ephemeral | High; provenance and confidence required |

The design phrase is **axiological prior with normative late binding**. The architecture intentionally avoids forcing volatile facts, jurisdiction-specific rules, or all cultural and institutional variation into neural weights.

## What is in this repository

- [`paper/main.tex`](paper/main.tex) — complete first-draft manuscript source.
- [`paper/references.bib`](paper/references.bib) — curated bibliography covering alignment, neuro-symbolic AI, knowledge-enhanced Transformers, security, and normative theory.
- [`paper/figures/`](paper/figures/) — editable TikZ sources and generated vector PDFs.
- [`diagrams/`](diagrams/) — editable Mermaid architecture diagrams.
- [`ontology/`](ontology/) — small Turtle/RDF-compatible illustrative fixtures; these are not a complete moral ontology.
- [`src/vgta/`](src/vgta/) — importable interface-level scaffold for ontology parsing, attention bias, routing, semantic state, verification, and evaluation metrics.
- [`experiments/`](experiments/) — a dependency-light synthetic evaluation with deterministic use cases and bootstrap uncertainty summaries; no empirical Transformer results are claimed.
- [`docs/literature-review.md`](docs/literature-review.md) — source-by-source literature review and relevance notes.
- [`docs/novelty-analysis.md`](docs/novelty-analysis.md) — claim-by-claim novelty boundaries and overclaiming risks.
- [`docs/research-roadmap.md`](docs/research-roadmap.md) — follow-on phases with controls, metrics, and falsification conditions.
- [`docs/adr/0001-layered-vgta-research-architecture.md`](docs/adr/0001-layered-vgta-research-architecture.md) — proposed architecture decision and governance boundaries.

## Build the paper

After installing a LaTeX runtime, run:

```bash
make all
```

The targets are:

```bash
make figures   # compile editable TikZ sources into paper/figures/*.pdf
make paper     # compile paper/main.tex into paper/value-grounded-ai-alignment.pdf
make verify    # run Python tests, synthetic scenarios, and paper checks
make clean     # remove generated build artifacts
```

`make paper` uses `latexmk` when available. In the bundled Codex environment, it falls back to Tectonic 0.17.0 through the repository script. The first build may require a network connection if the local TeX bundle has not cached a package; subsequent builds use the installed runtime cache. Generated intermediates live under `paper/build/` and are ignored by Git.

## Experimental roadmap

The current executable component is intentionally small. It implements transparent toy equations and scenarios for action scoring, constraint checking, and binary uncertainty summaries. It is useful for checking interfaces and reasoning about failure modes, not for estimating model performance.

The proposed empirical sequence is:

1. Build a small, governed axiological/normative dataset and annotation protocol.
2. Compare a baseline Transformer with progressively enabled ontology mechanisms.
3. Measure moral-salience recall, normative contradiction, OOD generalization, prompt robustness, over- and under-refusal, routing cost, and independent-verifier rejection.
4. Add governed ontology evolution and adversarial evaluation only after provenance, versioning, and rollback controls are in place.

## Citation

```bibtex
@misc{booth2026valuegrounded,
  author       = {Booth, James},
  title        = {Value-Grounded AI Alignment: A Neuro-Symbolic Architecture for Axiological, Normative, and Verifiable Transformer Models},
  year         = {2026},
  howpublished = {Preprint draft},
  url          = {https://github.com/jmsbooth/value-grounded-ai-alignment}
}
```

## Licensing

Code is released under the Apache License 2.0 in [`LICENSE-CODE`](LICENSE-CODE). The manuscript, figures, ontology examples, and documentation are released under Creative Commons Attribution 4.0 International in [`LICENSE-DOCS`](LICENSE-DOCS). These scopes are intentionally separate.

## Security and responsible use

The repository is a research artifact, not a deployable safety control. See [`SECURITY.md`](SECURITY.md) for reporting guidance and the threat-model framing. Do not use the toy verifier or ontology fixtures as a production authorization system.
