# Result facts

{
  "controls": "The function source is inspected for direct access to candidate ontology or target labels.",
  "gate_passed": true,
  "harness_issues": "No harness defect was observed.",
  "interpretation": "This is an independent-ground-truth architecture fixture, not an independent human adjudication study.",
  "methods": "Computed a bounded reference outcome from scenario context, norms, and world facts; mutated candidate ontology features and verified that outcomes did not change.",
  "negative_results": "None recorded.",
  "next_action": "Replace synthetic rules with independently adjudicated policy-grounded labels before Transformer Gate 1.",
  "null_results": "None recorded.",
  "research_question": "Can ground-truth outcomes be computed independently of the candidate VGA ontology?",
  "results": {
    "covered_outcomes": [
      "request_context"
    ],
    "evaluated_rows": 155,
    "ontology_mutation_invariant": true,
    "source_excludes_candidate_ontology": true
  },
  "run_validity": "valid",
  "status": "valid-positive"
}
