#!/usr/bin/env python3
"""Register the preserved v0.3 pilot without changing its raw contents."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.harness.common import REGISTRY_ROOT, generate_registry_index
from vgta_eval.registry import append_unique, read_jsonl
from vgta_eval.reporting import sha256_file


def _append_if_absent(path: Path, record: dict, field: str) -> None:
    if not any(str(item.get(field)) == str(record.get(field)) for item in read_jsonl(path)):
        append_unique(path, record, identity_field=field)


def main() -> int:
    raw_root = ROOT / "results/raw/empirical-small-20260908T222325Z"
    group_manifest_path = raw_root / "group-manifest.json"
    report_path = ROOT / "results/reports/experimental-validation-report.md"
    group = json.loads(group_manifest_path.read_text(encoding="utf-8"))
    created = group.get("created_at", datetime.now(timezone.utc).isoformat())
    protocol = "pilot-v0.3"
    experiment = "shared-mlp-gate1"
    run_id = "empirical-small-20260908T222325Z"
    # The historical pilot predates the v0.5 run-ID grammar; preserve its
    # original run identity and wrap it in the new report naming convention.
    report_id = f"{protocol}__{experiment}__{run_id}__a001"
    REGISTRY_ROOT.mkdir(parents=True, exist_ok=True)
    _append_if_absent(REGISTRY_ROOT / "experiments.jsonl", {"experiment_id": experiment, "protocol_version": protocol, "research_question": "Historical shared-MLP mechanism-validation pilot", "status": "historical", "created_at": created, "primary_metrics": ["moral_salience_recall", "normative_conflict_f1", "structural_ood_accuracy", "useful_conformance_rate"], "controls": ["A1", "B", "C1", "C2"], "prerequisite_experiments": []}, "experiment_id")
    _append_if_absent(REGISTRY_ROOT / "runs.jsonl", {"run_key": f"{protocol}__{experiment}__{run_id}", "protocol_version": protocol, "experiment_id": experiment, "run_id": run_id, "status": "historical", "evidence_status": "development-only", "path": str(raw_root.relative_to(ROOT)), "raw_manifest_sha256": sha256_file(group_manifest_path), "git_sha": group.get("git_sha", "unknown"), "dataset_version": "v0.3-small", "seeds": group.get("seeds", []), "variants": group.get("variants", [])}, "run_key")
    _append_if_absent(REGISTRY_ROOT / "analyses.jsonl", {"analysis_id": f"{report_id}__analysis", "protocol_version": protocol, "experiment_id": experiment, "run_id": run_id, "analysis_revision": 1, "report_id": report_id, "path": str(report_path.relative_to(ROOT)), "prior_analysis": None, "created_at": created}, "analysis_id")
    _append_if_absent(REGISTRY_ROOT / "reports.jsonl", {"report_id": report_id, "protocol_version": protocol, "experiment_id": experiment, "run_id": run_id, "analysis_revision": 1, "created_at": created, "git_sha": group.get("git_sha", "unknown"), "working_tree_clean": False, "working_tree_patch_sha256": None, "dataset_sha256": group.get("dataset_manifest", {}).get("split_hashes", {}).get("sealed-test"), "ontology_sha256": None, "verifier_sha256": None, "config_sha256": group.get("config_sha"), "analysis_code_sha256": None, "raw_manifest_sha256": sha256_file(group_manifest_path), "evidence_tier": "Tier 1 synthetic mechanism evidence", "status": "historical", "evidence_status": "development-only", "run_validity": "historical", "gate_passed": False, "path": str(report_path.relative_to(ROOT)), "historical": True}, "report_id")
    generate_registry_index()
    print(json.dumps({"registered": report_id, "raw_preserved": True, "report": str(report_path.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
