# `te-v0.6.1-pythia-development`

Bounded local development protocol for training and evaluating the verified
Pythia-410M integration. This phase is exploratory engineering evidence,
not a locked comparison and not evidence that VGA improves alignment.

## Boundary

The phase uses the pretrained `EleutherAI/pythia-410m` `step143000` revision,
the project-authored fictional policy benchmark `pythia-policy-dev-v2`, and
the existing LoRA topology. It covers response-format learning, task-SFT,
auxiliary-gradient isolation, resource measurement, and real eight-arm smoke
execution. It does not run the locked 40-run cohort, OLMo, C3, structural
attention, MoE, or solver-backed production enforcement. The manuscript,
figures, generated fragments, PDF, v1 fixture, and v1 locked files are frozen.

## Evidence boundaries

Pretrained, one-step diagnostic, memorization, and task-trained checkpoints
have distinct lineage. Format competence, policy-task performance, conditional
accuracy, end-to-end useful completion, fail-closed enforcement, and VGA
architectural evidence are reported separately. Data are synthetic and
fictional; the executable reference policy is a project oracle, not moral or
legal ground truth. Calibration and open-development data are exposed for
development and cannot become confirmatory holdouts.

## Execution order

WP0 preflight; WP1 output audit and strict parser; WP2 training contracts;
WP3 measured resources; WP4 eight-example memorization; WP5 v2 mini data;
WP6 two-seed A1 development training; WP7 all-eight-arm bounded smoke; WP8
paired clean/attack audit, analysis, and readiness. Each work package receives
its own run identity and immutable raw/report paths. A finite but poor model is
a valid result; a failed engineering contract is a separate status.

## Model and adaptation

The model is loaded offline at reviewed revision
`bba6a464f54bbf08fc174cfb351d9794d58af21d`. LoRA remains rank 8, alpha 16,
dropout 0, targeting the verified GPT-NeoX modules. Training is response-only
SFT with causal shifting once, explicit prompt/response/padding masks,
token-weighted accumulation, `use_cache=false`, global gradient clipping at
1.0, and no private labels in model-visible inputs. Auxiliary heads read only
the last valid prompt position.

## Stopping and authorization

The local budget is eight wall-hours for the phase, two wall-hours per attempt,
one resident model, no paid compute, and no upload. A resource boundary,
non-finite update, invalid data access, or corrupted artifact stops the attempt
and preserves partial evidence. This protocol cannot authorize
`te-freeze-cohort` or `te-run-cohort`; those commands remain fail-closed.
