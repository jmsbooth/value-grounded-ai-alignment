import pytest
from dataclasses import replace

from vgta_eval.input_contracts import InputContractError, validate_public_example, validate_public_mapping
from vgta_eval.semantic_worlds import ACTION_CATALOGUE, generate_semantic_dataset, generate_v2_dataset


def test_public_examples_have_fixed_catalogue_and_no_private_fields():
    dataset = generate_semantic_dataset(group_counts={"train": 2, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    for example in dataset.examples:
        validate_public_example(example)
        assert example.action_catalogue == ACTION_CATALOGUE
        assert example.public_id not in example.public_input
        assert "world-" not in example.public_input


def test_recursive_public_contract_rejects_reference_fields():
    with pytest.raises(InputContractError):
        validate_public_mapping({"input": {"labels": {"action": "candidate_01"}}})


def test_private_label_permutation_does_not_change_public_inference_bytes():
    dataset = generate_v2_dataset(profile="mini")
    example = dataset.by_split("train")[0]
    annotation = dataset.annotation_map()[example.public_id]
    permuted = replace(annotation, candidate_id="candidate_05", action="decline the requested operation")
    assert permuted.candidate_id != annotation.candidate_id
    assert example.model_bytes(structured=True) == example.model_bytes(structured=True)
    assert annotation.public_id not in example.model_bytes(structured=True).decode()
