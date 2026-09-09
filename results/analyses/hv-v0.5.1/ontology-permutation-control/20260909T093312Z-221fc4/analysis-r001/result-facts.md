# Result facts

{
  "controls": "The experiment records both original and permuted controls; it does not treat a performance drop alone as proof of semantic grounding.",
  "gate_passed": true,
  "harness_issues": "No harness defect was observed.",
  "interpretation": "The permutation is a valid control only when it demonstrably changes the structured input and remains separately identified from the original ontology.",
  "methods": "Applied a seeded edge permutation to held-out topology summaries while preserving row count and control code, then compared the topology-summary baseline.",
  "negative_results": "None recorded.",
  "next_action": "Add label-permuted and degree-preserving graph controls before confirmatory use.",
  "null_results": "None recorded.",
  "research_question": "Does semantic structure provide information beyond arbitrary graph/features?",
  "results": {
    "edge_permuted": true,
    "label_permutation": "not run in this bounded fixture",
    "original_topology_accuracy": 0.5098039215686274,
    "permutation_changed_rows": 49,
    "permuted_topology_accuracy": 0.5098039215686274
  },
  "run_validity": "valid",
  "status": "valid-positive"
}
