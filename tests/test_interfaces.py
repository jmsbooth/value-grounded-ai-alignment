import inspect
import unittest

from vgta.attention_bias import ontology_attention_bias
from vgta.router import OntologyConditionedRouter
from vgta.semantic_state import SemanticState


class InterfaceTests(unittest.TestCase):
    def test_attention_bias_shape_and_values(self):
        bias = ontology_attention_bias(
            ["agency", "credential"],
            {"agency": 1.0},
            {"credential": 0.5},
            {"credential": 1.0},
        )
        self.assertEqual(bias, ((0.25, 0.375), (0.25, 0.375)))

    def test_router_signature_remains_explicit(self):
        signature = inspect.signature(OntologyConditionedRouter.route)
        self.assertIn("hidden_state", signature.parameters)
        self.assertIn("context", signature.parameters)
        self.assertIn("k", signature.parameters)

    def test_semantic_state_is_serializable(self):
        state = SemanticState(goal="protect agency", relevant_values=["agency"])
        self.assertEqual(state.as_dict()["goal"], "protect agency")
