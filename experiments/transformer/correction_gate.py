#!/usr/bin/env python3
"""Fail-closed, receipt-linked v0.6.2 correction gate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt

PROTOCOL = "te-v0.6.2-pythia-correction"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cohort = args.cohort.resolve()
    value = json.loads(cohort.read_text(encoding="utf-8"))
    if value.get("protocol") != PROTOCOL:
        raise ValueError("correction gate requires a v0.6.2 artifact")
    receipt_paths = [Path(item) for item in value.get("artifact_inventory", {}).get("receipts", [])]
    receipts = []
    for relative in receipt_paths:
        path = ROOT / relative
        if path.exists():
            receipts.append(json.loads(path.read_text(encoding="utf-8")))
    statuses = {str(receipt.get("status")) for receipt in receipts}
    gates = {
        "IMPLEMENTATION_CONTRACTS": "CORRECTION_IMPLEMENTATION_VALIDATED" in statuses,
        "EOS_REAL_TOKENIZER_AUDIT": value.get("work_package_status", {}).get("eos_real_tokenizer_audit") == "PASS",
        "INDEPENDENT_SCORING": value.get("work_package_status", {}).get("independent_scoring") == "PASS",
        "HISTORY_BOUNDARY_RECORDED": value.get("protected_history", {}).get("comparison") in {"MATCH", "pending-finalize"},
        "NO_LOCKED_DATA": value.get("locked_data_read_or_scored") is False,
        "NO_LOCKED_AUTHORIZATION": value.get("locked_cohort_authorized") is False,
    }
    gates["CORRECTION_IMPLEMENTATION_VALIDATED"] = all(gates[name] for name in ("IMPLEMENTATION_CONTRACTS", "EOS_REAL_TOKENIZER_AUDIT", "INDEPENDENT_SCORING", "HISTORY_BOUNDARY_RECORDED", "NO_LOCKED_DATA", "NO_LOCKED_AUTHORIZATION"))
    result = {"protocol": PROTOCOL, "experiment_id": "correction-gate", "status": "CORRECTION_IMPLEMENTATION_VALIDATED" if gates["CORRECTION_IMPLEMENTATION_VALIDATED"] else "DEVELOPMENT_RESOURCE_OR_EVIDENCE_INCOMPLETE", "gates": gates, "receipt_count": len(receipts), "receipt_statuses": sorted(statuses), "locked_cohort_authorized": False, "locked_data_read_or_scored": False, "next_decision": "No locked cohort execution. Resolve each missing receipt or resource block in a separately budgeted development phase."}
    output = (args.output or ROOT / "results/reports" / PROTOCOL / "correction-gate.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="gate", protocol=PROTOCOL, status=result["status"], experiment_id=result["experiment_id"], gate_sha256=sha256_file(output), receipt_count=len(receipts), locked_data_read_or_scored=False)
    write_receipt(output.parent / "correction-gate-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "gates": gates, "output": str(output.relative_to(ROOT)), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0 if gates["CORRECTION_IMPLEMENTATION_VALIDATED"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
