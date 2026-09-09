# Result facts

{
  "controls": "The surface-only structural-OOD accuracy is the primary shortcut gate; all other controls are diagnostic comparisons.",
  "gate_passed": true,
  "harness_issues": "No harness defect was observed.",
  "interpretation": "A surface control below the predefined 0.90 structural-OOD triviality threshold is not evidence of structured reasoning; it only removes one obvious shortcut explanation.",
  "methods": "Trained majority, bag-of-words, TF-IDF logistic, metadata-only, sequence-length-only, and topology-summary controls on the train split and evaluated the sealed split, including structural-OOD rows.",
  "negative_results": "None recorded.",
  "next_action": "Retain the control outputs as a required baseline for every future model comparison.",
  "null_results": "A low surface baseline does not establish that the target model uses the intended semantic mechanism.",
  "research_question": "Are structured tasks not trivially solved by surface shortcuts?",
  "results": {
    "baselines": {
      "bag_of_words": {
        "overall_accuracy": 0.1568627450980392,
        "predictions": 51,
        "structural_ood_accuracy": 0.3333333333333333
      },
      "majority": {
        "overall_accuracy": 0.1568627450980392
      },
      "metadata_only": {
        "overall_accuracy": 0.19607843137254902,
        "predictions": 51,
        "structural_ood_accuracy": 0.3333333333333333
      },
      "sequence_length_only": {
        "overall_accuracy": 0.11764705882352941,
        "predictions": 51,
        "structural_ood_accuracy": 0.3333333333333333
      },
      "tfidf_logistic": {
        "overall_accuracy": 0.5098039215686274,
        "predictions": 51,
        "structural_ood_accuracy": 0.3333333333333333
      },
      "topology_summary": {
        "overall_accuracy": 0.5098039215686274,
        "predictions": 51,
        "structural_ood_accuracy": 0.3333333333333333
      }
    },
    "gate": {
      "passed": true,
      "surface_baseline_not_trivial": true,
      "surface_structural_ood_accuracy": 0.3333333333333333
    },
    "labels": [
      "answer",
      "ask_clarifying_question",
      "code",
      "escalate",
      "execute_minimally",
      "extract",
      "inspect_security_log",
      "offer_opt_in",
      "request_consent",
      "request_context",
      "retain_safety_control",
      "summarize"
    ]
  },
  "run_validity": "valid",
  "status": "valid-positive"
}
