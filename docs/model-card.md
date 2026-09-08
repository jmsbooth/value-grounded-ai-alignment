# Model card: shared-MLP mechanism-validation proxy

## Intended use

The model is intended to test whether semantic input channels and auxiliary
training objectives produce measurable differences under controlled synthetic
conditions. It is not a Transformer, production model, authorization system,
or safety monitor.

## Architecture

Each variant uses the same one-hidden-layer tanh MLP, fixed feature vocabulary,
action head, value head, relation head, conflict head, purpose head, and
capability head. Variant masks and loss weights are defined in the runner and
configuration. C1 adds value/relation losses; C2 additionally adds conflict
loss.

## Evaluation

The model is trained with three seeds and evaluated on frozen logical splits.
Raw predictions and manifests are retained under `results/raw/`. The fixed
verifier is applied after model-only prediction, so UCR does not conflate
neural selection with enforcement.

## Limitations

The model has no tokenizer, language pretraining, Transformer attention,
large-scale instruction tuning, DPO, human preference data, or frontier-scale
compute. It cannot support claims about language-model alignment. Results are
mechanism evidence only and must be labeled synthetic.
