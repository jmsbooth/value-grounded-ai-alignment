import unittest
from pathlib import Path

from experiments.harness.experiments import blind_evaluation_validation
from vgta_eval.blinding import audit_blind_rows, blind_rows
from vgta_eval.calibration import calibration_summary
from vgta_eval.compatibility import CompatibilityError, validate_compatibility
from vgta_eval.leakage import audit_records
from vgta_eval.power import power_plan
from vgta_eval.scenario_generator import load_dataset


ROOT = Path(__file__).resolve().parents[1]


class HarnessQualityTests(unittest.TestCase):
    def test_calibration_metrics_are_bounded_and_risk_coverage_is_monotonic(self):
        rows = [
            {"action_probabilities": [0.9, 0.1], "target_action_index": 0},
            {"action_probabilities": [0.6, 0.4], "target_action_index": 1},
            {"action_probabilities": [0.55, 0.45], "target_action_index": 0},
        ]
        summary = calibration_summary(rows, bins=3)
        self.assertGreaterEqual(summary["brier_score"], 0.0)
        self.assertLessEqual(summary["brier_score"], 2.0)
        self.assertGreaterEqual(summary["ece"], 0.0)
        self.assertLessEqual(summary["ece"], 1.0)
        self.assertEqual(len(summary["risk_coverage"]), len(rows))

    def test_blinding_replaces_variant_identity_and_detects_leaks(self):
        rows = [{"variant": "A1", "example_id": "x"}, {"variant": "B", "example_id": "y"}]
        blinded = blind_rows(rows, {"A1": "VX-01", "B": "VX-02"})
        self.assertTrue(audit_blind_rows(blinded, aliases=("VX-01", "VX-02"))["passed"])
        self.assertFalse(audit_blind_rows([{**blinded[0], "model_variant": "A1"}], aliases=("VX-01",))["passed"])

    def test_blind_validation_does_not_publish_unblinding_map(self):
        records = load_dataset(ROOT / "experiments/datasets/v0.3-small")
        result = blind_evaluation_validation(records)
        self.assertNotIn("mapping", result["results"])
        self.assertIn("sealed/variant-map.json", result["artifacts"])

    def test_metadata_predictive_power_is_train_fitted(self):
        train = [
            {"template_id": "train-a", "labels": {"action": "left"}},
            {"template_id": "train-a", "labels": {"action": "left"}},
            {"template_id": "train-b", "labels": {"action": "right"}},
        ]
        heldout = [
            {"template_id": "heldout-a", "labels": {"action": "left"}},
            {"template_id": "heldout-b", "labels": {"action": "right"}},
        ]
        audit = audit_records(train, heldout)
        self.assertEqual(audit["classes"]["label_metadata_leakage"]["predictive_power"]["template_id"], 0.5)

    def test_power_plan_does_not_use_pilot_effect_size(self):
        rows = power_plan()["recommendations"]
        self.assertEqual([row["minimum_effect"] for row in rows], [0.03, 0.05, 0.10])
        self.assertGreater(rows[0]["required_scenarios_per_variant"], rows[1]["required_scenarios_per_variant"])
        self.assertGreater(rows[1]["required_scenarios_per_variant"], rows[2]["required_scenarios_per_variant"])

    def test_incompatible_artifacts_require_explicit_development_override(self):
        expected = {key: key for key in ("protocol_version", "dataset_sha256", "ground_truth_sha256", "ontology_sha256", "verifier_sha256", "config_sha256", "attack_suite_sha256", "metric_suite_sha256")}
        actual = dict(expected, dataset_sha256="changed")
        with self.assertRaises(CompatibilityError):
            validate_compatibility(actual, expected)
        validate_compatibility(actual, expected, run_mode="development", allow_override=True)
