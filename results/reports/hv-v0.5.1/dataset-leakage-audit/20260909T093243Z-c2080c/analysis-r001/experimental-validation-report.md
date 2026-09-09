# VGA/VGTA Harness Validation Report — hv-v0.5.1__dataset-leakage-audit__20260909T093243Z-c2080c__a001

Experiment ID: `dataset-leakage-audit`  
Protocol: `hv-v0.5.1`  
Run ID: `20260909T093243Z-c2080c`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.1__dataset-leakage-audit__20260909T093243Z-c2080c__a001`  
Created: `2026-09-09T09:32:45.301299+00:00`  
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

Are train and held-out records free of unexplained leakage?

## Method

Audited train versus sealed-test records for exact normalized-surface duplicates, high paraphrase similarity, template identity, topology hashes, entity instances, metadata predictive power, and formatting markers.

## Controls

Documented template and entity overlap is reported separately from unexplained duplication. Structural topology overlap is never silently accepted.

## Results

```json
{
  "classes": {
    "entity_instance_overlap": {
      "count": 0,
      "status": "pass",
      "values": []
    },
    "exact_duplicate": {
      "count": 0,
      "pairs": [],
      "status": "pass"
    },
    "formatting_leakage": {
      "count": 0,
      "note": "No split marker is included in the surface text audit.",
      "status": "pass"
    },
    "label_metadata_leakage": {
      "count": 0,
      "excess_over_majority": {
        "family": 0.0025300442757748287,
        "surface_length": -0.036685641998734975,
        "template_id": -0.036685641998734975,
        "transform": -0.036685641998734975
      },
      "excess_threshold": 0.1,
      "majority_baseline": 0.1935483870967742,
      "predictive_power": {
        "family": 0.19607843137254902,
        "surface_length": 0.1568627450980392,
        "template_id": 0.1568627450980392,
        "transform": 0.1568627450980392
      },
      "status": "pass"
    },
    "paraphrase_similarity": {
      "count": 0,
      "highest_similarity_pairs": [],
      "status": "pass"
    },
    "template_identity": {
      "count": 0,
      "status": "pass",
      "values": []
    },
    "topology_overlap": {
      "count": 0,
      "status": "pass",
      "values": []
    }
  },
  "gate_passed": true,
  "heldout_records": 51,
  "interpretation": "Documented template/entity overlap is not treated as unexplained leakage; exact duplicates, high paraphrase similarity, topology overlap, and metadata predictive power require review before confirmatory use.",
  "train_records": 124
}
```

## Null results

None recorded.

## Negative results

The gate is not passed if exact duplicates, high similarity, topology overlap, or highly predictive metadata remain unexplained.

## Harness issues

No harness defect was observed.

## Interpretation

Documented template/entity overlap is not treated as unexplained leakage; exact duplicates, high paraphrase similarity, topology overlap, and metadata predictive power require review before confirmatory use.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Review each non-pass class and create a new frozen dataset version before confirmatory use.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.1/dataset-leakage-audit/20260909T093243Z-c2080c`
- Analysis: `results/analyses/hv-v0.5.1/dataset-leakage-audit/20260909T093243Z-c2080c/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.1/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
