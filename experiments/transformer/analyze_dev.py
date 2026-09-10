#!/usr/bin/env python3
"""Create a reporting-only aggregate for exact v0.6.1 development runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memorization", type=Path, required=True)
    parser.add_argument("--a1", type=Path, required=True)
    parser.add_argument("--variants", type=Path, required=True)
    parser.add_argument("--resource", type=Path, required=True)
    parser.add_argument("--attack", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/analyses/te-v0.6.1-pythia-development/development-summary/analysis-r001/analysis.json"))
    args = parser.parse_args()
    inputs = {"memorization": str(args.memorization), "a1": str(args.a1), "variants": str(args.variants), "resource": str(args.resource), "attack": str(args.attack) if args.attack else "not_measured"}
    memorization = load(args.memorization)
    a1 = load(args.a1)
    variants = load(args.variants)
    resource = load(args.resource)
    attack = load(args.attack) if args.attack else {"status": "not_measured"}
    aggregate = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "development-summary",
        "analysis_id": "development-summary__analysis-r001",
        "analysis_revision": 1,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "complete",
        "inputs": inputs,
        "input_digest": hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest(),
        "memorization_statuses": [attempt.get("status") for attempt in memorization.get("attempts", [])],
        "a1_attempts": [{"seed": attempt.get("seed"), "updates": attempt.get("updates_completed"), "selected_checkpoint": attempt.get("selected_checkpoint"), "open_dev": attempt.get("open_dev")} for attempt in a1.get("attempts", [])],
        "variant_smoke": {"status": variants.get("status"), "attempt_count": variants.get("attempt_count"), "expected_attempt_count": variants.get("expected_attempt_count")},
        "resource": {"status": resource.get("status"), "wall_seconds": resource.get("wall_seconds"), "peak_rss_gib": resource.get("peak_rss_gib"), "checkpoint": resource.get("checkpoint")},
        "attack": {"status": attack.get("status"), "metrics": attack.get("metrics")},
        "interpretation": "Exploratory development aggregate only. Repeated checkpoints, seeds, attacks, and paraphrases are not additional independent worlds; no VGA or alignment claim is inferred.",
        "training_rerun": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(aggregate, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    print(json.dumps({"status": aggregate["status"], "output": str(args.output), "input_digest": aggregate["input_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
