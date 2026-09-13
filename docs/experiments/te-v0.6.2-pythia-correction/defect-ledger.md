# v0.6.2 defect ledger

The ledger is a human-readable index. Machine-readable defect definitions are
in `experiments/protocols/te-v0.6.2-pythia-correction/defects.yaml`; decisive
test and run receipt links are added as the work packages execute.

| ID | Failure mode | Correction path | Status at phase start |
|---|---|---|---|
| F01 | Automatic or missing supervised EOS | `src/vgta_transformer/response_contract.py` and real tokenizer audit | open |
| F02 | B-TEXT-A used natural A1 input and uniform loss | corrected variant plan and response spans | open |
| F03 | C1-TEXT-N did not weight normative/conflict spans | corrected variant plan and response spans | open |
| F04 | C2-SHAM shuffled all auxiliary targets | seeded intended-target permutation only | open |
| F05 | Auxiliary diagnostic included response loss | aux-only, detach, disabled-head, gradient tests | open |
| F06 | Model booleans/literal reference score used for evaluation | independent candidate evaluator | open |
| F07 | Physical batching differed from A1 objective | global-denominator microbatch update | open |
| F08 | Parameter accounting counted frozen model parameters as allocated trainables | explicit parameter categories | open |
| F09 | Paper CI path and Transformer contract coverage were incomplete | workflow working directory and CPU contracts job | open |
| F10 | Readiness used names/counts/booleans without artifact receipts | receipt-linked non-vacuous gate | open |

No row is marked validated until its named test or actual run receipt exists.
