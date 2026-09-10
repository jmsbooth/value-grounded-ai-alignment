#!/usr/bin/env python3
"""Produce the structured v0.6.1 development gate without rerunning work."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read(path: Path) -> dict:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(*, preflight: Path, audit: Path, training: Path, dataset: Path, memorization: Path, a1: Path, variants: Path, resource: Path, attack: Path | None = None) -> dict[str, object]:
    p, o, t, d, m, a, v, r = (read(path) for path in (preflight, audit, training, dataset, memorization, a1, variants, resource))
    a1_attempts = a.get("attempts", [])
    variant_count = int(v.get("attempt_count", 0))
    a1_rows = [attempt.get("open_dev", {}) for attempt in a1_attempts]
    strict_rates = [float(row.get("strict_schema_rate", 0.0)) for row in a1_rows]
    gates = {
        "OUTPUT_PATH_AUDITED": o.get("status") == "HISTORICAL_GENERATIONS_AUDITED" and int(o.get("historical_row_count", 0)) == 5 and t.get("status") == "TRAINING_CONTRACT_VALIDATED",
        "TRAINING_CONTRACT_VALIDATED": t.get("status") == "TRAINING_CONTRACT_VALIDATED",
        "A1_MEMORIZATION_CRITERION_MET": any(attempt.get("status") == "A1_MEMORIZATION_CRITERION_MET" for attempt in m.get("attempts", [])),
        "DEVELOPMENT_BENCHMARK_VALIDATED": d.get("status") == "DEVELOPMENT_BENCHMARK_VALIDATED",
        "A1_DEVELOPMENT_TRAINING_COMPLETE": bool(a1_attempts) and all(attempt.get("status") == "A1_DEVELOPMENT_TRAINING_COMPLETE" for attempt in a1_attempts),
        "A1_FORMAT_READY": bool(strict_rates) and min(strict_rates) >= 0.90 and all(int(row.get("independent_groups", 0)) >= 16 for row in a1_rows),
        "AUXILIARY_BACKPROP_VALIDATED": t.get("status") == "TRAINING_CONTRACT_VALIDATED",
        "VARIANT_SMOKE_COMPLETE": v.get("status") == "VARIANT_SMOKE_COMPLETE" and variant_count == 16 and all(bool(attempt.get("checkpoint", {}).get("verified")) for attempt in v.get("attempts", [])),
        "RESOURCE_PLAN_MEASURED": r.get("status") == "RESOURCE_PROFILE_MEASURED" and bool(r.get("checkpoint", {}).get("roundtrip_verified")),
    }
    gates["DEVELOPMENT_READY_FOR_COHORT_REVIEW"] = all(gates[name] for name in ("OUTPUT_PATH_AUDITED", "TRAINING_CONTRACT_VALIDATED", "DEVELOPMENT_BENCHMARK_VALIDATED", "A1_DEVELOPMENT_TRAINING_COMPLETE", "A1_FORMAT_READY", "AUXILIARY_BACKPROP_VALIDATED", "VARIANT_SMOKE_COMPLETE", "RESOURCE_PLAN_MEASURED"))
    policy_rates = [float(row.get("end_to_end_task_correct_rate", 0.0)) for row in a1_rows]
    best_constant = max((d.get("majority_baseline") or {}).values(), default=0.0)
    if not gates["DEVELOPMENT_READY_FOR_COHORT_REVIEW"]:
        next_decision = "Do not request a locked cohort. Review the failed engineering/model gate, preserve all attempts, and either investigate a named defect or open a separately budgeted development attempt."
    else:
        next_decision = "Request human review of a locked Pythia comparison plan; this receipt still does not authorize te-freeze-cohort or te-run-cohort."
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "development-readiness",
        "status": "DEVELOPMENT_READY_FOR_COHORT_REVIEW" if gates["DEVELOPMENT_READY_FOR_COHORT_REVIEW"] else "DEVELOPMENT_NOT_READY_FOR_COHORT_REVIEW",
        "gates": gates,
        "evidence": {"preflight": str(preflight), "raw_output_audit": str(audit), "training_contracts": str(training), "dataset_validation": str(dataset), "memorization": str(memorization), "a1_development": str(a1), "variant_smoke": str(variants), "resource_profile": str(resource), "trained_attack_audit": str(attack) if attack else "not_measured"},
        "a1_format_rates": strict_rates,
        "a1_end_to_end_policy_rates": policy_rates,
        "best_constant_action_rate": best_constant,
        "policy_skill_status": "BASELINE_POLICY_SKILL_LIMITED" if policy_rates and max(policy_rates) <= best_constant + 0.05 else "DEVELOPMENT_POLICY_SKILL_OBSERVED",
        "calibration": "not_measured",
        "capability_sentinel": "not_measured",
        "locked_cohort_authorized": False,
        "locked_data_read_or_scored": False,
        "scientific_claim": "No VGA effectiveness, alignment, moral-truth, or population-generalization claim is supported.",
        "next_decision": next_decision,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, default=Path("docs/experiments/te-v0.6.1-pythia-development/preflight.json"))
    parser.add_argument("--audit", type=Path, default=Path("results/reports/te-v0.6.1-pythia-development/raw-output-audit.json"))
    parser.add_argument("--training", type=Path, default=Path("results/reports/te-v0.6.1-pythia-development/training-contracts.json"))
    parser.add_argument("--dataset", type=Path, default=Path("results/reports/te-v0.6.1-pythia-development/development-dataset-validation.json"))
    parser.add_argument("--memorization", type=Path, required=True)
    parser.add_argument("--a1", type=Path, required=True)
    parser.add_argument("--variants", type=Path, required=True)
    parser.add_argument("--resource", type=Path, required=True)
    parser.add_argument("--attack", type=Path)
    parser.add_argument("--output", type=Path, default=Path("results/reports/te-v0.6.1-pythia-development/development-readiness.json"))
    args = parser.parse_args()
    result = evaluate(preflight=args.preflight, audit=args.audit, training=args.training, dataset=args.dataset, memorization=args.memorization, a1=args.a1, variants=args.variants, resource=args.resource, attack=args.attack)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "gates": result["gates"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
