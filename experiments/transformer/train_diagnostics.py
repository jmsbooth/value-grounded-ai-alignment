#!/usr/bin/env python3
"""Run a tiny real-model LoRA/auxiliary-head diagnostic when available."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt
from phase_guards import require_semantic_gate
from vgta_eval.semantic_worlds import generate_semantic_dataset
from vgta_transformer.adaptation import add_lora, trainable_parameter_count
from vgta_transformer.auxiliary_heads import AuxiliaryHeads
from vgta_transformer.collator import collate_examples
from vgta_transformer.checkpointing import save_checkpoint, verify_checkpoint
from vgta_transformer.model_loader import ModelDependencyError, load_base_model, load_tokenizer
from vgta_transformer.training import tiny_train_step, trainable_parameters


def run(*, output_dir: Path, allow_download: bool, device: str) -> dict[str, object]:
    try:
        require_semantic_gate(ROOT)
        import torch
        dataset = generate_semantic_dataset(group_counts={"train": 2, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
        tokenizer = load_tokenizer(local_files_only=not allow_download)
        model = load_base_model(local_files_only=not allow_download, device=device)
        model = add_lora(model)
        batch = collate_examples(dataset.by_split("train"), tokenizer, annotations=dataset.annotation_map(), structured=True, max_length=2048)
        heads = AuxiliaryHeads(int(model.config.hidden_size), value_count=4, relation_count=8, norm_count=4, conflict_count=3).to(device)
        annotations = [dataset.annotation_map()[public_id] for public_id in batch["public_ids"]]
        value_labels = ("agency", "privacy", "accountability", "scope")
        relation_labels = ("consent_scope", "delegation_status", "recipient_authorization", "evidence_freshness", "policy_compliance", "requires_evidence", "governance", "unknown")
        norm_labels = ("norm_01", "norm_02", "norm_03", "norm_04")
        conflict_labels = ("no_conflict", "resolvable_conflict", "unresolved_conflict")
        auxiliary_targets = {
            "values": torch.tensor([[float(label in annotation.salient_values) for label in value_labels] for annotation in annotations], device=device),
            "relation": torch.tensor([[float(annotation.relation_class == label) for label in relation_labels] for annotation in annotations], device=device),
            "norms": torch.tensor([[float(label in annotation.applicable_norm_ids) for label in norm_labels] for annotation in annotations], device=device),
            "conflict": torch.tensor([[float(annotation.conflict_class == label) for label in conflict_labels] for annotation in annotations], device=device),
        }
        optimizer = torch.optim.AdamW(trainable_parameters(model, heads), lr=2e-5)
        before = {name: parameter.detach().clone() for name, parameter in model.named_parameters() if not parameter.requires_grad}
        metrics = tiny_train_step(model, batch, optimizer, auxiliary_heads=heads, auxiliary_targets=auxiliary_targets, auxiliary_weights={"values": 0.2, "relation": 0.2, "norms": 0.2, "conflict": 0.2})
        frozen_unchanged = all(torch.equal(parameter, before[name]) for name, parameter in model.named_parameters() if name in before)
        checkpoint_path = output_dir / "checkpoint"
        save_checkpoint(checkpoint_path, model, auxiliary_heads=heads, metadata={"protocol": "te-v0.6.0-pythia", "diagnostic_step": 1})
        checkpoint_ok = all(verify_checkpoint(checkpoint_path).values())
        result = {
            "status": "PYTHIA_TRAINING_DIAGNOSTIC_PASSED" if frozen_unchanged and checkpoint_ok else "PYTHIA_TRAINING_DIAGNOSTIC_REJECTED",
            "metrics": metrics,
            "trainable_parameters": trainable_parameter_count(model) + trainable_parameter_count(heads),
            "lora_trainable_parameters": trainable_parameter_count(model),
            "frozen_backbone_unchanged": frozen_unchanged,
            "checkpoint_roundtrip_verified": checkpoint_ok,
            "checkpoint_path": str(checkpoint_path.relative_to(ROOT)),
            "use_cache": False,
            "steps": 1,
            "synthetic_dataset": True,
            "real_pretrained_model": True,
        }
    except (ModelDependencyError, OSError, RuntimeError, ValueError, ImportError, FloatingPointError) as exc:
        result = {
            "status": "PYTHIA_TRAINING_DIAGNOSTIC_BLOCKED",
            "reason_type": type(exc).__name__,
            "reason": str(exc),
            "synthetic_dataset": True,
            "real_pretrained_model": False,
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "training-diagnostic.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(output_dir / "evidence-receipt.json", make_receipt(
        producer_kind="training_diagnostic", protocol="te-v0.6.0-pythia", status=str(result["status"]),
        real_pretrained_model=bool(result.get("real_pretrained_model")),
    ))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/training-diagnostics")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, allow_download=args.download, device=args.device)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
