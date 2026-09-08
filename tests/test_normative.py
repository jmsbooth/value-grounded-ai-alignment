import unittest

from vgta.normative import (
    NormativeAssertion,
    NormativeAuthority,
    authority_function,
    classify_conflict,
    resolve_conflict,
)


class NormativeTests(unittest.TestCase):
    def make_assertion(self, identifier: str, proposition: str) -> NormativeAssertion:
        return NormativeAssertion(
            identifier=identifier,
            proposition=proposition,
            scope="medical-record",
            authority=NormativeAuthority(
                source="policy",
                authority="review-board",
                jurisdiction="organization-a",
                precedence=1,
            ),
        )

    def test_conflict_remains_explicit_and_can_escalate(self):
        conflict = classify_conflict(
            self.make_assertion("privacy", "protect-confidentiality"),
            self.make_assertion("safety", "disclose-in-emergency"),
        )
        self.assertEqual(conflict.state, "unresolved")
        self.assertEqual(authority_function(self.make_assertion("n", "p")).precedence, 1)
        self.assertEqual(resolve_conflict(conflict), "escalate")
