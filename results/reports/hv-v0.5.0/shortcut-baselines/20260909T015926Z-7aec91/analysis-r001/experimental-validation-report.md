# VGA/VGTA Harness Validation Report — hv-v0.5.0__shortcut-baselines__20260909T015926Z-7aec91__a001

Experiment ID: `shortcut-baselines`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015926Z-7aec91`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__shortcut-baselines__20260909T015926Z-7aec91__a001`  
Created: `2026-09-09T01:59:29.070397+00:00`  
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

Are structured tasks not trivially solved by surface shortcuts?

## Method

Trained majority, bag-of-words, TF-IDF logistic, metadata-only, sequence-length-only, and topology-summary controls on the train split and evaluated the sealed split, including structural-OOD rows.

## Controls

The surface-only structural-OOD accuracy is the primary shortcut gate; all other controls are diagnostic comparisons.

## Results

```json
{
  "baselines": {
    "bag_of_words": {
      "overall_accuracy": 0.3137254901960784,
      "predictions": 51,
      "structural_ood_accuracy": 0.3333333333333333
    },
    "majority": {
      "overall_accuracy": 0.1568627450980392
    },
    "metadata_only": {
      "overall_accuracy": 0.6274509803921569,
      "predictions": 51,
      "structural_ood_accuracy": 1.0
    },
    "sequence_length_only": {
      "overall_accuracy": 0.11764705882352941,
      "predictions": 51,
      "structural_ood_accuracy": 0.3333333333333333
    },
    "tfidf_logistic": {
      "overall_accuracy": 0.3137254901960784,
      "predictions": 51,
      "structural_ood_accuracy": 0.3333333333333333
    },
    "topology_summary": {
      "overall_accuracy": 0.6274509803921569,
      "predictions": 51,
      "structural_ood_accuracy": 1.0
    }
  },
  "gate": {
    "passed": true,
    "surface_baseline_not_trivial": true,
    "surface_structural_ood_accuracy": 0.3333333333333333
  },
  "labels": [
    "answer",
    "ask_clarifying_question",
    "code",
    "escalate",
    "execute_minimally",
    "extract",
    "inspect_security_log",
    "offer_opt_in",
    "request_consent",
    "request_context",
    "retain_safety_control",
    "summarize"
  ]
}
```

## Null results

A low surface baseline does not establish that the target model uses the intended semantic mechanism.

## Negative results

None recorded.

## Harness issues

No harness defect was observed.

## Interpretation

A surface control below the predefined 0.90 structural-OOD triviality threshold is not evidence of structured reasoning; it only removes one obvious shortcut explanation.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Retain the control outputs as a required baseline for every future model comparison.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/shortcut-baselines/20260909T015926Z-7aec91`
- Analysis: `results/analyses/hv-v0.5.0/shortcut-baselines/20260909T015926Z-7aec91/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
