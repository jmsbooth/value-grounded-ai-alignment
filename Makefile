PYTHON ?= python3
LATEX_PLUGIN ?= /Users/jamesbooth/.codex/plugins/cache/openai-bundled/latex/0.2.6
PAPER_DIR := paper
PAPER_PDF := $(PAPER_DIR)/value-grounded-ai-alignment.pdf

.PHONY: all figures paper verify clean

all: figures paper verify

figures:
	./scripts/build-figures.sh

paper: figures
	./scripts/build-paper.sh

verify:
	./scripts/verify-paper.sh

clean:
	./scripts/clean.sh
