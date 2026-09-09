PYTHON ?= python3
LATEX_PLUGIN ?= /Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6
PAPER_DIR := paper
PAPER_PDF := $(PAPER_DIR)/value-grounded-ai-alignment.pdf

.PHONY: all figures paper verify empirical-small remediated-dataset analyze-results analyze-versioned paper-from-results harness-gate harness-ci verify-run verify-research-history compare-reports daily-report experiment register-history clean

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
