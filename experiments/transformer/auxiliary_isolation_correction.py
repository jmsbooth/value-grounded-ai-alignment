#!/usr/bin/env python3
"""Run tiny and, when requested, actual-Pythia auxiliary-only diagnostics."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gc
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import auxiliary_target_tensors, batch_for, build_model, dataset_for_profile, optimizer_for, seed_everything
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_transformer.losses import masked_bce_with_logits_stats
from vgta_transformer.training import parameter_accounting


def run(device: str, *, actual: bool) -> dict[str, object]:
    import torch
    seed_everything(11)
    dataset = dataset_for_profile("mini")
    example = dataset.by_split("train")[0]
    annotations = dataset.annotation_map()
    model, tokenizer, heads, active = build_model(11, device=device, variant="C2")
    optimizer = optimizer_for(model, heads, learning_rate=2e-4, weight_decay=0.0)
    batch = batch_for(example, annotations[example.public_id], tokenizer, structured=True, device=device)
    targets = auxiliary_target_tensors([annotations[example.public_id]], device=device)
    rows = []
    isolated_shared_gradients = {}
    model.eval()
    for name in active:
        optimizer.zero_grad(set_to_none=True)
        outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], output_hidden_states=True, use_cache=False)
        from vgta_transformer.auxiliary_heads import pool_prompt_hidden
        logits = heads(pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]))[name]
        loss = masked_bce_with_logits_stats(logits, targets[name])[0] / masked_bce_with_logits_stats(logits, targets[name])[1].clamp_min(1.0)
        loss.backward()
        shared = [parameter for key, parameter in model.named_parameters() if "lora_" in key]
        head_parameters = list(heads.parameters())
        isolated_shared_gradients[name] = [parameter.grad.detach().clone() if parameter.grad is not None else torch.zeros_like(parameter) for parameter in shared]
        rows.append({"head": name, "response_loss_coefficient": 0.0, "loss": float(loss.detach().cpu()), "shared_lora_nonzero_gradient": any(parameter.grad is not None and bool(parameter.grad.detach().ne(0).any()) for parameter in shared), "head_nonzero_gradient": any(parameter.grad is not None and bool(parameter.grad.detach().ne(0).any()) for parameter in head_parameters), "optimizer_step_taken": False})
        del outputs, logits, loss
    optimizer.zero_grad(set_to_none=True)
    outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], output_hidden_states=True, use_cache=False)
    combined_logits = heads(pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]))
    combined_loss = sum(masked_bce_with_logits_stats(combined_logits[name], targets[name])[0] / masked_bce_with_logits_stats(combined_logits[name], targets[name])[1].clamp_min(1.0) for name in active)
    combined_loss.backward()
    shared = [parameter for key, parameter in model.named_parameters() if "lora_" in key]
    expected = [sum(isolated_shared_gradients[name][index] for name in active) for index in range(len(shared))]
    max_gradient_difference = max(float((left.grad - right).abs().max().cpu()) for left, right in zip(shared, expected))
    rows.append({"test": "combined_vs_isolated_gradients", "max_abs_difference": max_gradient_difference, "combined_gradient_finite": all(parameter.grad is not None and bool(torch.isfinite(parameter.grad).all()) for parameter in shared), "optimizer_step_taken": False})
    optimizer.zero_grad(set_to_none=True)
    outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], output_hidden_states=True, use_cache=False)
    disabled_logits = heads(pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]))
    disabled_loss = masked_bce_with_logits_stats(disabled_logits["values"], targets["values"])[0] / masked_bce_with_logits_stats(disabled_logits["values"], targets["values"])[1].clamp_min(1.0)
    disabled_loss.backward()
    relation_parameters = list(heads.relation.parameters())
    rows.append({"test": "disabled_head_no_gradient", "enabled_head": "values", "disabled_head": "relation", "disabled_head_nonzero_gradient": any(parameter.grad is not None and bool(parameter.grad.detach().ne(0).any()) for parameter in relation_parameters), "optimizer_step_taken": False})
    del outputs, combined_logits, combined_loss, disabled_logits, disabled_loss
    # Detaching the pooled representation is a negative control: head gradients
    # remain possible, while the shared LoRA path must be zero.
    optimizer.zero_grad(set_to_none=True)
    outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], output_hidden_states=True, use_cache=False)
    pooled = pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]).detach()
    detached_logits = heads(pooled)["values"]
    detached_loss = masked_bce_with_logits_stats(detached_logits, targets["values"])[0] / masked_bce_with_logits_stats(detached_logits, targets["values"])[1].clamp_min(1.0)
    detached_loss.backward()
    rows.append({"test": "detached_pooled_representation", "shared_lora_nonzero_gradient": any(parameter.grad is not None and bool(parameter.grad.detach().ne(0).any()) for key, parameter in model.named_parameters() if "lora_" in key), "head_nonzero_gradient": any(parameter.grad is not None and bool(parameter.grad.detach().ne(0).any()) for parameter in heads.parameters()), "optimizer_step_taken": False})
    counts = parameter_accounting(model, heads, optimizer)
    result = {"protocol": "te-v0.6.2-pythia-correction", "experiment_id": "auxiliary-isolation", "status": "AUXILIARY_ISOLATION_ACTUAL_PYTHIA" if actual else "AUXILIARY_ISOLATION_TINY", "device": device, "actual_pythia": actual, "active_heads": list(active), "rows": rows, "parameter_accounting": counts, "response_loss_included": False, "weight_decay_counted_as_gradient": False, "locked_data_read_or_scored": False}
    del model, tokenizer, heads, optimizer
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--actual", action="store_true")
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-aux-only")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/auxiliary-isolation" / run_id
    result = run(args.device, actual=args.actual)
    result["run_id"] = run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="training_diagnostic", protocol=result["protocol"], status=result["status"], experiment_id=result["experiment_id"], run_id=run_id, result_sha256=sha256_file(output), actual_pythia=args.actual, locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "run_id": run_id, "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
