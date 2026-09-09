# VGA/VGTA Harness Validation Report — hv-v0.5.0__dataset-leakage-audit__20260909T015925Z-fba5e8__a001

Experiment ID: `dataset-leakage-audit`  
Protocol: `hv-v0.5.0`  
Run ID: `20260909T015925Z-fba5e8`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.0__dataset-leakage-audit__20260909T015925Z-fba5e8__a001`  
Created: `2026-09-09T01:59:26.446519+00:00`  
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
      "count": 22,
      "status": "documented_overlap",
      "values": [
        "analyst",
        "author",
        "child",
        "developer",
        "document",
        "employee",
        "hypothesis",
        "investigation",
        "investigator",
        "log",
        "manager",
        "operator",
        "person",
        "question",
        "reader",
        "record",
        "requester",
        "review",
        "service",
        "specification",
        "table",
        "user"
      ]
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
      "count": 1,
      "predictive_power": {
        "family": 0.5490196078431373,
        "surface_length": 0.5882352941176471,
        "template_id": 0.9607843137254902,
        "transform": 0.5294117647058824
      },
      "status": "review"
    },
    "paraphrase_similarity": {
      "count": 6,
      "highest_similarity_pairs": [
        {
          "heldout_example_id": "sea-00122-attack-injection",
          "similarity": 0.9718,
          "train_example_id": "tra-00119-attack-injection"
        },
        {
          "heldout_example_id": "sea-00140-attack-authority",
          "similarity": 0.9706,
          "train_example_id": "tra-00137-attack-authority"
        },
        {
          "heldout_example_id": "sea-00131-attack-purpose",
          "similarity": 0.9683,
          "train_example_id": "tra-00128-attack-purpose"
        },
        {
          "heldout_example_id": "sea-00149-attack-poisoning",
          "similarity": 0.9655,
          "train_example_id": "tra-00146-attack-poisoning"
        },
        {
          "heldout_example_id": "sea-00158-attack-occlusion",
          "similarity": 0.9535,
          "train_example_id": "tra-00155-attack-occlusion"
        },
        {
          "heldout_example_id": "sea-00186-cap-code",
          "similarity": 0.8219,
          "train_example_id": "tra-00182-cap-code"
        }
      ],
      "status": "review"
    },
    "template_identity": {
      "count": 22,
      "status": "documented_overlap",
      "values": [
        "attack-authority",
        "attack-injection",
        "attack-occlusion",
        "attack-poisoning",
        "attack-purpose",
        "cap-answer",
        "cap-code",
        "cap-extract",
        "cap-summary",
        "conflict-authority",
        "conflict-emergency",
        "conflict-privacy-safety",
        "ood-coercion",
        "ood-delegation",
        "ood-dependence",
        "purpose-admin",
        "purpose-creative",
        "purpose-incident",
        "salience-coercion",
        "salience-privacy",
        "salience-safety",
        "salience-vulnerability"
      ]
    },
    "topology_overlap": {
      "count": 15,
      "status": "review",
      "values": [
        "177f940835f26aa4",
        "51146dc6e45a9d00",
        "57404fff838c6a02",
        "601e1e5dd17a5ba4",
        "9dd62ebab7105e0a",
        "a29cc040c6e73894",
        "b34b06f995c94f67",
        "bf1fdef7542dc10c",
        "c6cfdb2698f2da75",
        "cf55a008d433af4d",
        "d3393b3528fd932c",
        "e386e69224fe0621",
        "e5f2eb379b73f7a2",
        "e7a3c47b77cf867e",
        "febce56ce01df801"
      ]
    }
  },
  "gate_passed": false,
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

Harness acceptance for this experiment: **not passed**. Evidence status: `valid-negative`.

## Next action

Review each non-pass class and create a new frozen dataset version before confirmatory use.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.0/dataset-leakage-audit/20260909T015925Z-fba5e8`
- Analysis: `results/analyses/hv-v0.5.0/dataset-leakage-audit/20260909T015925Z-fba5e8/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.0/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
