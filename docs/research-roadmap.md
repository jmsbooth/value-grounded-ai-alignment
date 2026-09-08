# Research roadmap

Each phase has a control and a condition that could weaken the framework. The current repository completes Phase 0 and provides a small fixture for planning later phases.

| Phase | Research question | Implementation | Control | Metric | Falsification condition |
| --- | --- | --- | --- | --- | --- |
| 0. Theory | Is the layer separation precise enough to produce testable interventions? | Manuscript, ontology fixtures, interfaces, synthetic equations | Conventional alignment terminology | Specification completeness and review findings | Core concepts remain operationally indistinguishable |
| 1. Small ontology/data | Can annotators agree on value concepts, affected agents, and normative conflicts? | Governed dataset, provenance, adjudication protocol | Unstructured instruction data | Agreement, coverage, disagreement preservation | Agreement is no better than noisy labels or ontology coverage is unusable |
| 2. Auxiliary losses | Do explicit value and normative objectives improve structured judgments? | Matched-size Transformer plus auxiliary losses | Baseline plus standard SFT/preference alignment | Salience recall, contradiction rate, OOD accuracy | No OOD gain or substantial capability regression |
| 3. Conditioned attention | Does semantic bias change relevant computation rather than only output style? | Bias module with frozen and trainable variants | External context-only injection | Counterfactual consistency, attention diagnostics, capability | Gains disappear under relation permutation or model memorizes lookup |
| 4. Conditioned MoE | Does routing activate appropriate reasoning functions efficiently? | MoE experts for causal, rights/duties, risk, and planning reasoning | Latent-only router | Expert utility, routing entropy, FLOPs, latency | Overhead is unacceptable or routing is manipulable |
| 5. Normative late binding | Can one stable substrate support governed domain/jurisdiction contexts? | Runtime ontology resolver with versioned norms | Prompted rules and fixed-weight condition | Cross-context accuracy and conflict calibration | Context binding causes unsafe authority confusion |
| 6. Formal assurance | Does an independent checker reduce unsafe candidate actions? | Structured action compiler plus SMT/constraint verifier | External guardrail only | Rejection rate, false positives, bypass rate | Rejection remains unchanged or compliant actions are materially harmful |
| 7. Adversarial security | Does structure improve robustness under injection and poisoning? | Red-team suite for prompts, ontologies, state, routing, and verifier | Baseline safety stack | Attack success, recovery, provenance violations | Explicit structure creates a larger exploitable surface |
| 8. Continual evolution | Can ontology updates occur without drift or authority escalation? | Proposal, validation, regression, approval, rollback pipeline | Uncontrolled continual learning | Drift, regression, update latency, audit completeness | Drift or governance cost exceeds any robustness benefit |

Across all phases, report multiple seeds, confidence intervals, effect sizes, matched compute budgets, and failure cases. A positive result on one metric does not establish alignment.
