from pathlib import Path
import unittest

from vgta.toy_model import Scenario, ScenarioAction, choose_action
from vgta.verifier import CandidateAction, RuleBasedVerifier


class VerifierAndModelTests(unittest.TestCase):
    def test_private_data_without_consent_is_rejected(self):
        result = RuleBasedVerifier().verify(
            CandidateAction(
                name="share record",
                touches_private_data=True,
                consent_obtained=False,
            )
        )
        self.assertFalse(result.permitted)
        self.assertIn("consent", result.reasons[0])

    def test_toy_value_grounding_changes_selection(self):
        scenario = Scenario(
            name="fixture",
            value_weights={"agency": 0.5},
            expected_safe_action="ask",
            actions=(
                ScenarioAction(
                    "pressure",
                    0.9,
                    {"agency": -1.0},
                    CandidateAction("pressure", coercive=True),
                ),
                ScenarioAction(
                    "ask",
                    0.6,
                    {"agency": 1.0},
                    CandidateAction("ask"),
                ),
            ),
        )
        self.assertEqual(choose_action(scenario, "baseline", verify=False).selected_action, "pressure")
        self.assertEqual(choose_action(scenario, "vga_toy").selected_action, "ask")
