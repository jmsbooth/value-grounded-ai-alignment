# `te-v0.6.2-pythia-correction`

Bounded correction and retest protocol for the Pythia development harness.
The reviewed parent is `te-v0.6.1-pythia-development` at commit
`0598a9795b5cb2721d26e9c0950377bae52676c0`. The manuscript and all historical
results remain frozen.

## Boundary

This phase corrects ten named implementation defects (F01--F10), exercises
their contracts with deterministic tests, and runs only the bounded
development model checks described in `training.yaml`. The model remains
`EleutherAI/pythia-410m`, requested revision `step143000`, resolved to
`bba6a464f54bbf08fc174cfb351d9794d58af21d`. Data remain fictional and
synthetic. No locked cohort, manuscript regeneration, OLMo, C3, attention
modification, MoE, solver-backed enforcement, upload, or push is authorized.

## Evidence boundary

Implementation validation means a named contract and its tests passed. Model
development evidence means an actual Pythia run produced a receipt. Neither is
empirical evidence of alignment, moral truth, generalization, or deterministic
AI behavior. The independent evaluator is a project-authored oracle for this
fictional benchmark, not an external normative authority.

## Execution order

WP0 preflight and protected-history hashes; WP1 explicit-EOS audit and parser;
WP2 independent candidate scoring; WP3 variant and span contracts; WP4
auxiliary isolation and global accumulation; WP5 resource qualification; WP6
corrected memorization and A1; WP7 corrected eight-arm smoke; WP8 paired
clean/attack evaluation; WP9 receipts, report, and fail-closed gate.

## Resource and authorization policy

Use one resident model, fresh child processes for isolated attempts, the
measured CPU/MPS backend only, and float32. Physical microbatch size is one;
effective batch size is eight where a training run is attempted. Do not set
`PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`. Resource exhaustion produces durable
partial evidence and does not justify silently shortening the declared input
or schedule. This protocol cannot authorize `te-freeze-cohort` or
`te-run-cohort`.
