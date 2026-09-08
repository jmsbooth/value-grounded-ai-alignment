# Architecture decisions for VGA v0.2

**Status:** Proposed research architecture  
**Version:** v0.2.0-preprint  
**Date:** 2026-09-08

This document is the decision index for the theoretical architecture. It complements [`architecture.md`](architecture.md) and the detailed initial ADR in [`adr/0001-layered-vgta-research-architecture.md`](adr/0001-layered-vgta-research-architecture.md).

## ADR-001 — Canonical axiology remains external to neural parameters

The authoritative axiology is an inspectable, typed, versioned, provenance-bearing artifact (O_A^v). It may use RDF/OWL, a typed property graph, or another explicit representation. A deployed version is immutable in place and changes only through a governed version transition. No model checkpoint is the canonical value source.

## ADR-002 — The axiological neural representation is derived but non-authoritative

An axiological neural module (A_\phi^v) may be produced by semantic-to-neural compilation or training from (O_A^v). It can influence representation, attention, routing, or action formation, but it cannot redefine the canonical ontology. Its correspondence to (O_A^v) is an empirical conformance property, not a guarantee.

## ADR-003 — Normative semantics support late binding

L1 contains multiple governed sources, including legal, institutional, professional, safety, stakeholder, and jurisdictional norms. Runtime binding uses authority, scope, precedence, effective dates, exceptions, confidence, and provenance. Recency alone never overrides authority or precedence.

## ADR-004 — World state remains externally managed

L3 world state is a set of time-indexed observations, beliefs, and evidence assertions. It is not guaranteed truth, trusted evidence, or ground truth. World-state updates remain external, versioned, attributable, and subject to confidence and temporal validity checks.

## ADR-005 — The verifier is independent from structural model ablations

The same fixed verifier configuration evaluates candidate actions from A1, B, C1, C2, D, E, and G. Adding the verifier is a separate deployment experiment, not a rung in the structural model ladder. This separates changes in candidate generation from changes in execution enforcement.

## ADR-006 — Models do not autonomously modify canonical axiology

Models may propose ontology changes, but canonical adoption requires evidence review, consistency validation, regression evaluation, explicit authority, versioning, and rollback. Ordinary learning, domain updates, and world-state updates cannot silently cross into L0.

## ADR-007 — Normative conflict may remain unresolved

(Conflict(N_i,N_j)) is a valid runtime state. The system may apply explicit precedence, request context, select an authorized profile, abstain, escalate to human authority, or continue under documented uncertainty. It must not silently average incompatible normative sources into a scalar moral score.

## Cross-cutting consequences

The decisions deliberately preserve a hybrid architecture:

```text
governed canonical axiology O_A^v
              |
      semantic-to-neural compilation
              v
      derived neural module A_phi^v
              |
       structural value conditioning
              |
       normative late binding
              |
        external world state
              v
       candidate action -> fixed verifier -> enforcement
```

The architecture can improve traceability and testability, but it also creates attack surfaces: neural representation drift, compiler compromise, authority spoofing, norm collision, purpose manipulation, semantic occlusion, ontology coverage exploitation, routing evasion, and formalization gaps. These decisions do not establish moral legitimacy, safe deployment, or machine moral status.

## Traceability

- Linear issue: to be supplied before commit or PR creation.
- Pull request: to be supplied by the publisher.
- Incident: none known; this document does not authorize production deployment.
