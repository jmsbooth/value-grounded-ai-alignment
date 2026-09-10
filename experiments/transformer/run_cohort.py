#!/usr/bin/env python3
"""Locked cohort runner guard; full execution requires an explicit freeze."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt


def run(*, freeze_path: Path, output_dir: Path) -> dict[str, object]:
    reasons: list[str] = []
    if not freeze_path.exists():
        reasons.append("no frozen cohort plan")
    else:
        freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
        if freeze.get("status") != "COHORT_FROZEN":
            reasons.extend(freeze.get("reasons", []))
    result = {
        "protocol": "te-v0.6.0-pythia",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "LOCKED_RUN_NOT_STARTED" if reasons else "LOCKED_RUN_AUTHORIZED",
        "reasons": reasons,
        "execution": "not started" if reasons else "requires explicit launch of each frozen child run",
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cohort-run-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(output_dir / "cohort-run-receipt.json", make_receipt(producer_kind="gate", protocol="te-v0.6.0-pythia", status=str(result["status"]), reasons=reasons))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, default=ROOT / "results/plans/te-v0.6.0-pythia/freeze-result.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/raw/te-v0.6.0-pythia")
    args = parser.parse_args()
    result = run(freeze_path=args.freeze, output_dir=args.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

