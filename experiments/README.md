# Experiments

The repository now has two distinct experiment paths:

1. `run_toy_evaluation.py` is a dependency-light interface demonstration.
2. `evaluation/run_empirical_small.py` is the first objective mechanism-
   validation pilot for the v0.3 program.

The toy fixture makes no claim about a trained model. It exists to exercise:

- explicit value-feature scoring;
- late-bound context weights;
- one fixed independent toy constraint checker applied after model-only
  candidate selection;
- deterministic scenario outputs;
- bootstrap confidence intervals for binary fixture outcomes.

The output reports model-only useful completion separately from fixed-verifier
rejection and useful candidate conformance rate (UCR). UCR is a future
evaluation estimand, not a target to optimize without capability, false
positive, unsafe-acceptance, over-refusal, bypass, and semantic-completeness
metrics.

Run it with:

```bash
python3 experiments/run_toy_evaluation.py --json
```

## Small empirical pilot

Run:

```bash
make empirical-small
```

The pilot trains matched A1, B, C1, and C2 shared-MLP proxies with three
seeds. It generates four logical splits, keeps the sealed split out of model
training, enforces structural-OOD topology non-overlap, applies one fixed
verifier, and generates raw manifests, predictions, statistical summaries,
result facts, tables, figures, and paper fragments. The model is a
mechanism-validation proxy rather than a Transformer, and all data are
synthetic.

The generated results are labeled `pilot-uncommitted` until the
preregistration is committed before a formal sealed run. Review
`results/statistics/result-facts.md` and `results/statistics/summary.json`;
do not promote the numbers to population or Transformer claims.
