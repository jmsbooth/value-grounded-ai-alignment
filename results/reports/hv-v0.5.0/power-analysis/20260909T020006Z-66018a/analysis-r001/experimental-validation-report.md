# VGA/VGTA Harness Validation Report — hv-v0.5.0__power-analysis__20260909T020006Z-66018a__a001

Experiment ID: `power-analysis`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T020006Z-66018a`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__power-analysis__20260909T020006Z-66018a__a001`  
Created: `2026-09-09T02:00:06.814988+00:00`  
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

What scenario and seed counts should be planned for future Transformer effects without using the pilot's enormous effects?

## Method

Estimated per-variant binary-comparison sample sizes for 3, 5, and 10 percentage-point minimum effects using a two-sided alpha of 0.05 and 80% power.

## Controls

The planning baseline is 0.5 and independent of the observed MLP pilot effect sizes; this is not a substitute for paired or hierarchical power analysis.

## Results

```json
{
  "assumptions": {
    "alpha": 0.05,
    "baseline": 0.5,
    "method": "normal approximation for independent binary proportions; planning only",
    "power": 0.8,
    "two_sided": true
  },
  "recommendations": [
    {
      "minimum_effect": 0.03,
      "required_scenarios_per_variant": 4359,
      "seeds": [
        3,
        5
      ],
      "total_evaluations_per_variant": 8718
    },
    {
      "minimum_effect": 0.05,
      "required_scenarios_per_variant": 1568,
      "seeds": [
        3,
        5
      ],
      "total_evaluations_per_variant": 3136
    },
    {
      "minimum_effect": 0.1,
      "required_scenarios_per_variant": 391,
      "seeds": [
        3,
        5
      ],
      "total_evaluations_per_variant": 782
    }
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

The output is a planning recommendation, not evidence that the future model will achieve any listed effect.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Refine with pilot variance, paired scenario structure, multiple-comparison correction, and actual Transformer compute constraints.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/power-analysis/20260909T020006Z-66018a`
- Analysis: `results/analyses/hv-v0.5.0/power-analysis/20260909T020006Z-66018a/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
