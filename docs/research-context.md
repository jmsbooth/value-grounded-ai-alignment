# Research context: canonical methodology and Pythia correction

**Method reference:** [vga-master-v1.0.0](../experiments/protocols/vga-master-v1.0.0/protocol.md)  
**Current implementation baseline:** `07b4aaf48f82cc04c906b522d0b2f3da7f084d83`  
**Implementation phase:** `te-v0.6.2-pythia-correction`, correction plus bounded retest; no locked comparison.

This context is navigation for the next agent. It is not a replacement for versioned source, run and report artifacts. Read [TESTING.md](../TESTING.md), the [execution runbook](../experiments/protocols/vga-master-v1.0.0/runbook.md), and the exact adopted study registration before work.

## Stable research boundaries

- Model sequence: Pythia-410M now; OLMo 2 1B only under a separate reviewed study. Current Pythia is task-SFT with LoRA and auxiliary objectives, not the complete VGTA reference architecture.
- Keep the manuscript, generated figures/fragments/PDF and historical experiment outputs unchanged while implementation/development proceeds.
- Do not add C3, custom attention, MoE, recursive ontology evolution or solver-backed deployment to the current experiment. Those are separately registered questions.
- No positive VGA effect is required. Preserve adverse, equivalent, null, uncertain, invalid and resource-limited outcomes with the correct scope.
- A fixture, a real-model canary, a development experiment and a locked comparison are distinct. Hashes and status strings do not prove semantic validity, actual computation or completion.
- All main arms receive the same true response supervision and necessary task facts. B/C1/C2 share exact model input bytes. Text-weighted and sham controls must implement their intended loss changes.
- Model-generated permission/usefulness are claims. Independent candidate evaluation controls metrics and any mock enforcement.
- Never reinterpret a one-update, one-seed selected canary as completion of a required sixteen- or forty-run schedule.
- The master document defines prospective requirements. Publishing it does not certify current code, validate current scientific claims, run models, or authorize locked/paid execution.

## Evidence at the adoption baseline

Actual-Pythia auxiliary-only gradients, detached-state negative controls, EOS-tokenizer construction and independent-scoring fixtures have recorded diagnostic artifacts. The correction learning attempts were only one update/one seed with short generation limits. Only C2-SHAM was exercised in the selected smoke canary, and the attack audit used an eight-token generation cap. These are not the meaningful bounded retest or an assessment of VGA effectiveness.

The prior source review identifies unresolved smoke-summary execution, parent/child output isolation, exact response-value spans, weighted-loss reporting, receipt/content compatibility verification, and truthful protocol-coverage accounting. Reproduce them against the actual checkout; newer changes may already address a finding. The detailed reviewed paths and evidence requirements are in the [runbook](../experiments/protocols/vga-master-v1.0.0/runbook.md).

## Next work sequence

1. Inventory and preserve the current checkout; resolve review findings with regression tests, without modifying historical evidence.
2. Bind one effective variant/training/evaluation plan to actual code. Qualify EOS, real-tokenizer spans, independent scoring, auxiliary-only gradients and common accumulation.
3. Profile the longest structured inputs and full response generation under the actual device/storage budget.
4. Execute the already-defined bounded memorization and two-seed A1 development retests with a response-feasible generation cap.
5. Execute all eight arms/two seeds under the qualified common training path; record any unexecuted scope as partial.
6. Evaluate actual clean/attacked predictions and uncertainty/capability diagnostics; produce hash-verified, scope-aware reports.
7. Only then review a complete, owner-approved locked-study registration with new uninspected evaluation material and power/precision planning.

Use the [study template](../experiments/protocols/vga-master-v1.0.0/study-template.yaml) for each new study and preserve the historical H1-H10 mapping at its manuscript commit. Do not silently convert the prospective salience macro-F1 endpoint into the historical recall endpoint or change a previously observed result's status.

Do not invoke paper-generating aggregate commands during this work. Existing command names and their implementation caveats are documented in the runbook. A request to prepare methodology alone is not a request to start training.
