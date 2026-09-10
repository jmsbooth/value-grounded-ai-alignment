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

## Versioned harness validation

The original `v0.5.0` harness phase is preserved as a failed baseline. The
remediation phase is `hv-v0.5.1` and is executed as separate experiments rather
than one mutable report. Each `make experiment EXP=...` invocation creates an
immutable run under `results/raw/hv-v0.5.1/<experiment>/<run-id>/`, a versioned
analysis under `results/analyses/`, and a report under `results/reports/`. The
append-only registries and human index live under `results/registry/`.

The active harness defaults to `v0.4-structure-heldout`; use
`VGTA_DATASET_VERSION=v0.4-structure-heldout` explicitly in automation or CI.
The leakage rule fits metadata predictors on `train` and evaluates them only
on `sealed-test`; it does not score held-out identifiers in-sample.

Use `make harness-gate` to evaluate registered readiness. It reads evidence
artifacts and never substitutes a fresh test run for a missing report.

## Pythia v0.6.1 development/training phase

The active next protocol is `te-v0.6.1-pythia-development`, with the prior
`te-v0.6.0-pythia` integration report preserved. It is separate from the
historical MLP and `hv-v0.5.x` harness artifacts. The v0.6.1 benchmark is
`pythia-policy-dev-v2`: readable fictional policy worlds, explicit observed
facts and rules, typed graphs, a fixed public action catalogue, private
annotations, and an oracle independent of template names and candidate
answers. Its mini profile has 64/16/16/16 grouped rows for train,
validation, calibration, and open development; it has no locked split.

Run the lightweight path first:

```bash
make te-preflight
make te-semantic-audit
make te-plan-cohort DEVELOPMENT=1
```

Run the bounded development path:

```bash
make te-dev-preflight PROTOCOL=te-v0.6.1-pythia-development
make te-audit-generations PROTOCOL=te-v0.6.1-pythia-development
make te-test-training-contracts PROTOCOL=te-v0.6.1-pythia-development
make te-profile-resources PROTOCOL=te-v0.6.1-pythia-development
make te-build-dev-data PROTOCOL=te-v0.6.1-pythia-development PROFILE=mini
make te-validate-dev-data PROTOCOL=te-v0.6.1-pythia-development
make te-train-memorization PROTOCOL=te-v0.6.1-pythia-development
make te-train-a1-dev PROTOCOL=te-v0.6.1-pythia-development PROFILE=mini
make te-run-variant-smoke PROTOCOL=te-v0.6.1-pythia-development
```

The development parser is strict and uses continuation token IDs sliced at
the actual generation-call tensor width. Raw generated IDs, prompts, parser
taxonomy, checkpoint lineage, and resource measurements are retained. A1 is
task-SFT rather than a generally aligned assistant; format competence and
policy skill are reported independently. Calibration and capability sentinel
measurements are `not_measured` unless a separately declared diagnostic is
run.

Optional Pythia dependencies are isolated and pinned in
`environments/te-v0.6.0-pythia/requirements.lock`. The model loader pins the
reviewed `step143000` revision, disables remote code, validates the GPT-NeoX
configuration, and defaults to local-files-only. Use `DOWNLOAD=1` only for the
first explicitly authorized local cache fill.

The command sequence is:

```bash
make te-model-smoke
make te-train-diagnostics
make te-evaluate-model LIMIT=1
make te-plan-cohort
make te-freeze-cohort
make te-run-cohort
make te-analyze
make te-gate
```

`te-freeze-cohort` and `te-run-cohort` fail closed until the protocol/config is
tracked in a clean owner-approved commit, the semantic gate passes, model and
environment hashes are verified, and the resource plan is measured. A blocked
or null phase is a valid result. No command in this phase changes the paper or
reruns `make paper-from-results`.

The v0.6.1 readiness command reads exact development evidence paths and never
runs training as a side effect. It cannot authorize a locked cohort:

```bash
make te-dev-gate PROTOCOL=te-v0.6.1-pythia-development \
  MEMORIZATION=... A1=... VARIANTS=... RESOURCE=...
```

The executed development chain is recorded in the
[v0.6.1 experimental validation report](../results/reports/te-v0.6.1-pythia-development/development-summary/20260910T145343Z-development-summary/analysis-r001/experimental-validation-report.md).
Its readiness state is `DEVELOPMENT_NOT_READY_FOR_COHORT_REVIEW`: the v2
benchmark, training contracts, A1 training, and clean/attack audit completed,
but the A1 format criterion and full variant smoke gate did not.
