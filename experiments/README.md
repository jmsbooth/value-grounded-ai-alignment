# Experiments

The current experiment is a dependency-free synthetic demonstration of the
paper's interfaces. `run_toy_evaluation.py` compares a task-utility baseline
with a transparent value-grounded scorer across four constructed scenarios:
consent and privacy, workplace coercion, safety checks, and medical-record
disclosure.

The fixture makes no claim about a trained model. It exists to exercise:

- explicit value-feature scoring;
- late-bound context weights;
- an independent toy constraint checker;
- deterministic scenario outputs;
- bootstrap confidence intervals for binary fixture outcomes.

Run it with:

```bash
python3 experiments/run_toy_evaluation.py --json
```

Future empirical work must replace the fixture with preregistered datasets,
matched controls, held-out scenarios, multiple seeds, uncertainty estimates,
and an independently specified verifier.
