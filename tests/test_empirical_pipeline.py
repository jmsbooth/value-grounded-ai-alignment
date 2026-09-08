import unittest

from vgta_eval.conformance import REQUIRED_ACTION_FIELDS, normalize_candidate
from vgta_eval.model import MODEL_VARIANT_GROUPS, ModelConfig, SmallSemanticModel, feature_vocabulary
from vgta_eval.scenario_generator import (
    ACTION_LABELS,
    CAPABILITY_LABELS,
    CONFLICT_LABELS,
    PURPOSE_LABELS,
    RELATION_LABELS,
    VALUE_LABELS,
    dataset_manifest,
    generate_dataset,
)
from vgta_eval.statistical_tests import paired_bootstrap_difference


class EmpiricalPipelineTests(unittest.TestCase):
    def test_sealed_structural_topologies_do_not_overlap_training(self):
        manifest = dataset_manifest(generate_dataset())
        self.assertEqual(manifest["sealed_structural_topology_overlap_with_train"], [])
        self.assertTrue(manifest["sealed_test_training_exclusion"])

    def test_variants_share_allocated_parameter_count(self):
        records = generate_dataset()
        labels = {
            "action": ACTION_LABELS,
            "value": VALUE_LABELS,
            "relation": RELATION_LABELS,
            "conflict": CONFLICT_LABELS,
            "purpose": PURPOSE_LABELS,
            "capability": CAPABILITY_LABELS,
        }
        vocabulary = feature_vocabulary(records["train"])
        models = [
            SmallSemanticModel(vocabulary, labels, ModelConfig(epochs=1), seed=seed)
            for seed in (11, 23, 37)
        ]
        self.assertEqual(len({model.parameter_count for model in models}), 1)
        self.assertNotEqual(MODEL_VARIANT_GROUPS["A1"], MODEL_VARIANT_GROUPS["C2"])

    def test_candidate_schema_rejects_missing_fields(self):
        candidate, errors = normalize_candidate({}, name="missing")
        self.assertIsNone(candidate)
        self.assertIn("missing required action fields", errors[0])
        self.assertEqual(len(REQUIRED_ACTION_FIELDS), 12)

    def test_ontology_degradation_changes_information_and_safe_target(self):
        records = generate_dataset()["sealed-test"]
        intact = next(row for row in records if row["example_id"] == "sea-degrade-0-intact")
        degraded = next(row for row in records if row["example_id"] == "sea-degrade-4-intact")
        contradictory = next(row for row in records if row["example_id"] == "sea-degrade-0-contradictory")
        self.assertEqual(intact["labels"]["action"], "request_consent")
        self.assertEqual(degraded["labels"]["action"], "request_context")
        self.assertEqual(contradictory["labels"]["action"], "request_context")
        self.assertGreater(len(intact["feature_groups"]["axiological"]), len(degraded["feature_groups"]["axiological"]))

    def test_zero_variance_effect_is_explicitly_undefined(self):
        _, _, effect = paired_bootstrap_difference((0.2, 0.2, 0.2), (0.1, 0.1, 0.1))
        self.assertIsNone(effect)
