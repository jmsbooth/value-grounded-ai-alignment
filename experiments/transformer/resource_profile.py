#!/usr/bin/env python3
"""Measure representative real-Pythia training, generation, and checkpoint cost."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import shutil
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import auxiliary_target_tensors, batch_for, build_model, dataset_for_profile, optimizer_for, save_model_checkpoint, generate_record
from vgta_transformer.checkpointing import verify_checkpoint
from vgta_transformer.model_loader import model_load_info
from vgta_transformer.training import tiny_train_step


def _rss() -> int:
    import psutil
    return int(psutil.Process().memory_info().rss)


def run(output_dir: Path, *, device: str = "cpu") -> dict[str, object]:
    start = time.perf_counter()
    dataset = dataset_for_profile("mini")
    annotation_map = dataset.annotation_map()
    examples = dataset.by_split("train")[:2]
    model, tokenizer, heads, active = build_model(11, device=device, variant="C2")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
    batches = [batch_for(example, annotation_map[example.public_id], tokenizer, structured=True, device=device) for example in examples]
    warmups = []
    measured = []
    peak = _rss()
    for index in range(2):
        tick = time.perf_counter()
        targets = auxiliary_target_tensors([annotation_map[examples[index % len(examples)].public_id]], device=device)
        metrics = tiny_train_step(model, batches[index % len(batches)], optimizer, auxiliary_heads=heads, auxiliary_targets=targets, auxiliary_weights={name: 0.2 for name in active})
        warmups.append({"iteration": index, "seconds": time.perf_counter() - tick, "metrics": metrics})
        peak = max(peak, _rss())
    for index in range(5):
        tick = time.perf_counter()
        row_index = index % len(batches)
        targets = auxiliary_target_tensors([annotation_map[examples[row_index].public_id]], device=device)
        metrics = tiny_train_step(model, batches[row_index], optimizer, auxiliary_heads=heads, auxiliary_targets=targets, auxiliary_weights={name: 0.2 for name in active})
        elapsed = time.perf_counter() - tick
        measured.append({"iteration": index, "seconds": elapsed, "examples_per_second": 1.0 / elapsed, "supervised_response_tokens": metrics["response_token_count"], "tokens_per_second": metrics["response_token_count"] / elapsed, "metrics": metrics})
        peak = max(peak, _rss())
    generation_rows = []
    for example in examples:
        tick = time.perf_counter()
        row = generate_record(model, tokenizer, example, annotation_map[example.public_id], structured=True, max_new_tokens=256, device=device)
        row["seconds"] = time.perf_counter() - tick
        generation_rows.append(row)
        peak = max(peak, _rss())
    checkpoint = output_dir / "checkpoint"
    tick = time.perf_counter()
    save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": "te-v0.6.1-pythia-development", "experiment_id": "resource-profile", "update_count": 7})
    save_seconds = time.perf_counter() - tick
    roundtrip = all(verify_checkpoint(checkpoint).values())
    total, used, free = shutil.disk_usage(ROOT)
    del total, used
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "resource-profile",
        "status": "RESOURCE_PROFILE_MEASURED",
        "model": model_load_info(model, device=device, local_files_only=True).__dict__,
        "variant": "C2-representative-worst-case-auxiliary",
        "warmups": warmups,
        "measured_iterations": measured,
        "generation_rows": generation_rows,
        "checkpoint": {"save_seconds": save_seconds, "roundtrip_verified": roundtrip, "path": str(checkpoint.relative_to(ROOT))},
        "peak_rss_bytes": peak,
        "peak_rss_gib": round(peak / 2**30, 4),
        "disk_free_gib_after": round(free / 2**30, 3),
        "wall_seconds": time.perf_counter() - start,
        "resource_budget": {"phase_wall_hours": 8, "attempt_wall_hours": 2, "resident_models": 1},
        "extrapolation_boundary": "measured C2 mini-sequence cost; no locked-cohort cost is authorized or inferred",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "resource-profile.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    del model, heads, optimizer
    gc.collect()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-resource")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.1-pythia-development/resource-profile" / run_id
    result = run(output_dir, device=args.device)
    print(json.dumps({"status": result["status"], "wall_seconds": result["wall_seconds"], "peak_rss_gib": result["peak_rss_gib"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
