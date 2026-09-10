#!/usr/bin/env python3
"""Development-only clean/attack evaluation using the actual Pythia model."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt
from phase_guards import require_semantic_gate
from vgta_eval.model_attacks import execute_model_attacks
from vgta_eval.semantic_worlds import generate_semantic_dataset
from vgta_transformer.decoding import generate_greedy, parse_response
from vgta_transformer.model_loader import ModelDependencyError, load_base_model, load_tokenizer, model_load_info


def run(*, output_dir: Path, limit: int, device: str) -> dict[str, object]:
    try:
        require_semantic_gate(ROOT)
        dataset = generate_semantic_dataset(group_counts={"train": 2, "validation": 1, "calibration": 1, "open-dev": max(1, limit), "locked-engineering-eval": 1})
        examples = dataset.by_split("open-dev")[:limit]
        annotation_map = dataset.annotation_map()
        tokenizer = load_tokenizer(local_files_only=True)
        model = load_base_model(local_files_only=True, device=device)

        def predict(text: str) -> str:
            return generate_greedy(model, tokenizer, text, max_new_tokens=48, device=device)

        rows: list[dict[str, object]] = []
        clean_outputs: dict[str, dict[str, object]] = {}
        for example in examples:
            raw = predict(example.public_input)
            parsed = parse_response(raw)
            annotation = annotation_map[example.public_id]
            clean_outputs[example.public_id] = {"raw": raw, "parsed": parsed, "expected": annotation.candidate_id}
            rows.append({
                "public_id": example.public_id,
                "world_group_id": example.world_group_id,
                "variant": "pretrained-base-natural",
                "seed": None,
                "split": example.split,
                "attack": None,
                "raw_model_output": raw,
                "parsed": parsed,
                "parse_success": parsed is not None,
                "correct": bool(parsed and parsed.get("candidate_id") == annotation.candidate_id),
                "expected_candidate_id": annotation.candidate_id,
            })
        attack_results = execute_model_attacks(examples, predict)
        for attack in attack_results:
            annotation = annotation_map[attack.base_public_id]
            parsed = parse_response(attack.raw_model_output)
            rows.append({
                "public_id": attack.base_public_id,
                "world_group_id": next(example.world_group_id for example in examples if example.public_id == attack.base_public_id),
                "variant": "pretrained-base-natural",
                "seed": None,
                "split": "open-dev",
                "attack": attack.attack_id,
                "raw_model_output": attack.raw_model_output,
                "parsed": parsed,
                "parse_success": parsed is not None,
                "correct": bool(parsed and parsed.get("candidate_id") == annotation.candidate_id),
                "attack_safe": bool(parsed and parsed.get("candidate_id") == annotation.candidate_id),
                "expected_candidate_id": annotation.candidate_id,
                "attack_executed": attack.executed,
            })
        status = "MODEL_DEVELOPMENT_EVALUATION_COMPLETE"
        result: dict[str, object] = {
            "status": status,
            "protocol": "te-v0.6.0-pythia",
            "synthetic_dataset": True,
            "real_pretrained_model": True,
            "model": model_load_info(model, device=device, local_files_only=True).__dict__,
            "examples": len(examples),
            "rows": len(rows),
            "clean_parse_rate": sum(bool(row["parse_success"]) for row in rows[:len(examples)]) / max(1, len(examples)),
            "attack_rows": len(attack_results),
            "attack_parse_rate": sum(bool(row["parse_success"]) for row in rows[len(examples):]) / max(1, len(attack_results)),
            "attack_safe_rate": sum(bool(row.get("attack_safe")) for row in rows[len(examples):]) / max(1, len(attack_results)),
            "evaluation_boundary": "development-only pretrained inference; not a locked comparison or alignment result",
        }
    except (ModelDependencyError, OSError, RuntimeError, ValueError) as exc:
        rows = []
        result = {"status": "MODEL_DEVELOPMENT_EVALUATION_BLOCKED", "protocol": "te-v0.6.0-pythia", "real_pretrained_model": False, "reason_type": type(exc).__name__, "reason": str(exc), "synthetic_dataset": True}
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    (output_dir / "evaluation.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    write_receipt(output_dir / "evidence-receipt.json", make_receipt(producer_kind="model_prediction", protocol="te-v0.6.0-pythia", status=str(result["status"]), real_pretrained_model=bool(result.get("real_pretrained_model")), row_count=len(rows)))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/raw/te-v0.6.0-pythia/development-evaluation")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, limit=max(1, args.limit), device=args.device)
    print(json.dumps(result, sort_keys=True, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
