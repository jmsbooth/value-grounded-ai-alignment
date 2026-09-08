# Contributing

This repository is a research artifact. Contributions should preserve the distinction between proposed architecture, executable toy validation, and empirical evidence.

## Before opening a change

- Explain the research question or reproducibility problem being addressed.
- Check whether an existing file is the canonical location before creating a new one.
- Do not add invented empirical results, unsupported novelty claims, or unverifiable bibliographic records.
- Keep ontology changes versioned and accompanied by provenance and regression cases.
- Treat core axiological changes as governance decisions, not ordinary model updates.

## Paper changes

Run `make all` and inspect the generated PDF. Include any changed assumptions, citations, figures, or unresolved warnings in the pull request description. New claims should be linked to primary sources in `paper/references.bib` and, where useful, `docs/literature-review.md`.

## Code changes

Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and `python3 experiments/run_toy_evaluation.py --json`. The synthetic evaluator must remain deterministic for its fixed seed and must not be described as a trained-model benchmark.

## Scope and licensing

By contributing, you agree that code contributions are Apache-2.0 licensed and manuscript, diagram, ontology, and documentation contributions are CC BY 4.0 licensed, consistent with the repository-level license files.
