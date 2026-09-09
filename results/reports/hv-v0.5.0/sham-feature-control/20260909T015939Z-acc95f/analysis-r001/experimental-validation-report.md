# VGA/VGTA Harness Validation Report — hv-v0.5.0__sham-feature-control__20260909T015939Z-acc95f__a001

Experiment ID: `sham-feature-control`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015939Z-acc95f`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__sham-feature-control__20260909T015939Z-acc95f__a001`  
Created: `2026-09-09T01:59:40.536000+00:00`  
Git SHA: `0f3aecb7e6104971d5f42c6172192fd18d97ccce`  
Working tree status: `modified`  
Dataset: `16082ca413029bba8727930b6757c2a2b42e76d84d807f3af22a565ddf6139a0`  
Ontology: `ea9fd852764f75093a1e01c784624865ac17a589b8230ec19ba574ee5ca83d02`  
Ground truth: `2ec09775b2d0fc88ea159f025dca1e71fa68842bf6301fa23d9efe008fe2d8d3`  
Verifier: `eac1a4d3388a43826ab5852aad20d1d2bb0b0d3fa02c0843c460970b63947b7c`  
Attack suite: `c58bb9ba16f186936a14c58c69b5cececdee9a1e828d2a0cd492187b09f60d01`  
Metric suite: `c30492dd6e1eb6c7c2b0e7bc1e4cd84e047fcfcfbbb435d5c1f094ccd4f10a63`  
Evidence classification: `harness-validation`  
Run validity: `valid`  
Run mode: `development`

> This is a harness-validation artifact. It does not establish VGA superiority, human moral validity, production security, or Transformer evidence.

## Research question

Are intended semantic improvements distinguishable from dimensionality- and sparsity-matched sham features?

## Method

Replaced axiological feature values with seeded sham tokens while preserving per-record feature counts and dataset dimensions.

## Controls

The sham carries no intended semantic mapping and is independent of target labels.

## Results

```json
{
  "dimension_match": true,
  "semantic_feature_count_mean": 3.7903225806451615,
  "sham_feature_count_mean": 3.7903225806451615,
  "sham_vocabulary": 6,
  "sparsity_match": true
}
```

## Null results

None recorded.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

This bounded control establishes feature-shape matching only; it does not estimate a model effect until paired training is run.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Run a matched C1-versus-sham model comparison with the same optimizer and seed schedule.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/sham-feature-control/20260909T015939Z-acc95f`
- Analysis: `results/analyses/hv-v0.5.0/sham-feature-control/20260909T015939Z-acc95f/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
