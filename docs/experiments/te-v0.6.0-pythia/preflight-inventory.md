# Pythia phase preflight inventory

Specification: `VGA-SDD-TE-006`  
Proposed protocol: `te-v0.6.0-pythia`  
Inventory timestamp: `2026-09-09`  
Starting commit: `7aa20ea115239bab646225b63642693590ec0d4d`  
Starting worktree: clean; no dirty or untracked files observed.

This inventory records the state before Pythia-phase modifications. It is an
engineering preflight, not evidence that a Pythia comparison has executed.

## Execution constraints

- Host: macOS 26.3.1, Darwin arm64, Apple M2, 8 CPU cores, 16 GiB RAM.
- Accelerator: Apple M2 integrated GPU with Metal support; CUDA is unavailable.
- Disk: approximately 14 GiB available on the workspace volume at inventory
  time.
- Python: 3.14.4 from the active shared development environment. The active
  interpreter is not repository-local and must not be treated as the locked
  Pythia environment.
- Existing relevant packages: NumPy 2.4.4, PyYAML 6.0.3, jsonschema 4.26.0.
- Missing relevant packages: PyTorch, Transformers, PEFT, Safetensors, and
  psutil were absent from the active environment.
- Network: official Hugging Face metadata was reachable. No paid compute,
  external upload, release, push, or visibility change is authorized.

## Model resolution

- Requested model: `EleutherAI/pythia-410m`.
- Requested checkpoint: `step143000`.
- Resolved Hugging Face revision: `bba6a464f54bbf08fc174cfb351d9794d58af21d`.
- Expected architecture from the official configuration: `GPTNeoXForCausalLM`,
  24 layers, hidden size 1024, 16 attention heads, intermediate size 4096,
  maximum position length 2048.
- The model files, tokenizer files, and checksums were not present in the
  repository at inventory time. They must be downloaded once into a verified
  local cache and used offline thereafter.

## Protected artifacts

The following artifacts are frozen and must not be rewritten by this phase:

- Manuscript source, bibliography, PDF, generated fragments, and referenced
  figures under `paper/`.
- Frozen architecture and ontology interfaces under `src/vgta/` and
  `ontology/`.
- Historical MLP pilot and harness raw/report artifacts under `results/`.
- Existing `hv-v0.5.0` and `hv-v0.5.1` protocol/report history.
- Existing Make targets, registry identity fields, and append-only report
  behavior except where extended through a new versioned schema.

Protected baseline spot-check hashes at inventory time:

```text
README.md                                      dd2f80a0c0396a2bce1bb82e92b2e6c0b8ea7a36083961e39307446563d33f4e
paper/main.tex                                 8ae4d4171e2f2e98be4771d5c1480bfa3b8149a52ee546b1fbe6572e6f00d12e
paper/value-grounded-ai-alignment.pdf         39e495dc1628e01363e77ea264305f21a7db60229c76818216be1491b1832c69
paper/references.bib                           1b87da811401b6bb7312fc39cd4ddeba62380f2c408d31c11962e871c80a9386
```

## Existing implementation and commands

- Dependency-light interface implementation: `src/vgta/`.
- Synthetic NumPy pilot: `src/vgta_eval/` and `experiments/evaluation/`.
- Versioned harness lifecycle: `experiments/harness/`, `results/registry/`,
  `scripts/verify_run.py`, `scripts/harness_gate.py`, and
  `scripts/verify_research_history.py`.
- Existing lightweight validation: `make harness-ci` and
  `make verify-research-history`.
- Existing paper commands include `make all`, `make empirical-small`, and
  `make paper-from-results`. The latter reruns the old MLP experiment and is
  prohibited in this phase.

## Applicable instructions

- User request: review and execute the attached Pythia phase specification.
- Repository operating instructions: preserve immutable history, inventory
  before creating files, use canonical locations, keep claims conservative,
  and do not push or publish without authorization.
- Specification contract: no manuscript rewrite, no OLMo run, no custom
  attention topology, no paid compute, no uncommitted run described as
  preregistered, and no locked cohort before protocol/config ownership is
  committed or explicitly approved.
- Evidence boundary: development fixtures, semantic validation, pretrained
  inference, trained-model inference, and scientific conclusions must remain
  separate producer classes.

## Requirement-to-implementation map

| Requirement | Planned implementation | Status at inventory |
| --- | --- | --- |
| Preflight and protected baseline | This inventory, baseline manifest, environment lock | Started |
| Semantic benchmark | `pythia-policy-dev-v1` world generator, projector, renderer, oracle, labels, checker | Not started |
| Semantic validity protocol | `hv-v0.5.2-semantic-validity` | Not started |
| Pythia model integration | Optional `src/vgta_transformer/` loader/adaptation/training stack | Not started |
| Five-seed matched cohort | Versioned plan/freeze/run commands with fail-closed resource/ownership gates | Not started |
| Provenance and receipts | Versioned artifact schema, prediction receipts, registry extension | Not started |
| Analysis and gates | Grouped analysis, calibration, attacks, capability, truthful phase states | Not started |
| OLMo handoff | Separate evidence-scoped design brief; no model execution | Not started |

## Preflight decision

Proceed with semantic-validity implementation, optional dependency resolution,
and fixture-sized/model-smoke development work. Do not begin a locked Pythia
comparison until the semantic gate passes, the cohort plan is frozen, the
environment/model artifacts are hashed, and the owner has committed or
explicitly approved the protocol state.
