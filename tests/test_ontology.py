from pathlib import Path
import unittest

from vgta.ontology import Ontology, parse_turtle


ROOT = Path(__file__).resolve().parents[1]


class OntologyTests(unittest.TestCase):
    def test_core_fixture_parses(self):
        ontology = Ontology.from_turtle(ROOT / "ontology/axiology/core-axiology.ttl")
        self.assertGreaterEqual(len(ontology.triples), 10)
        self.assertTrue(
            ontology.contains(
                "https://example.org/vga#Coercion",
                "https://example.org/vga#negativelyAffects",
                "https://example.org/vga#Agency",
            )
        )

    def test_parser_expands_prefixes(self):
        ontology = parse_turtle(
            "@prefix x: <https://example.test#> .\n"
            "x:A x:rel x:B .\n"
        )
        self.assertEqual(ontology.triples[0].subject, "https://example.test#A")
