#!/usr/bin/env python3
"""Generate a convenience summary for reports created on a UTC date."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.registry import read_jsonl


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    args = parser.parse_args()
    reports = [item for item in read_jsonl(ROOT / "results/registry/reports.jsonl") if str(item.get("created_at", "")).startswith(args.date)]
    lines = [f"# Daily research summary — {args.date} UTC", "", f"{len(reports)} reports recorded. This is a convenience index, not a scientific evidence artifact.", "", "| Experiment | Protocol | Dataset | Run | Analysis | Status | Report |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for report in reports:
        lines.append(f"| `{report.get('experiment_id')}` | `{report.get('protocol_version')}` | `{report.get('dataset_version', 'unspecified')}` | `{report.get('run_id')}` | `a{int(report.get('analysis_revision', 0)):03d}` | `{report.get('evidence_status')}` | [{report.get('report_id')}]({ROOT / str(report.get('path', ''))}) |")
    output = ROOT / "results/daily" / f"{args.date}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
