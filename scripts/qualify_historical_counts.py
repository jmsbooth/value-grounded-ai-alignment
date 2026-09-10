#!/usr/bin/env python3
"""Append an auditable qualification for the historical pilot count wording.

The original report is intentionally not edited. This script creates a
versioned correction that reconciles raw rows by split, variant, family, and
transform and appends a separate qualification event to the registry.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import canonical_digest, make_receipt, write_receipt
from vgta_eval.registry import append_unique


RUN_ROOT = ROOT / "results/raw/empirical-small-20260908T222325Z"
REPORT_ROOT = ROOT / "results/reports/historical-qualification/mlp-count-reconciliation"
REGISTRY = ROOT / "results/registry/qualifications.jsonl"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qualify() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    files: list[str] = []
    for path in sorted(RUN_ROOT.glob("*/predictions.jsonl")):
        files.append(str(path.relative_to(ROOT)))
        rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    by_split = Counter(str(row["split"]) for row in rows)
    by_variant = Counter(str(row["variant"]) for row in rows)
    by_family = Counter(str(row["family"]) for row in rows)
    by_split_variant = Counter((str(row["split"]), str(row["variant"])) for row in rows)
    by_split_family = Counter((str(row["split"]), str(row["family"])) for row in rows)
    sealed_rows_per_run = by_split["sealed-test"] // (4 * 3)
    claimed_sealed = 4 * 3 * sealed_rows_per_run
    observed_total = len(rows)
    observed_sealed = by_split["sealed-test"]
    qualification_id = "historical-qualification__empirical-small-20260908T222325Z__count-reconciliation-v1"
    report = {
        "qualification_id": qualification_id,
        "qualification_version": "historical-count-reconciliation-v1",
        "source_run_group": "empirical-small-20260908T222325Z",
        "source_report": "results/reports/experimental-validation-report.md",
        "source_files": files,
        "observed_total_prediction_rows": observed_total,
        "observed_sealed_rows": observed_sealed,
        "original_sealed_only_claim": claimed_sealed,
        "claim_reconciliation": "The report's 1,140 aggregate is 12 runs across validation, development-test, and sealed-test (22 + 22 + 51 = 95 rows per run). The 612 value is the sealed-test-only subtotal (51 rows x 4 variants x 3 seeds).",
        "by_split": dict(sorted(by_split.items())),
        "by_variant": dict(sorted(by_variant.items())),
        "by_family": dict(sorted(by_family.items())),
        "by_split_variant": {f"{split}|{variant}": count for (split, variant), count in sorted(by_split_variant.items())},
        "by_split_family": {f"{split}|{family}": count for (split, family), count in sorted(by_split_family.items())},
        "evidence_boundary": "This qualifies historical accounting only; it does not change historical metrics, thresholds, or scientific conclusions.",
    }
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    (REPORT_ROOT / "count-reconciliation.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Historical pilot count reconciliation",
        "",
        "Status: qualification of accounting; historical source files are unchanged.",
        "",
        f"The raw group contains **{observed_total}** prediction rows across 12 runs. The sealed-test subtotal is **{observed_sealed}** rows. The previously stated 1,140 aggregate is therefore a whole-evaluation total, while 612 is the sealed-test-only subtotal.",
        "",
        "## Rows by split",
        "",
        "| Split | Rows |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{key}` | {value} |" for key, value in sorted(by_split.items()))
    lines.extend(["", "## Rows by split and variant", "", "| Split | Variant | Rows |", "| --- | --- | ---:|"])
    lines.extend(f"| `{split}` | `{variant}` | {value} |" for (split, variant), value in sorted(by_split_variant.items()))
    lines.extend(["", "## Scope", "", "The original report remains immutable. This qualification corrects interpretation only and does not promote the historical MLP experiment to Transformer or human-value evidence.", ""])
    (REPORT_ROOT / "count-reconciliation.md").write_text("\n".join(lines), encoding="utf-8")
    receipt = make_receipt(producer_kind="historical_qualification", protocol="te-v0.6.0-pythia", status="HISTORICAL_COUNT_QUALIFIED", source_run_group=report["source_run_group"], observed_total=observed_total, observed_sealed=observed_sealed, report_digest=canonical_digest(report))
    write_receipt(REPORT_ROOT / "evidence-receipt.json", receipt)
    event = {
        "registry_schema": "qualification-event-v1",
        "qualification_id": qualification_id,
        "event_type": "historical_qualification",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "protocol_version": "te-v0.6.0-pythia",
        "source_run_group": report["source_run_group"],
        "report_path": str((REPORT_ROOT / "count-reconciliation.md").relative_to(ROOT)),
        "status": "complete",
        "historical_files_unchanged": True,
        "report_sha256": _sha(REPORT_ROOT / "count-reconciliation.md"),
    }
    try:
        append_unique(REGISTRY, event, identity_field="qualification_id")
    except ValueError as exc:
        if "duplicate qualification_id" not in str(exc):
            raise
    return report


if __name__ == "__main__":
    print(json.dumps(qualify(), sort_keys=True))
