#!/usr/bin/env python3
"""Evaluate one corrected checkpoint with independent clean/attack scoring."""

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

from experiment_utils import dataset_for_profile, generate_record, generate_record_for_prompt, reload_checkpoint
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_eval.model_attacks import make_attack_inputs
from vgta_eval.observation_projection import project_world
from vgta_transformer.variant_plan import load_variant_specs

PLAN = ROOT / "experiments/protocols/te-v0.6.2-pythia-correction/variants.yaml"
PROTOCOL = "te-v0.6.2-pythia-correction"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            value.update(str(item.relative_to(path)).encode())
            value.update(item.read_bytes())
    return value.hexdigest()


def run(checkpoint: Path, output_dir: Path, *, device: str, generation_cap: int) -> dict[str, object]:
    checkpoint = checkpoint.resolve()
    metadata = json.loads((checkpoint / "metadata.json").read_text(encoding="utf-8"))
    variant = str(metadata.get("variant", "A1"))
    specs = load_variant_specs(PLAN)
    if variant not in specs:
        raise ValueError(f"checkpoint variant {variant} is absent from corrected plan")
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    worlds = {world.world_id: world for world in dataset.worlds}
    model, tokenizer, _, _ = reload_checkpoint(checkpoint, device=device, variant=variant)
    clean_rows, attack_rows = [], []
    for example in dataset.by_split("open-dev"):
        annotation = annotations[example.public_id]
        observation = project_world(worlds[example.public_id.removeprefix("public-")])
        clean = generate_record(model, tokenizer, example, annotation, structured=specs[variant].structured, max_new_tokens=generation_cap, device=device, observation=observation)
        clean.update({"protocol": PROTOCOL, "experiment_id": "corrected-clean-attack-evaluation", "variant": variant, "checkpoint": str(checkpoint.relative_to(ROOT))})
        clean_rows.append(clean)
        for attack in make_attack_inputs(example):
            attacked = generate_record_for_prompt(model, tokenizer, example, annotation, prompt=attack.transformed_input, structured=False, max_new_tokens=generation_cap, device=device, attack=attack.attack_id, observation=observation)
            attacked.update({"protocol": PROTOCOL, "experiment_id": "corrected-clean-attack-evaluation", "variant": variant, "checkpoint": str(checkpoint.relative_to(ROOT)), "attack_executed": True, "base_clean_parse_success": clean["parse_success"], "base_clean_reference_match": clean.get("evaluator", {}).get("reference_decision_match")})
            attack_rows.append(attacked)
    eligible = [row for row in clean_rows if row.get("parse_success") and row.get("evaluator", {}).get("reference_decision_match")]
    eligible_ids = {row["public_id"] for row in eligible}
    conditional_attacks = [row for row in attack_rows if row["public_id"] in eligible_ids]
    metrics = {
        "clean": {"n": len(clean_rows), "strict_schema_valid": sum(bool(row["parse_success"]) for row in clean_rows), "evaluator_assessable": sum(row.get("evaluator") is not None and row.get("parse_success") is True for row in clean_rows), "exact_reference_decision": sum(row.get("evaluator", {}).get("reference_decision_match") is True for row in clean_rows), "accepted_action": sum(row.get("evaluator", {}).get("permission") is True for row in clean_rows), "useful_action": sum(row.get("evaluator", {}).get("utility") is True for row in clean_rows)},
        "attacks": {"attempts": len(attack_rows), "eligible_clean_exact_reference": len(conditional_attacks), "conditional_reference_disruption": sum(1 for row in conditional_attacks if row.get("evaluator", {}).get("reference_decision_match") is not True) / len(conditional_attacks) if conditional_attacks else "not_estimable", "clean_valid_to_attacked_invalid": sum(1 for row in attack_rows if bool(row.get("base_clean_parse_success")) and not bool(row.get("parse_success"))) / len(attack_rows) if attack_rows else "not_estimable", "clean_exact_to_attacked_wrong": sum(1 for row in attack_rows if bool(row.get("base_clean_reference_match")) and row.get("evaluator", {}).get("reference_decision_match") is not True) / len(attack_rows) if attack_rows else "not_estimable", "unknown_or_unassessable": sum(1 for row in attack_rows if row.get("evaluator") is None or not row.get("parse_success"))},
        "reference": {"scoring_authority": "candidate-evaluator-v1", "literal_constant_score_used": False, "candidate_catalogue": [candidate_id for candidate_id, _ in example.action_catalogue] if clean_rows else []},
    }
    result = {"protocol": PROTOCOL, "experiment_id": "corrected-clean-attack-evaluation", "status": "CORRECTED_CLEAN_ATTACK_EVALUATION_COMPLETE", "checkpoint": str(checkpoint.relative_to(ROOT)), "checkpoint_digest": digest(checkpoint), "variant": variant, "generation": {"mode": "greedy", "do_sample": False, "max_new_tokens": generation_cap, "explicit_eos": True, "constrained_decoding": False}, "metrics": metrics, "clean_rows": len(clean_rows), "attack_rows": len(attack_rows), "calibration": "not_measured", "capability_sentinel": "not_measured", "locked_data_read_or_scored": False, "alignment_claim_supported": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    (output_dir / "predictions.jsonl").write_text("".join(json.dumps(row, sort_keys=True, default=list) + "\n" for row in clean_rows + attack_rows), encoding="utf-8")
    receipt = make_receipt(producer_kind="model_prediction", protocol=PROTOCOL, status=result["status"], experiment_id=result["experiment_id"], checkpoint_digest=result["checkpoint_digest"], result_sha256=sha256_file(output), clean_rows=len(clean_rows), attack_rows=len(attack_rows), locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--generation-cap", type=int, default=256)
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-corrected-eval")
    result = run(args.checkpoint, args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/clean-attack-evaluation" / run_id, device=args.device, generation_cap=args.generation_cap)
    print(json.dumps({"status": result["status"], "run_id": run_id, "clean_rows": result["clean_rows"], "attack_rows": result["attack_rows"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
