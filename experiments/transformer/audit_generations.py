#!/usr/bin/env python3
"""Classify the five parent-phase generations without rewriting them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_transformer.response_parser import strict_parse


def audit(source: Path, output: Path) -> dict[str, object]:
    rows = []
    if source.exists():
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                original = json.loads(line)
                parsed = strict_parse(str(original.get("raw_model_output", "")))
                rows.append({
                    "public_id": original.get("public_id"),
                    "world_group_id": original.get("world_group_id"),
                    "condition": "clean" if not original.get("attack") else "attack",
                    "attack": original.get("attack"),
                    "model_state": "pretrained-base-natural",
                    "raw_output_present": bool(original.get("raw_model_output")),
                    "prompt_and_token_ids_present": False,
                    "prompt_hash": None,
                    "generated_token_ids": None,
                    "generation_cap": None,
                    "primary_error": parsed.primary_error,
                    "parser_detail": parsed.detail,
                    "historical_metadata_complete": False,
                })
    status = "HISTORICAL_GENERATIONS_AUDITED" if rows else "HISTORICAL_RAW_OUTPUTS_UNAVAILABLE"
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "raw-output-audit",
        "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
        "status": status,
        "historical_row_count": len(rows),
        "expected_historical_generation_count": 5,
        "rows": rows,
        "limitations": [
            "Parent raw strings are present locally, but prompt token IDs, generated token IDs, and effective generation settings were not retained in the parent artifact.",
            "The new v0.6.1 path records tensor-width extraction and generation metadata for every new output.",
        ] if rows else ["The five parent raw strings are not present locally; no historical output text was invented."],
        "historical_results_unchanged": True,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT / "results/raw/te-v0.6.0-pythia/development-evaluation/predictions.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "results/reports/te-v0.6.1-pythia-development/raw-output-audit.json")
    args = parser.parse_args()
    result = audit(args.source, args.output)
    print(json.dumps({"status": result["status"], "historical_row_count": result["historical_row_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
