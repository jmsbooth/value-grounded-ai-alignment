#!/usr/bin/env python3
"""Compare protected v0.6.2 preflight hashes and write the final state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from preflight_correction import collect


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/experiments/te-v0.6.2-pythia-correction")
    args = parser.parse_args()
    preflight_path = args.output_dir / "preflight.json"
    before = json.loads(preflight_path.read_text(encoding="utf-8"))
    after = collect()
    paper_match = before["protected"]["paper"] == after["protected"]["paper"]
    historical_match = before["protected"]["historical"] == after["protected"]["historical"]
    comparison = "MATCH" if paper_match and historical_match else "MISMATCH"
    state = {"protocol": "te-v0.6.2-pythia-correction", "finalized_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "status": "CORRECTION_IMPLEMENTATION_VALIDATED" if comparison == "MATCH" else "PROTECTED_HISTORY_MISMATCH", "protected_history_comparison": comparison, "paper_hashes_unchanged": paper_match, "historical_hashes_unchanged": historical_match, "end_paper_tree_digest": after["protected"]["paper_tree_digest"], "end_historical_tree_digests": after["protected"]["historical_tree_digests"], "locked_data_read_or_scored": False, "locked_cohort_authorized": False, "next_decision": "No locked execution; human review is required after all development evidence and unresolved resource limits are considered."}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "final-state.json"
    output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    handoff = args.output_dir / "outcome-and-handoff.md"
    handoff.write_text(f"""# v0.6.2 outcome and handoff

Final state: `{state['status']}`  
Protected manuscript/history comparison: `{comparison}`  
Paper hashes unchanged: `{paper_match}`  
Historical v0.6.1 hashes unchanged: `{historical_match}`

The phase separates implementation-contract validation from bounded Pythia
development results. Full 32-update/two-seed/eight-arm execution is not
inferred from partial canaries; any missing or resource-blocked run remains
explicit in the correction report. Calibration and capability are
`NOT_MEASURED` unless an executed artifact says otherwise. The benchmark and
oracle are fictional project-authored fixtures, not external normative truth.

No locked cohort is authorized by this phase. The next decision is human
review of the receipt-linked correction report and a separately budgeted
development plan if the resource boundary requires more work.
""", encoding="utf-8")
    receipt = make_receipt(producer_kind="preflight", protocol=state["protocol"], status=state["status"], final_state_sha256=sha256_file(output), protected_history_comparison=comparison, locked_data_read_or_scored=False)
    write_receipt(args.output_dir / "final-state-receipt.json", receipt)
    receipt_files = []
    for receipt_root in (ROOT / "results/raw/te-v0.6.2-pythia-correction", ROOT / "results/reports/te-v0.6.2-pythia-correction", ROOT / "docs/experiments/te-v0.6.2-pythia-correction"):
        if receipt_root.exists():
            receipt_files.extend(receipt_root.rglob("*receipt.json"))
    receipt_files = sorted(set(receipt_files))
    receipts = []
    for path in receipt_files:
        try:
            receipts.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            continue
    def evidence(statuses: set[str], path_hint: str | None = None) -> tuple[str, str, str]:
        candidates = [(path, receipt) for path, receipt in receipts if receipt.get("status") in statuses and (path_hint is None or path_hint in str(path))]
        for path, receipt in reversed(candidates):
            if receipt.get("status") in statuses:
                return (str(path.relative_to(ROOT)), str(receipt.get("receipt_digest")), "PASS")
        return ("pending", "pending", "PENDING")
    trace_rows = [
        ("F01", "response_contract.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F02", "test_variant_correction.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F03", "test_variant_correction.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F04", "corrected_variant_smoke.py", {"CORRECTED_VARIANT_SMOKE_COMPLETE"}, "corrected-variant-smoke"),
        ("F05", "auxiliary_isolation_correction.py", {"AUXILIARY_ISOLATION_ACTUAL_PYTHIA", "AUXILIARY_ISOLATION_TINY"}, "auxiliary-isolation"),
        ("F06", "candidate_evaluator.py", {"INDEPENDENT_SCORING_VALIDATED"}, "independent-scoring"),
        ("F07", "training.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F08", "training.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F09", ".github/workflows/transformer-contracts.yml", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "contract-tests"),
        ("F10", "correction_gate.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "correction-gate"),
        ("EOS", "audit_eos_correction.py", {"EOS_REAL_TOKENIZER_AUDIT_COMPLETE"}, "eos-tokenizer-audit"),
        ("RESOURCE", "resource_profile_correction.py", {"COMMON_RESOURCE_PROFILE_MEASURED"}, "common-resource-profile"),
        ("HISTORY", "finalize_correction.py", {"CORRECTION_IMPLEMENTATION_VALIDATED"}, "final-state"),
    ]
    trace_lines = ["# v0.6.2 requirement traceability", "", "Statuses are tied to receipt digests; missing model runs remain explicit and do not become passes.", "", "| Requirement | Implementation path | Receipt | Receipt hash | Status |", "|---|---|---|---|---|"]
    for key, implementation, statuses, path_hint in trace_rows:
        path, receipt_digest, status = evidence(statuses, path_hint)
        trace_lines.append(f"| {key} | `{implementation}` | `{path}` | `{receipt_digest}` | `{status}` |" )
    trace_lines.extend(["", "The actual Pythia memorization, A1, variant-smoke, and clean/attack artifacts are listed in the correction report. A partial canary is not substituted for the full declared matrix.", ""])
    (args.output_dir / "requirement-traceability.md").write_text("\n".join(trace_lines), encoding="utf-8")
    print(json.dumps({"status": state["status"], "comparison": comparison, "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0 if comparison == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
