PYTHON ?= python3
LATEX_PLUGIN ?= /Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6
PAPER_DIR := paper
PAPER_PDF := $(PAPER_DIR)/value-grounded-ai-alignment.pdf

.PHONY: all figures paper verify empirical-small remediated-dataset analyze-results analyze-versioned paper-from-results harness-gate harness-ci verify-run verify-research-history compare-reports daily-report experiment register-history clean te-preflight te-semantic-audit te-model-smoke te-train-diagnostics te-evaluate-model te-plan-cohort te-freeze-cohort te-run-cohort te-analyze te-gate te-report te-ci te-dev-preflight te-audit-generations te-test-training-contracts te-profile-resources te-build-dev-data te-validate-dev-data te-train-memorization te-train-a1-dev te-test-aux-gradients te-run-variant-smoke te-evaluate-trained-dev te-analyze-dev te-dev-gate

all: figures paper verify

empirical-small:
	PYTHONPATH=src $(PYTHON) experiments/evaluation/run_empirical_small.py

remediated-dataset:
	PYTHONPATH=src $(PYTHON) scripts/generate_remediated_dataset.py

analyze-results:
	@if [ -z "$(RAW_ROOT)" ]; then echo 'Usage: make analyze-results RAW_ROOT=results/raw/empirical-small-...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) scripts/analyze_results.py --raw-root "$(RAW_ROOT)"

analyze-versioned:
	@if [ -z "$(PROTOCOL)" ] || [ -z "$(EXPERIMENT)" ] || [ -z "$(RUN_ID)" ]; then echo 'Usage: make analyze-versioned PROTOCOL=hv-v0.5.1 EXPERIMENT=... RUN_ID=... [REANALYZE=1 REASON="..."]'; exit 1; fi
	PYTHONPATH=src $(PYTHON) scripts/analyze_results.py --protocol "$(PROTOCOL)" --experiment "$(EXPERIMENT)" --run-id "$(RUN_ID)" $(if $(REANALYZE),--reanalyze,) $(if $(REASON),--reason "$(REASON)",)

register-history:
	PYTHONPATH=src $(PYTHON) scripts/register_historical_pilot.py

harness-gate:
	PYTHONPATH=src $(PYTHON) scripts/harness_gate.py

harness-ci:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
	PYTHONPATH=src $(PYTHON) -m compileall -q src scripts experiments tests
	PYTHONPATH=src $(PYTHON) scripts/verify_research_history.py

verify-run:
	@if [ -z "$(PROTOCOL)" ] || [ -z "$(EXPERIMENT)" ] || [ -z "$(RUN_ID)" ]; then echo 'Usage: make verify-run PROTOCOL=... EXPERIMENT=... RUN_ID=...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) scripts/verify_run.py --protocol "$(PROTOCOL)" --experiment "$(EXPERIMENT)" --run-id "$(RUN_ID)"

verify-research-history:
	PYTHONPATH=src $(PYTHON) scripts/verify_research_history.py

compare-reports:
	@if [ -z "$(REPORT_A)" ] || [ -z "$(REPORT_B)" ]; then echo 'Usage: make compare-reports REPORT_A=... REPORT_B=...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) scripts/compare_reports.py "$(REPORT_A)" "$(REPORT_B)"

daily-report:
	PYTHONPATH=src $(PYTHON) scripts/daily_report.py $(if $(DATE),--date "$(DATE)",)

experiment:
	@if [ -z "$(EXP)" ]; then echo 'Usage: make experiment EXP=dataset-leakage-audit'; exit 1; fi
	@case "$(EXP)" in \
		dataset-leakage-audit) script=experiments/harness/dataset_leakage_audit.py;; \
		shortcut-baselines) script=experiments/harness/shortcut_baselines.py;; \
		random-label-control) script=experiments/harness/random_label_control.py;; \
		ontology-permutation-control) script=experiments/harness/ontology_permutation_control.py;; \
		sham-feature-control) script=experiments/harness/sham_feature_control.py;; \
		ground-truth-independence) script=experiments/harness/ground_truth_independence.py;; \
		scenario-transformation-validation) script=experiments/harness/transformation_validation.py;; \
		attack-discrimination) script=experiments/harness/attack_discrimination.py;; \
		calibration-validation) script=experiments/harness/calibration_validation.py;; \
		verifier-property-validation) script=experiments/harness/verifier_property_validation.py;; \
		verifier-mutation-validation) script=experiments/harness/verifier_mutation_validation.py;; \
		verifier-differential-validation) script=experiments/harness/verifier_differential_validation.py;; \
		blind-evaluation-validation) script=experiments/harness/blind_evaluation_validation.py;; \
		power-analysis) script=experiments/harness/power_analysis.py;; \
		*) echo "Unknown harness experiment: $(EXP)"; exit 1;; \
	esac; \
	PYTHONPATH=src $(PYTHON) "$$script"

paper-from-results: empirical-small
	$(MAKE) paper

figures:
	./scripts/build-figures.sh

paper: figures
	./scripts/build-paper.sh

verify:
	./scripts/verify-paper.sh

clean:
	./scripts/clean.sh

te-preflight:
	PYTHONPATH=src $(PYTHON) experiments/transformer/preflight.py

te-semantic-audit:
	PYTHONPATH=src $(PYTHON) experiments/transformer/semantic_audit.py

te-model-smoke:
	PYTHONPATH=src $(PYTHON) experiments/transformer/model_smoke.py $(if $(DOWNLOAD),--download,) $(if $(DEVICE),--device "$(DEVICE)",)

te-train-diagnostics:
	PYTHONPATH=src $(PYTHON) experiments/transformer/train_diagnostics.py $(if $(DOWNLOAD),--download,) $(if $(DEVICE),--device "$(DEVICE)",)

te-evaluate-model:
	PYTHONPATH=src $(PYTHON) experiments/transformer/evaluate_model.py $(if $(LIMIT),--limit "$(LIMIT)",) $(if $(DEVICE),--device "$(DEVICE)",)

te-plan-cohort:
	PYTHONPATH=src $(PYTHON) experiments/transformer/plan_cohort.py $(if $(DEVELOPMENT),--development,)

te-freeze-cohort:
	PYTHONPATH=src $(PYTHON) experiments/transformer/freeze_cohort.py

te-run-cohort:
	PYTHONPATH=src $(PYTHON) experiments/transformer/run_cohort.py

te-analyze:
	PYTHONPATH=src $(PYTHON) experiments/transformer/analyze.py $(if $(INPUT),--input "$(INPUT)",)

te-gate:
	PYTHONPATH=src $(PYTHON) experiments/transformer/gate.py

te-report:
	PYTHONPATH=src $(PYTHON) experiments/transformer/report_phase.py

te-ci:
	PYTHONPATH=src $(PYTHON) -m pytest -q
	PYTHONPATH=src $(PYTHON) experiments/transformer/semantic_audit.py
	PYTHONPATH=src $(PYTHON) -m compileall -q src scripts experiments tests
	PYTHONPATH=src $(PYTHON) scripts/verify_research_history.py

te-dev-preflight:
	PYTHONPATH=src $(PYTHON) experiments/transformer/preflight_development.py

te-audit-generations:
	PYTHONPATH=src $(PYTHON) experiments/transformer/audit_generations.py $(if $(SOURCE_RUN),--source "$(SOURCE_RUN)",)

te-test-training-contracts:
	PYTHONPATH=src $(PYTHON) experiments/transformer/training_contracts.py

te-profile-resources:
	PYTHONPATH=src $(PYTHON) experiments/transformer/resource_profile.py $(if $(DEVICE),--device "$(DEVICE)",)

te-build-dev-data:
	PYTHONPATH=src $(PYTHON) experiments/transformer/build_dataset.py --version v2 --profile "$(if $(PROFILE),$(PROFILE),mini)"

te-validate-dev-data:
	PYTHONPATH=src $(PYTHON) experiments/transformer/validate_dev_data.py --profile "$(if $(PROFILE),$(PROFILE),mini)"

te-train-memorization:
	PYTHONPATH=src $(PYTHON) experiments/transformer/train_memorization.py $(if $(MAX_UPDATES),--max-updates "$(MAX_UPDATES)",) $(if $(GENERATION_CAP),--generation-cap "$(GENERATION_CAP)",) $(if $(DEVICE),--device "$(DEVICE)",)

te-train-a1-dev:
	PYTHONPATH=src $(PYTHON) experiments/transformer/train_a1_dev.py $(if $(MAX_UPDATES),--max-updates "$(MAX_UPDATES)",) $(if $(GENERATION_CAP),--generation-cap "$(GENERATION_CAP)",) $(if $(DEVICE),--device "$(DEVICE)",)

te-test-aux-gradients: te-test-training-contracts

te-run-variant-smoke:
	PYTHONPATH=src $(PYTHON) experiments/transformer/variant_smoke.py $(if $(MAX_UPDATES),--max-updates "$(MAX_UPDATES)",) $(if $(GENERATION_CAP),--generation-cap "$(GENERATION_CAP)",) $(if $(DEVICE),--device "$(DEVICE)",)

te-evaluate-trained-dev:
	@if [ -z "$(CHECKPOINT)" ]; then echo 'Usage: make te-evaluate-trained-dev CHECKPOINT=exact/path'; exit 1; fi
	PYTHONPATH=src $(PYTHON) experiments/transformer/evaluate_trained_dev.py --checkpoint "$(CHECKPOINT)" $(if $(GENERATION_CAP),--generation-cap "$(GENERATION_CAP)",) $(if $(DEVICE),--device "$(DEVICE)",)

te-analyze-dev:
	@if [ -z "$(MEMORIZATION)" ] || [ -z "$(A1)" ] || [ -z "$(VARIANTS)" ] || [ -z "$(RESOURCE)" ]; then echo 'Usage: make te-analyze-dev MEMORIZATION=... A1=... VARIANTS=... RESOURCE=...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) experiments/transformer/analyze_dev.py --memorization "$(MEMORIZATION)" --a1 "$(A1)" --variants "$(VARIANTS)" --resource "$(RESOURCE)"

te-dev-gate:
	@if [ -z "$(MEMORIZATION)" ] || [ -z "$(A1)" ] || [ -z "$(VARIANTS)" ] || [ -z "$(RESOURCE)" ]; then echo 'Usage: make te-dev-gate MEMORIZATION=... A1=... VARIANTS=... RESOURCE=...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) experiments/transformer/development_readiness.py --memorization "$(MEMORIZATION)" --a1 "$(A1)" --variants "$(VARIANTS)" --resource "$(RESOURCE)" $(if $(ATTACK),--attack "$(ATTACK)",)
