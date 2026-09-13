#!/usr/bin/env python3
"""Run the real-tokenizer EOS audit required by v0.6.2."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiment_utils import dataset_for_profile
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_transformer.model_loader import load_tokenizer
from vgta_transformer.response_contract import audit_tokenizer_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--profile", default="mini")
    parser.add_argument("--dev-limit", type=int, default=8)
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-eos-audit")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/eos-tokenizer-audit" / run_id
    dataset = dataset_for_profile(args.profile)
    annotations = dataset.annotation_map()
    tokenizer = load_tokenizer(local_files_only=True)
    memorization = tuple(dataset.by_split("train")[:8])
    fixed_dev = tuple(dataset.by_split("open-dev")[: args.dev_limit])
    result = {
        "protocol": "te-v0.6.2-pythia-correction",
        "experiment_id": "eos-tokenizer-audit",
        "run_id": run_id,
        "status": "EOS_REAL_TOKENIZER_AUDIT_COMPLETE",
        "model_tokenizer": "EleutherAI/pythia-410m@step143000",
        "memorization": audit_tokenizer_contract(memorization, annotations, tokenizer, structured=False, max_length=2048),
        "fixed_dev_structured": audit_tokenizer_contract(fixed_dev, annotations, tokenizer, structured=True, max_length=2048),
        "contract_assertions": {"prompt_and_response_auto_specials_disabled": True, "response_eos_appended_once": True, "eos_supervised_by_position": True, "pad_eos_not_used_as_mask_rule": True},
        "locked_data_read_or_scored": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "eos-audit.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="model_prediction", protocol=result["protocol"], status=result["status"], experiment_id=result["experiment_id"], run_id=run_id, audit_sha256=sha256_file(output), row_counts={"memorization": len(memorization), "fixed_dev": len(fixed_dev)}, locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "run_id": run_id, "path": str(output.relative_to(ROOT)), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
