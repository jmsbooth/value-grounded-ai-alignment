#!/usr/bin/env python3
"""Teach the fixed response contract on eight examples, retaining all outputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import batch_for, build_model, dataset_for_profile, evaluate_nll, examples_for, generate_record, optimizer_for, save_model_checkpoint, seed_everything
from vgta_transformer.model_loader import model_load_info
from vgta_transformer.training import accumulated_response_step


def select_examples(dataset):
    annotations = dataset.annotation_map()
    train = list(dataset.by_split("train"))
    selected = []
    seen_actions = set()
    seen_domains = set()
    for example in train:
        annotation = annotations[example.public_id]
        if annotation.candidate_id not in seen_actions or example.domain not in seen_domains:
            selected.append(example)
            seen_actions.add(annotation.candidate_id)
            seen_domains.add(example.domain)
        if len(selected) == 8:
            return tuple(selected)
    for example in train:
        if example not in selected:
            selected.append(example)
        if len(selected) == 8:
            break
    return tuple(selected)


def run_seed(seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int) -> dict[str, object]:
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    selected = select_examples(dataset)
    model, tokenizer, heads, active = build_model(seed, device=device, variant="A1")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.0)
    rows = []
    predictions = []
    checkpoints = []
    started = time.perf_counter()
    eval_steps = {0, 25, 50, 75, 100, 125, 150, 175, 200}
    for update in range(max_updates + 1):
        if update in eval_steps:
            evaluation = evaluate_nll(model, tokenizer, selected, annotations, structured=False, device=device)
            evaluation.update({"seed": seed, "update": update, "elapsed_seconds": time.perf_counter() - started})
            rows.append(evaluation)
            checkpoint = output_dir / f"checkpoints/step-{update:04d}"
            save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": "te-v0.6.1-pythia-development", "experiment_id": "a1-memorization", "seed": seed, "update_count": update, "selection": "fixed-eight-train-examples"})
            checkpoints.append({"update": update, "path": str(checkpoint.relative_to(ROOT))})
            for example in selected:
                record = generate_record(model, tokenizer, example, annotations[example.public_id], structured=False, max_new_tokens=generation_cap, device=device)
                record.update({"experiment_id": "a1-memorization", "seed": seed, "update": update, "variant": "A1"})
                predictions.append(record)
        if update == max_updates:
            break
        indices = [(update * 4 + offset) % len(selected) for offset in range(4)]
        batches = [batch_for(selected[index], annotations[selected[index].public_id], tokenizer, structured=False, device=device) for index in indices]
        metrics = accumulated_response_step(model, batches, optimizer, max_grad_norm=1.0)
        metrics.update({"seed": seed, "update": update + 1, "microbatches": len(batches), "examples": len(set(indices))})
        (output_dir / "training-metrics.jsonl").parent.mkdir(parents=True, exist_ok=True)
        with (output_dir / "training-metrics.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metrics, sort_keys=True) + "\n")
    by_update = {row["update"]: row for row in rows}
    criterion_rows = []
    for update in sorted(by_update):
        outputs = [row for row in predictions if row["update"] == update]
        criterion_rows.append({
            "update": update,
            "schema_valid": sum(bool(row["parse_success"]) for row in outputs),
            "acceptable_action": sum(bool(row["task_correct"]) for row in outputs),
            "n": len(outputs),
            "nll": by_update[update]["response_nll"],
        })
    meets = False
    for previous, current in zip(criterion_rows, criterion_rows[1:]):
        if previous["schema_valid"] >= 7 and current["schema_valid"] >= 7 and previous["acceptable_action"] >= 7 and current["acceptable_action"] >= 7 and current["nll"] <= criterion_rows[0]["nll"] * 0.7:
            meets = True
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "a1-memorization",
        "attempt_id": f"seed-{seed}",
        "seed": seed,
        "status": "A1_MEMORIZATION_CRITERION_MET" if meets else "A1_MEMORIZATION_CRITERION_NOT_MET",
        "model": model_load_info(model, device=device, local_files_only=True).__dict__,
        "selected_public_ids": [example.public_id for example in selected],
        "selected_domains": sorted({example.domain for example in selected}),
        "max_updates_requested": max_updates,
        "updates_completed": max_updates,
        "evaluation_curve": rows,
        "criterion_curve": criterion_rows,
        "generated_output_count": len(predictions),
        "checkpoints": checkpoints,
        "prediction_model_state": "fresh-adapter-a1",
        "synthetic_data": True,
        "locked_data_read_or_scored": False,
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
    parser.add_argument("--max-updates", type=int, default=200)
    parser.add_argument("--generation-cap", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-memorization")
    root = args.output_root or ROOT / "results/raw/te-v0.6.1-pythia-development/a1-memorization" / run_id
    results = [run_seed(seed, root / f"seed-{seed}", max_updates=args.max_updates, device=args.device, generation_cap=args.generation_cap) for seed in args.seeds]
    summary = {"protocol": "te-v0.6.1-pythia-development", "experiment_id": "a1-memorization", "run_id": run_id, "status": "COMPLETE", "attempts": results}
    root.mkdir(parents=True, exist_ok=True)
    (root / "run-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": summary["status"], "attempts": [{"seed": row["seed"], "status": row["status"], "updates": row["updates_completed"]} for row in results]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
