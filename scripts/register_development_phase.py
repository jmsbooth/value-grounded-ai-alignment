#!/usr/bin/env python3
"""Register one immutable v0.6.1 development-summary report chain."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.registry import append_unique, read_jsonl
from vgta_eval.evidence_receipts import make_receipt, write_receipt


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(file.relative_to(path)).encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()


def append_if_absent(path: Path, record: dict, field: str) -> None:
    if not any(str(item.get(field)) == str(record.get(field)) for item in read_jsonl(path)):
        append_unique(path, record, identity_field=field)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--readiness", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, default=ROOT / "docs/experiments/te-v0.6.1-pythia-development/preflight.json")
    parser.add_argument("--final-state", type=Path, default=ROOT / "docs/experiments/te-v0.6.1-pythia-development/final-state.json")
    args = parser.parse_args()
    for name in ("report", "analysis", "readiness", "preflight", "final_state"):
        setattr(args, name, getattr(args, name).resolve())
    protocol = "te-v0.6.1-pythia-development"
    experiment = "development-summary"
    raw_dir = ROOT / "results/raw" / protocol / experiment / args.run_id
    analysis_dir = ROOT / "results/analyses" / protocol / experiment / args.run_id / "analysis-r001"
    report_dir = ROOT / "results/reports" / protocol / experiment / args.run_id / "analysis-r001"
    raw_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.analysis, analysis_dir / "analysis.json")
    shutil.copy2(args.report, report_dir / "experimental-validation-report.md")
    preflight = json.loads(args.preflight.read_text(encoding="utf-8"))
    final = json.loads(args.final_state.read_text(encoding="utf-8"))
    readiness = json.loads(args.readiness.read_text(encoding="utf-8"))
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    source_files = preflight.get("source_inventory", {}).get("files", {})
    manifest = {
        "run_key": f"{protocol}__{experiment}__{args.run_id}", "run_id": args.run_id, "protocol_version": protocol, "experiment_id": experiment, "created_at": created_at,
        "lifecycle_status": "completed", "validity": "development", "outcome": readiness.get("status"), "missing_work": [name for name, passed in readiness.get("gates", {}).items() if not passed],
        "source_commit": preflight.get("repo", {}).get("head"), "dirty_patch_sha256": preflight.get("repo", {}).get("dirty_patch_sha256"), "untracked_source_manifest_sha256": preflight.get("source_inventory", {}).get("untracked_source_manifest_sha256"), "source_files": source_files,
        "environment_lock_hash": preflight.get("environment", {}).get("environment_digest"), "actual_environment_receipt": preflight.get("environment"), "base_model_revision": preflight.get("current_model", {}).get("resolved_revision_sha"), "model_asset_digest": preflight.get("current_model", {}).get("asset_digest"),
        "dataset_id": "pythia-policy-dev-v2", "dataset_manifest_sha256": sha(ROOT / "experiments/datasets/pythia-policy-dev-v2/manifest.json"), "input_contract_hash": sha(ROOT / "experiments/protocols/te-v0.6.1-pythia-development/input-contracts.yaml"), "response_schema_hash": sha(ROOT / "experiments/protocols/te-v0.6.1-pythia-development/response-schema.json"), "protocol_content_hash": tree_digest(ROOT / "experiments/protocols/te-v0.6.1-pythia-development"),
        "resource_budget": preflight.get("budget"), "protected_paper_tree_start": preflight.get("protected_paper_tree", {}).get("tree_digest"), "protected_paper_tree_end": final.get("end_paper_tree_digest"), "locked_comparison": False, "locked_data_read_or_scored": False,
        "readiness_path": str(args.readiness.relative_to(ROOT)), "report_path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT)),
    }
    raw_manifest = raw_dir / "run-manifest.json"
    raw_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_id = f"{protocol}__{experiment}__{args.run_id}__a001"
    report_manifest = {"report_id": report_id, "protocol_version": protocol, "experiment_id": experiment, "run_id": args.run_id, "analysis_revision": 1, "created_at": created_at, "raw_manifest_sha256": sha(raw_manifest)}
    (report_dir / "report-manifest.json").write_text(json.dumps(report_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(raw_dir / "evidence-receipt.json", make_receipt(
        producer_kind="analysis",
        protocol=protocol,
        status=str(readiness.get("status")),
        run_manifest_sha256=sha(raw_manifest),
        analysis_sha256=sha(analysis_dir / "analysis.json"),
        report_sha256=sha(report_dir / "experimental-validation-report.md"),
        readiness_path=str(args.readiness.relative_to(ROOT)),
        locked_data_read_or_scored=False,
    ))
    registry = ROOT / "results/registry"
    append_if_absent(registry / "experiments.jsonl", {"experiment_id": experiment, "protocol_version": protocol, "research_question": "Can the v0.6.1 Pythia task-training and matched-control path execute with valid output contracts and measured local resources?", "status": "development", "created_at": created_at, "primary_metrics": ["strict_schema_validity", "response_nll", "task_correctness", "resource_cost"], "controls": ["a1-memorization", "auxiliary-gradient-isolation", "eight-arm-smoke", "clean-attack-pairing"], "prerequisite_experiments": ["pythia-phase-development"]}, "experiment_id")
    append_if_absent(registry / "runs.jsonl", manifest, "run_key")
    append_if_absent(registry / "analyses.jsonl", {"analysis_id": f"{report_id}__analysis", "protocol_version": protocol, "experiment_id": experiment, "run_id": args.run_id, "analysis_revision": 1, "report_id": report_id, "path": str((analysis_dir / "analysis.json").relative_to(ROOT)), "prior_analysis": None, "created_at": created_at}, "analysis_id")
    append_if_absent(registry / "reports.jsonl", {**report_manifest, "git_sha": manifest["source_commit"], "working_tree_clean": False, "working_tree_patch_sha256": manifest["dirty_patch_sha256"], "dataset_sha256": manifest["dataset_manifest_sha256"], "ontology_sha256": None, "verifier_sha256": None, "config_sha256": manifest["protocol_content_hash"], "analysis_code_sha256": sha(ROOT / "experiments/transformer/analyze_dev.py"), "evidence_tier": "Transformer development and implementation evidence", "status": "complete", "evidence_status": "development-only", "run_validity": "development", "gate_passed": bool(readiness.get("gates", {}).get("DEVELOPMENT_READY_FOR_COHORT_REVIEW")), "path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT)), "historical": False}, "report_id")
    from experiments.harness.common import generate_registry_index
    generate_registry_index()
    subprocess.run([sys.executable, str(ROOT / "scripts/verify_research_history.py")], cwd=ROOT, check=True)
    print(json.dumps({"report_id": report_id, "run_key": manifest["run_key"], "path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
