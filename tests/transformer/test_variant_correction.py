from pathlib import Path

import torch

from experiments.transformer.experiment_utils import auxiliary_target_tensors
from vgta_eval.semantic_worlds import generate_v2_dataset
from vgta_transformer.variant_plan import load_variant_specs


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "experiments/protocols/te-v0.6.2-pythia-correction/variants.yaml"


def test_corrected_variants_have_exact_declared_input_and_sham_scope():
    variants = load_variant_specs(PLAN)
    assert variants["B-TEXT-A"].structured
    assert variants["B-TEXT-A"].span_weight_fields == ("salient_values", "relation_class")
    assert variants["C1-TEXT-N"].span_weight_fields == ("applicable_norm_ids", "conflict_class")
    assert variants["C1-SHAM"].shuffled_targets == ("values", "relation")
    assert variants["C2-SHAM"].shuffled_targets == ("norms", "conflict")
    assert not variants["C1-SHAM"].shuffled_targets == ("values", "relation", "norms", "conflict")
    assert len({variant.fingerprint for variant in variants.values()}) == 8


def test_all_arms_share_public_bytes_for_structured_variants():
    dataset = generate_v2_dataset(profile="mini")
    example = dataset.by_split("train")[0]
    variants = load_variant_specs(PLAN)
    structured_bytes = example.model_bytes(structured=True)
    assert all(example.model_bytes(structured=spec.structured) == structured_bytes for name, spec in variants.items() if spec.structured)
    assert variants["A1"].structured is False


def test_sham_targets_change_only_the_declared_arrays():
    dataset = generate_v2_dataset(profile="mini")
    annotations = dataset.annotation_map()
    train = dataset.by_split("train")
    targets = auxiliary_target_tensors([annotations[example.public_id] for example in train])
    permutation = list(reversed(range(len(train))))
    c1_sham = {name: value[permutation] if name in {"values", "relation"} else value for name, value in targets.items()}
    c2_sham = {name: value[permutation] if name in {"norms", "conflict"} else value for name, value in targets.items()}
    assert all(torch.equal(targets[name], c2_sham[name]) for name in ("values", "relation"))
    assert all(torch.equal(targets[name], c1_sham[name]) for name in ("norms", "conflict"))
    assert any(not torch.equal(targets[name], c1_sham[name]) for name in ("values", "relation"))
    assert any(not torch.equal(targets[name], c2_sham[name]) for name in ("norms", "conflict"))
