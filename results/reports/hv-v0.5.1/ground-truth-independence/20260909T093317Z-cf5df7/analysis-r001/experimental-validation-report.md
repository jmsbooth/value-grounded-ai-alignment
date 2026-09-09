# VGA/VGTA Harness Validation Report — hv-v0.5.1__ground-truth-independence__20260909T093317Z-cf5df7__a001

Experiment ID: `ground-truth-independence`  
Protocol: `hv-v0.5.1`  
Run ID: `20260909T093317Z-cf5df7`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.1__ground-truth-independence__20260909T093317Z-cf5df7__a001`  
Created: `2026-09-09T09:33:18.127385+00:00`  
Git SHA: `0f3aecb7e6104971d5f42c6172192fd18d97ccce`  
Working tree status: `modified`  
Dataset version: `v0.4-structure-heldout`  
Dataset: `76bbeae451c1df8afb49358886008faf40245690bc0d9b8c5eaed88a7caab857`  
Ontology: `ea9fd852764f75093a1e01c784624865ac17a589b8230ec19ba574ee5ca83d02`  
Ground truth: `36b287a28366797385ffcbecdb1837b252228f8d401b832c8cf10261f059bd37`  
Verifier: `eac1a4d3388a43826ab5852aad20d1d2bb0b0d3fa02c0843c460970b63947b7c`  
Attack suite: `c58bb9ba16f186936a14c58c69b5cececdee9a1e828d2a0cd492187b09f60d01`  
Metric suite: `c30492dd6e1eb6c7c2b0e7bc1e4cd84e047fcfcfbbb435d5c1f094ccd4f10a63`  
Evidence classification: `harness-validation`  
Run validity: `valid`  
Run mode: `development`

> This is a harness-validation artifact. It does not establish VGA superiority, human moral validity, production security, or Transformer evidence.

## Research question

Can ground-truth outcomes be computed independently of the candidate VGA ontology?

## Method

Computed a bounded reference outcome from scenario context, norms, and world facts; mutated candidate ontology features and verified that outcomes did not change.

## Controls

The function source is inspected for direct access to candidate ontology or target labels.

## Results

```json
{
  "covered_outcomes": [
    "request_context"
  ],
  "evaluated_rows": 155,
  "ontology_mutation_invariant": true,
  "source_excludes_candidate_ontology": true
}
```

## Null results

None recorded.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

This is an independent-ground-truth architecture fixture, not an independent human adjudication study.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Replace synthetic rules with independently adjudicated policy-grounded labels before Transformer Gate 1.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.1/ground-truth-independence/20260909T093317Z-cf5df7`
- Analysis: `results/analyses/hv-v0.5.1/ground-truth-independence/20260909T093317Z-cf5df7/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.1/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
