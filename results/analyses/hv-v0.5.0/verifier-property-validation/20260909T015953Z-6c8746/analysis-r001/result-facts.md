# Result facts

{
  "artifacts": {},
  "controls": "The property predicate is separate from the verifier implementation and includes incomplete semantic state as rejection.",
  "gate_passed": true,
  "harness_issues": "No bounded property mismatch observed.",
  "interpretation": "Passing bounded property checks is not formal assurance; it is a prerequisite for claiming stronger verifier coverage.",
  "methods": "Exhaustively enumerated the bounded boolean and threshold fixture space against an independently written property predicate.",
  "negative_results": "None recorded.",
  "next_action": "Add property-based generation and explicit stale-evidence/conflict fixtures.",
  "null_results": "None recorded.",
  "research_question": "Does the verifier obey authorization, consent, coercion, harm, completeness, and unknown-state properties?",
  "results": {
    "fixtures": 64,
    "properties": [
      "authorization",
      "consent",
      "coercion",
      "harm",
      "semantic completeness",
      "unknown state"
    ],
    "property_failures": []
  },
  "run_validity": "valid",
  "status": "valid-positive"
}
