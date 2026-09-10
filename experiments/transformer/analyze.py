#!/usr/bin/env python3
"""Analyze prediction receipts only; this command never trains or regenerates data."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import canonical_digest, make_receipt, write_receipt
from vgta_eval.paired_analysis import clustered_bootstrap_delta, raw_denominators


def _rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError("prediction rows must be JSON objects")
                rows.append(value)
    return rows


def analyze(*, input_path: Path, output_dir: Path) -> dict[str, object]:
    rows = _rows(input_path)
    if not rows:
        result = {
            "protocol": "te-v0.6.0-pythia",
            "status": "ANALYSIS_BLOCKED_NO_MODEL_PREDICTIONS",
            "unit_of_inference": "world_group_id",
            "training_performed": False,
            "data_regenerated": False,
            "raw_denominators": {},
            "contrasts": [],
        }
    else:
        variants = sorted({str(row.get("variant", "")) for row in rows})
        contrasts = []
        for left, right in (("A1", "B"), ("B", "C1"), ("C1", "C2")):
            if left in variants and right in variants:
                contrasts.append(clustered_bootstrap_delta(rows, left_variant=left, right_variant=right, score_key="correct"))
        result = {
            "protocol": "te-v0.6.0-pythia",
            "status": "ANALYSIS_COMPLETE",
            "unit_of_inference": "world_group_id",
            "training_performed": False,
            "data_regenerated": False,
            "input_digest": canonical_digest(rows),
            "raw_denominators": raw_denominators(rows),
            "contrasts": contrasts,
        }
    result["created_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(output_dir / "evidence-receipt.json", make_receipt(producer_kind="analysis", protocol="te-v0.6.0-pythia", status=str(result["status"]), input_digest=result.get("input_digest"), unit_of_inference="world_group_id"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "results/raw/te-v0.6.0-pythia/predictions.jsonl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/analysis")
    args = parser.parse_args()
    result = analyze(input_path=args.input, output_dir=args.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

