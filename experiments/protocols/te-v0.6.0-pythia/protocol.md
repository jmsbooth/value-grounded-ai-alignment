# `te-v0.6.0-pythia`

Engineering and development protocol for a pretrained Pythia-410M comparison.
This phase is not a confirmatory study and does not license a claim that VGA
works, improves alignment, or generalizes to human values.

## Model and data

- Model: `EleutherAI/pythia-410m`, checkpoint `step143000`.
- Required immutable revision: `bba6a464f54bbf08fc174cfb351d9794d58af21d`.
- Expected configuration: GPT-NeoX causal LM, 24 layers, hidden size 1024,
  16 heads, intermediate size 4096, context length 2048.
- Dataset: `pythia-policy-dev-v1`, a project-authored synthetic benchmark with
  fictional delegated-access and purpose-limited-disclosure worlds.
- Data source: `src/vgta_eval/semantic_worlds.py`; public/private materialized
  separately by `experiments/transformer/build_dataset.py`.

## Variants

The comparison is paired by world group and seed. A1 is the response-only
baseline; B adds the structured observation; C1 adds auxiliary value/relation
readouts; C2 adds norm/conflict readouts. Text and sham controls are specified
in `variants.yaml`. LoRA is the only adaptation mechanism: rank 8, alpha 16,
dropout 0.0. No custom attention topology or hidden private channel is used.

## Phase rules

- `fixture` validates contracts without model weights.
- `development` permits small local diagnostics and open-development data.
- `locked-pythia-comparison` requires a committed protocol/config, a passing
  semantic gate, verified model and environment hashes, a frozen cohort plan,
  untouched locked engineering evaluation data, and a measured resource plan.
- A dirty-worktree or owner-unapproved run cannot be described as
  preregistered or locked.
- No automatic hyperparameter tuning may consume locked evaluation examples.
- Pretrained loading is exact and offline after cache verification; no generic
  model fallback is valid evidence.

## Required states

`FIXTURE_TESTS_PASSED`, `SEMANTIC_DATASET_VALIDATED`,
`PYTHIA_INTEGRATION_VALIDATED`, `LOCKED_PYTHIA_COMPARISON_COMPLETE`, and
`READY_FOR_OLMO_PROTOCOL_DESIGN` are emitted only by their corresponding
producer and receipt. A blocked or resource-limited phase is reported as such.

