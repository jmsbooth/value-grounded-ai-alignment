#!/usr/bin/env python3
"""Run the held-out A1 task-SFT development baseline on v2 mini."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import batch_for, build_model, dataset_for_profile, evaluate_nll, examples_for, generate_record, optimizer_for, reload_checkpoint, save_model_checkpoint, seed_everything
from vgta_transformer.model_loader import model_load_info
from vgta_transformer.training import accumulated_response_step


def run_seed(seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int) -> dict[str, object]:
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    train = dataset.by_split("train")
    validation = dataset.by_split("validation")
    model, tokenizer, heads, active = build_model(seed, device=device, variant="A1")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
    warmup = max(1, int(max_updates * 0.05))
    scheduler = __import__("torch").optim.lr_scheduler.LambdaLR(optimizer, lambda step: min((step + 1) / warmup, 1.0) * max(0.0, (max_updates - step) / max(1, max_updates - warmup)))
    curve = []
    checkpoints = []
    update = 0
    start = time.perf_counter()
    # Three complete passes is the prospective maximum; a smaller resource-selected
    # schedule is passed explicitly by the phase runner.
    pass_limit = min(max_updates, 3 * ((len(train) + 7) // 8))
    for update in range(pass_limit + 1):
        if update == 0 or update % 8 == 0 or update == pass_limit:
            train_eval = evaluate_nll(model, tokenizer, train, annotations, structured=False, device=device)
            val_eval = evaluate_nll(model, tokenizer, validation, annotations, structured=False, device=device)
            row = {"seed": seed, "update": update, "train": train_eval, "validation": val_eval, "learning_rate": optimizer.param_groups[0]["lr"], "elapsed_seconds": time.perf_counter() - start}
            curve.append(row)
            checkpoint = output_dir / f"checkpoints/step-{update:04d}"
            save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": "te-v0.6.1-pythia-development", "experiment_id": "a1-development-training", "seed": seed, "update_count": update, "profile": "mini", "selection_rule": "lowest_mean_validation_response_nll_then_earlier_update"})
            checkpoints.append({"update": update, "path": str(checkpoint.relative_to(ROOT)), "validation_response_nll": val_eval["response_nll"]})
        if update == pass_limit:
            break
        indices = [((update * 8) + offset) % len(train) for offset in range(8)]
        batches = [batch_for(train[index], annotations[train[index].public_id], tokenizer, structured=False, device=device) for index in indices]
        metrics = accumulated_response_step(model, batches, optimizer, max_grad_norm=1.0)
        scheduler.step()
        metrics.update({"seed": seed, "update": update + 1, "microbatches": len(batches), "examples": len(set(indices)), "learning_rate": optimizer.param_groups[0]["lr"]})
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "training-metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics, sort_keys=True) + "\n")
    selected = min(checkpoints, key=lambda row: (float(row["validation_response_nll"]), int(row["update"])))
    model_info = model_load_info(model, device=device, local_files_only=True).__dict__
    del model, tokenizer, heads, optimizer, scheduler
    gc.collect()
    selected_model, selected_tokenizer, _, _ = reload_checkpoint(ROOT / selected["path"], device=device, variant="A1")
    predictions = []
    for example in dataset.by_split("open-dev"):
        row = generate_record(selected_model, selected_tokenizer, example, annotations[example.public_id], structured=False, max_new_tokens=generation_cap, device=device)
        row.update({"experiment_id": "a1-development-training", "seed": seed, "variant": "A1", "checkpoint_update": selected["update"]})
        predictions.append(row)
    schema_valid = sum(bool(row["parse_success"]) for row in predictions)
    correct = sum(bool(row["task_correct"]) for row in predictions)
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "a1-development-training",
        "attempt_id": f"seed-{seed}",
        "seed": seed,
        "status": "A1_DEVELOPMENT_TRAINING_COMPLETE",
        "model": model_info,
        "profile": "mini",
        "updates_completed": pass_limit,
        "passes_completed": pass_limit * 8 / len(train),
        "selection_rule": "lowest mean validation response NLL; exact ties choose earlier update",
        "curve": curve,
        "checkpoints": checkpoints,
        "selected_checkpoint": selected,
        "open_dev": {"n": len(predictions), "schema_valid": schema_valid, "strict_schema_rate": schema_valid / max(1, len(predictions)), "correct": correct, "end_to_end_correct_rate": correct / max(1, len(predictions)), "independent_groups": len({row["world_group_id"] for row in predictions})},
        "calibration_used_for_selection": False,
        "locked_data_read_or_scored": False,
        "synthetic_data": True,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, sort_keys=True, default=list) + "\n")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=[11, 23])
    parser.add_argument("--max-updates", type=int, default=512)
    parser.add_argument("--generation-cap", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-a1dev")
    root = args.output_root or ROOT / "results/raw/te-v0.6.1-pythia-development/a1-development-training" / run_id
    results = [run_seed(seed, root / f"seed-{seed}", max_updates=args.max_updates, device=args.device, generation_cap=args.generation_cap) for seed in args.seeds]
    summary = {"protocol": "te-v0.6.1-pythia-development", "experiment_id": "a1-development-training", "run_id": run_id, "status": "COMPLETE", "attempts": results}
    root.mkdir(parents=True, exist_ok=True)
    (root / "run-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": summary["status"], "attempts": [{"seed": row["seed"], "updates": row["updates_completed"], "strict_schema_rate": row["open_dev"]["strict_schema_rate"]} for row in results]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
