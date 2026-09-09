#!/usr/bin/env python3
"""Compare two immutable report manifests without merging their evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.run_identity import new_run_id


def _manifest(value: str) -> tuple[Path, dict]:
    path = Path(value)
    if path.is_dir():
        path = path / "report-manifest.json"
    elif path.name == "experimental-validation-report.md":
        path = path.parent / "report-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return path, data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_a")
    parser.add_argument("report_b")
    args = parser.parse_args()
    path_a, a = _manifest(args.report_a)
    path_b, b = _manifest(args.report_b)
    comparison_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{new_run_id().rsplit('-', 1)[1]}"
    fields = ("protocol_version", "experiment_id", "run_id", "analysis_revision", "dataset_version", "dataset_path", "dataset_sha256", "ground_truth_sha256", "ontology_sha256", "verifier_sha256", "config_sha256", "attack_suite_sha256", "metric_suite_sha256", "analysis_code_sha256", "evidence_tier", "status", "working_tree_clean")
    lines = [f"# Research report comparison — {comparison_id}", "", f"Report A: `{a.get('report_id')}` (`{path_a.relative_to(ROOT) if path_a.is_relative_to(ROOT) else path_a}`)", f"Report B: `{b.get('report_id')}` (`{path_b.relative_to(ROOT) if path_b.is_relative_to(ROOT) else path_b}`)", "", "| Field | Report A | Report B | Equal |", "| --- | --- | --- | --- |"]
    for field in fields:
        left, right = a.get(field), b.get(field)
        lines.append(f"| `{field}` | `{left}` | `{right}` | `{left == right}` |")
    lines.extend(["", "The comparison is a navigation artifact; neither report is modified or superseded by this file.", ""])
    output = ROOT / "results/comparisons" / f"{comparison_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
