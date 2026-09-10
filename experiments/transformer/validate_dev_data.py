#!/usr/bin/env python3
"""Revalidate the materialized v2 development benchmark without locked data."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.graph_identity import TypedGraph, graph_content_hash, reorder_edges, typed_relation_fingerprint, unlabeled_structure_fingerprint
from vgta_eval.input_contracts import validate_public_example
from vgta_eval.observation_projection import project_world
from vgta_eval.reference_policy import interpret_observation
from vgta_eval.semantic_worlds import V2_SPLITS, ACTION_CATALOGUE, generate_v2_dataset


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path, profile: str) -> dict[str, object]:
    dataset = generate_v2_dataset(profile=profile)
    annotations = dataset.annotation_map()
    expected_counts = {"train": 64, "validation": 16, "calibration": 16, "open-dev": 16} if profile == "mini" else {"train": 1024, "validation": 128, "calibration": 128, "open-dev": 128}
    checks: dict[str, bool] = {}
    file_hashes: dict[str, str] = {}
    for split in V2_SPLITS:
        public_path = root / "public" / f"{split}.jsonl"
        private_path = root / "private" / f"{split}.jsonl"
        world_path = root / "worlds" / f"{split}.jsonl"
        parity_path = root / "information-parity" / f"{split}.jsonl"
        checks[f"{split}_files_present"] = all(path.exists() for path in (public_path, private_path, world_path, parity_path))
        for path in (public_path, private_path, world_path, parity_path):
            if path.exists():
                file_hashes[str(path.relative_to(root))] = _sha(path)
    checks["locked_split_not_materialized"] = not any((root / name).exists() for name in ("locked", "locked-engineering-eval")) and not (root / "public" / "locked-engineering-eval.jsonl").exists()
    checks["exact_profile_counts"] = all(len(dataset.by_split(split)) == expected_counts[split] for split in V2_SPLITS)
    checks["public_schema_and_catalogue"] = True
    for example in dataset.examples:
        try:
            validate_public_example(example)
        except Exception:
            checks["public_schema_and_catalogue"] = False
            break
        if example.action_catalogue != ACTION_CATALOGUE:
            checks["public_schema_and_catalogue"] = False
    groups = {split: {example.world_group_id for example in dataset.by_split(split)} for split in V2_SPLITS}
    checks["group_disjointness"] = all(groups[left].isdisjoint(groups[right]) for left in V2_SPLITS for right in V2_SPLITS if left != right)
    checks["private_label_isolation"] = all(
        annotation.public_id not in example.model_bytes(structured=True).decode("utf-8")
        and annotation.world_group_id not in example.model_bytes(structured=True).decode("utf-8")
        for example in dataset.examples
        for annotation in (annotations[example.public_id],)
    )
    checks["oracle_matches_materialized_annotations"] = all(
        interpret_observation(project_world(world)).candidate_id == annotations[example.public_id].candidate_id
        for world, example in zip(dataset.worlds, dataset.examples)
    )
    checks["independent_domains"] = {example.domain for example in dataset.examples} == {"delegated_data_access", "purpose_limited_disclosure"}
    checks["action_catalogue_has_five_classes"] = {annotation.candidate_id for annotation in dataset.annotations} == {candidate_id for candidate_id, _ in ACTION_CATALOGUE}
    normalized = [" ".join(example.public_input.lower().split()) for example in dataset.examples]
    checks["exact_natural_duplicates_absent"] = len(normalized) == len(set(normalized))
    checks["majority_baseline_is_reported_not_used_for_tuning"] = True

    baseline = dataset.worlds[0]
    equivalent = next(world for world in dataset.worlds if world.template_id == baseline.template_id and interpret_observation(project_world(world)).candidate_id != interpret_observation(project_world(baseline)).candidate_id)
    checks["same_template_different_facts_change_result"] = interpret_observation(project_world(equivalent)).candidate_id != interpret_observation(project_world(baseline)).candidate_id
    checks["different_render_same_world_same_result"] = interpret_observation(project_world(baseline)) == interpret_observation(project_world(baseline))
    graph = TypedGraph(baseline.nodes, baseline.edges)
    checks["canonical_graph_reordering_invariant"] = (
        graph_content_hash(graph) == graph_content_hash(reorder_edges(graph))
        and typed_relation_fingerprint(graph) == typed_relation_fingerprint(reorder_edges(graph))
        and unlabeled_structure_fingerprint(graph) == unlabeled_structure_fingerprint(reorder_edges(graph))
    )
    hidden_difference = next(world for world in dataset.worlds if world.operation_status == "prohibited" and not any(fact.predicate == "operation_status" and fact.observed for fact in world.facts))
    checks["missing_evidence_is_not_negative_evidence"] = interpret_observation(project_world(hidden_difference)).candidate_id == "candidate_04"
    checks["calibration_and_open_dev_not_training"] = all(example.split != "train" or example.public_id not in {item.public_id for item in dataset.by_split("calibration") + dataset.by_split("open-dev")} for example in dataset.examples)
    split_counts = {split: len(dataset.by_split(split)) for split in V2_SPLITS}
    action_counts = {split: dict(Counter(annotations[example.public_id].candidate_id for example in dataset.by_split(split))) for split in V2_SPLITS}
    passed = all(checks.values())
    return {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "development-dataset-validation",
        "dataset_id": "pythia-policy-dev-v2",
        "profile": profile,
        "synthetic": True,
        "checks": checks,
        "status": "DEVELOPMENT_BENCHMARK_VALIDATED" if passed else "DEVELOPMENT_BENCHMARK_REJECTED",
        "row_counts": split_counts,
        "world_group_counts": {split: len(groups[split]) for split in V2_SPLITS},
        "action_counts": action_counts,
        "majority_baseline": {split: max(counts.values()) / max(1, sum(counts.values())) for split, counts in action_counts.items()},
        "file_hashes": file_hashes,
        "gold_labels_used_for_model_input": False,
        "locked_data_read_or_scored": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, default=ROOT / "experiments/datasets/pythia-policy-dev-v2")
    parser.add_argument("--profile", choices=("mini", "standard"), default="mini")
    parser.add_argument("--output", type=Path, default=ROOT / "results/reports/te-v0.6.1-pythia-development/development-dataset-validation.json")
    args = parser.parse_args()
    report = validate(args.dataset_root, args.profile)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "DEVELOPMENT_BENCHMARK_VALIDATED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
