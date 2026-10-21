#!/usr/bin/env python3
"""Write an immutable scope-limited report from one verified evidence inventory.

No latest-receipt scans, status-only acceptance, or model-quality claims.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from vgta_eval.verified_inventory import EvidenceError, digest, read_json, verify_inventory


def write_json(path: Path, data: dict) -> None:
    with path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True, allow_nan=False)
        file.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--approved-plan-sha256", required=True)
    parser.add_argument("--scope", choices=("fixture", "canary", "development", "locked", "replication"), required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root, inventory = args.root.resolve(), args.inventory.resolve()
    try:
        if not inventory.is_relative_to(root):
            raise EvidenceError("inventory escapes evidence root")
        proof = verify_inventory(root, inventory, approved_plan_sha256=args.approved_plan_sha256, expected_scope=args.scope)
        inventory_doc = read_json(inventory)
        plan = read_json(root / inventory_doc["plan"]["path"])
        requirements = [{"role": r["role"], "producer_kind": r["producer_kind"],
                         "assertions_verified": len(r["assertions"])} for r in plan["requirements"]]
    except (EvidenceError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "EVIDENCE_REPORT_REJECTED", "reason": str(exc)}), file=sys.stderr)
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:10]
    output = (args.output_dir or root / "results/reports" / proof["protocol"] / "explicit-inventory" / run_id / "analysis-r001").resolve()
    if not output.is_relative_to(root):
        print("report output escapes evidence root", file=sys.stderr)
        return 1
    report = {
        "status": "EVIDENCE_REPORT_RECORDED", "scope": args.scope, "protocol": proof["protocol"],
        "report_run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
        "source_context": plan["context"], "inventory_path": str(inventory.relative_to(root)),
        "inventory_sha256": digest(inventory), "approved_plan_sha256": args.approved_plan_sha256,
        "verified_roles": proof["verified_roles"], "requirements": requirements,
        "required_role_count": len(requirements), "verified_role_count": len(proof["verified_roles"]),
        "source_file_count": len(plan["source_files"]), "protected_file_count": len(plan["protected_files"]),
        "locked_launch_authorized": False, "complete_model_protocol_run": False,
        "model_effectiveness_claim": "not_evaluated_by_evidence_reporting",
    }
    markdown = [
        "# Pythia explicit-inventory evidence report", "",
        f"Protocol: `{proof['protocol']}`  ", f"Scope: `{args.scope}`  ",
        f"Run: `{run_id}`  ", f"Plan SHA-256: `{args.approved_plan_sha256}`  ",
        f"Inventory SHA-256: `{report['inventory_sha256']}`", "",
        f"Verified **{len(proof['verified_roles'])}/{len(requirements)} roles specified by this exact plan**.",
        "This is artifact integrity evidence, **not** full-study completion, model performance, or permission to train.", "",
        "| Role | Producer kind | Checked assertions |", "|---|---|---:|",
    ]
    markdown += [f"| `{r['role']}` | `{r['producer_kind']}` | {r['assertions_verified']} |" for r in requirements]
    markdown += ["", "No receipt was selected by timestamp, directory search, or a PASS string.",
                 "Missing model runs, calibration, capabilities and attack outputs remain unmeasured unless separately verified.",
                 "The independently supplied plan hash is an input to review, not proof of owner approval.", ""]
    try:
        output.mkdir(parents=True, exist_ok=False)
        write_json(output / "report.json", report)
        with (output / "experimental-validation-report.md").open("x", encoding="utf-8") as file:
            file.write("\n".join(markdown))
        write_json(output / "report-manifest.json", {
            "status": report["status"], "report_run_id": run_id, "protocol": proof["protocol"],
            "scope": args.scope, "approved_plan_sha256": args.approved_plan_sha256,
            "inventory_sha256": digest(inventory), "report_json_sha256": digest(output / "report.json"),
            "report_markdown_sha256": digest(output / "experimental-validation-report.md"),
            "locked_launch_authorized": False,
        })
    except OSError as exc:
        print(json.dumps({"status": "EVIDENCE_REPORT_WRITE_REJECTED", "reason": str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"], "report_dir": str(output),
                      "verified_roles": len(proof["verified_roles"]), "locked_launch_authorized": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
