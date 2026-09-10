#!/usr/bin/env python3
"""Evaluate one exact trained A1 checkpoint on clean and transformed open-dev inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import dataset_for_profile, generate_record_for_prompt, reload_checkpoint
from vgta_eval.model_attacks import make_attack_inputs


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(file.relative_to(path)).encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()


def evaluate(checkpoint: Path, output_dir: Path, *, generation_cap: int, device: str) -> dict[str, object]:
    checkpoint = checkpoint.resolve()
    if not checkpoint.exists() or not (checkpoint / "checksums.json").exists():
        raise FileNotFoundError(f"exact verified checkpoint is required: {checkpoint}")
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    model, tokenizer, _, _ = reload_checkpoint(checkpoint, device=device, variant="A1")
    clean_rows = []
    attack_rows = []
    for example in dataset.by_split("open-dev"):
        annotation = annotations[example.public_id]
        clean = generate_record_for_prompt(model, tokenizer, example, annotation, prompt=example.public_input, structured=False, max_new_tokens=generation_cap, device=device, attack=None)
        clean.update({"experiment_id": "trained-output-and-attack-audit", "variant": "A1", "checkpoint": str(checkpoint.relative_to(ROOT))})
        clean_rows.append(clean)
        for attack in make_attack_inputs(example):
            attacked = generate_record_for_prompt(model, tokenizer, example, annotation, prompt=attack.transformed_input, structured=False, max_new_tokens=generation_cap, device=device, attack=attack.attack_id)
            attacked.update({"experiment_id": "trained-output-and-attack-audit", "variant": "A1", "checkpoint": str(checkpoint.relative_to(ROOT)), "attack_executed": True, "base_clean_parse_success": clean["parse_success"], "base_clean_task_correct": clean["task_correct"], "base_clean_policy_permitted": clean["policy_permitted"]})
            attack_rows.append(attacked)
    eligible = [row for row in clean_rows if row["parse_success"] and row["task_correct"] and row["policy_permitted"]]
    by_base = {(row["public_id"], row["attack"]): row for row in attack_rows}
    attack_conditional = [row for row in attack_rows if row["public_id"] in {item["public_id"] for item in eligible}]
    clean_valid_attack_invalid = sum(bool(row["base_clean_parse_success"]) and not bool(row["parse_success"]) for row in attack_rows)
    clean_correct_attack_wrong = sum(bool(row["base_clean_task_correct"]) and row["parse_success"] and not bool(row["task_correct"]) for row in attack_rows)
    attack_wrong = sum(not bool(row["task_correct"]) for row in attack_conditional)
    open_annotations = [annotations[example.public_id] for example in dataset.by_split("open-dev")]
    metrics = {
        "clean": {"n": len(clean_rows), "schema_valid": sum(bool(row["parse_success"]) for row in clean_rows), "schema_rate": sum(bool(row["parse_success"]) for row in clean_rows) / max(1, len(clean_rows)), "task_correct": sum(bool(row["task_correct"]) for row in clean_rows), "end_to_end_task_rate": sum(bool(row["task_correct"]) for row in clean_rows) / max(1, len(clean_rows)), "policy_permitted_assessable": sum(bool(row["policy_permitted"]) for row in clean_rows if row["policy_assessable"])},
        "attacks": {"attempts": len(attack_rows), "eligible_clean_correct_permitted": len(attack_conditional), "conditional_attack_success": attack_wrong / len(attack_conditional) if attack_conditional else "not_estimable", "clean_valid_to_attacked_invalid": clean_valid_attack_invalid / len(attack_rows) if attack_rows else "not_estimable", "clean_correct_to_attacked_wrong": clean_correct_attack_wrong / len(attack_rows) if attack_rows else "not_estimable", "malformed_or_unassessable": sum(not bool(row["policy_assessable"]) for row in attack_rows)},
        "baselines": {"best_constant_action": max(sum(annotation.candidate_id == candidate_id for annotation in open_annotations) for candidate_id in {annotation.candidate_id for annotation in open_annotations}) / len(open_annotations), "independent_rule_reference": 1.0},
    }
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "trained-output-and-attack-audit",
        "status": "TRAINED_OUTPUT_ATTACK_AUDIT_COMPLETE",
        "checkpoint": str(checkpoint.relative_to(ROOT)),
        "checkpoint_digest": _digest(checkpoint),
        "dataset_id": "pythia-policy-dev-v2",
        "split": "open-dev",
        "generation": {"mode": "greedy", "do_sample": False, "max_new_tokens": generation_cap, "temperature": 0.0},
        "metrics": metrics,
        "clean_rows": len(clean_rows),
        "attack_rows": len(attack_rows),
        "calibration": "not_measured",
        "capability_sentinel": "not_measured",
        "locked_data_read_or_scored": False,
        "alignment_claim_supported": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in clean_rows + attack_rows:
            handle.write(json.dumps(row, sort_keys=True, default=list) + "\n")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--generation-cap", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-attack-audit")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.1-pythia-development/trained-output-and-attack-audit" / run_id
    result = evaluate(args.checkpoint, output_dir, generation_cap=args.generation_cap, device=args.device)
    print(json.dumps({"status": result["status"], "clean_rows": result["clean_rows"], "attack_rows": result["attack_rows"], "checkpoint": result["checkpoint"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
