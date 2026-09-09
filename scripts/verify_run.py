#!/usr/bin/env python3
"""Verify one versioned run, analysis, report, and registry chain."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from experiments.harness.common import artifact_identity, dataset_root_for_manifest
from vgta_eval.reporting import sha256_file
from vgta_eval.registry import read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--experiment", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    raw = ROOT / "results/raw" / args.protocol / args.experiment / args.run_id
    manifest_path = raw / "run-manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"missing run manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset_root = dataset_root_for_manifest(manifest)
    expected = artifact_identity(dataset_root, str(manifest.get("protocol_version", args.protocol)))
    for manifest_key, expected_key in (("dataset", "dataset_sha256"), ("ontology", "ontology_sha256"), ("ground_truth", "ground_truth_sha256"), ("verifier", "verifier_sha256"), ("config", "config_sha256"), ("attack_suite", "attack_suite_sha256"), ("metric_suite", "metric_suite_sha256")):
        if manifest.get(manifest_key) != expected[expected_key]:
            raise SystemExit(f"hash mismatch for {manifest_key}")
    for relative, digest in manifest.get("raw_artifact_sha256", {}).items():
        path = raw / relative
        if not path.exists() or sha256_file(path) != digest:
            raise SystemExit(f"raw artifact hash mismatch: {path}")
    reports = [item for item in read_jsonl(ROOT / "results/registry/reports.jsonl") if item.get("protocol_version") == args.protocol and item.get("experiment_id") == args.experiment and item.get("run_id") == args.run_id]
    if not reports:
        raise SystemExit("no registered report for run")
    report = sorted(reports, key=lambda item: int(item.get("analysis_revision", 0)))[-1]
    report_manifest_path = ROOT / str(report["path"]).replace("experimental-validation-report.md", "report-manifest.json")
    report_manifest = json.loads(report_manifest_path.read_text(encoding="utf-8"))
    if "dataset_version" in report_manifest or "dataset_path" in report_manifest:
        if report_manifest.get("dataset_version") != dataset_root.name or report_manifest.get("dataset_path") != str(dataset_root.relative_to(ROOT)):
            raise SystemExit("report dataset identity does not match raw run")
    if report_manifest.get("raw_manifest_sha256") != sha256_file(manifest_path):
        raise SystemExit("report does not reference the current raw manifest")
    if report_manifest.get("run_id") != args.run_id or report_manifest.get("experiment_id") != args.experiment:
        raise SystemExit("report identity does not match requested run")
    print(f"VERIFIED RUN {args.protocol}/{args.experiment}/{args.run_id} -> {report_manifest['report_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
