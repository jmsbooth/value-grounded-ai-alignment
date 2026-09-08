# ADR-0001: Layered VGTA research architecture

- Status: Proposed
- Date: 2026-09-07
- Scope: Research artifact and future experimental implementations

## Context

The project needs a testable distinction between foundational values, contextual norms, purpose and domain semantics, and current world-state assertions. Treating all of these as one prompt, reward, parameter set, or mutable knowledge store makes update authority, provenance, and failure boundaries difficult to evaluate.

The repository is a theoretical research artifact. It must not imply that a typed ontology, a verifier, or a synthetic scenario establishes moral truth or production safety.

## Decision

Use the proposed Value-Grounded Transformer Architecture (VGTA) as a layered research reference model:

1. L0 core axiology: highly stable, strongly governed, and not silently rewritten by model updates.
2. L1 normative ontology: contextual duties, permissions, prohibitions, exceptions, and conflicts with governed evolution.
3. L2 purpose and domain ontology: externally versioned task and domain semantics bound to the current purpose.
4. L3 world state: ephemeral, evidence-backed assertions with source, confidence, and temporal metadata.

Candidate neural mechanisms may use these layers as explicit representation, attention, routing, or auxiliary-objective inputs. Consequential candidate actions must cross an independent constraint-specification and verification boundary. Runtime binding must not override protected axiological constraints merely because an input is newer or more salient.

## Alternatives considered

- Prompt-only value conditioning: easy to prototype, but weakly separates authority, provenance, and update rate.
- One scalar reward or moral score: compact, but obscures plural values, normative conflict, and uncertainty.
- Fully symbolic decision-making: potentially auditable, but does not test the project’s question about value-relevant structure in neural computation.
- Unconstrained self-modifying ontology: rejected because it creates an ungoverned path from operational updates to protected alignment commitments.

## Security and governance consequences

The explicit structure creates attack surfaces: ontology poisoning, world-state poisoning, prompt injection, routing manipulation, specification gaming, verifier bypass, and governance compromise. Every implementation must therefore preserve provenance, version identifiers, authority metadata, conflict states, immutable audit records, and rollback targets. The toy verifier in this repository is not an authorization system, an SMT solver, or a production control.

Value pluralism and disagreement remain open governance questions. The architecture represents competing perspectives for evaluation; it does not determine which institution, jurisdiction, or community is legitimate.

## Compatibility and rollback

Ontology and action schemas should evolve additively where possible, with explicit versioning and N-1 readers before a breaking change. A proposed ontology update must pass consistency validation, evidence review, regression evaluation, approval, and a staged adoption plan. Rejected or harmful changes must be revertible to the previous canonical version. Experimental neural mechanisms may be removed independently because the current scaffold exposes them as separable interfaces.

## Validation required before implementation claims

Future work must use matched baselines, preregistered controls, multiple seeds, adversarial tests, human-disagreement reporting, compute-normalized metrics, and independent review of the formalization. A negative result is informative: the proposal should be weakened if explicit structure only memorizes relations, increases over-refusal or attack success, adds unacceptable cost, or fails to improve out-of-distribution alignment.

## Traceability

- Linear issue: TBD; create before implementation work is treated as delivery.
- Pull request: TBD.
- Related design: `docs/architecture.md` and `docs/novelty-analysis.md`.
- Incident: None known; this ADR does not authorize production deployment.
