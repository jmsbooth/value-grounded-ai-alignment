#!/usr/bin/env python3
"""Run the v0.5.2 semantic-validity gate on the new benchmark."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt
from vgta_eval.graph_identity import TypedGraph, graph_content_hash, reorder_edges, typed_relation_fingerprint, unlabeled_structure_fingerprint
from vgta_eval.input_contracts import validate_public_example
from vgta_eval.observation_projection import project_world
from vgta_eval.reference_policy import interpret_observation
from vgta_eval.semantic_worlds import ACTION_CATALOGUE, build_worlds, generate_semantic_dataset


def audit() -> dict[str, object]:
    dataset = generate_semantic_dataset(group_counts={"train": 12, "validation": 6, "calibration": 6, "open-dev": 6, "locked-engineering-eval": 6})
    checks: dict[str, bool] = {}
    for example in dataset.examples:
        validate_public_example(example)
    checks["public_label_isolation"] = True
    checks["fixed_action_catalogue"] = all(example.action_catalogue == ACTION_CATALOGUE for example in dataset.examples)
    checks["split_group_disjointness"] = all(
        len({example.world_group_id for example in dataset.examples if example.split == left}.intersection(
            {example.world_group_id for example in dataset.examples if example.split == right})) == 0
        for left in {example.split for example in dataset.examples}
        for right in {example.split for example in dataset.examples}
        if left != right
    )
    worlds = build_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    baseline = worlds[0]
    checks["template_permutation_invariance"] = interpret_observation(project_world(baseline)) == interpret_observation(project_world(replace(baseline, template_id="unrelated-template")))
    changed = replace(baseline, facts=tuple(replace(fact, object="inactive" if fact.subject == "delegation" else fact.object) for fact in baseline.facts))
    checks["facts_change_outcome"] = interpret_observation(project_world(baseline)).candidate_id != interpret_observation(project_world(changed)).candidate_id
    graph = TypedGraph(baseline.nodes, baseline.edges)
    checks["graph_edge_reordering_invariant"] = (
        unlabeled_structure_fingerprint(graph) == unlabeled_structure_fingerprint(reorder_edges(graph))
        and typed_relation_fingerprint(graph) == typed_relation_fingerprint(reorder_edges(graph))
        and graph_content_hash(graph) == graph_content_hash(reorder_edges(graph))
    )
    checks["semantic_outcomes_present"] = len({annotation.candidate_id for annotation in dataset.annotations}) >= 4
    passed = all(checks.values())
    return {
        "protocol": "hv-v0.5.2-semantic-validity",
        "dataset_version": "pythia-policy-dev-v1",
        "synthetic": True,
        "checks": checks,
        "status": "SEMANTIC_DATASET_VALIDATED" if passed else "SEMANTIC_DATASET_REJECTED",
        "row_counts": {split: len(dataset.by_split(split)) for split in {example.split for example in dataset.examples}},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/semantic-validity")
    args = parser.parse_args()
    report = audit()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "semantic-audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(args.output_dir / "evidence-receipt.json", make_receipt(
        producer_kind="semantic_audit",
        protocol="hv-v0.5.2-semantic-validity",
        status=str(report["status"]),
        checks=report["checks"],
        synthetic=True,
    ))
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "SEMANTIC_DATASET_VALIDATED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
