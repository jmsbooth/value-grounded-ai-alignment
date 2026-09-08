# Architecture notes

VGTA is specified as a research intervention over a standard Transformer, not as a claim that a particular implementation is already validated. The conceptual data path is:

```text
L0 core axiology ──────────────┐
L1 normative ontology ─────────┼─> semantic integration ─> Transformer computation
L2 purpose/domain ontology ────┤             │
L3 world state ────────────────┘             v
                                  structured candidate action
                                             │
                                  constraint specification
                                             │
                                  independent verifier -> execute / reconsider
```

The proposed mechanisms are separable ablations:

1. concept and relation representations;
2. ontology-conditioned attention bias;
3. ontology-conditioned sparse expert routing;
4. optional episode semantic state;
5. auxiliary consistency, normative inference, and moral-salience objectives;
6. late-bound external ontology and world-state context;
7. independent formal assurance at high-consequence boundaries.

The repository scaffold implements only the interfaces and a transparent synthetic evaluator. It does not claim differentiable end-to-end training, formal verification completeness, or production authorization semantics.
