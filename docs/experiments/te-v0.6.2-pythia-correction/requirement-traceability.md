# v0.6.2 requirement traceability

Statuses are tied to receipt digests; missing model runs remain explicit and do not become passes.

| Requirement | Implementation path | Receipt | Receipt hash | Status |
|---|---|---|---|---|
| F01 | `response_contract.py` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F02 | `test_variant_correction.py` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F03 | `test_variant_correction.py` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F04 | `corrected_variant_smoke.py` | `results/raw/te-v0.6.2-pythia-correction/corrected-variant-smoke/20260912T212527Z-corrected-smoke/evidence-receipt.json` | `fb2821428941ffdc6723f94e4f86a2dc62cb00a29c43c699c35c430fc95db17c` | `PASS` |
| F05 | `auxiliary_isolation_correction.py` | `results/raw/te-v0.6.2-pythia-correction/auxiliary-isolation/20260912T211208Z-aux-only/evidence-receipt.json` | `538936a1761df16fa3de42097fb5ef3ae46846b439d1bfb2c7452a92ac6e2ee3` | `PASS` |
| F06 | `candidate_evaluator.py` | `results/raw/te-v0.6.2-pythia-correction/independent-scoring/20260912T210941Z-independent-score/evidence-receipt.json` | `204a746d45807cb25dbfea1599b03baac9adf0d03d5f845c4612c51867f6c20b` | `PASS` |
| F07 | `training.py` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F08 | `training.py` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F09 | `.github/workflows/transformer-contracts.yml` | `results/raw/te-v0.6.2-pythia-correction/contract-tests/20260912T213317Z-contracts/evidence-receipt.json` | `51284f44dbbdb61af43b921f1279f7fadfdcb40569986ad22e15108957c9cb40` | `PASS` |
| F10 | `correction_gate.py` | `results/reports/te-v0.6.2-pythia-correction/correction-gate-receipt.json` | `405aea61425c5baaf74e17316774bfb7b738748346f9b61950311dbab96c9f7f` | `PASS` |
| EOS | `audit_eos_correction.py` | `results/raw/te-v0.6.2-pythia-correction/eos-tokenizer-audit/20260912T210948Z-eos-audit/evidence-receipt.json` | `976af0f80c03cf65b92a58d900cd43b77cc291a7ffe8c535b21cf67426ecca1b` | `PASS` |
| RESOURCE | `resource_profile_correction.py` | `results/raw/te-v0.6.2-pythia-correction/common-resource-profile/20260912T211352Z-common-resource/evidence-receipt.json` | `a07ead5a5ba1a6981df30b24d8dad11b37fdb2466f3c1f65b79863e418073c3a` | `PASS` |
| HISTORY | `finalize_correction.py` | `docs/experiments/te-v0.6.2-pythia-correction/final-state-receipt.json` | `5032c9d5f2bca5829b66e95666ad9be18b339e5972bbec019a21f62cdd6314ea` | `PASS` |

The actual Pythia memorization, A1, variant-smoke, and clean/attack artifacts are listed in the correction report. A partial canary is not substituted for the full declared matrix.
