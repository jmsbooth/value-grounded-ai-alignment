#!/usr/bin/env python3
"""Execute the first reproducible VGTA empirical mechanism-validation pilot.

The runner trains A1/B/C1/C2 as matched shared-MLP proxies across three
seeds, evaluates frozen logical splits, writes immutable raw run directories,
and then invokes the result analyzer. It deliberately does not implement a
Transformer, D, E, or G; those are gated on the preregistered early results.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.conformance import verify_prediction
from vgta_eval.model import MODEL_VARIANT_GROUPS, ModelConfig, SmallSemanticModel, feature_vocabulary
from vgta_eval.scenario_generator import (
    ACTION_LABELS,
    CAPABILITY_LABELS,
    CONFLICT_LABELS,
    DATASET_VERSION,
    PURPOSE_LABELS,
    RELATION_LABELS,
    SPLITS,
    VALUE_LABELS,
    load_dataset,
    write_dataset,
)


CONFIG_PATH = ROOT / "experiments/configs/v0.3-small.toml"
DATASET_PATH = ROOT / "experiments/datasets/v0.3-small"
PREREGISTRATION_PATH = ROOT / "experiments/preregistration/v0.3.md"


def _config() -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
        raise RuntimeError("Python 3.11+ or a TOML parser is required")
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_preregistration(*, formal_sealed: bool) -> tuple[str, bool]:
    if not PREREGISTRATION_PATH.exists():
        raise FileNotFoundError(f"missing preregistration: {PREREGISTRATION_PATH}")
    preregistration_sha = _git("hash-object", str(PREREGISTRATION_PATH))
    status = _git("status", "--porcelain")
    tracked_preregistration = "experiments/preregistration/v0.3.md" not in status and _git("ls-files", str(PREREGISTRATION_PATH))
    clean = not status
    if formal_sealed and (not clean or not tracked_preregistration):
        raise RuntimeError(
            "formal sealed execution requires a clean worktree with the preregistration committed; "
            "use the default local-pilot mode while developing"
        )
    return preregistration_sha, bool(clean and tracked_preregistration)


def _model_labels() -> dict[str, Sequence[str]]:
    return {
        "action": ACTION_LABELS,
        "value": VALUE_LABELS,
        "relation": RELATION_LABELS,
        "conflict": CONFLICT_LABELS,
        "purpose": PURPOSE_LABELS,
        "capability": CAPABILITY_LABELS,
    }


def _training_tasks(variant: str) -> dict[str, float]:
    """Keep the ladder's auxiliary objectives distinct and preregistered."""

    tasks = {
        "action": 1.0,
        "value": 0.0,
        "relation": 0.0,
        "conflict": 0.0,
        "purpose": 0.0,
        "capability": 0.20,
    }
    if variant in {"C1", "C2"}:
        tasks.update({"value": 0.45, "relation": 0.45})
    if variant == "C2":
        tasks["conflict"] = 0.55
    return tasks


def _prediction_rows(model: SmallSemanticModel, records: Sequence[Mapping[str, Any]], variant: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    groups = MODEL_VARIANT_GROUPS[variant]
    for record in records:
        prediction = model.predict(record, groups)
        verification = verify_prediction(record, prediction["action"])
        labels = record["labels"]
        target_action = str(labels["action"])
        action_correct = prediction["action"] == target_action
        rows.append({
            "example_id": record["example_id"],
            "family": record["family"],
            "split": record["split"],
            "transform": record["transform"],
            "template_id": record["template_id"],
            "topology_hash": record["topology_hash"],
            "attack": record["attack"],
            "coverage": record["coverage"],
            "predicted_action": prediction["action"],
            "target_action": target_action,
            "action_correct": action_correct,
            "predicted_values": prediction["values"],
            "true_values": labels["values"],
            "predicted_relation": prediction["relation"],
            "true_relation": labels["relation"],
            "predicted_conflict": prediction["conflict"],
            "true_conflict": labels["conflict"],
            "predicted_purpose": prediction["purpose"],
            "true_purpose": labels["purpose"],
            "purpose_correct": prediction["purpose"] == labels["purpose"],
            "predicted_capability": prediction["capability"],
            "true_capability": labels["capability"],
            "capability_correct": labels["capability"] is not None and prediction["capability"] == labels["capability"],
            "verifier_permitted": verification["permitted"],
            "verifier_reasons": verification["reasons"],
            "parser_failure": verification["parser_failure"],
            "attack_safe": action_correct and verification["permitted"],
            "counterfactual_consistent": action_correct,
            "action_confidence": float(prediction["action_confidence"]),
            "semantic_completeness": next(
                (float(payload.get("semantic_completeness", 1.0)) for name, payload in record["candidate_actions"].items() if name == prediction["action"]),
                0.0,
            ),
        })
    return rows


def _relation_accuracy(model: SmallSemanticModel, records: Sequence[Mapping[str, Any]], variant: str) -> float:
    relevant = [record for record in records if record["family"] in {"moral_salience", "structural_ood", "ontology_degradation"}]
    if not relevant:
        return 0.0
    groups = MODEL_VARIANT_GROUPS[variant]
    return sum(model.predict(record, groups)["relation"] == record["labels"]["relation"] for record in relevant) / len(relevant)


def _drift_measurement(model: SmallSemanticModel, variant: str, records: Mapping[str, Sequence[Mapping[str, Any]]], config: ModelConfig) -> dict[str, float | str]:
    probe_records = records["sealed-test"]
    before = _relation_accuracy(model, probe_records, variant)
    capability_train = [record for record in records["train"] if record["family"] == "capability"]
    unrestricted = model.clone()
    unrestricted.fit(
        capability_train,
        MODEL_VARIANT_GROUPS[variant],
        tasks={"action": 0.0, "value": 0.0, "relation": 0.0, "conflict": 0.0, "purpose": 0.0, "capability": 1.0},
    )
    frozen = model.clone()
    frozen.fit(
        capability_train,
        MODEL_VARIANT_GROUPS[variant],
        tasks={"action": 0.0, "value": 0.0, "relation": 0.0, "conflict": 0.0, "purpose": 0.0, "capability": 1.0},
        freeze_groups=("axiological",),
    )
    after_unrestricted = _relation_accuracy(unrestricted, probe_records, variant)
    after_frozen = _relation_accuracy(frozen, probe_records, variant)
    return {
        "relation_accuracy_before": before,
        "relation_accuracy_after_unrestricted": after_unrestricted,
        "relation_accuracy_after_frozen_axiology": after_frozen,
        "acd_unrestricted": before - after_unrestricted,
        "acd_frozen_axiology": before - after_frozen,
    }


def run(*, formal_sealed: bool = False) -> Path:
    config = _config()
    preregistration_sha, preregistration_committed = _validate_preregistration(formal_sealed=formal_sealed)
    dataset_manifest = write_dataset(DATASET_PATH)
    if dataset_manifest["sealed_structural_topology_overlap_with_train"]:
        raise RuntimeError("structural OOD topology hash overlaps training data")
    records = load_dataset(DATASET_PATH)
    feature_names = feature_vocabulary(records["train"])
    labels = _model_labels()
    model_config = ModelConfig(
        hidden_dim=int(config["experiment"]["hidden_dim"]),
        epochs=int(config["experiment"]["epochs"]),
        learning_rate=float(config["experiment"]["learning_rate"]),
        l2=float(config["experiment"]["l2"]),
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_root = ROOT / "results/raw" / f"empirical-small-{timestamp}"
    raw_root.mkdir(parents=True, exist_ok=False)
    run_summaries: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    for variant in config["experiment"]["variants"]:
        if variant not in MODEL_VARIANT_GROUPS:
            raise ValueError(f"unsupported pilot variant: {variant}")
        for seed in config["experiment"]["seeds"]:
            started = time.time()
            model = SmallSemanticModel(feature_names, labels, model_config, seed=int(seed))
            fit_summary = model.fit(
                records["train"],
                MODEL_VARIANT_GROUPS[variant],
                tasks=_training_tasks(variant),
            )
            predictions = _prediction_rows(model, [record for split in SPLITS[1:] for record in records[split]], variant)
            for row in predictions:
                row.update({"variant": variant, "seed": int(seed)})
            drift = _drift_measurement(model, variant, records, model_config) if variant in {"C1", "C2"} else {"status": "not_applicable_before_axiological_training"}
            run_id = f"{raw_root.name}-{variant.lower()}-seed-{seed}"
            run_dir = raw_root / run_id
            run_dir.mkdir()
            (run_dir / "predictions.jsonl").write_text("\n".join(json.dumps(row, sort_keys=True) for row in predictions) + "\n", encoding="utf-8")
            (run_dir / "drift.json").write_text(json.dumps(drift, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            manifest = {
                "run_id": run_id,
                "git_sha": _git("rev-parse", "HEAD"),
                "preregistration_sha": preregistration_sha,
                "preregistration_sha_kind": "git-blob-content-digest",
                "preregistration_committed": preregistration_committed,
                "model_variant": variant,
                "model_family": config["experiment"]["model_family"],
                "base_model_hash": "shared-mlp-mechanism-proxy-v0.3",
                "parameter_count": model.parameter_count,
                "dataset_version": DATASET_VERSION,
                "dataset_manifest_sha": _sha256(DATASET_PATH / "dataset-manifest.json"),
                "config_sha": _sha256(CONFIG_PATH),
                "ontology_version": "core-axiology-v1",
                "verifier_version": "rule-based-toy-v0.2-fixed",
                "seed": int(seed),
                "hyperparameters": {
                    "groups": MODEL_VARIANT_GROUPS[variant],
                    "hidden_dim": model_config.hidden_dim,
                    "epochs": model_config.epochs,
                    "learning_rate": model_config.learning_rate,
                    "l2": model_config.l2,
                },
                "hardware": {"platform": platform.platform(), "machine": platform.machine(), "gpu": "none"},
                "start_time": datetime.fromtimestamp(started, timezone.utc).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "training_seconds": time.time() - started,
                "gpu_hours": 0.0,
                "training_flops_estimate": int(2 * model.parameter_count * len(records["train"]) * model_config.epochs),
                "inference_flops_estimate": int(2 * model.parameter_count * len(predictions)),
                "cost_estimate_method": "2 * allocated parameters * examples * epochs; CPU-only pilot; approximate",
                "status": "complete",
                "scientific_status": "pilot-uncommitted" if not preregistration_committed else "formal-sealed",
                "sealed_test_rows": sum(row["split"] == "sealed-test" for row in predictions),
                "fit_summary": fit_summary,
                "drift_summary": drift,
            }
            (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            run_summaries.append(manifest)
            all_predictions.extend(predictions)
    group_manifest = {
        "run_group": raw_root.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "config_path": str(CONFIG_PATH.relative_to(ROOT)),
        "config_sha": _sha256(CONFIG_PATH),
        "dataset_manifest": dataset_manifest,
        "git_sha": _git("rev-parse", "HEAD"),
        "preregistration_sha": preregistration_sha,
        "preregistration_committed": preregistration_committed,
        "scientific_status": "pilot-uncommitted" if not preregistration_committed else "formal-sealed",
        "variants": list(config["experiment"]["variants"]),
        "seeds": list(config["experiment"]["seeds"]),
        "runs": [summary["run_id"] for summary in run_summaries],
        "prediction_rows": len(all_predictions),
        "sealed_test_rows_per_run": sum(row["split"] == "sealed-test" for row in all_predictions) // len(run_summaries),
        "sealed_structural_topology_overlap_with_train": dataset_manifest["sealed_structural_topology_overlap_with_train"],
        "hardware": run_summaries[0]["hardware"] if run_summaries else {},
        "parameter_count": run_summaries[0]["parameter_count"] if run_summaries else 0,
        "training_flops_estimate": sum(summary["training_flops_estimate"] for summary in run_summaries),
        "inference_flops_estimate": sum(summary["inference_flops_estimate"] for summary in run_summaries),
    }
    (raw_root / "group-manifest.json").write_text(json.dumps(group_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (raw_root / "all-predictions.jsonl").write_text("\n".join(json.dumps(row, sort_keys=True) for row in all_predictions) + "\n", encoding="utf-8")
    subprocess.check_call([sys.executable, str(ROOT / "scripts/analyze_results.py"), "--raw-root", str(raw_root)], cwd=ROOT)
    print(json.dumps({"run_group": str(raw_root.relative_to(ROOT)), "scientific_status": group_manifest["scientific_status"], "rows": len(all_predictions)}, indent=2))
    return raw_root


def smoke() -> None:
    """Run one tiny fit without writing results; suitable for CI."""

    config = _config()
    from vgta_eval.scenario_generator import generate_dataset

    in_memory = generate_dataset()
    feature_names = feature_vocabulary(in_memory["train"])
    model = SmallSemanticModel(
        feature_names,
        _model_labels(),
        ModelConfig(hidden_dim=8, epochs=1, learning_rate=float(config["experiment"]["learning_rate"]), l2=float(config["experiment"]["l2"])),
        seed=11,
    )
    model.fit(in_memory["train"], MODEL_VARIANT_GROUPS["C2"], tasks=_training_tasks("C2"))
    predictions = _prediction_rows(model, in_memory["sealed-test"][:4], "C2")
    if len(predictions) != 4 or not predictions[0]["example_id"]:
        raise RuntimeError("empirical smoke test did not produce predictions")
    print(f"empirical smoke: {len(predictions)} sealed predictions; {model.parameter_count} parameters")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-sealed", action="store_true", help="require a committed preregistration and clean worktree")
    parser.add_argument("--smoke", action="store_true", help="run one tiny fit without writing result artifacts")
    args = parser.parse_args()
    if args.smoke:
        smoke()
    else:
        run(formal_sealed=args.formal_sealed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
