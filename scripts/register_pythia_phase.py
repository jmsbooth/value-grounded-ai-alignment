#!/usr/bin/env python3
"""Register the bounded Pythia development phase in the append-only chain."""

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
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from vgta_eval.registry import append_unique, read_jsonl


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protocol_digest() -> str:
    digest = hashlib.sha256()
    root = ROOT / "experiments/protocols/te-v0.6.0-pythia"
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _append_if_absent(path: Path, record: dict, field: str) -> None:
    if not any(str(item.get(field)) == str(record.get(field)) for item in read_jsonl(path)):
        append_unique(path, record, identity_field=field)


def register(run_id: str) -> dict[str, str]:
    experiment_id = "pythia-phase-development"
    protocol = "te-v0.6.0-pythia"
    report_id = f"{protocol}__{experiment_id}__{run_id}__a001"
    run_key = f"{protocol}__{experiment_id}__{run_id}"
    report_source = ROOT / "results/reports/te-v0.6.0-pythia/phase-execution-report.md"
    analysis_source = ROOT / "results/reports/te-v0.6.0-pythia/analysis-development/analysis.json"
    raw_dir = ROOT / "results/raw" / protocol / experiment_id / run_id
    analysis_dir = ROOT / "results/analyses" / protocol / experiment_id / run_id / "analysis-r001"
    report_dir = ROOT / "results/reports" / protocol / experiment_id / run_id / "analysis-r001"
    raw_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    smoke = json.loads((ROOT / "results/reports/te-v0.6.0-pythia/model-smoke/model-smoke.json").read_text(encoding="utf-8"))
    preflight = json.loads((ROOT / "results/reports/te-v0.6.0-pythia/preflight/preflight.json").read_text(encoding="utf-8"))
    dataset_manifest = ROOT / "experiments/datasets/pythia-policy-dev-v1/manifest.json"
    run_manifest = {
        "run_key": run_key,
        "run_id": run_id,
        "protocol_version": protocol,
        "experiment_id": experiment_id,
        "created_at": created_at,
        "status": "development-only",
        "run_mode": "development",
        "evidence_status": "development-only",
        "dataset_version": "pythia-policy-dev-v1",
        "dataset_manifest_sha256": sha256(dataset_manifest),
        "config_sha256": protocol_digest(),
        "model_id": smoke.get("model", {}).get("model_id"),
        "model_revision_sha": smoke.get("model", {}).get("resolved_revision_sha"),
        "model_asset_digest": smoke.get("model_asset_digest"),
        "environment_digest": preflight.get("environment_digest"),
        "variants": ["pretrained-base-natural"],
        "seeds": [],
        "locked_comparison": False,
        "working_tree_clean": bool(preflight.get("repo", {}).get("worktree_clean")),
    }
    raw_manifest_path = raw_dir / "run-manifest.json"
    raw_manifest_path.write_text(json.dumps(run_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shutil.copy2(analysis_source, analysis_dir / "analysis.json")
    shutil.copy2(report_source, report_dir / "experimental-validation-report.md")
    report_manifest = {
        "report_id": report_id,
        "protocol_version": protocol,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "analysis_revision": 1,
        "created_at": created_at,
        "raw_manifest_sha256": sha256(raw_manifest_path),
    }
    (report_dir / "report-manifest.json").write_text(json.dumps(report_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    registry = ROOT / "results/registry"
    _append_if_absent(registry / "experiments.jsonl", {
        "experiment_id": experiment_id,
        "protocol_version": protocol,
        "research_question": "Can the reviewed Pythia integration execute the policy-grounded development path with traceable semantics and training diagnostics?",
        "status": "development",
        "created_at": created_at,
        "primary_metrics": ["response_parse_rate", "gradient_finiteness", "checkpoint_integrity"],
        "controls": ["semantic-validity-gate", "real-model-attack-execution"],
        "prerequisite_experiments": [],
    }, "experiment_id")
    _append_if_absent(registry / "runs.jsonl", run_manifest, "run_key")
    _append_if_absent(registry / "analyses.jsonl", {
        "analysis_id": f"{report_id}__analysis",
        "protocol_version": protocol,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "analysis_revision": 1,
        "report_id": report_id,
        "path": str(analysis_dir.relative_to(ROOT)),
        "prior_analysis": None,
        "created_at": created_at,
    }, "analysis_id")
    _append_if_absent(registry / "reports.jsonl", {
        **report_manifest,
        "git_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip(),
        "working_tree_clean": False,
        "working_tree_patch_sha256": None,
        "dataset_sha256": sha256(dataset_manifest),
        "ontology_sha256": None,
        "verifier_sha256": None,
        "config_sha256": protocol_digest(),
        "analysis_code_sha256": sha256(ROOT / "experiments/transformer/analyze.py"),
        "evidence_tier": "Transformer integration and development evidence",
        "status": "complete",
        "evidence_status": "development-only",
        "run_validity": "development",
        "gate_passed": False,
        "path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT)),
        "historical": False,
    }, "report_id")
    from experiments.harness.common import generate_registry_index
    generate_registry_index()
    return {"report_id": report_id, "run_key": run_key, "report_path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    print(json.dumps(register(args.run_id), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
