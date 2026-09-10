from vgta_eval.semantic_worlds import ACTION_CATALOGUE, generate_semantic_dataset


def test_natural_and_structured_variants_share_the_same_public_catalogue():
    dataset = generate_semantic_dataset(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    example = dataset.examples[0]
    assert example.action_catalogue == ACTION_CATALOGUE
    assert example.model_bytes(structured=True) != example.model_bytes(structured=False)
    assert "candidate_id" not in example.model_bytes(structured=True).decode()

