#!/usr/bin/env python3
"""Fail-closed cohort freeze requiring committed protocol state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt


def _git_status() -> list[str]:
    output = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=False).stdout
    return [line for line in output.splitlines() if line.strip()]


def freeze(plan_path: Path, output_dir: Path) -> dict[str, object]:
    reasons: list[str] = []
    if not plan_path.exists():
        reasons.append("cohort plan does not exist")
    dirty = _git_status()
    if dirty:
        reasons.append("worktree is not clean; protocol/config ownership is not committed")
    protocol_files = [ROOT / "experiments/protocols/te-v0.6.0-pythia/protocol.md", ROOT / "experiments/protocols/te-v0.6.0-pythia/gates.yaml"]
    for file_path in protocol_files:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(file_path.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True, check=False).returncode == 0
        if not tracked:
            reasons.append(f"protocol file is not tracked: {file_path.relative_to(ROOT)}")
    semantic_report = ROOT / "results/reports/te-v0.6.0-pythia/semantic-validity/semantic-audit.json"
    if not semantic_report.exists():
        reasons.append("semantic audit report is absent")
    else:
        semantic = json.loads(semantic_report.read_text(encoding="utf-8"))
        if semantic.get("status") != "SEMANTIC_DATASET_VALIDATED":
            reasons.append("semantic gate has not passed")
    result = {"protocol": "te-v0.6.0-pythia", "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "status": "COHORT_FROZEN" if not reasons else "COHORT_FREEZE_BLOCKED", "reasons": reasons, "plan": str(plan_path.relative_to(ROOT)) if plan_path.is_relative_to(ROOT) else str(plan_path), "worktree_clean": not dirty}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "freeze-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(output_dir / "freeze-receipt.json", make_receipt(producer_kind="gate", protocol="te-v0.6.0-pythia", status=str(result["status"]), reasons=reasons))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=ROOT / "results/plans/te-v0.6.0-pythia/cohort-plan.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/plans/te-v0.6.0-pythia")
    args = parser.parse_args()
    result = freeze(args.plan, args.output_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

