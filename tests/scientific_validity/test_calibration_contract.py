from vgta_eval.calibration import brier_score, expected_calibration_error


def test_known_brier_and_ece_fixture_values():
    rows = [
        {"action_probabilities": [0.9, 0.1], "target_action_index": 0},
        {"action_probabilities": [0.6, 0.4], "target_action_index": 1},
    ]
    # Multiclass Brier score averages the squared error over all action
    # coordinates: (0.02 + 0.72) / 2 = 0.37.
    assert abs(brier_score(rows) - 0.37) < 1e-12
    # Both confidences fall in the upper bin: mean confidence .75, accuracy .5.
    assert abs(expected_calibration_error(rows, bins=2) - 0.25) < 1e-12
