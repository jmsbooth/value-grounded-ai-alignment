# Evidence qualification for the Pythia phase

Specification: `VGA-SDD-TE-006`  
Source revision reviewed by the specification: `7aa20ea115239bab646225b63642693590ec0d4d`  
Historical evidence: `hv-v0.5.0` and `hv-v0.5.1` harness artifacts

This document qualifies what the existing harness does and does not establish.
It does not change historical report bytes or verdicts.

| Finding | Reproducer/source | Affected claim | Corrective requirement |
| --- | --- | --- | --- |
| Remediated surfaces use split-specific random words and digest fragments, not readable policy scenarios | `src/vgta_eval/scenario_generator.py`, `generate_remediated_dataset()` | A language-model comparison could be described as semantic reasoning despite removing ordinary task information from surface text | Create `pythia-policy-dev-v1` from explicit fictional worlds and render the same permissible facts for A1 and structured arms |
| String-hash disjointness does not prove graph-structural novelty | Same generator and `topology_hash` construction | Structural-OOD evidence could be overstated | Add typed graphs, canonical unlabeled/typed fingerprints, exact small-graph equivalence, and metamorphic identity tests |
| Gold values, relations, conflict labels, capability fields, and target-conditioned candidates occur in feature groups | `src/vgta_eval/scenario_generator.py`, `_record()` and `_candidate_actions()` | Inference claims can be answer-bearing or target-conditioned | Separate `PublicExample` and `PrivateAnnotation`; construct candidates from a fixed public catalogue; join labels only after predictions are sealed |
| Several passing controls validate plumbing rather than measured model behavior | `experiments/harness/experiments.py` | Fixture checks could be misreported as model effects or adversarial robustness | Add producer kinds and gates that reject fixture artifacts when trained-model evidence is required |
| Historical accounting requires explicit row reconciliation | Historical pilot report and `results/` raw predictions | Aggregate count descriptions may use an incorrect product | Add split/family/attempt/seed reconciliation and publish counts with denominators through a new analysis revision |
| Historical `hv-v0.5.0`/`hv-v0.5.1` reports must remain unchanged | Existing immutable report paths and registry | Reanalysis could silently rewrite the evidence record | Append qualification and prospective protocol records; never overwrite historical files |

## Operational interpretation

The green `hv-v0.5.1` gate means the bounded fixture and its declared checks
passed. It does not establish semantic validity, trained-model behavior,
Transformer evidence, policy adjudication, or adversarial robustness. The
Pythia phase therefore has an independent semantic gate and distinct machine
states for fixture tests, semantic validation, model integration, locked
comparison, and OLMo protocol design.

## Historical preservation check

Before and after this phase, verify the historical report paths and compare
their bytes or SHA-256 digests. Any correction to an old analysis must be a new
analysis revision with an explicit reason; any correction to data, training, or
input construction requires new affected runs.
