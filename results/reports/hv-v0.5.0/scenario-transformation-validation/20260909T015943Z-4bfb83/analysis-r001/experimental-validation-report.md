# VGA/VGTA Harness Validation Report — hv-v0.5.0__scenario-transformation-validation__20260909T015943Z-4bfb83__a001

Experiment ID: `scenario-transformation-validation`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015943Z-4bfb83`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__scenario-transformation-validation__20260909T015943Z-4bfb83__a001`  
Created: `2026-09-09T01:59:44.888756+00:00`  
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

Do invariant transformations preserve outcomes while causal transformations change outcomes where defined?

## Method

Grouped matched training transformations by semantic structure to test label invariance and inspected the sealed ontology-degradation family for explicitly defined causal changes.

## Controls

Only transformations with shared semantic features are treated as invariant; causal changes are not expected for every degradation level.

## Results

```json
{
  "causal_label_changes_observed": 1,
  "causal_rows": 20,
  "invariant_pairs": 102,
  "invariant_violations": 0,
  "transformations_checked": [
    "surface substitutions",
    "ontology degradation"
  ]
}
```

## Null results

None recorded.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

The bounded generator supports transformation checks, but paraphrase and authority/consent interventions need richer paired fixtures.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Add names, harmless paraphrases, ordering, authority, consent, exception, affected-party, and purpose transformation pairs.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/scenario-transformation-validation/20260909T015943Z-4bfb83`
- Analysis: `results/analyses/hv-v0.5.0/scenario-transformation-validation/20260909T015943Z-4bfb83/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
