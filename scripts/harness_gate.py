#!/usr/bin/env python3
"""Evaluate readiness from registered immutable harness reports."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from vgta_eval.registry import read_jsonl, validate_registry
from experiments.harness.common import PROTOCOL


REQUIRED = ("dataset-leakage-audit", "shortcut-baselines", "random-label-control", "ontology-permutation-control", "sham-feature-control", "ground-truth-independence", "scenario-transformation-validation", "attack-discrimination", "calibration-validation", "verifier-property-validation", "verifier-mutation-validation", "verifier-differential-validation", "blind-evaluation-validation", "power-analysis")


def main() -> int:
    registry = ROOT / "results/registry"
    reports = validate_registry(registry / "reports.jsonl", identity_field="report_id") if (registry / "reports.jsonl").exists() else []
    latest: dict[str, dict] = {}
    for report in reports:
        if report.get("protocol_version") != PROTOCOL:
            continue
        current = latest.get(str(report.get("experiment_id")))
        if current is None or str(report.get("created_at", "")) > str(current.get("created_at", "")):
            latest[str(report.get("experiment_id"))] = report
    missing = [experiment for experiment in REQUIRED if experiment not in latest]
    failed = [experiment for experiment in REQUIRED if experiment in latest and not bool(latest[experiment].get("gate_passed"))]
    invalid = [experiment for experiment in REQUIRED if experiment in latest and latest[experiment].get("run_validity") != "valid"]
    if not missing and not failed and not invalid:
        print("HARNESS READY FOR CONFIRMATORY TRANSFORMER STUDY")
        return 0
    print("HARNESS NOT READY")
    if missing:
        print("\nMissing:")
        for item in missing:
            print(f"- {item}")
    if failed:
        print("\nFailed:")
        for item in failed:
            print(f"- {item}")
    if invalid:
        print("\nInvalid:")
        for item in invalid:
            print(f"- {item}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
