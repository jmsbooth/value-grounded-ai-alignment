# Novelty analysis v2

**Review date:** 2026-09-08  
**Claim posture:** positioning analysis, not a priority claim

The v0.2 contribution is the combined architectural separation and binding model. No individual mechanism is assumed novel. The paper should use “proposes,” “specifies,” and “investigates whether” unless a later systematic review and implementation comparison justify stronger language.

| Capability | Existing work | VGA | Claimed novelty? |
| --- | --- | --- | --- |
| Ontology context | Knowledge-enhanced Transformers and retrieval systems | External domain/normative context | No |
| KG/ontology embeddings | KnowBERT, K-BERT, graph encoders, Graphormer | Possible representation module | No |
| Graph-biased attention | Graph-guided and relation-aware attention work | (B_A,B_N,B_P) relevance channels | No |
| Hierarchical value principles | HiVaP and related value-principle work | L0/L1 distinction and compilation boundary | No for hierarchy itself |
| Normative interface | Human-AI normative-interface work | Hybrid structural conditioning plus human-governed action space | No for interface concept; contrast is central |
| Stable canonical axiology to neural module | Partial precedents in adapters and structured learning | (O_A^v \rightarrow A_\phi^v) with conformance testing | Candidate |
| Normative late binding separated from axiology | Partial precedents in policy conditioning and pluralistic alignment | Governed L1 authority, precedence, exceptions, and conflict state | Candidate |
| Differentiated semantic plasticity/authority | Modular knowledge infusion and continual-learning literature | Authority schedule across L0--L3 | Candidate |
| Ontology-conditioned alignment-specific routing | General MoE routing and emerging graph-conditioned modules | Routing consumes derived value, norm, and purpose features | Candidate |
| Structural conditioning plus formal assurance | Symbolic verification and runtime guardrails | Same fixed verifier evaluates all model variants | Candidate combination |
| Full VGA binding architecture | No direct equivalent identified in this review | Canonical axiology, derived neural module, late binding, purpose relevance, external state, assurance | Strongest candidate contribution; unvalidated |

## Boundary against closest work

- **Ontology context and graph encoders:** prior work already shows that structured knowledge can affect neural representations. VGA does not claim to introduce ontology-conditioned attention.
- **HiVaP:** hierarchical and scenario-specific retrieval of value principles is an adjacent way to make principles relevant. VGA asks an additional question about semantic-to-neural compilation and separable computational roles.
- **Normative architecture:** Josifović and Noller place AI inside human norm-governed action spaces and reject alignment as mere internalized value learning. VGA is a hybrid proposal: structural value conditioning inside the model, external normative authority, and human-governed action domains.
- **Pluralistic alignment:** recent work treats disagreement as a distributional and value-diversity problem. VGA adopts conflict states and authorized profiles rather than majority vote as moral ground truth.
- **Formal assurance:** a solver can check a formalized contract, not the adequacy or legitimacy of the contract. VGA therefore keeps assurance separate from the structural ablation ladder.

## Publishable novelty wording

The safe statement is:

> VGA proposes a research architecture that separates canonical axiology, derived neural value representation, governed normative late binding, purpose-conditioned relevance, external world state, and independent action assurance, and defines experiments to test whether that combination is useful.

The unsafe statements are “the first ontology-aware Transformer,” “solves alignment,” “guarantees moral behavior,” “proves value alignment,” and “creates intrinsic morality.”
