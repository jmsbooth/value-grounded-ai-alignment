#!/usr/bin/env python3
"""Aggregate phase-state gate without importing historical MLP results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt


def evaluate() -> dict[str, object]:
    semantic_path = ROOT / "results/reports/te-v0.6.0-pythia/semantic-validity/semantic-audit.json"
    smoke_path = ROOT / "results/reports/te-v0.6.0-pythia/model-smoke/model-smoke.json"
    diagnostic_path = ROOT / "results/reports/te-v0.6.0-pythia/training-diagnostics/training-diagnostic.json"
    freeze_path = ROOT / "results/plans/te-v0.6.0-pythia/freeze-result.json"
    def status(path: Path) -> str:
        if not path.exists():
            return "MISSING"
        return str(json.loads(path.read_text(encoding="utf-8")).get("status", "UNKNOWN"))
    semantic = status(semantic_path)
    smoke = status(smoke_path)
    diagnostic = status(diagnostic_path)
    freeze = status(freeze_path)
    if semantic == "SEMANTIC_DATASET_VALIDATED" and smoke == "PYTHIA_INTEGRATION_VALIDATED" and diagnostic == "PYTHIA_TRAINING_DIAGNOSTIC_PASSED" and freeze == "COHORT_FROZEN":
        state = "LOCKED_PYTHIA_COMPARISON_COMPLETE"
    elif semantic == "SEMANTIC_DATASET_VALIDATED":
        state = "SEMANTIC_DATASET_VALIDATED"
    else:
        state = "SEMANTIC_DATASET_REJECTED"
    return {"protocol": "te-v0.6.0-pythia", "state": state, "inputs": {"semantic": semantic, "model_smoke": smoke, "training_diagnostic": diagnostic, "freeze": freeze}, "locked_comparison_claim": state == "LOCKED_PYTHIA_COMPARISON_COMPLETE"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/gate")
    args = parser.parse_args()
    result = evaluate()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "gate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(args.output_dir / "evidence-receipt.json", make_receipt(producer_kind="gate", protocol="te-v0.6.0-pythia", status=str(result["state"]), inputs=result["inputs"]))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

