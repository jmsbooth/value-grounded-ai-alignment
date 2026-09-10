#!/usr/bin/env python3
"""Create an explicit, unfrozen Pythia cohort plan."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import canonical_digest, make_receipt, write_receipt
from vgta_eval.semantic_worlds import SEMANTIC_DATASET_VERSION, build_worlds, semantic_manifest, generate_semantic_dataset
from vgta_transformer.model_loader import MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA

VARIANTS = ("A1", "B", "C1", "C2", "B-TEXT-A", "C1-TEXT-N", "C1-SHAM", "C2-SHAM")
SEEDS = (11, 23, 37, 53, 71)


def make_plan(*, development: bool = False) -> dict[str, object]:
    dataset = generate_semantic_dataset(group_counts={"train": 8, "validation": 4, "calibration": 4, "open-dev": 4, "locked-engineering-eval": 4})
    seeds = SEEDS[:2] if development else SEEDS
    runs = [{"run_id": f"{variant.lower()}-seed-{seed}", "variant": variant, "seed": seed, "mode": "development" if development else "locked-pending-freeze"} for variant in VARIANTS for seed in seeds]
    # This is a transparent estimate, not a measured benchmark. Actual costs
    # are recorded by the training producer before any locked promotion.
    prompt_bytes = [len(example.public_input.encode()) for example in dataset.examples if example.split in {"train", "locked-engineering-eval"}]
    return {
        "plan_version": "cohort-plan-v1",
        "protocol": "te-v0.6.0-pythia",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "DEVELOPMENT_PLAN" if development else "PLANNED_NOT_FROZEN",
        "approval_required": not development,
        "synthetic_dataset": True,
        "dataset_version": SEMANTIC_DATASET_VERSION,
        "dataset_manifest_digest": canonical_digest(semantic_manifest(dataset)),
        "model": {"model_id": MODEL_ID, "requested_revision": REQUESTED_REVISION, "resolved_revision_sha": RESOLVED_REVISION_SHA},
        "variants": list(VARIANTS),
        "seeds": list(seeds),
        "run_count": len(runs),
        "runs": runs,
        "estimated_cost": {
            "basis": "character-count proxy; not measured tokenization or wall time",
            "prompt_bytes": int(sum(prompt_bytes)),
            "training_steps_per_run": 8 if development else 128,
            "locked_cost_measured": False,
        },
        "resource_gate": "measured resource plan and owner-approved committed protocol required before locked execution",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/plans/te-v0.6.0-pythia")
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    plan = make_plan(development=args.development)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plan_path = args.output_dir / ("development-plan.json" if args.development else "cohort-plan.json")
    plan["plan_digest"] = canonical_digest(plan)
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(args.output_dir / ("development-plan-receipt.json" if args.development else "cohort-plan-receipt.json"), make_receipt(
        producer_kind="known_fixture", protocol="te-v0.6.0-pythia", status=str(plan["status"]), plan_digest=plan["plan_digest"], run_count=plan["run_count"],
    ))
    print(json.dumps({"status": plan["status"], "path": str(plan_path), "run_count": plan["run_count"], "plan_digest": plan["plan_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

