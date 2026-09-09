# VGA/VGTA Harness Validation Report — hv-v0.5.1__ontology-permutation-control__20260909T093312Z-221fc4__a001

Experiment ID: `ontology-permutation-control`  
Protocol: `hv-v0.5.1`  
Run ID: `20260909T093312Z-221fc4`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.1__ontology-permutation-control__20260909T093312Z-221fc4__a001`  
Created: `2026-09-09T09:33:15.977073+00:00`  
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

Does semantic structure provide information beyond arbitrary graph/features?

## Method

Applied a seeded edge permutation to held-out topology summaries while preserving row count and control code, then compared the topology-summary baseline.

## Controls

The experiment records both original and permuted controls; it does not treat a performance drop alone as proof of semantic grounding.

## Results

```json
{
  "edge_permuted": true,
  "label_permutation": "not run in this bounded fixture",
  "original_topology_accuracy": 0.5098039215686274,
  "permutation_changed_rows": 49,
  "permuted_topology_accuracy": 0.5098039215686274
}
```

## Null results

None recorded.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

The permutation is a valid control only when it demonstrably changes the structured input and remains separately identified from the original ontology.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Add label-permuted and degree-preserving graph controls before confirmatory use.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.1/ontology-permutation-control/20260909T093312Z-221fc4`
- Analysis: `results/analyses/hv-v0.5.1/ontology-permutation-control/20260909T093312Z-221fc4/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.1/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
