# Result facts

{
  "controls": "Mutations are evaluated against the independent property/reference behavior, not only against the implementation's own output.",
  "gate_passed": true,
  "harness_issues": "No harness defect was observed.",
  "interpretation": "A 100% detection rate is limited to the enumerated mutations and fixture domain.",
  "methods": "Applied five declared verifier mutations and checked that each produced a disagreement on the bounded critical-fixture suite.",
  "negative_results": "None recorded.",
  "next_action": "Keep mutation testing in CI and expand mutations as verifier rules grow.",
  "null_results": "None recorded.",
  "research_question": "Do verifier tests detect every explicitly enumerated critical mutation?",
  "results": {
    "fixtures": 64,
    "mutation_detection_rate": 1.0,
    "mutations": {
      "change AND to OR": true,
      "drop consent check": true,
      "ignore stale evidence": true,
      "invert authorization check": true,
      "skip unknown condition": true
    },
    "target": 1.0
  },
  "run_validity": "valid",
  "status": "valid-positive"
}
