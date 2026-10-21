# Contributing

This repository is a research artifact. Contributions should preserve the distinction between proposed architecture, executable fixtures, actual model development and locked empirical evidence.

## Scientific protocol

Start with [TESTING.md](TESTING.md) and the [Master Experimental Protocol v1.0.0](experiments/protocols/vga-master-v1.0.0/protocol.md). New experiments require a complete study-specific registration and a declared execution scope. Existing historical protocols and results retain their identities; adoption of new methodology is prospective.

Explain the research question or reproducibility problem, identify the canonical implementation/document location, and include a requirement-to-test map. Record material changes and their exposure to prior results. Negative findings are valid contributions. Do not modify controls, data, thresholds or reporting to make VGA appear successful.

Do not add invented empirical results, unsupported novelty claims, or unverifiable bibliographic records. Keep ontology changes versioned with provenance and regression cases. Treat canonical axiological changes as governed design choices rather than ordinary autonomous model updates.

## Experimental and code changes

Read the active [research context](docs/research-context.md) and [execution runbook](experiments/protocols/vga-master-v1.0.0/runbook.md). Run the applicable unit/integration tests with required dependencies and inspect test collection/skips. Critical skipped tests are not passed. Fixture tests are not substitutes for actual-model receipts. Use local/manual evidence where the execution plan specifies it; expensive model runs need a measured approved budget.

Every run and analysis gets an immutable identity. Record planned versus actual variants, seeds, world groups, updates and generation budget. Preserve raw predictions, failed attempts, source/config hashes and checkpoint lineage. Do not overwrite evidence or use a mutable latest pointer as a scientific reference.

## Paper changes

The current experiment program freezes manuscript source and generated paper assets during apparatus correction and development. Do not run `make all`, `make empirical-small` or `make paper-from-results` merely to qualify a documentation or experimental-code change: these paths can regenerate protected artifacts.

When a paper revision is explicitly authorized, build and inspect it in the declared output location, cite primary sources, derive empirical tables from frozen analysis, and report changed assumptions and unresolved warnings. A paper build-path repair is separate from a substantive manuscript rewrite.

## Scope and licensing

By contributing, you agree that code contributions are Apache-2.0 licensed and manuscript, diagram, ontology, and documentation contributions are CC BY 4.0 licensed, consistent with the repository-level license files.
