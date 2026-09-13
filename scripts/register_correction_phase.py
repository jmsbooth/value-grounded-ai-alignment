#!/usr/bin/env python3
"""Register one immutable v0.6.2 correction report chain."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from vgta_eval.registry import append_unique, read_jsonl
from vgta_eval.reporting import sha256_file

PROTOCOL = "te-v0.6.2-pythia-correction"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=list).encode()).hexdigest()


def append_if_missing(path: Path, record: dict, field: str) -> None:
    if any(str(item.get(field)) == str(record[field]) for item in read_jsonl(path)):
        return
    append_unique(path, record, identity_field=field)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: register_correction_phase.py path/to/correction-report.json", file=sys.stderr)
        return 2
    report_json = Path(sys.argv[1]).resolve()
    report_dir = report_json.parent
    markdown = report_dir / "experimental-validation-report.md"
    if not markdown.exists():
        raise FileNotFoundError(markdown)
    run_id = report_dir.parent.name
    report_id = f"{PROTOCOL}__correction-report__{run_id}__a001"
    created_at = datetime.now(timezone.utc).isoformat()
    raw_dir = ROOT / "results/raw" / PROTOCOL / "correction-report" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    try:
        source_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError:
        source_commit = "unknown"
    raw_manifest = raw_dir / "run-manifest.json"
    manifest = {"run_key": f"{PROTOCOL}__correction-report__{run_id}", "protocol_version": PROTOCOL, "experiment_id": "correction-report", "run_id": run_id, "source_commit": source_commit, "created_at": created_at, "cohort_path": json.loads(report_json.read_text(encoding="utf-8")).get("cohort_path"), "report_json": str(report_json.relative_to(ROOT)), "report_markdown": str(markdown.relative_to(ROOT)), "locked_data_read_or_scored": False, "locked_cohort_authorized": False}
    raw_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_manifest = {"report_id": report_id, "protocol_version": PROTOCOL, "experiment_id": "correction-report", "run_id": run_id, "analysis_revision": 1, "created_at": created_at, "raw_manifest_sha256": sha256_file(raw_manifest)}
    (report_dir / "report-manifest.json").write_text(json.dumps(report_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    registry = ROOT / "results/registry"
    append_if_missing(registry / "experiments.jsonl", {"experiment_id": "correction-report", "protocol_version": PROTOCOL, "research_question": "Did the Pythia harness corrections produce receipt-linked implementation and bounded development evidence without changing protected history?", "status": "development", "created_at": created_at, "primary_metrics": ["contract_validation", "eos_contract", "independent_scoring", "resource_cost", "strict_schema_validity"], "controls": ["tokenizer_audit", "auxiliary_isolation", "candidate_mutation", "clean_attack_pairing"], "prerequisite_experiments": ["pythia-phase-development"]}, "experiment_id")
    append_if_missing(registry / "runs.jsonl", {**manifest, "status": "development", "evidence_status": "development-only", "path": str(raw_dir.relative_to(ROOT)), "raw_manifest_sha256": sha256_file(raw_manifest)}, "run_key")
    append_if_missing(registry / "analyses.jsonl", {"analysis_id": f"{report_id}__analysis", "protocol_version": PROTOCOL, "experiment_id": "correction-report", "run_id": run_id, "analysis_revision": 1, "report_id": report_id, "path": str(report_dir.relative_to(ROOT)), "prior_analysis": None, "created_at": created_at}, "analysis_id")
    gate = ROOT / "results/reports" / PROTOCOL / "correction-gate.json"
    gate_data = json.loads(gate.read_text(encoding="utf-8")) if gate.exists() else {}
    append_if_missing(registry / "reports.jsonl", {**report_manifest, "git_sha": source_commit, "working_tree_clean": False, "working_tree_patch_sha256": None, "dataset_sha256": None, "ontology_sha256": None, "verifier_sha256": None, "config_sha256": digest(PROTOCOL), "analysis_code_sha256": sha256_file(ROOT / "experiments/transformer/correction_report.py"), "evidence_tier": "Transformer implementation and bounded development evidence", "status": "complete", "evidence_status": "development-only", "run_validity": "development", "gate_passed": bool(gate_data.get("gates", {}).get("CORRECTION_IMPLEMENTATION_VALIDATED", False)), "path": str(markdown.relative_to(ROOT)), "historical": False}, "report_id")
    from experiments.harness.common import generate_registry_index
    generate_registry_index()
    subprocess.run([sys.executable, str(ROOT / "scripts/verify_research_history.py")], cwd=ROOT, check=True)
    print(json.dumps({"status": "CORRECTION_PHASE_REGISTERED", "report_id": report_id, "report": str(markdown.relative_to(ROOT)), "raw_manifest": str(raw_manifest.relative_to(ROOT))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
