# VGA/VGTA Harness Validation Report — hv-v0.5.0__random-label-control__20260909T015930Z-a7d725__a001

Experiment ID: `random-label-control`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015930Z-a7d725`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__random-label-control__20260909T015930Z-a7d725__a001`  
Created: `2026-09-09T01:59:33.213394+00:00`  
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

Does randomizing target labels reduce performance toward chance?

## Method

Preserved record count and the observed action-label vocabulary while independently permuting training and held-out target labels, then reran the same lightweight control suite.

## Controls

The expected result is near chance; failure indicates leakage, an evaluator defect, or a control that is reading target information.

## Results

```json
{
  "all_baselines": {
    "bag_of_words": {
      "overall_accuracy": 0.17647058823529413,
      "predictions": 51,
      "structural_ood_accuracy": 0.3333333333333333
    },
    "majority": {
      "overall_accuracy": 0.21568627450980393
    },
    "metadata_only": {
      "overall_accuracy": 0.17647058823529413,
      "predictions": 51,
      "structural_ood_accuracy": 0.25
    },
    "sequence_length_only": {
      "overall_accuracy": 0.1568627450980392,
      "predictions": 51,
      "structural_ood_accuracy": 0.3333333333333333
    },
    "tfidf_logistic": {
      "overall_accuracy": 0.17647058823529413,
      "predictions": 51,
      "structural_ood_accuracy": 0.08333333333333333
    },
    "topology_summary": {
      "overall_accuracy": 0.1568627450980392,
      "predictions": 51,
      "structural_ood_accuracy": 0.16666666666666666
    }
  },
  "chance_accuracy": 0.08333333333333333,
  "tfidf_accuracy": 0.17647058823529413
}
```

## Null results

Observed randomized TF-IDF accuracy was 0.176; expected chance was 0.083.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

Random-label behavior is a test of the test, not evidence for or against VGA.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

If the observed score is not near chance, inspect target access and split construction before any model study.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/random-label-control/20260909T015930Z-a7d725`
- Analysis: `results/analyses/hv-v0.5.0/random-label-control/20260909T015930Z-a7d725/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
