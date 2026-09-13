#!/usr/bin/env python3
"""Assemble an artifact-linked v0.6.2 correction report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt

PROTOCOL = "te-v0.6.2-pythia-correction"
RAW_ROOT = ROOT / "results/raw" / PROTOCOL


def digest(path: Path) -> str:
    value = hashlib.sha256()
    for item in sorted(path.rglob("*")) if path.is_dir() else [path]:
        if item.is_file():
            value.update(str(item.relative_to(path if path.is_dir() else item.parent)).encode())
            value.update(item.read_bytes())
    return value.hexdigest()


def find_files(name: str, path_hint: str | None = None) -> list[str]:
    paths = sorted(RAW_ROOT.rglob(name)) if RAW_ROOT.exists() else []
    if path_hint is not None:
        paths = [path for path in paths if path_hint in str(path)]
    return [str(path.relative_to(ROOT)) for path in paths]


def latest_receipt(statuses: set[str], path_hint: str | None = None) -> str | None:
    candidates = []
    for relative in find_files("evidence-receipt.json", path_hint):
        path = ROOT / relative
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if receipt.get("status") in statuses:
            candidates.append((str(receipt.get("created_at", "")), relative))
    return max(candidates)[1] if candidates else None


def evidence_for_package(name: str, state: str) -> str:
    receipt_map = {
        "implementation_contracts": latest_receipt({"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        "eos_real_tokenizer_audit": latest_receipt({"EOS_REAL_TOKENIZER_AUDIT_COMPLETE"}, "eos-tokenizer-audit"),
        "independent_scoring": latest_receipt({"INDEPENDENT_SCORING_VALIDATED"}, "independent-scoring"),
        "actual_auxiliary_isolation": latest_receipt({"AUXILIARY_ISOLATION_ACTUAL_PYTHIA", "AUXILIARY_ISOLATION_TINY"}, "auxiliary-isolation"),
        "common_resource_profile": latest_receipt({"COMMON_RESOURCE_PROFILE_MEASURED"}, "common-resource-profile"),
        "clean_attack_evaluation": latest_receipt({"CORRECTED_CLEAN_ATTACK_EVALUATION_COMPLETE"}, "clean-attack-evaluation"),
    }
    if name in receipt_map and receipt_map[name]:
        return str(receipt_map[name])
    if name == "corrected_model_results":
        paths = find_files("run-summary.json")
        return ", ".join(paths) if paths else "not recorded"
    if state == "NOT_MEASURED":
        return "not measured; no artifact"
    return "recorded; no dedicated receipt"


def status_for(name: str, expected_status: str | None = None) -> str:
    paths = find_files(name)
    if not paths:
        return "NOT_MEASURED"
    if expected_status is None:
        return "RECORDED"
    for path in paths:
        try:
            value = json.loads((ROOT / path).read_text(encoding="utf-8"))
            if value.get("status") == expected_status:
                return "PASS"
        except (OSError, json.JSONDecodeError):
            continue
    return "RECORDED"


def build_report(cohort: Path) -> dict[str, object]:
    preflight = ROOT / "docs/experiments/te-v0.6.2-pythia-correction/preflight.json"
    cohort = cohort.resolve()
    cohort_data = json.loads(cohort.read_text(encoding="utf-8"))
    receipts = find_files("evidence-receipt.json")
    defects = {
        "F01": {"reproducer": "auto-special tokenizer path and missing explicit EOS", "correction": "response_contract explicit EOS", "test_or_run": "tests/transformer/test_response_contract.py", "residual": "real Pythia model training outcome remains development evidence only"},
        "F02": {"reproducer": "B-TEXT-A plan used natural input", "correction": "exact-b-structured plus salient_values/relation_class span weights", "test_or_run": "tests/transformer/test_variant_correction.py", "residual": "model effect not isolated by this contract test"},
        "F03": {"reproducer": "C1-TEXT-N had no normative span weighting", "correction": "applicable_norm_ids/conflict_class span weights", "test_or_run": "tests/transformer/test_variant_correction.py", "residual": "model effect not isolated by this contract test"},
        "F04": {"reproducer": "sham path could permute all auxiliary targets", "correction": "declared intended target arrays only", "test_or_run": "tests/transformer/test_variant_correction.py", "residual": "permutation receipt requires a smoke attempt"},
        "F05": {"reproducer": "response loss included in auxiliary diagnostic", "correction": "auxiliary-only and detach/disabled-head diagnostics", "test_or_run": "experiments/transformer/auxiliary_isolation_correction.py", "residual": "actual Pythia status depends on measured receipt"},
        "F06": {"reproducer": "model booleans and literal reference score used", "correction": "candidate-evaluator-v1 and model-claim separation", "test_or_run": "tests/transformer/test_independent_scoring.py", "residual": "fictional project oracle is not external normative ground truth"},
        "F07": {"reproducer": "physical batch and A1 accumulation differed", "correction": "one-example microbatch global denominators", "test_or_run": "tests/transformer/test_accumulation.py", "residual": "full Pythia schedule is resource-bounded"},
        "F08": {"reproducer": "allocated count included frozen parameters", "correction": "parameter_accounting categories", "test_or_run": "tests/transformer/test_parameter_accounting.py", "residual": "changed-parameter count is available after a training update"},
        "F09": {"reproducer": "paper path and Transformer coverage were incomplete", "correction": "paper working directory and CPU workflow", "test_or_run": ".github/workflows/paper.yml and .github/workflows/transformer-contracts.yml", "residual": "remote CI result is not available locally"},
        "F10": {"reproducer": "readiness relied on names/counts/booleans", "correction": "report/gate require receipt-linked artifacts", "test_or_run": "experiments/transformer/correction_gate.py", "residual": "no locked cohort authorization"},
    }
    implementation = status_for("result.json", "CORRECTION_IMPLEMENTATION_VALIDATED")
    final_state = ROOT / "docs/experiments/te-v0.6.2-pythia-correction/final-state.json"
    final_state_data = json.loads(final_state.read_text(encoding="utf-8")) if final_state.exists() else {}
    result = {
        "protocol": PROTOCOL,
        "experiment_id": "correction-report",
        "status": "CORRECTION_REPORT_RECORDED",
        "cohort_path": str(cohort.relative_to(ROOT)),
        "cohort": cohort_data,
        "defects": defects,
        "artifact_inventory": {"receipts": receipts, "eos_audits": find_files("eos-audit.json"), "independent_scoring": find_files("result.json", "independent-scoring"), "resource_profiles": find_files("resource-profile.json"), "predictions": find_files("predictions.jsonl"), "checkpoints": find_files("checksums.json"), "contract_tests": find_files("result.json", "contract-tests")},
        "work_package_status": {"implementation_contracts": implementation, "eos_real_tokenizer_audit": status_for("eos-audit.json", "EOS_REAL_TOKENIZER_AUDIT_COMPLETE"), "independent_scoring": status_for("result.json", "INDEPENDENT_SCORING_VALIDATED"), "actual_auxiliary_isolation": status_for("result.json", "AUXILIARY_ISOLATION_ACTUAL_PYTHIA"), "common_resource_profile": status_for("resource-profile.json", "COMMON_RESOURCE_PROFILE_MEASURED"), "corrected_model_results": "RECORDED" if find_files("run-summary.json") else "NOT_MEASURED", "clean_attack_evaluation": status_for("result.json", "CORRECTED_CLEAN_ATTACK_EVALUATION_COMPLETE"), "calibration": "NOT_MEASURED", "capability_sentinel": "NOT_MEASURED"},
        "protected_history": {"preflight_path": str(preflight.relative_to(ROOT)) if preflight.exists() else "MISSING", "preflight_sha256": hashlib.sha256(preflight.read_bytes()).hexdigest() if preflight.exists() else None, "final_state_path": str(final_state.relative_to(ROOT)) if final_state.exists() else "MISSING", "comparison": final_state_data.get("protected_history_comparison", "pending-finalize")},
        "resources_and_next_cohort": "Use only measured B/C2 longest-input cost and explicitly budget fresh processes; no locked estimate is inferred from a partial run.",
        "scientific_boundary": "Synthetic fictional benchmark and project oracle only; no alignment, moral-truth, safety, or population-generalization claim.",
        "locked_cohort_authorized": False,
        "locked_data_read_or_scored": False,
        "next_decision": "Review the receipt-linked correction gate. If any engineering or resource gate is missing, open a separately budgeted development attempt; do not run a locked cohort.",
    }
    lines = ["# v0.6.2 Pythia correction and bounded retest report", "", "This report is artifact-linked and conservative. It distinguishes contract validation from actual Pythia development-model evidence. The manuscript, historical predictions, reports, generated assets, and locked data remain outside this phase's write/scoring boundary.", "", f"Cohort input: `{cohort.relative_to(ROOT)}`", "", "## Work packages", "", "| Work package | State | Evidence |", "|---|---|---|"]
    for name, state in result["work_package_status"].items():
        lines.append(f"| {name} | `{state}` | `{evidence_for_package(name, state)}` |" )
    lines.extend(["", "## F01-F10 defect ledger", "", "| ID | Correction | Test/run | Residual boundary |", "|---|---|---|---|"])
    for key, value in defects.items():
        lines.append(f"| {key} | {value['correction']} | `{value['test_or_run']}` | {value['residual']} |" )
    lines.extend(["", "## Claims and handoff", "", "Calibration and capability-sentinel results are `NOT_MEASURED` unless an artifact is listed. Clean/attack results must use independent evaluator fields and actual denominators; no literal reference score is accepted. The possible handoff remains development-only and does not authorize `te-freeze-cohort` or `te-run-cohort`.", ""])
    result["markdown"] = "\n".join(lines)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-correction-report")
    output_dir = args.output_dir or ROOT / "results/reports" / PROTOCOL / "correction-summary" / run_id / "analysis-r001"
    result = build_report(args.cohort)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = output_dir / "correction-report.json"
    report.write_text(json.dumps({key: value for key, value in result.items() if key != "markdown"}, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    markdown = output_dir / "experimental-validation-report.md"
    markdown.write_text(result["markdown"], encoding="utf-8")
    receipt = make_receipt(producer_kind="analysis", protocol=PROTOCOL, status=result["status"], experiment_id=result["experiment_id"], run_id=run_id, report_sha256=sha256_file(markdown), json_sha256=sha256_file(report), locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "run_id": run_id, "report": str(markdown.relative_to(ROOT)), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
