#!/usr/bin/env python3
"""Measure the common v0.6.2 resource envelope on longest B and C2 inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import batch_for, build_model, dataset_for_profile, generate_record, optimizer_for, save_model_checkpoint, seed_everything
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_eval.observation_projection import project_world
from vgta_transformer.response_contract import build_training_sequence
from vgta_transformer.training import accumulated_response_step

PROTOCOL = "te-v0.6.2-pythia-correction"


def rss() -> int:
    import psutil
    return int(psutil.Process().memory_info().rss)


def run(output_dir: Path, *, device: str) -> dict[str, object]:
    import shutil
    start = time.perf_counter()
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    tokenizer = __import__("vgta_transformer.model_loader", fromlist=["load_tokenizer"]).load_tokenizer(local_files_only=True)
    world_map = {world.world_id: world for world in dataset.worlds}
    selected: dict[str, dict[str, object]] = {}
    for variant, structured in (("B", True), ("C2", True)):
        lengths = []
        for example in dataset.by_split("train"):
            seq = build_training_sequence(example, annotations[example.public_id], tokenizer, structured=structured, max_length=2048)
            lengths.append((len(seq.input_ids), example))
        _, longest = max(lengths, key=lambda item: item[0])
        seed_everything(11)
        model, model_tokenizer, heads, active = build_model(11, device=device, variant=variant)
        optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
        batch = batch_for(longest, annotations[longest.public_id], model_tokenizer, structured=structured, device=device)
        peak = rss()
        tick = time.perf_counter()
        train_metrics = accumulated_response_step(model, [batch], optimizer, max_grad_norm=1.0)
        train_seconds = time.perf_counter() - tick
        peak = max(peak, rss())
        tick = time.perf_counter()
        row = generate_record(model, model_tokenizer, longest, annotations[longest.public_id], structured=structured, max_new_tokens=256, device=device, observation=project_world(world_map[longest.public_id.removeprefix("public-")]))
        generation_seconds = time.perf_counter() - tick
        peak = max(peak, rss())
        checkpoint = output_dir / f"{variant.lower()}-checkpoint"
        save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": PROTOCOL, "experiment_id": "common-resource-profile", "variant": variant, "seed": 11, "longest_example": longest.public_id, "physical_microbatch_size": 1, "effective_batch_size": 1})
        selected[variant] = {"public_id": longest.public_id, "sequence_tokens": int(batch["attention_mask"].sum().item()), "prompt_tokens": int(batch["prompt_token_count"]), "response_tokens": int(batch["response_token_count"]), "train_seconds": train_seconds, "generation_seconds": generation_seconds, "peak_rss_bytes": peak, "peak_rss_gib": round(peak / 2**30, 4), "train_metrics": train_metrics, "generation_parse_success": row["parse_success"], "checkpoint": str(checkpoint.relative_to(ROOT))}
        del model, model_tokenizer, heads, optimizer
        gc.collect()
        if device == "mps":
            import torch
            torch.mps.empty_cache()
    _, _, free = shutil.disk_usage(ROOT)
    result = {"protocol": PROTOCOL, "experiment_id": "common-resource-profile", "status": "COMMON_RESOURCE_PROFILE_MEASURED", "device": device, "precision": "float32", "context_length": 2048, "generation_cap": 256, "physical_microbatch_size": 1, "effective_batch_size": 1, "same_config_for_arms": True, "selected": selected, "disk_free_gib_after": round(free / 2**30, 3), "wall_seconds": time.perf_counter() - start, "unsafe_mps_watermark_override": False, "locked_data_read_or_scored": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "resource-profile.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="historical_qualification", protocol=PROTOCOL, status=result["status"], experiment_id=result["experiment_id"], result_sha256=sha256_file(output), variants=["B", "C2"], locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-common-resource")
    result = run(args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/common-resource-profile" / run_id, device=args.device)
    print(json.dumps({"status": result["status"], "run_id": run_id, "selected": {key: value["sequence_tokens"] for key, value in result["selected"].items()}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
