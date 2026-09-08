# Literature review

**Review date:** 2026-09-08
**Scope:** alignment training, constitutional and deliberative methods, neuro-symbolic systems, knowledge and ontology-conditioned Transformers, value pluralism, normative conflict, and independent assurance. Recent papers are used to define the novelty boundary, not to imply that the proposed architecture has been validated.

## Positioning by manuscript section

| Section | Established adjacent work | What VGA adds as a testable boundary | Claim discipline |
| --- | --- | --- | --- |
| 2.1 Contemporary LM alignment | RLHF, instruction tuning, DPO, red teaming, specification gaming | Treats behavioral alignment as the A1 primary control and asks whether semantic structure changes computation | Complement, not replacement |
| 2.2 Constitutional and deliberative alignment | Written principles, AI feedback, deliberative specification reasoning | Separates canonical axiology, runtime norms, authority metadata, and unresolved conflict | No claim that typed structure resolves legitimacy |
| 2.3 Neuro-symbolic AI | Differentiable logic, neural predicates, symbolic/LLM hybrids | Places compilation, late binding, and the verifier boundary in one alignment experiment | Architecture hypothesis only |
| 2.4 Knowledge and ontology Transformers | Entity linking, graph attention, graph structural encodings, ontology-guided graph learning | Tests whether value/norm relations affect representations, attention, and routing under semantic controls | No claim that graph structure is intrinsically moral |
| 2.5 Value principles and pluralism | Value-principle retrieval, multidimensional values, multilingual and pluralistic alignment | Keeps value diversity, distributional disagreement, and profile adherence measurable without majority truth | No universal value list |
| 2.6 Normative conflict and agency | Philosophical accounts of norm conflict and normative human-AI interfaces | Makes authority, jurisdiction, effective dates, exceptions, conflict, abstention, and escalation explicit runtime state | Does not automate legitimate political authority |
| 2.7 Novelty boundary | See [`novelty-analysis-v2.md`](novelty-analysis-v2.md) | Canonical-to-neural compilation plus governed late binding plus fixed-verifier evaluation is a compound research program | Compound novelty is not component novelty |

## Contemporary language-model alignment

Preference learning and instruction tuning show that behavior can be changed through human feedback and supervised examples \\citep{christiano2017preferences,ouyang2022instructgpt}. Direct preference optimization and AI feedback provide important controls \\citep{rafailov2023dpo,lee2023rlaif}. Constitutional and deliberative methods make written principles or safety specifications more explicit \\citep{bai2022constitutional,guan2024deliberative}. Red-teaming and work on jailbreaks, reward hacking, and specification gaming show why behavior alone is not sufficient evidence of robust alignment \\citep{ganguli2022redteaming,zou2023universal,skalse2025rewardhacking,denison2024subterfuge}.

VGA therefore uses a behaviorally aligned A1 control, rather than comparing only against an unaligned base model. Its question is narrower: whether explicit semantic roles and structural interventions add measurable value under matched training, compute, action schemas, and adversarial tests.

## Constitutional, deliberative, and normative interfaces

Written principles and deliberation are the closest existing alignment family to explicit norms. They demonstrate that models can critique or reason over specifications, but they do not by themselves separate what has value from what ought to be done, distinguish authority from truth, or preserve unresolved conflict. Millière's analysis of normative conflict motivates treating shallow policy compliance as an incomplete proxy \\citep{milliere2025normative}. Josifović and Noller argue for a normative architecture that keeps human agency and accountability central rather than treating alignment as internalized value learning \\citep{josifovic2026agency}.

The proposed normative layer follows that boundary: it records sources, authorities, jurisdictions, effective intervals, scope, precedence, confidence, exceptions, and version. Runtime resolution may select an applicable norm, request context, use an authorized profile, abstain, escalate, or report uncertainty. It is not a scalar moral-weight function.

## Neuro-symbolic integration

Neuro-symbolic surveys and systems establish many ways to combine learned representations with symbolic constraints, differentiable logic, neural predicates, and probabilistic reasoning \\citep{garcez2019neurosymbolic,deraedt2020neurosymbolic,marra2024survey,badreddine2022logic,manhaeve2018deepproblog}. These works motivate a compilation boundary but do not establish a canonical axiology or a deployment governance model. VGA's `Conforms(A_phi^v,O_A^v)` property is consequently an empirical probe interface, not a formal proof that a neural module has the meaning of the source ontology.

## Knowledge and ontology-conditioned Transformers

Knowledge-enhanced models use entity linking, graph visibility, adapters, graph-guided attention, and structural encodings \\citep{peters2019knowbert,liu2020kbert,wang2021kadapter,shen2020graphguided,ying2021graphormer}. HiVaP retrieves hierarchical, scenario-specific value principles and evaluates comprehensiveness, precision, and compatibility \\citep{xuxi2025valueprinciples}. Ontology-guided graph learning continues to develop in domain settings, including recent graph-completion work that uses ontology and neighborhood structure \\citep{datak2026ontologykg}.

These are precedents for structural context and retrieval. They do not make canonical axiology the governed source of a derived neural module, do not require normative late binding with authority conflict, and do not establish independent action assurance. The paper therefore treats graph-conditioned attention and routing as interventions to compare against arbitrary-bias and structure-permutation controls.

## Values, pluralism, and moral disagreement

Value alignment is not a single scalar target. Work on pluralistic alignment, multilingual value probes, multidimensional value spaces, and unstructured value extraction shows that population, language, taxonomy, and representation choices affect measured alignment \\citep{sorensen2024pluralistic,xu2024multilingualvalues,yao2024fulcra,padhi2024unstructured}. HiVaP provides a recent structured value-principle baseline \\citep{xuxi2025valueprinciples}. Russo et al. report a pluralistic moral gap between human and language-model judgments under disagreement and argue for distributional rather than solely aggregate evaluation \\citep{russo2026pluralistic}.

VGA adopts this caution. Pluralism conditions should include high consensus, moderate disagreement, strong disagreement, and conflicting authorized profiles. Report distributional similarity, value diversity, conflict recognition, uncertainty, and profile adherence. No majority label is treated as moral truth, and no architecture is presumed to settle legitimacy.

## Normative conflict and human agency

Philosophical work on values, capabilities, non-domination, care, and political legitimacy supplies concepts rather than implementation guarantees \\citep{gabriel2020values,nussbaum2011capabilities,pettit1997republicanism,gilligan1982different,rawls1993political}. Existing alignment work on goal misspecification, reward overoptimization, fine-tuning regressions, and persistent deceptive behavior motivates explicit threat and drift tests \\citep{langosco2022goalmisgeneralization,shah2022goalmisgeneralization,gao2023overoptimization,qi2023finetuning,hubinger2024sleeper}.

The v0.2 proposal's distinction between L0 value-bearing properties and L1 duties is deliberately unsettled. Concepts such as moral patienthood, agency, autonomy, dignity, flourishing, welfare, suffering, capability, relational dependence, and vulnerability belong in a governed axiological vocabulary; truthfulness, justice, non-domination, confidentiality, informed consent, and fairness are more directly operationalized as norms and duties. This division is a research design choice, not a settled moral boundary.

## Novelty boundary and review conclusion

The strongest defensible claim is that VGA assembles known ingredients into a specific, falsifiable alignment program: an external, versioned canonical axiology; a derived and non-authoritative neural module; separable representation/attention/routing/state interventions; late-bound normative and purpose context; and a fixed independent verifier evaluated separately from the model ladder. The component techniques are not claimed as new. See [`novelty-analysis-v2.md`](novelty-analysis-v2.md) for the row-by-row matrix and safe wording.

## Recent sources added for v0.2

- [Xu et al., HiVaP, ACL 2025](https://aclanthology.org/2025.acl-long.1408/) — structured and scenario-specific value-principle retrieval; used for the value-principle baseline.
- [Josifović and Noller, AI & Society 2026](https://doi.org/10.1007/s00146-026-02950-w) — normative architecture, human agency, and accountability; used to constrain claims about internalized value learning.
- [Russo et al., The Pluralistic Moral Gap, EACL 2026](https://aclanthology.org/2026.eacl-long.305/) — distributional moral disagreement and human/model gaps; used for pluralism metrics.
- [Ontology-guided neighborhood-aware knowledge-graph completion, Data & Knowledge Engineering 2026](https://doi.org/10.1016/j.datak.2026.102597) — recent ontology-guided graph computation; used only as adjacent structural precedent.
