# te-v0.6.4: explicit evidence-report integration

Master protocol: `vga-master-v1.0.0`
Parent source: `f823cbbf8e252dd85e8271807e2adfbcc4b84b28`
Scope: fixture and execution-contract validation.
Locked comparison: NOT EXECUTED. Manuscript/historical artifacts: unchanged.

## Execution and results

- Local subset: source files from the v0.6.3 evidence bundle with the added report generator and six report-regression cases.
- Command: `PYTHONPATH=src python -m pytest -q tests/protocol --junitxml=... > ...`.
- Outcome: **52 passed, zero failed, zero skipped**, 9.39 seconds.
- Original test-output SHA-256: `9d6bc9a8999e2ed4d186669343a62a6f36a9507382e96c1de1857490946c7e64`.
- Original JUnit XML SHA-256: `4de4778a60a36f0882b0d8624c1a2e4718b9c4a2cf49d4768daf18175dde6d5a`.
- The original stdout/XML are retained in the conversation's local working evidence, not yet incorporated into the repository research registry. These digests alone are not a substitute for the original artifacts.

## Added and tested

1. Correction reports are generated only after verifying one explicitly pinned evidence plan and exact inventory.
2. Legacy `--cohort` PASS/status scans are no longer an accepted report input.
3. Each generated report uses a unique run ID, exclusive directory creation, hashed JSON/Markdown and a manifest.
4. Tampered evidence, unpinned plans, reused output locations and paths outside the evidence root are rejected.
5. Full protocol completion and scientific efficacy are never inferred from fixture-scope evidence.
6. Make targets now forward `INVENTORY`, `PLAN_SHA256`, and `SCOPE`; Makefile was inspected and updated, but the full repository Make target was not executed in the subset environment.

## Independent historical verification

The archived v0.6.3 fixture inventory was verified against its preexisting approved plan digest:
`7b158018530e470f9d042971bae26b8edd2f1c123c262073106a2711c7094c2b`.
Its single role `local_contract_suite` passed its declared assertions, with `locked_launch_authorized=false`. A separate non-overwriting explicit report was generated from it. This does not establish a full Pythia training run.

## Outstanding

- Merge/review only after full-checkout integration, Make target tests, and repository-level regression.
- Model dependency preflight and real tokenizer span checks on the original development host with pinned Pythia assets.
- Two-seed memorization, A1 development, eight-arm/two-seed smoke, paired attacks and calibration: **not executed**.
- A locked 40-run study is neither approved nor ready. No Pythia/VGA benefit or harm inference is made.

The development protocol remains prospective; failed runs and missing evidence are not silently converted into passing outcomes.
