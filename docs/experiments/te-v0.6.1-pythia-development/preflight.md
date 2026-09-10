# v0.6.1 Pythia development preflight

Created: `2026-09-09T20:41:03.714883Z`  
Starting commit: `7aa20ea115239bab646225b63642693590ec0d4d`; branch: `main`; worktree clean: `False`.

This is a dirty-tree-capable local development preflight. The exact commit, dirty patch digest, approved research-source manifest, dependency versions, model identity, and protected paper-tree hashes are recorded in `preflight.json`. System `.DS_Store` files and locked dataset contents were excluded from source-content inventories; no credentials or environment secrets were captured.

## Protected boundary

The existing manuscript and all files under `paper/**` (excluding ignored build output) are byte-hashed before execution. The v1 dataset, including its existing locked files, and historical reports/raw outputs are preserved. This phase will not run `make all`, `make paper-from-results`, legacy aggregate analyses, `te-freeze-cohort`, or `te-run-cohort`.

## Source-derived versus current state

The supplied starting state records the verified Pythia checkpoint, a one-step LoRA diagnostic, and five historical parser failures. The current state is a dirty development checkout with the same reviewed base model identity and a new v0.6.1 protocol. The new v2 benchmark is generated separately; the v1 fixture is not regenerated or scored by this phase.

## Resources and budget

At preflight, free disk was `6.638` GiB. The permitted budget is 8 wall-hours for the phase, 2 wall-hours per attempt, one resident model, float32 CPU or explicitly available MPS, no paid compute, no upload, and no push. The local host is resource constrained, so a partial but durable result is valid and a locked cohort remains unauthorized.

## Requirement map

- `WP1`: `src/vgta_transformer/response_parser.py`, `tests/transformer/test_response_parser.py`
- `WP2`: `src/vgta_transformer/losses.py`, `src/vgta_transformer/training.py`, `src/vgta_transformer/checkpointing.py`, `tests/transformer/test_training_contracts.py`
- `WP3`: `experiments/transformer/resource_profile.py`
- `WP4-WP6`: `experiments/transformer/train_memorization.py`, `experiments/transformer/train_a1_dev.py`
- `WP5`: `src/vgta_eval/semantic_worlds.py`, `experiments/transformer/build_dataset.py`, `experiments/transformer/validate_dev_data.py`
- `WP7-WP8`: `experiments/transformer/variant_smoke.py`, `experiments/transformer/evaluate_trained_dev.py`, `experiments/transformer/development_readiness.py`

See `preflight.json` for the complete status inventory, command graph, hashes, and exclusions.
