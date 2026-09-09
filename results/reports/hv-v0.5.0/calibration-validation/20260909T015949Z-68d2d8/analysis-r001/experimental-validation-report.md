# VGA/VGTA Harness Validation Report — hv-v0.5.0__calibration-validation__20260909T015949Z-68d2d8__a001

Experiment ID: `calibration-validation`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015949Z-68d2d8`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__calibration-validation__20260909T015949Z-68d2d8__a001`  
Created: `2026-09-09T01:59:51.391364+00:00`  
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

Are calibration and selective-risk metrics implemented correctly?

## Method

Computed multiclass Brier score, fixed-bin ECE, thresholded selective accuracy, abstention rate, false confidence, and a full risk-coverage curve on known probability fixtures.

## Controls

Known synthetic distributions provide boundedness and length assertions; they are not calibration evidence for a trained model.

## Results

```json
{
  "known_fixture": {
    "abstention_rate": 0.0,
    "brier_score": 0.49629999999999996,
    "ece": 0.24,
    "false_confidence_rate": 0.0,
    "n": 4,
    "risk_coverage": [
      {
        "coverage": 0.25,
        "risk": 0.0,
        "selective_accuracy": 1.0
      },
      {
        "coverage": 0.5,
        "risk": 0.5,
        "selective_accuracy": 0.5
      },
      {
        "coverage": 0.75,
        "risk": 0.33333333333333337,
        "selective_accuracy": 0.6666666666666666
      },
      {
        "coverage": 1.0,
        "risk": 0.5,
        "selective_accuracy": 0.5
      }
    ],
    "selective_accuracy_at_threshold": 0.5
  },
  "metrics": [
    "brier_score",
    "ece",
    "selective_accuracy",
    "abstention_rate",
    "false_confidence_rate",
    "risk_coverage"
  ],
  "self_test": {
    "abstention_rate": 0.0,
    "brier_score": 0.37,
    "ece": 0.25,
    "false_confidence_rate": 0.0,
    "n": 2,
    "risk_coverage": [
      {
        "coverage": 0.5,
        "risk": 0.0,
        "selective_accuracy": 1.0
      },
      {
        "coverage": 1.0,
        "risk": 0.5,
        "selective_accuracy": 0.5
      }
    ],
    "selective_accuracy_at_threshold": 0.5
  }
}
```

## Null results

None recorded.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

The metric implementation is available for future model runs. Calibration quality still requires independent held-out predictions.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Attach these metrics to the blinded Transformer evaluation and report confidence under missing semantic context.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/calibration-validation/20260909T015949Z-68d2d8`
- Analysis: `results/analyses/hv-v0.5.0/calibration-validation/20260909T015949Z-68d2d8/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
