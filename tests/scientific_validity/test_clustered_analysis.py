from vgta_eval.paired_analysis import clustered_bootstrap_delta, raw_denominators


def test_bootstrap_uses_world_group_as_unit_and_preserves_denominators():
    rows = [
        {"variant": "A1", "seed": 11, "split": "locked", "attack": "none", "world_group_id": "g1", "correct": 0},
        {"variant": "B", "seed": 11, "split": "locked", "attack": "none", "world_group_id": "g1", "correct": 1},
        {"variant": "A1", "seed": 11, "split": "locked", "attack": "none", "world_group_id": "g2", "correct": 0},
        {"variant": "B", "seed": 11, "split": "locked", "attack": "none", "world_group_id": "g2", "correct": 0},
    ]
    result = clustered_bootstrap_delta(rows, left_variant="A1", right_variant="B", resamples=100, seed=1)
    assert result["unit_of_inference"] == "world_group_id"
    assert result["clusters"] == 2
    assert result["delta"] == 0.5
    assert sum(raw_denominators(rows).values()) == 4

