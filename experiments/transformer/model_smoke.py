#!/usr/bin/env python3
"""Load the real Pythia checkpoint and perform one deterministic forward pass."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt
from phase_guards import require_semantic_gate
from vgta_transformer.model_loader import ModelDependencyError, config_digest, load_base_model, load_tokenizer, model_load_info, snapshot_asset_digest


def run(*, output_dir: Path, allow_download: bool, device: str) -> dict[str, object]:
    try:
        require_semantic_gate(ROOT)
        tokenizer = load_tokenizer(local_files_only=not allow_download)
        model = load_base_model(local_files_only=not allow_download, device=device)
        import torch
        text = "Apply the stated policy to the observed fictional world. Return one action."
        encoded = tokenizer(text, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**encoded, use_cache=False)
        finite = bool(torch.isfinite(outputs.logits).all().cpu())
        asset_digest, asset_file_count = snapshot_asset_digest(local_files_only=not allow_download)
        result = {
            "status": "PYTHIA_INTEGRATION_VALIDATED" if finite else "PYTHIA_INTEGRATION_REJECTED",
            "model": model_load_info(model, device=device, local_files_only=not allow_download).__dict__,
            "config_digest": config_digest(model),
            "model_asset_digest": asset_digest,
            "model_asset_file_count": asset_file_count,
            "tokenizer_vocab_size": len(tokenizer),
            "input_tokens": int(encoded["input_ids"].shape[1]),
            "logit_shape": list(outputs.logits.shape),
            "finite_logits": finite,
            "download_allowed": allow_download,
            "synthetic": False,
        }
    except (ModelDependencyError, OSError, RuntimeError, ValueError) as exc:
        result = {
            "status": "PYTHIA_INTEGRATION_BLOCKED",
            "reason_type": type(exc).__name__,
            "reason": str(exc),
            "download_allowed": allow_download,
            "synthetic": False,
        }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "model-smoke.json").write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    write_receipt(output_dir / "evidence-receipt.json", make_receipt(
        producer_kind="model_smoke", protocol="te-v0.6.0-pythia", status=str(result["status"]),
        model_revision_sha="bba6a464f54bbf08fc174cfb351d9794d58af21d", finite_logits=result.get("finite_logits", False),
        model_asset_digest=result.get("model_asset_digest"), model_asset_file_count=result.get("model_asset_file_count"),
    ))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/model-smoke")
    parser.add_argument("--download", action="store_true", help="permit the first official model download")
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    args = parser.parse_args()
    result = run(output_dir=args.output_dir, allow_download=args.download, device=args.device)
    print(json.dumps(result, sort_keys=True, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
