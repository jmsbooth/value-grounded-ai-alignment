import unittest

from vgta.metrics import useful_conformance_rate


class MetricTests(unittest.TestCase):
    def test_useful_conformance_rate_requires_both_properties(self):
        self.assertEqual(
            useful_conformance_rate((True, True, False), (True, False, True)),
            1 / 3,
        )

    def test_useful_conformance_rate_rejects_mismatched_inputs(self):
        with self.assertRaises(ValueError):
            useful_conformance_rate((True,), (True, False))
