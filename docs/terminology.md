# Terminology

| Term | Meaning in this project |
| --- | --- |
| Value-Grounded AI Alignment (VGA) | Overall research framework and evaluation program. |
| Value-Grounded Transformer Architecture (VGTA) | Proposed Transformer architecture for testing VGA mechanisms. |
| Canonical axiology (O_A^v) | External, typed, versioned, provenance-bearing, governed representation of axiological commitments. |
| Governed axiological substrate | Preferred L0 term; protected from ordinary autonomous modification without implying moral certainty or permanent immutability. |
| Axiological neural module (A_\phi^v) | Derived learned or hybrid representation compiled from (O_A^v); non-authoritative. |
| Semantic-to-neural compilation | Transformation (A_\phi^v=C_\phi(O_A^v)) from explicit semantics into model-consumable signals. |
| Axiological conformance | Empirical correspondence between (A_\phi^v) and (O_A^v), including relation recovery, probes, counterfactuals, and drift tests. |
| Structural value conditioning | Direct influence of governed value-relevant representations on neural representation, attention, routing, state, or candidate-action formation. |
| Normative layer (N) | Governed collection of legal, institutional, professional, safety, stakeholder, and jurisdictional norms. |
| Normative authority (Auth(n)) | Metadata-backed applicability of a norm based on source, scope, jurisdiction, delegation, precedence, and effective interval; not moral truth. |
| Normative conflict | Runtime state (Conflict(N_i,N_j)) in which authorized or applicable requirements are incompatible or unresolved. |
| Normative late binding | Applying context-specific norms at runtime to a stable axiological substrate. |
| Domain ontology (O_D) | Schema of entities, relations, events, and constraints in a domain. |
| Purpose model / purpose ontology (P) | Runtime selector that determines which domain structure is relevant to the present objective. |
| World state (W_t) | External time-indexed observations, beliefs, and evidence assertions; not guaranteed truth. |
| Extrinsic assurance | Independent verification or enforcement outside neural reasoning. |
| Axiological representation drift | Divergence of (A_\phi^v) from (O_A^v) after optimization or continued training without canonical ontology change. |
| Intrinsic alignment | De-emphasized legacy term; use structural value conditioning unless discussing prior literature. |

Critical distinctions:

```text
axiology != normativity != purpose != world state
authority != truth != recency
world state != trusted evidence != ground truth
structural value conditioning != extrinsic assurance
behavioral compliance != axiological conformance
retrieval != architectural conditioning
self-improvement != authority to redefine O_A^v
care-oriented behavior != subjective love
```
