# Pythia contract continuation

Master: `vga-master-v1.0.0`. This is a fixture-scope source correction and local regression execution, not a Pythia training study.

Read the [versioned execution report](../../../results/reports/te-v0.6.3-contract-revalidation/20261021T203008Z-6c932eaa/analysis-r001/experimental-validation-report.md) and its adjacent summary/preflight JSON.

The targeted command is:

```sh
PYTHONPATH=src python -m pytest -q tests/protocol
```

It ran 46 tests with no failures or skips in the source-subset workspace. The serializer projection and model attempts are explicitly mocked; the actual loss/update functions are tested with algebra fixtures. This does not establish pretrained-model behavior or full-repository integration.

The new evidence checker accepts explicit, plan-pinned artifacts:

```sh
PYTHONPATH=src python experiments/transformer/correction_gate.py \
  --inventory path/to/evidence-inventory.json \
  --approved-plan-sha256 APPROVED_PLAN_HASH \
  --scope fixture
```

The placeholders must be resolved from the selected study. Never derive approval merely by accepting whatever plan the inventory names. Legacy `--cohort` reports are rejected. Existing Makefile/report-aggregation integration remains follow-up work; do not mistake this partial branch for completed research readiness.

No Pythia weights were available here. Full regression, real-tokenizer verification and the actual two-seed training schedules must run in the verified Pythia environment, using the same baseline information and meaningful controls. Do not reduce generation length or seed count and reclassify the result as the original study.

The complete original XML/stdout/source evidence bundle accompanies the conversation. Full repository registry/archive ingestion remains pending. Historical reports and manuscript assets are unchanged.
