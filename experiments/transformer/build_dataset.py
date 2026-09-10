#!/usr/bin/env python3
"""Materialize the policy-grounded development dataset.

The writer creates separately joinable public inputs and private annotations.
All paths in manifests are repository-relative; no local machine path is
serialized into the artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import canonical_digest, make_receipt, write_receipt
from vgta_eval.input_contracts import assert_annotation_is_private, validate_public_example
from vgta_eval.semantic_worlds import (
    SEMANTIC_DATASET_VERSION,
    SEMANTIC_SPLITS,
    V2_DATASET_VERSION,
    V2_SPLITS,
    annotation_to_dict,
    generate_semantic_dataset,
    generate_v2_dataset,
    public_example_to_dict,
    semantic_manifest,
    world_to_dict,
)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


def materialize(output_root: Path, *, group_counts: dict[str, int] | None = None, version: str = "v1", profile: str = "mini") -> dict[str, Any]:
    if version == "v2":
        dataset = generate_v2_dataset(profile=profile)
        splits = V2_SPLITS
        dataset_version = V2_DATASET_VERSION
        protocol = "te-v0.6.1-pythia-development"
    else:
        dataset = generate_semantic_dataset(group_counts=group_counts)
        splits = SEMANTIC_SPLITS
        dataset_version = SEMANTIC_DATASET_VERSION
        protocol = "te-v0.6.0-pythia"
    annotations = dataset.annotation_map()
    manifest = semantic_manifest(dataset, dataset_version=dataset_version, generator_version=("semantic-worlds-v2" if version == "v2" else "semantic-worlds-v1"), splits=splits)
    manifest["artifact_version"] = "public-private-dataset-v1"
    manifest["root"] = str(output_root.relative_to(ROOT)) if output_root.is_relative_to(ROOT) else str(output_root)
    file_hashes: dict[str, str] = {}
    for split in splits:
        examples = [example for example in dataset.examples if example.split == split]
        public_rows: list[dict[str, Any]] = []
        private_rows: list[dict[str, Any]] = []
        world_rows: list[dict[str, Any]] = []
        parity_rows: list[dict[str, Any]] = []
        for example in examples:
            validate_public_example(example)
            annotation = annotations[example.public_id]
            assert_annotation_is_private(annotation)
            public_rows.append({
                "public_id": example.public_id,
                "world_group_id": example.world_group_id,
                "split": example.split,
                "domain": example.domain,
                "public_input": example.public_input,
                "structured_input": example.structured_input,
                "action_catalogue": [{"id": cid, "description": description} for cid, description in example.action_catalogue],
                "input_digest": example.input_digest,
            })
            private_rows.append(annotation_to_dict(annotation))
            world = next(world for world in dataset.worlds if world.world_group_id == example.world_group_id)
            world_rows.append(world_to_dict(world))
            parity_rows.append({
                "public_id": example.public_id,
                "world_group_id": example.world_group_id,
                "natural_digest": hashlib.sha256(example.public_input.encode()).hexdigest(),
                "structured_digest": hashlib.sha256(example.structured_input.encode()).hexdigest(),
                "natural_bytes": len(example.public_input.encode()),
                "structured_bytes": len(example.structured_input.encode()),
                "shared_domain": example.domain,
                "shared_action_catalogue_digest": canonical_digest(example.action_catalogue),
            })
        file_hashes[f"public/{split}.jsonl"] = _write_jsonl(output_root / "public" / f"{split}.jsonl", public_rows)
        file_hashes[f"private/{split}.jsonl"] = _write_jsonl(output_root / "private" / f"{split}.jsonl", private_rows)
        file_hashes[f"worlds/{split}.jsonl"] = _write_jsonl(output_root / "worlds" / f"{split}.jsonl", world_rows)
        file_hashes[f"information-parity/{split}.jsonl"] = _write_jsonl(output_root / "information-parity" / f"{split}.jsonl", parity_rows)
    manifest["file_hashes"] = file_hashes
    manifest_path = output_root / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = make_receipt(
        producer_kind="known_fixture",
        protocol=protocol,
        status="SEMANTIC_DATASET_MATERIALIZED",
        dataset_version=dataset_version,
        synthetic=True,
        manifest_digest=canonical_digest(manifest),
    )
    write_receipt(output_root / "materialization-receipt.json", receipt)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--version", choices=("v1", "v2"), default="v1")
    parser.add_argument("--profile", choices=("mini", "standard"), default="mini")
    parser.add_argument("--small", action="store_true", help="write a fixture-sized dataset for fast tests")
    args = parser.parse_args()
    default_root = ROOT / ("experiments/datasets/pythia-policy-dev-v2" if args.version == "v2" else "experiments/datasets/pythia-policy-dev-v1")
    output_root = args.output_root or default_root
    counts = ({"train": 8, "validation": 4, "calibration": 4, "open-dev": 4, "locked-engineering-eval": 4} if args.small else None)
    manifest = materialize(output_root, group_counts=counts, version=args.version, profile=args.profile)
    print(json.dumps({"status": "SEMANTIC_DATASET_MATERIALIZED", "output_root": str(output_root), "row_counts": manifest["row_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
