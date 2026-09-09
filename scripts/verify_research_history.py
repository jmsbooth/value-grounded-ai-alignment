#!/usr/bin/env python3
"""Validate registry uniqueness and existence of all versioned artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.registry import read_jsonl, validate_registry
from vgta_eval.reporting import sha256_file


def main() -> int:
    registry = ROOT / "results/registry"
    validate_registry(registry / "experiments.jsonl", identity_field="experiment_id")
    validate_registry(registry / "runs.jsonl", identity_field="run_key")
    validate_registry(registry / "analyses.jsonl", identity_field="analysis_id")
    reports = validate_registry(registry / "reports.jsonl", identity_field="report_id")
    checked = 0
    for report in reports:
        path = ROOT / str(report["path"])
        if not path.exists():
            raise SystemExit(f"missing registered report: {path}")
        if report.get("historical"):
            continue
        manifest_path = path.parent / "report-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("report_id") != report.get("report_id") or manifest.get("raw_manifest_sha256") is None:
            raise SystemExit(f"invalid report manifest: {manifest_path}")
        raw_manifest = ROOT / "results/raw" / str(manifest["protocol_version"]) / str(manifest["experiment_id"]) / str(manifest["run_id"]) / "run-manifest.json"
        if not raw_manifest.exists() or sha256_file(raw_manifest) != manifest.get("raw_manifest_sha256"):
            raise SystemExit(f"raw/report provenance mismatch: {path}")
        checked += 1
    print(f"VERIFIED RESEARCH HISTORY: {len(reports)} reports; {checked} versioned report chains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
