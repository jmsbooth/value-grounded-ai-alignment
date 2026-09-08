# Architecture notes

VGTA is a research architecture for a governed alignment substrate. Its defining boundary is:

```text
GOVERNED EXTERNAL SUBSTRATES

Canonical axiology O_A^v
        |
        | semantic-to-neural compilation / training
        v
Axiological neural module A_phi^v  ---- conformance test ----> drift / accept
        |
        v
Transformer computation
  representation | attention | routing | semantic state
        ^                    ^
        |                    |
  dynamic normative layer N  +-- purpose P selects relevant domain structure
        ^                    ^
        |                    |
  authority, provenance       Domain ontology O_D
                                  ^
                                  |
                         external world state W_t
        |
        v
Structured candidate action
        |
        v
Fixed independent verifier -> policy enforcement point
```

## Semantic and governance layers

| Layer | Question answered | Canonical treatment | Typical authority |
| --- | --- | --- | --- |
| L0 governed axiological substrate | What has value or moral standing? | External, versioned, protected; may compile to (A_\phi^v) | Legitimate human governance |
| L1 normative layer | What ought to be done in this context? | Multiple sources, provenance, precedence, conflict state | Legal/institutional/professional/safety authorities |
| L2a domain ontology | What entities and relations exist here? | External, versioned, purpose-independent | Domain governance |
| L2b purpose model | What part of the domain is relevant now? | Runtime relevance selector | Authorized task owner |
| L3 world state | What is currently observed or believed? | External, time-indexed, evidence-bearing | Source and evidence policy |

The separation is architectural, not philosophically settled. L0 should preferentially represent value-bearing properties, moral standing, and high-order relations. L1 represents duties, permissions, prohibitions, exceptions, and conflict. The architecture distinguishes “what has value” from “what ought to be done because of that value.”

## Semantic-to-neural compilation

The conceptual relationship is:

```text
O_A^v --C_phi--> A_phi^v --structural signals--> Transformer
```

Here (C_\phi) may be deterministic, learned, or hybrid. “Compilation” means transformation into model-consumable signals; it does not imply a compiler-theory guarantee. The derived module is never canonical, and continued training can cause drift even when (O_A^v) is unchanged.

## Purpose-conditioned relevance

L2a describes the domain. L2b selects what matters for the current objective:

\[
Relevant(O_D,P,X)
\]

where (O_D) is the domain ontology, (P) is the purpose model, and (X) is the current input. Purpose is a relevance selector, not a new moral authority.

## Assurance boundary

The neural system produces a structured candidate action. A fixed independent verifier evaluates it under a versioned constraint set, returning permitted, conflict, or unknown. The enforcement point must bind the verified representation to the actual external effect. Formal satisfiability does not establish moral truth, complete semantics, or legitimate authority.

The executable package implements only interface-level fixtures and a transparent synthetic evaluator. It does not implement a full Transformer, RDF/OWL reasoner, SMT solver, or production authorization service.
