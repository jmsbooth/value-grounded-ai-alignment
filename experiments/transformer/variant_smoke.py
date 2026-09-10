#!/usr/bin/env python3
"""Execute real bounded training/checkpoint/inference for all eight arms."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import subprocess
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import auxiliary_target_tensors, build_model, dataset_for_profile, generate_record, optimizer_for, reload_checkpoint, save_model_checkpoint, seed_everything
from vgta_transformer.checkpointing import verify_checkpoint
from vgta_transformer.collator import collate_examples
from vgta_transformer.training import tiny_train_step


ARMS = ("A1", "B", "C1", "C2", "B-TEXT-A", "C1-TEXT-N", "C1-SHAM", "C2-SHAM")


def run_attempt(variant: str, seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int) -> dict[str, object]:
    import torch

    if device == "mps":
        torch.mps.empty_cache()
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    train = dataset.by_split("train")[:8]
    open_dev = dataset.by_split("open-dev")[:8]
    model, tokenizer, heads, active = build_model(seed, device=device, variant=variant)
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
    structured = variant not in {"A1", "B-TEXT-A"}
    batch = collate_examples(train, tokenizer, annotations={example.public_id: annotations[example.public_id] for example in train}, structured=structured, max_length=2048)
    batch = {key: value.to(device) if hasattr(value, "to") else value for key, value in batch.items()}
    targets = auxiliary_target_tensors([annotations[example.public_id] for example in train], device=device)
    if variant.endswith("-SHAM"):
        permutation = [(index + seed) % len(train) for index in range(len(train))]
        targets = {name: value[permutation] for name, value in targets.items()}
    weights = {name: 0.2 for name in active}
    metrics = []
    started = time.perf_counter()
    for update in range(max_updates):
        result = tiny_train_step(model, batch, optimizer, auxiliary_heads=heads, auxiliary_targets=targets if active else None, auxiliary_weights=weights if active else None)
        result.update({"update": update + 1, "seed": seed, "variant": variant, "examples": len(train), "effective_batch_size": len(train)})
        metrics.append(result)
    checkpoint = output_dir / "checkpoint"
    save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": "te-v0.6.1-pythia-development", "experiment_id": "variant-training-smoke", "variant": variant, "seed": seed, "update_count": max_updates, "sham_permutation": "fixed-seed-rotation" if variant.endswith("-SHAM") else None})
    checkpoint_ok = all(verify_checkpoint(checkpoint).values())
    allocated_parameters = sum(value.numel() for value in model.parameters())
    updated_adapter_parameters = sum(value.numel() for name, value in model.named_parameters() if value.requires_grad and "lora_" in name)
    updated_auxiliary_parameters = sum(value.numel() for value in heads.parameters()) if heads is not None else 0
    del model, tokenizer, heads, optimizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    loaded_model, loaded_tokenizer, _, _ = reload_checkpoint(checkpoint, device=device, variant=variant)
    predictions = []
    for example in open_dev:
        row = generate_record(loaded_model, loaded_tokenizer, example, annotations[example.public_id], structured=structured, max_new_tokens=generation_cap, device=device)
        row.update({"experiment_id": "variant-training-smoke", "variant": variant, "seed": seed, "checkpoint_update": max_updates})
        predictions.append(row)
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "variant-training-smoke",
        "attempt_id": f"{variant}-seed-{seed}",
        "variant": variant,
        "seed": seed,
        "status": "VARIANT_SMOKE_ATTEMPT_COMPLETE",
        "updates_completed": max_updates,
        "device": device,
        "schedule": {
            "protocol_max_updates": 32,
            "selected_max_updates": max_updates,
            "amendment_id": "te-v0.6.1-variant-smoke-bounded-schedule",
        },
        "train_examples_per_update": len(train),
        "active_auxiliary_heads": list(active),
        "allocated_trainable_parameters": allocated_parameters,
        "updated_adapter_parameters": updated_adapter_parameters,
        "updated_auxiliary_parameters": updated_auxiliary_parameters,
        "training_metrics": metrics,
        "checkpoint": {"path": str(checkpoint.relative_to(ROOT)), "verified": checkpoint_ok, "reloaded": True},
        "open_dev": {"n": len(predictions), "schema_valid": sum(bool(row["parse_success"]) for row in predictions), "task_correct": sum(bool(row["task_correct"]) for row in predictions)},
        "wall_seconds": time.perf_counter() - started,
        "structured_input": structured,
        "same_public_training_bytes_as_paired_arm": variant in {"C1", "C2", "C1-SHAM", "C2-SHAM", "C1-TEXT-N"},
        "locked_data_read_or_scored": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as handle:
        for row in predictions:
            handle.write(json.dumps(row, sort_keys=True, default=list) + "\n")
    (output_dir / "training-metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    del loaded_model, loaded_tokenizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=[11, 23])
    parser.add_argument("--variants", nargs="+", default=list(ARMS), choices=ARMS)
    parser.add_argument("--max-updates", type=int, default=32)
    parser.add_argument("--generation-cap", type=int, default=64)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--isolate-attempts", action="store_true", help="run each arm/seed in a fresh child process")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-variant-smoke")
    root = args.output_root or ROOT / "results/raw/te-v0.6.1-pythia-development/variant-training-smoke" / run_id
    attempts = []
    if args.isolate_attempts:
        for variant in args.variants:
            for seed in args.seeds:
                child_root = root / f"child-{variant}-seed-{seed}"
                command = [sys.executable, str(Path(__file__).resolve()), "--output-root", str(child_root), "--variants", variant, "--seeds", str(seed), "--max-updates", str(args.max_updates), "--generation-cap", str(args.generation_cap), "--device", args.device]
                child_result = child_root / variant / f"seed-{seed}" / "result.json"
                completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                if completed.returncode == 0 and child_result.exists():
                    attempts.append(json.loads(child_result.read_text(encoding="utf-8")))
                else:
                    attempts.append({
                        "protocol": "te-v0.6.1-pythia-development",
                        "experiment_id": "variant-training-smoke",
                        "attempt_id": f"{variant}-seed-{seed}",
                        "variant": variant,
                        "seed": seed,
                        "status": "VARIANT_SMOKE_ATTEMPT_FAILED",
                        "updates_completed": 0,
                        "device": args.device,
                        "error": (completed.stderr or completed.stdout)[-4000:],
                        "checkpoint": {"verified": False, "reloaded": False},
                        "locked_data_read_or_scored": False,
                    })
        successful = len(attempts) == 16 and all(attempt.get("status") == "VARIANT_SMOKE_ATTEMPT_COMPLETE" and bool(attempt.get("checkpoint", {}).get("verified")) for attempt in attempts)
        summary = {"protocol": "te-v0.6.1-pythia-development", "experiment_id": "variant-training-smoke", "run_id": run_id, "status": "VARIANT_SMOKE_COMPLETE" if successful else "VARIANT_SMOKE_PARTIAL", "attempt_count": len(attempts), "expected_attempt_count": 16, "execution_isolation": "fresh-child-process-per-arm-seed", "attempts": attempts}
        root.mkdir(parents=True, exist_ok=True)
        (root / "run-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
        print(json.dumps({"run_id": run_id, "status": summary["status"], "attempt_count": len(attempts)}, sort_keys=True))
        return 0
    for variant in args.variants:
        for seed in args.seeds:
            attempts.append(run_attempt(variant, seed, root / f"{variant}/seed-{seed}", max_updates=args.max_updates, device=args.device, generation_cap=args.generation_cap))
    summary = {"protocol": "te-v0.6.1-pythia-development", "experiment_id": "variant-training-smoke", "run_id": run_id, "status": "VARIANT_SMOKE_COMPLETE" if len(attempts) == 16 else "VARIANT_SMOKE_PARTIAL", "attempt_count": len(attempts), "expected_attempt_count": 16, "attempts": attempts}
    root.mkdir(parents=True, exist_ok=True)
    (root / "run-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": summary["status"], "attempt_count": len(attempts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
