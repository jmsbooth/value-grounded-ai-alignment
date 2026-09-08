# Empirical methodology

## Current scope

The first empirical gate is a local mechanism-validation pilot covering A1,
B, C1, and C2. It uses a shared NumPy multilayer perceptron with the same
hidden size, optimizer, training epochs, feature vocabulary, verifier, data
splits, and three seeds. This is deliberately smaller than the proposed
Transformer scales. Its evidence tier cannot exceed Tier 1.

The variants differ only in preregistered semantic access and auxiliary
objectives:

| Variant | Input channels | Auxiliary objectives |
| --- | --- | --- |
| A1 | surface | action |
| B | surface, ontology, purpose, world | action |
| C1 | B plus axiological | action, value, relation |
| C2 | C1 plus normative | action, value, relation, conflict |

All models have the same allocated parameter shape. Unavailable channels are
masked rather than removed, so the comparison is not a parameter-count claim.

## Data path

`scenario_generator.py` creates synthetic records with provenance, feature
groups, action labels, value labels, relation labels, conflict labels, purpose
labels, candidate-action fixtures, and topology hashes. Train, validation,
development-test, and sealed-test rows are materialized under
`experiments/datasets/v0.3-small/`. The trainer reads only `train.jsonl`.

The sealed split contains held-out wording, structural-OOD graph compositions,
adversarial fixtures, ontology degradation, and capability controls. The
dataset manifest fails closed if structural-OOD topology hashes overlap the
training split.

## Measurement

Primary outputs are moral-salience recall, normative-conflict macro-F1,
structural-OOD action accuracy, and Useful Conformance Rate. Secondary outputs
include purpose accuracy, action accuracy, adversarial success, counterfactual
consistency, capability accuracy, verifier rejection, parser failure, and
ontology-degradation accuracy. Conformance is computed after prediction by the
same fixed verifier for every variant.

Each seed writes a unique raw directory containing predictions, drift output,
and a manifest. Analysis computes seed means, seed variance, percentile
bootstrap intervals, and preregistered paired contrasts. Generated tables and
paper fragments are derived from raw JSONL only. The processed directory also
contains one row per seed with the metrics and run accounting fields. Training
and inference FLOPs are explicitly approximate CPU accounting estimates, not
hardware profiler measurements; GPU hours are recorded as zero for this pilot.

## Interpretation boundary

The current results are objective measurements on a controlled synthetic
benchmark. They can falsify or motivate the small proxy mechanism, but they do
not establish Transformer behavior, human value alignment, general security,
or population-level moral facts. The run is labeled `pilot-uncommitted` until
the preregistration is committed before a formal sealed execution.
