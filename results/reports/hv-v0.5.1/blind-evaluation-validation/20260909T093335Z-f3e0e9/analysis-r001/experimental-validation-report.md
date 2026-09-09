# VGA/VGTA Harness Validation Report — hv-v0.5.1__blind-evaluation-validation__20260909T093335Z-f3e0e9__a001

Experiment ID: `blind-evaluation-validation`  
Protocol: `hv-v0.5.1`  
Run ID: `20260909T093335Z-f3e0e9`  
Analysis revision: `analysis-r001`  
Report ID: `hv-v0.5.1__blind-evaluation-validation__20260909T093335Z-f3e0e9__a001`  
Created: `2026-09-09T09:33:36.259790+00:00`  
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

Can variant identity remain hidden through metric generation?

## Method

Replaced model variant labels with opaque VX aliases and audited output rows for variant-name fields, architecture fields, and invalid aliases.

## Controls

The unblinding map is stored separately from the blinded rows and is not used during metric generation.

## Results

```json
{
  "audit": {
    "invalid_aliases": [],
    "leaks": [],
    "passed": true
  },
  "blinded_rows": [
    {
      "example_id": "v04-sea-00008-salience-privacy",
      "variant": "VX-03"
    },
    {
      "example_id": "v04-sea-00017-salience-coercion",
      "variant": "VX-01"
    },
    {
      "example_id": "v04-sea-00026-salience-safety",
      "variant": "VX-04"
    },
    {
      "example_id": "v04-sea-00035-salience-vulnerability",
      "variant": "VX-02"
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

The bounded alias audit validates the interface only; a real blind evaluator must separate file paths, logs, and analysis access as well.

## Gate decision

Harness acceptance for this experiment: **passed**. Evidence status: `valid-positive`.

## Next action

Store sealed variant-map.json outside the analysis input path and test end-to-end unblinding after report draft generation.

## Source artifacts

- Raw run: `results/raw/hv-v0.5.1/blind-evaluation-validation/20260909T093335Z-f3e0e9`
- Analysis: `results/analyses/hv-v0.5.1/blind-evaluation-validation/20260909T093335Z-f3e0e9/analysis-r001`
- Protocol: `experiments/protocols/hv-v0.5.1/`

This report is immutable. Reanalysis must create a new analysis revision and report ID.
