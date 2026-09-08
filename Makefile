PYTHON ?= python3
LATEX_PLUGIN ?= /Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6
PAPER_DIR := paper
PAPER_PDF := $(PAPER_DIR)/value-grounded-ai-alignment.pdf

.PHONY: all figures paper verify empirical-small analyze-results paper-from-results clean

all: figures paper verify

empirical-small:
	PYTHONPATH=src $(PYTHON) experiments/evaluation/run_empirical_small.py

analyze-results:
	@if [ -z "$(RAW_ROOT)" ]; then echo 'Usage: make analyze-results RAW_ROOT=results/raw/empirical-small-...'; exit 1; fi
	PYTHONPATH=src $(PYTHON) scripts/analyze_results.py --raw-root "$(RAW_ROOT)"

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
