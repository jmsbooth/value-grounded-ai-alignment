#!/usr/bin/env python3
"""Bounded v0.6.2 eight-arm smoke with matched accumulation and sham maps."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import auxiliary_target_tensors, batch_for, build_model, dataset_for_profile, generate_record, optimizer_for, reload_checkpoint, save_model_checkpoint, seed_everything
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_transformer.checkpointing import verify_checkpoint
from vgta_transformer.training import accumulated_train_step, parameter_accounting
from vgta_transformer.variant_plan import VariantSpec, load_variant_specs

PROTOCOL = "te-v0.6.2-pythia-correction"
PLAN = ROOT / "experiments/protocols/te-v0.6.2-pythia-correction/variants.yaml"


def _tensor_hash(value: object) -> str:
    return hashlib.sha256(value.detach().cpu().numpy().tobytes()).hexdigest()


def run_attempt(spec: VariantSpec, seed: int, output_dir: Path, *, max_updates: int, device: str, generation_cap: int, config: dict[str, object]) -> dict[str, object]:
    import torch
    start = time.perf_counter()
    seed_everything(seed)
    dataset = dataset_for_profile("mini")
    annotations = dataset.annotation_map()
    train = dataset.by_split("train")
    open_dev = dataset.by_split("open-dev")
    world_map = {world.world_id: world for world in dataset.worlds}
    model, tokenizer, heads, active = build_model(seed, device=device, variant=spec.name)
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.01)
    before_parameters = {name: value.detach().clone() for name, value in list(model.named_parameters()) + (list(heads.named_parameters()) if heads is not None else []) if value.requires_grad}
    all_targets = auxiliary_target_tensors([annotations[example.public_id] for example in train], device=device)
    sham_rng = random.Random(seed + 104729)
    permutation = list(range(len(train)))
    if spec.shuffled_targets:
        sham_rng.shuffle(permutation)
    mapping = {
        name: {"seed": seed + 104729, "target": name, "source_indices": permutation, "source_hash": _tensor_hash(all_targets[name][permutation]), "changed_fraction": sum(left != right for left, right in zip(range(len(permutation)), permutation)) / len(permutation), "class_distribution": all_targets[name].sum(dim=0).detach().cpu().tolist()}
        for name in spec.shuffled_targets
    }
    metrics = []
    for update in range(max_updates):
        indices = [((update * 8) + offset) % len(train) for offset in range(8)]
        batches = [batch_for(train[index], annotations[train[index].public_id], tokenizer, structured=spec.structured, device=device, span_weight_fields=spec.span_weight_fields) for index in indices]
        target_rows: list[dict[str, object]] | None = None
        if active:
            target_rows = []
            for index in indices:
                row: dict[str, object] = {}
                for name in active:
                    source_index = permutation[index] if name in spec.shuffled_targets else index
                    row[name] = all_targets[name][source_index : source_index + 1]
                target_rows.append(row)
        update_metrics = accumulated_train_step(model, batches, optimizer, auxiliary_heads=heads, auxiliary_targets=target_rows, auxiliary_weights=spec.auxiliary_weights)
        update_metrics.update({"seed": seed, "variant": spec.name, "update": update + 1, "train_indices": indices, "effective_batch_size": len(batches)})
        metrics.append(update_metrics)
    checkpoint = output_dir / "checkpoint"
    save_model_checkpoint(checkpoint, model, heads, optimizer, metadata={"protocol": PROTOCOL, "experiment_id": "corrected-variant-smoke", "variant": spec.name, "variant_fingerprint": spec.fingerprint, "seed": seed, "update_count": max_updates, "physical_microbatch_size": 1, "effective_batch_size": 8, "sham_mapping": mapping, "model_visible_structured": spec.structured, "config": config})
    checkpoint_ok = all(verify_checkpoint(checkpoint).values())
    counts = parameter_accounting(model, heads, optimizer, before=before_parameters)
    del model, tokenizer, heads, optimizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    loaded_model, loaded_tokenizer, _, _ = reload_checkpoint(checkpoint, device=device, variant=spec.name)
    predictions = []
    for example in open_dev:
        world = world_map[example.public_id.removeprefix("public-")]
        row = generate_record(loaded_model, loaded_tokenizer, example, annotations[example.public_id], structured=spec.structured, max_new_tokens=generation_cap, device=device, observation=__import__("vgta_eval.observation_projection", fromlist=["project_world"]).project_world(world))
        row.update({"experiment_id": "corrected-variant-smoke", "variant": spec.name, "seed": seed, "checkpoint_update": max_updates, "variant_fingerprint": spec.fingerprint})
        predictions.append(row)
    del loaded_model, loaded_tokenizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    result = {
        "protocol": PROTOCOL,
        "experiment_id": "corrected-variant-smoke",
        "attempt_id": f"{spec.name}-seed-{seed}",
        "variant": spec.name,
        "variant_fingerprint": spec.fingerprint,
        "config": config,
        "seed": seed,
        "status": "CORRECTED_VARIANT_ATTEMPT_COMPLETE",
        "updates_completed": max_updates,
        "device": device,
        "input_mode": spec.input_mode,
        "structured_input": spec.structured,
        "span_weight_fields": list(spec.span_weight_fields),
        "active_auxiliary_heads": list(active),
        "sham_mapping": mapping,
        "training_metrics": metrics,
        "parameter_accounting": counts,
        "checkpoint": {"path": str(checkpoint.relative_to(ROOT)), "verified": checkpoint_ok, "reloaded": True},
        "open_dev": {"n": len(predictions), "strict_schema_valid": sum(bool(row["parse_success"]) for row in predictions), "evaluator_assessable": sum(row.get("evaluator") is not None and row.get("parse_success") is True for row in predictions)},
        "wall_seconds": time.perf_counter() - start,
        "locked_data_read_or_scored": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "predictions.jsonl").write_text("".join(json.dumps(row, sort_keys=True, default=list) + "\n" for row in predictions), encoding="utf-8")
    (output_dir / "training-metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    (output_dir / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    return result


def main() -> int:
    from uuid import uuid4
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=[11, 23])
    parser.add_argument("--variants", nargs="+", default=None)
    parser.add_argument("--max-updates", type=int, default=32)
    parser.add_argument("--generation-cap", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--isolate-attempts", action="store_true")
    args = parser.parse_args()
    config_path = args.config.resolve() if args.config else PLAN
    if not config_path.is_file():
        raise FileNotFoundError(config_path)
    config = {"path": str(config_path), "sha256": hashlib.sha256(config_path.read_bytes()).hexdigest()}
    specs = load_variant_specs(config_path)
    names = args.variants or list(specs)
    seeds = args.seeds
    required_names = {"A1", "B", "C1", "C2", "B-TEXT-A", "C1-TEXT-N", "C1-SHAM", "C2-SHAM"}
    required_seeds = {11, 23}
    if set(specs) != required_names:
        raise ValueError("this protocol requires the declared eight-arm plan")
    if len(names) != len(set(names)) or not set(names).issubset(required_names):
        raise ValueError("selected arms must be unique members of the protocol")
    if len(seeds) != len(set(seeds)) or not set(seeds).issubset(required_seeds):
        raise ValueError("selected seeds must be unique members of the protocol")
    if not 1 <= args.max_updates <= 32 or args.generation_cap <= 0:
        raise ValueError("invalid bounded update or generation budget")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:10]
    root = (args.output_root or ROOT / "results/raw" / PROTOCOL / "corrected-variant-smoke" / run_id).resolve()
    # Reserve the execution directory before expensive work. Never overwrite evidence.
    root.mkdir(parents=True, exist_ok=False)
    selected_pairs = {(name, seed) for name in names for seed in seeds}
    protocol_pairs = {(name, seed) for name in required_names for seed in required_seeds}
    resolved = {"protocol": PROTOCOL, "run_id": run_id, "config": config,
                "selected_pairs": sorted(selected_pairs), "protocol_pairs": sorted(protocol_pairs),
                "requested_updates": args.max_updates, "protocol_updates": 32,
                "generation_cap": args.generation_cap, "device": args.device}
    (root / "resolved-execution.json").write_text(json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    attempts = []
    for name in names:
        for seed in seeds:
            child = root / name / f"seed-{seed}"
            try:
                if args.isolate_attempts:
                    # Each subprocess owns its own summary, receipts, and attempt tree.
                    child_root = root / "child-processes" / name / f"seed-{seed}"
                    command = [sys.executable, str(Path(__file__).resolve()), "--output-root", str(child_root), "--config", str(config_path), "--variants", name, "--seeds", str(seed), "--max-updates", str(args.max_updates), "--generation-cap", str(args.generation_cap), "--device", args.device]
                    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
                    log_dir = root / "process-logs" / name / f"seed-{seed}"
                    log_dir.mkdir(parents=True, exist_ok=False)
                    (log_dir / "stdout.log").write_text(completed.stdout or "", encoding="utf-8")
                    (log_dir / "stderr.log").write_text(completed.stderr or "", encoding="utf-8")
                    path = child_root / name / f"seed-{seed}" / "result.json"
                    if completed.returncode != 0 or not path.is_file():
                        raise RuntimeError(f"child exit={completed.returncode}; result_present={path.is_file()}")
                    item = json.loads(path.read_text(encoding="utf-8"))
                else:
                    item = run_attempt(specs[name], seed, child, max_updates=args.max_updates, device=args.device, generation_cap=args.generation_cap, config=config)
                if (item.get("variant"), item.get("seed")) != (name, seed):
                    raise ValueError("child identity does not match its scheduled arm/seed")
                attempts.append(item)
            except Exception as exc:
                failure = {"protocol": PROTOCOL, "experiment_id": "corrected-variant-smoke",
                           "attempt_id": f"{name}-seed-{seed}", "variant": name, "seed": seed,
                           "status": "CORRECTED_VARIANT_ATTEMPT_FAILED",
                           "error_type": type(exc).__name__, "error": str(exc),
                           "checkpoint": {"verified": False, "reloaded": False},
                           "locked_data_read_or_scored": False}
                attempts.append(failure)
                failure_path = root / "failures" / f"{name}-seed-{seed}.json"
                failure_path.parent.mkdir(parents=True, exist_ok=True)
                failure_path.write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    completed_pairs = {
        (item.get("variant"), item.get("seed")) for item in attempts
        if item.get("status") == "CORRECTED_VARIANT_ATTEMPT_COMPLETE"
        and item.get("updates_completed") == args.max_updates
        and item.get("checkpoint", {}).get("verified") is True
        and item.get("checkpoint", {}).get("reloaded") is True
    }
    selected_complete = completed_pairs == selected_pairs
    full_pairs = completed_pairs if args.max_updates == 32 and args.generation_cap >= 256 else set()
    protocol_complete = full_pairs == protocol_pairs
    summary = {
        "protocol": PROTOCOL, "experiment_id": "corrected-variant-smoke", "run_id": run_id, "config": config,
        "status": "CORRECTED_VARIANT_SMOKE_COMPLETE" if protocol_complete else "CORRECTED_VARIANT_SMOKE_PARTIAL",
        "selected_execution_complete": selected_complete,
        "selected_scope": "development" if selected_pairs == protocol_pairs and args.max_updates == 32 and args.generation_cap >= 256 else "canary",
        "attempt_count": len(attempts), "expected_attempt_count": len(selected_pairs),
        "protocol_expected_attempt_count": len(protocol_pairs), "protocol_completed_attempt_count": len(full_pairs),
        "protocol_missing_pairs": sorted(protocol_pairs - full_pairs),
        "updates_per_attempt": args.max_updates, "protocol_updates_per_attempt": 32,
        "generation_cap": args.generation_cap, "attempts": attempts,
        "locked_data_read_or_scored": False, "locked_cohort_authorized": False,
    }
    output = root / "run-summary.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="model_prediction", protocol=PROTOCOL, status=summary["status"], experiment_id=summary["experiment_id"], run_id=run_id, result_sha256=sha256_file(output), attempt_count=len(attempts), locked_data_read_or_scored=False)
    write_receipt(root / "evidence-receipt.json", receipt)
    print(json.dumps({"status": summary["status"], "run_id": run_id, "attempt_count": len(attempts), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0 if selected_complete else 1

if __name__ == "__main__":
    raise SystemExit(main())
