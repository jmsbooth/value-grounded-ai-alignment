#!/usr/bin/env python3
"""Corrected v0.6.2 memorization and A1 development runs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import batch_for, build_model, dataset_for_profile, evaluate_nll, generate_record, optimizer_for, save_model_checkpoint, seed_everything
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_eval.observation_projection import project_world
from vgta_transformer.checkpointing import verify_checkpoint
from vgta_transformer.training import accumulated_response_step

PROTOCOL = "te-v0.6.2-pythia-correction"


def load_training_config(path: Path | None, mode: str) -> dict[str, object]:
    if path is None:
        return {"path": None, "sha256": None, "section": {}}
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    section_name = "memorization" if mode == "memorization" else "a1_development"
    section = data.get(section_name, {})
    if not isinstance(section, dict):
        raise ValueError(f"training config section {section_name!r} must be a mapping")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "section": section}


def _selected_memorization(dataset):
    annotations = dataset.annotation_map()
    selected = []
    seen = set()
    for example in dataset.by_split("train"):
        if annotations[example.public_id].candidate_id not in seen:
            selected.append(example)
            seen.add(annotations[example.public_id].candidate_id)
        if len(selected) == 8:
            return tuple(selected)
    return tuple(dataset.by_split("train")[:8])


def _record_predictions(model, tokenizer, examples, annotations, worlds, *, structured, seed, update, experiment_id, device, generation_cap):
    rows = []
    for example in examples:
        world = worlds[example.public_id.removeprefix("public-")]
        row = generate_record(model, tokenizer, example, annotations[example.public_id], structured=structured, max_new_tokens=generation_cap, device=device, observation=project_world(world))
        row.update({"protocol": PROTOCOL, "experiment_id": experiment_id, "variant": "A1", "seed": seed, "update": update})
        rows.append(row)
    return rows


def run_memorization(seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int, config: dict[str, object]) -> dict[str, object]:
    import torch
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    selected = _selected_memorization(dataset)
    worlds = {world.world_id: world for world in dataset.worlds}
    model, tokenizer, heads, _ = build_model(seed, device=device, variant="A1")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.0)
    evaluation_steps = [step for step in (0, 25, 50, 75, 100) if step <= max_updates]
    if max_updates not in evaluation_steps:
        evaluation_steps.append(max_updates)
    curve, predictions, checkpoints = [], [], []
    start = time.perf_counter()
    for update in range(max_updates + 1):
        if update in set(evaluation_steps):
            evaluation = evaluate_nll(model, tokenizer, selected, annotations, structured=False, device=device)
            evaluation.update({"seed": seed, "update": update, "elapsed_seconds": time.perf_counter() - start})
            curve.append(evaluation)
            checkpoint = output_dir / f"checkpoints/step-{update:04d}"
            save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": PROTOCOL, "experiment_id": "corrected-memorization", "seed": seed, "update_count": update, "response_contract": "te-v0.6.2-response-eos-v1", "config": config})
            checkpoints.append({"update": update, "path": str(checkpoint.relative_to(ROOT)), "verified": all(verify_checkpoint(checkpoint).values())})
            predictions.extend(_record_predictions(model, tokenizer, selected, annotations, worlds, structured=False, seed=seed, update=update, experiment_id="corrected-memorization", device=device, generation_cap=generation_cap))
        if update == max_updates:
            break
        batches = [batch_for(example, annotations[example.public_id], tokenizer, structured=False, device=device) for example in selected]
        metrics = accumulated_response_step(model, batches, optimizer, max_grad_norm=1.0)
        metrics.update({"seed": seed, "update": update + 1, "microbatches": len(batches), "effective_batch_size": len(batches)})
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "training-metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics, sort_keys=True) + "\n")
    by_update = {row["update"]: row for row in curve}
    criterion_curve = []
    for update in sorted(by_update):
        rows = [row for row in predictions if row["update"] == update]
        criterion_curve.append({"update": update, "strict_schema": sum(bool(row["parse_success"]) for row in rows), "accepted_action": sum(row.get("evaluator", {}).get("utility") is True for row in rows), "eos_rate": sum(row.get("stop_reason") == "eos_or_model_stop" for row in rows) / max(1, len(rows)), "nll": by_update[update]["response_nll"], "n": len(rows)})
    meets = any(previous["strict_schema"] >= 7 and current["strict_schema"] >= 7 and previous["accepted_action"] >= 7 and current["accepted_action"] >= 7 and current["nll"] <= criterion_curve[0]["nll"] * 0.7 and previous["eos_rate"] >= 0.875 and current["eos_rate"] >= 0.875 for previous, current in zip(criterion_curve, criterion_curve[1:])) if criterion_curve else False
    result = {"protocol": PROTOCOL, "experiment_id": "corrected-memorization", "attempt_id": f"seed-{seed}", "seed": seed, "status": "CORRECTED_MEMORIZATION_CRITERION_MET" if meets else "CORRECTED_MEMORIZATION_CRITERION_NOT_MET", "max_updates_requested": max_updates, "updates_completed": max_updates, "selected_public_ids": [example.public_id for example in selected], "evaluation_curve": curve, "criterion_curve": criterion_curve, "checkpoints": checkpoints, "generated_output_count": len(predictions), "config": config, "synthetic_data": True, "locked_data_read_or_scored": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "predictions.jsonl").write_text("".join(json.dumps(row, sort_keys=True, default=list) + "\n" for row in predictions), encoding="utf-8")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    del model, tokenizer, heads, optimizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    return result


def run_a1(seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int, config: dict[str, object]) -> dict[str, object]:
    import torch
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    train, validation, open_dev = dataset.by_split("train"), dataset.by_split("validation"), dataset.by_split("open-dev")
    worlds = {world.world_id: world for world in dataset.worlds}
    model, tokenizer, heads, _ = build_model(seed, device=device, variant="A1")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
    schedule = min(max_updates, 3 * ((len(train) + 7) // 8))
    curve, checkpoints = [], []
    start = time.perf_counter()
    for update in range(schedule + 1):
        if update == 0 or update % 8 == 0 or update == schedule:
            validation_nll = evaluate_nll(model, tokenizer, validation, annotations, structured=False, device=device)
            curve.append({"seed": seed, "update": update, "validation": validation_nll, "elapsed_seconds": time.perf_counter() - start})
            checkpoint = output_dir / f"checkpoints/step-{update:04d}"
            save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": PROTOCOL, "experiment_id": "corrected-a1-development", "seed": seed, "update_count": update, "response_contract": "te-v0.6.2-response-eos-v1", "config": config})
            checkpoints.append({"update": update, "path": str(checkpoint.relative_to(ROOT)), "validation_response_nll": validation_nll["response_nll"], "verified": all(verify_checkpoint(checkpoint).values())})
        if update == schedule:
            break
        indices = [((update * 8) + offset) % len(train) for offset in range(8)]
        batches = [batch_for(train[index], annotations[train[index].public_id], tokenizer, structured=False, device=device) for index in indices]
        metrics = accumulated_response_step(model, batches, optimizer, max_grad_norm=1.0)
        metrics.update({"seed": seed, "update": update + 1, "microbatches": 8, "effective_batch_size": 8, "train_indices": indices})
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "training-metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics, sort_keys=True) + "\n")
    selected = min(checkpoints, key=lambda row: (float(row["validation_response_nll"]), int(row["update"])))
    checkpoint = ROOT / selected["path"]
    # Keep selection and final evaluation tied to the exact checkpoint receipt.
    from experiment_utils import reload_checkpoint
    del model, tokenizer, heads, optimizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    selected_model, selected_tokenizer, _, _ = reload_checkpoint(checkpoint, device=device, variant="A1")
    predictions = _record_predictions(selected_model, selected_tokenizer, open_dev, annotations, worlds, structured=False, seed=seed, update=selected["update"], experiment_id="corrected-a1-development", device=device, generation_cap=generation_cap)
    result = {"protocol": PROTOCOL, "experiment_id": "corrected-a1-development", "attempt_id": f"seed-{seed}", "seed": seed, "status": "CORRECTED_A1_DEVELOPMENT_COMPLETE", "updates_completed": schedule, "passes_completed": schedule * 8 / len(train), "selection_rule": "lowest validation response NLL then earlier update", "curve": curve, "checkpoints": checkpoints, "selected_checkpoint": selected, "open_dev": {"n": len(predictions), "strict_schema_valid": sum(bool(row["parse_success"]) for row in predictions), "evaluator_assessable": sum(row.get("evaluator") is not None and row.get("parse_success") is True for row in predictions), "reference_decision_match": sum(row.get("evaluator", {}).get("reference_decision_match") is True for row in predictions)}, "config": config, "synthetic_data": True, "locked_data_read_or_scored": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "predictions.jsonl").write_text("".join(json.dumps(row, sort_keys=True, default=list) + "\n" for row in predictions), encoding="utf-8")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    del selected_model, selected_tokenizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("memorization", "a1"), required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--max-updates", type=int)
    parser.add_argument("--generation-cap", type=int)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    config = load_training_config(args.config, args.mode)
    section = config["section"]
    default_updates = int(section.get("max_updates", 100 if args.mode == "memorization" else 24))
    max_updates = args.max_updates if args.max_updates is not None else default_updates
    generation_cap = args.generation_cap if args.generation_cap is not None else 256
    seeds = args.seeds if args.seeds is not None else list(section.get("seeds", [11, 23]))
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-" + args.mode)
    experiment_id = "corrected-memorization" if args.mode == "memorization" else "corrected-a1-development"
    root = args.output_root or ROOT / f"results/raw/{PROTOCOL}/{experiment_id}" / run_id
    attempts = []
    for seed in seeds:
        output_dir = root / f"seed-{seed}"
        attempts.append(run_memorization(seed, output_dir, max_updates=max_updates, device=args.device, generation_cap=generation_cap, config=config) if args.mode == "memorization" else run_a1(seed, output_dir, max_updates=max_updates, device=args.device, generation_cap=generation_cap, config=config))
    root.mkdir(parents=True, exist_ok=True)
    summary = {"protocol": PROTOCOL, "experiment_id": experiment_id, "run_id": run_id, "status": "COMPLETE", "config": config, "generation_cap": generation_cap, "attempts": attempts, "locked_data_read_or_scored": False}
    output = root / "run-summary.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="model_prediction", protocol=PROTOCOL, status=summary["status"], experiment_id=experiment_id, run_id=run_id, result_sha256=sha256_file(output), attempt_count=len(attempts), locked_data_read_or_scored=False)
    write_receipt(root / "evidence-receipt.json", receipt)
    print(json.dumps({"status": summary["status"], "run_id": run_id, "attempts": len(attempts), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
