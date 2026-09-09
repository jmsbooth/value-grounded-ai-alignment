"""Shared lifecycle machinery for immutable v0.5 harness experiments."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.registry import append_unique, read_jsonl
from vgta_eval.compatibility import validate_compatibility
from vgta_eval.reporting import (
    allocate_analysis,
    immutable_json_write,
    immutable_write,
    make_manifest,
    sha256_file,
    working_tree_clean,
)
from vgta_eval.run_identity import reserve_run_directory
from vgta_eval.scenario_generator import REMEDIATED_DATASET_VERSION, load_dataset


PROTOCOL = "hv-v0.5.1"
PROTOCOLS_ROOT = ROOT / "experiments/protocols"
PROTOCOL_ROOT = PROTOCOLS_ROOT / PROTOCOL
DATASETS_ROOT = ROOT / "experiments/datasets"
DEFAULT_DATASET_VERSION = REMEDIATED_DATASET_VERSION
DATASET_ROOT = DATASETS_ROOT / DEFAULT_DATASET_VERSION
REGISTRY_ROOT = ROOT / "results/registry"


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, default=str) + "\n"


def sha256_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        if path.is_file():
            digest.update(str(path.relative_to(ROOT)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def protocol_root_for_version(protocol_version: str = PROTOCOL) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", protocol_version):
        raise ValueError(f"invalid protocol version: {protocol_version}")
    path = PROTOCOLS_ROOT / protocol_version
    if not path.is_dir():
        raise FileNotFoundError(f"protocol version is not materialized: {path}")
    return path


def protocol_sha256(protocol_version: str = PROTOCOL) -> str:
    root = protocol_root_for_version(protocol_version)
    return sha256_paths([path for path in root.rglob("*") if path.is_file()])


def dataset_root_for_version(version: str | None = None) -> Path:
    selected = version or os.environ.get("VGTA_DATASET_VERSION", DEFAULT_DATASET_VERSION)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", selected):
        raise ValueError(f"invalid dataset version: {selected}")
    path = DATASETS_ROOT / selected
    if not path.is_dir():
        raise FileNotFoundError(f"dataset version is not materialized: {path}")
    return path


def dataset_root_for_manifest(manifest: Mapping[str, Any]) -> Path:
    dataset_path = manifest.get("dataset_path")
    if dataset_path:
        candidate = (ROOT / str(dataset_path)).resolve()
        try:
            candidate.relative_to(DATASETS_ROOT.resolve())
        except ValueError as exc:
            raise ValueError(f"dataset path is outside the repository dataset registry: {dataset_path}") from exc
        if candidate.parent != DATASETS_ROOT.resolve():
            raise ValueError(f"dataset path must name a direct dataset version: {dataset_path}")
        if not candidate.is_dir():
            raise FileNotFoundError(f"dataset version is not materialized: {candidate}")
        return candidate
    expected_manifest_sha = str(manifest.get("dataset", ""))
    for candidate in sorted(DATASETS_ROOT.iterdir()):
        manifest_path = candidate / "dataset-manifest.json"
        if candidate.is_dir() and manifest_path.exists() and sha256_file(manifest_path) == expected_manifest_sha:
            return candidate
    return DATASET_ROOT


def artifact_identity(dataset_root: Path | None = None, protocol_version: str = PROTOCOL) -> dict[str, str]:
    dataset_root = dataset_root or DATASET_ROOT
    return {
        "dataset_sha256": sha256_file(dataset_root / "dataset-manifest.json"),
        "ontology_sha256": sha256_file(ROOT / "ontology/axiology/core-axiology.ttl"),
        "verifier_sha256": sha256_file(ROOT / "src/vgta/verifier.py"),
        "config_sha256": protocol_sha256(protocol_version),
        "ground_truth_sha256": sha256_paths([dataset_root / "dataset-manifest.json", dataset_root / "train.jsonl", dataset_root / "sealed-test.jsonl"]),
        "attack_suite_sha256": sha256_file(ROOT / "src/vgta_eval/attacks.py"),
        "metric_suite_sha256": sha256_paths([ROOT / "src/vgta_eval/metrics.py", ROOT / "src/vgta_eval/calibration.py"]),
    }


def experiment_record(experiment_id: str, research_question: str, *, primary_metrics: list[str] | None = None, controls: list[str] | None = None, prerequisites: list[str] | None = None) -> dict[str, Any]:
    return {
        "experiment_id": experiment_id,
        "protocol_version": PROTOCOL,
        "research_question": research_question,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "primary_metrics": primary_metrics or [],
        "controls": controls or [],
        "prerequisite_experiments": prerequisites or [],
    }


def ensure_experiment(record: Mapping[str, Any]) -> None:
    path = REGISTRY_ROOT / "experiments.jsonl"
    existing = read_jsonl(path)
    if any(item.get("experiment_id") == record.get("experiment_id") for item in existing):
        return
    append_unique(path, record, identity_field="experiment_id")


def _register_run(manifest: Mapping[str, Any], result: Mapping[str, Any]) -> None:
    record = dict(manifest)
    record["run_key"] = f"{manifest['protocol_version']}__{manifest['experiment_id']}__{manifest['run_id']}"
    record["evidence_status"] = result.get("status", "development-only")
    append_unique(REGISTRY_ROOT / "runs.jsonl", record, identity_field="run_key")


def _register_analysis(manifest: Mapping[str, Any], analysis_dir: Path, prior_analysis: str | None = None) -> None:
    record = {
        "analysis_id": f"{manifest['report_id']}__analysis",
        "protocol_version": manifest["protocol_version"],
        "experiment_id": manifest["experiment_id"],
        "run_id": manifest["run_id"],
        "analysis_revision": manifest["analysis_revision"],
        "report_id": manifest["report_id"],
        "path": str(analysis_dir.relative_to(ROOT)),
        "prior_analysis": prior_analysis,
        "created_at": manifest["created_at"],
    }
    append_unique(REGISTRY_ROOT / "analyses.jsonl", record, identity_field="analysis_id")


def _register_report(manifest: Mapping[str, Any], report_dir: Path, result: Mapping[str, Any]) -> None:
    record = {
        **dict(manifest),
        "path": str((report_dir / "experimental-validation-report.md").relative_to(ROOT)),
        "run_validity": result.get("run_validity", "valid"),
        "gate_passed": bool(result.get("gate_passed", False)),
        "evidence_status": result.get("status", "development-only"),
    }
    append_unique(REGISTRY_ROOT / "reports.jsonl", record, identity_field="report_id")


def generate_registry_index() -> Path:
    REGISTRY_ROOT.mkdir(parents=True, exist_ok=True)
    reports = sorted(read_jsonl(REGISTRY_ROOT / "reports.jsonl"), key=lambda item: (str(item.get("created_at", "")), str(item.get("report_id", ""))))
    lines = [
        "# Research experiment registry",
        "",
        "This is the human entry point for immutable experiment, analysis, and report history. The canonical evidence artifact is the versioned report path; this index is navigation only.",
        "",
        "| Date | Protocol | Dataset | Experiment | Run | Analysis | Status | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for report in reports:
        created = str(report.get("created_at", ""))[:10]
        report_path = str(report.get("path", ""))
        lines.append(f"| {created} | `{report.get('protocol_version')}` | `{report.get('dataset_version', 'unspecified')}` | `{report.get('experiment_id')}` | `{report.get('run_id')}` | `a{int(report.get('analysis_revision', 0)):03d}` | `{report.get('evidence_status')}` | [{report.get('report_id')}]({ROOT / report_path}) |")
    lines.extend(["", f"Reports recorded: `{len(reports)}`.", ""])
    index_path = REGISTRY_ROOT / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def append_experiment_log(*, experiment_id: str, run_id: str, report_path: Path, protocol: str, status: str) -> None:
    path = ROOT / "docs/experiment-log.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = "\n".join([
        "",
        f"## {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} — {experiment_id}",
        "",
        f"- Protocol: `{protocol}`",
        f"- Experiment: `{experiment_id}`",
        f"- Run: `{run_id}`",
        f"- Status: `{status}`",
        f"- Report: [{report_path.name}](../{report_path.relative_to(ROOT)})",
        "",
        "This entry records lifecycle chronology only; metrics remain in the immutable report.",
        "",
    ])
    with path.open("a", encoding="utf-8") as handle:
        handle.write(event)


def render_report(*, result: Mapping[str, Any], report_id: str, protocol: str, experiment_id: str, run_id: str, revision: int, created_at: str, git_sha: str, clean: bool, identities: Mapping[str, str], run_validity: str, run_mode: str, raw_path: Path, analysis_path: Path) -> str:
    methods = result.get("methods", "The experiment uses a bounded synthetic fixture and deterministic analysis code.")
    controls = result.get("controls", "Controls are recorded in the result payload.")
    results = result.get("results", {})
    status = result.get("status", "development-only")
    gate = "passed" if result.get("gate_passed") else "not passed"
    def fenced(value: Any) -> str:
        return "```json\n" + _json(value) + "```"
    def display_path(path: Path) -> str:
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
    return "\n".join([
        f"# VGA/VGTA Harness Validation Report — {report_id}",
        "",
        f"Experiment ID: `{experiment_id}`  ",
        f"Protocol: `{protocol}`  ",
        f"Run ID: `{run_id}`  ",
        f"Analysis revision: `analysis-r{revision:03d}`  ",
        f"Report ID: `{report_id}`  ",
        f"Created: `{created_at}`  ",
        f"Git SHA: `{git_sha}`  ",
        f"Working tree status: `{'clean' if clean else 'modified'}`  ",
        f"Dataset version: `{identities.get('dataset_version', 'unspecified')}`  ",
        f"Dataset: `{identities.get('dataset_sha256')}`  ",
        f"Ontology: `{identities.get('ontology_sha256')}`  ",
        f"Ground truth: `{identities.get('ground_truth_sha256')}`  ",
        f"Verifier: `{identities.get('verifier_sha256')}`  ",
        f"Attack suite: `{identities.get('attack_suite_sha256')}`  ",
        f"Metric suite: `{identities.get('metric_suite_sha256')}`  ",
        "Evidence classification: `harness-validation`  ",
        f"Run validity: `{run_validity}`  ",
        f"Run mode: `{run_mode}`",
        "",
        "> This is a harness-validation artifact. It does not establish VGA superiority, human moral validity, production security, or Transformer evidence.",
        "",
        "## Research question",
        "",
        str(result.get("research_question", "")),
        "",
        "## Method",
        "",
        str(methods),
        "",
        "## Controls",
        "",
        str(controls),
        "",
        "## Results",
        "",
        fenced(results),
        "",
        "## Null results",
        "",
        str(result.get("null_results", "None recorded beyond the result payload.")),
        "",
        "## Negative results",
        "",
        str(result.get("negative_results", "None recorded beyond the result payload.")),
        "",
        "## Harness issues",
        "",
        str(result.get("harness_issues", "No harness defect was observed.")),
        "",
        "## Interpretation",
        "",
        str(result.get("interpretation", "Interpretation is limited to the named fixture and protocol.")),
        "",
        "## Gate decision",
        "",
        f"Harness acceptance for this experiment: **{gate}**. Evidence status: `{status}`.",
        "",
        "## Next action",
        "",
        str(result.get("next_action", "Preserve the artifact and continue only under the protocol.")),
        "",
        "## Source artifacts",
        "",
        f"- Raw run: `{display_path(raw_path)}`",
        f"- Analysis: `{display_path(analysis_path)}`",
        f"- Protocol: `experiments/protocols/{protocol}/`",
        "",
        "This report is immutable. Reanalysis must create a new analysis revision and report ID.",
        "",
    ])


def _write_analysis_bundle(*, experiment_id: str, run_id: str, raw_dir: Path, raw_manifest: Mapping[str, Any], result: Mapping[str, Any], run_mode: str, reanalysis_reason: str | None = None, prior_analysis: str | None = None) -> Path:
    protocol = str(raw_manifest.get("protocol_version", PROTOCOL))
    dataset_root = dataset_root_for_manifest(raw_manifest)
    identities = artifact_identity(dataset_root, protocol)
    identities["dataset_version"] = dataset_root.name
    validate_compatibility(
        {
            "protocol_version": raw_manifest.get("protocol_version"),
            "dataset_sha256": raw_manifest.get("dataset"),
            "ground_truth_sha256": raw_manifest.get("ground_truth"),
            "ontology_sha256": raw_manifest.get("ontology"),
            "verifier_sha256": raw_manifest.get("verifier"),
            "config_sha256": raw_manifest.get("config"),
            "attack_suite_sha256": raw_manifest.get("attack_suite"),
            "metric_suite_sha256": raw_manifest.get("metric_suite"),
        },
        {"protocol_version": protocol, **identities},
        run_mode=run_mode,
    )
    revision, analysis_dir = allocate_analysis(ROOT, protocol, experiment_id, run_id)
    code_hash = sha256_file(Path(__file__))
    report_manifest = make_manifest(
        root=ROOT,
        protocol=protocol,
        experiment=experiment_id,
        run_id=run_id,
        revision=revision,
        raw_manifest_path=raw_dir / "run-manifest.json",
        dataset_sha256=identities["dataset_sha256"],
        ground_truth_sha256=identities["ground_truth_sha256"],
        ontology_sha256=identities["ontology_sha256"],
        verifier_sha256=identities["verifier_sha256"],
        config_sha256=identities["config_sha256"],
        analysis_code_sha256=code_hash,
        attack_suite_sha256=identities["attack_suite_sha256"],
        metric_suite_sha256=identities["metric_suite_sha256"],
        dataset_version=dataset_root.name,
        dataset_path=str(dataset_root.relative_to(ROOT)),
        evidence_tier="harness-validation",
        status="complete",
        prior_analysis=prior_analysis,
        reason_for_reanalysis=reanalysis_reason,
    )
    stats = {"report_id": report_manifest["report_id"], "protocol_version": protocol, "experiment_id": experiment_id, "run_id": run_id, "analysis_revision": revision, "result": dict(result), "identities": identities}
    immutable_json_write(analysis_dir / "statistics.json", stats)
    immutable_write(analysis_dir / "result-facts.md", "# Result facts\n\n" + _json(result))
    report_dir = ROOT / "results/reports" / protocol / experiment_id / run_id / analysis_dir.name
    report_dir.mkdir(parents=True, exist_ok=True)
    report = render_report(result=result, report_id=str(report_manifest["report_id"]), protocol=protocol, experiment_id=experiment_id, run_id=run_id, revision=revision, created_at=str(report_manifest["created_at"]), git_sha=str(report_manifest["git_sha"]), clean=bool(report_manifest["working_tree_clean"]), identities=identities, run_validity=str(result.get("run_validity", "valid")), run_mode=run_mode, raw_path=raw_dir, analysis_path=analysis_dir)
    immutable_write(report_dir / "experimental-validation-report.md", report)
    report_manifest["report_path"] = str((report_dir / "experimental-validation-report.md").relative_to(ROOT))
    report_manifest["analysis_path"] = str(analysis_dir.relative_to(ROOT))
    immutable_json_write(report_dir / "report-manifest.json", report_manifest)
    _register_analysis(report_manifest, analysis_dir, prior_analysis=prior_analysis)
    _register_report(report_manifest, report_dir, result)
    generate_registry_index()
    append_experiment_log(experiment_id=experiment_id, run_id=run_id, report_path=report_dir / "experimental-validation-report.md", protocol=protocol, status=str(result.get("status", "development-only")))
    return report_dir / "experimental-validation-report.md"


def run_experiment(*, experiment_id: str, research_question: str, compute: Callable[[Mapping[str, list[dict[str, Any]]]], Mapping[str, Any]], controls: list[str] | None = None, primary_metrics: list[str] | None = None, run_mode: str = "development", new_sealed_dataset: bool = False, sealed_outputs_uninspected: bool = False, preregistration_committed: bool = False) -> Path:
    if run_mode not in {"development", "confirmatory"}:
        raise ValueError("run_mode must be development or confirmatory")
    if run_mode == "confirmatory":
        validate_confirmatory_requirements(new_sealed_dataset=new_sealed_dataset, sealed_outputs_uninspected=sealed_outputs_uninspected, preregistration_committed=preregistration_committed)
    dataset_root = dataset_root_for_version()
    if PROTOCOL == "hv-v0.5.1" and dataset_root.name != REMEDIATED_DATASET_VERSION:
        raise RuntimeError(f"{PROTOCOL} requires dataset version {REMEDIATED_DATASET_VERSION}; got {dataset_root.name}")
    records = load_dataset(dataset_root)
    run_id, raw_dir = reserve_run_directory(ROOT / "results/raw" / PROTOCOL / experiment_id)
    identities = artifact_identity(dataset_root, PROTOCOL)
    identities["dataset_version"] = dataset_root.name
    result = dict(compute(records))
    result.setdefault("research_question", research_question)
    result.setdefault("status", "development-only" if run_mode == "development" else "inconclusive")
    result.setdefault("run_validity", "valid")
    result.setdefault("gate_passed", False)
    artifact_payloads = dict(result.pop("artifacts", {}))
    (raw_dir / "predictions").mkdir()
    (raw_dir / "logs").mkdir()
    (raw_dir / "artifacts").mkdir()
    immutable_json_write(raw_dir / "config.snapshot.json", {"protocol_version": PROTOCOL, "experiment_id": experiment_id, "run_mode": run_mode, "dataset_version": dataset_root.name, "dataset_path": str(dataset_root.relative_to(ROOT)), "identities": identities})
    immutable_json_write(raw_dir / "artifacts/result.json", result)
    raw_artifacts = ["config.snapshot.json", "artifacts/result.json"]
    for relative, artifact in artifact_payloads.items():
        artifact_path = raw_dir / str(relative)
        immutable_json_write(artifact_path, artifact)
        raw_artifacts.append(str(relative))
    raw_manifest = {
        "protocol_version": PROTOCOL,
        "experiment_id": experiment_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip() or "unknown",
        "working_tree_clean": working_tree_clean(ROOT),
        "working_tree_patch_sha256": None,
        "run_mode": run_mode,
        "dataset_version": dataset_root.name,
        "dataset_path": str(dataset_root.relative_to(ROOT)),
        "dataset": identities["dataset_sha256"],
        "ontology": identities["ontology_sha256"],
        "ground_truth": identities["ground_truth_sha256"],
        "verifier": identities["verifier_sha256"],
        "config": identities["config_sha256"],
        "attack_suite": identities["attack_suite_sha256"],
        "metric_suite": identities["metric_suite_sha256"],
        "status": "complete",
        "evidence_status": result.get("status", "development-only"),
        "failure_classification": result.get("failure_classification", "none"),
        "raw_artifacts": raw_artifacts,
        "raw_artifact_sha256": {relative: sha256_file(raw_dir / relative) for relative in raw_artifacts},
    }
    if not raw_manifest["working_tree_clean"]:
        from vgta_eval.reporting import working_tree_patch_sha256
        raw_manifest["working_tree_patch_sha256"] = working_tree_patch_sha256(ROOT)
    immutable_json_write(raw_dir / "run-manifest.json", raw_manifest)
    ensure_experiment(experiment_record(experiment_id, research_question, primary_metrics=primary_metrics, controls=controls))
    _register_run(raw_manifest, result)
    report = _write_analysis_bundle(experiment_id=experiment_id, run_id=run_id, raw_dir=raw_dir, raw_manifest=raw_manifest, result=result, run_mode=run_mode)
    print(json.dumps({"protocol": PROTOCOL, "experiment": experiment_id, "run_id": run_id, "report": str(report.relative_to(ROOT)), "status": result.get("status"), "gate_passed": result.get("gate_passed")}, indent=2))
    return report


def validate_confirmatory_requirements(*, new_sealed_dataset: bool, sealed_outputs_uninspected: bool, preregistration_committed: bool) -> None:
    """Fail closed unless all preconditions for a confirmatory run are explicit."""

    if not working_tree_clean(ROOT):
        raise RuntimeError("confirmatory runs require a clean Git tree")
    protocol_file = PROTOCOL_ROOT / "protocol.md"
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(protocol_file.relative_to(ROOT))], cwd=ROOT, capture_output=True, text=True, check=False).returncode == 0
    if not tracked or not preregistration_committed:
        raise RuntimeError("confirmatory runs require a committed protocol/preregistration")
    gate = subprocess.run([sys.executable, str(ROOT / "scripts/harness_gate.py")], cwd=ROOT, capture_output=True, text=True, check=False)
    if gate.returncode != 0:
        raise RuntimeError("confirmatory runs require a passing harness gate")
    if not new_sealed_dataset:
        raise RuntimeError("confirmatory runs require a new sealed dataset")
    if not sealed_outputs_uninspected:
        raise RuntimeError("confirmatory runs require an explicit uninspected-sealed-output attestation")


def reanalyze(*, protocol: str = PROTOCOL, experiment_id: str, run_id: str, reason: str) -> Path:
    if not reason.strip():
        raise ValueError("--reason is required for reanalysis")
    raw_dir = ROOT / "results/raw" / protocol / experiment_id / run_id
    raw_manifest = json.loads((raw_dir / "run-manifest.json").read_text(encoding="utf-8"))
    result = json.loads((raw_dir / "artifacts/result.json").read_text(encoding="utf-8"))
    analyses = sorted((ROOT / "results/analyses" / protocol / experiment_id / run_id).glob("analysis-r*"))
    prior = analyses[-1].name if analyses else None
    return _write_analysis_bundle(experiment_id=experiment_id, run_id=run_id, raw_dir=raw_dir, raw_manifest=raw_manifest, result=result, run_mode=str(raw_manifest.get("run_mode", "development")), reanalysis_reason=reason, prior_analysis=prior)


def analyze_existing(*, protocol: str = PROTOCOL, experiment_id: str, run_id: str, reanalysis: bool = False, reason: str | None = None) -> Path:
    """Analyze an existing immutable run, refusing ambiguous replacement."""

    raw_dir = ROOT / "results/raw" / protocol / experiment_id / run_id
    if not (raw_dir / "run-manifest.json").exists() or not (raw_dir / "artifacts/result.json").exists():
        raise FileNotFoundError(f"immutable run is missing required artifacts: {raw_dir}")
    analyses = sorted((ROOT / "results/analyses" / protocol / experiment_id / run_id).glob("analysis-r*"))
    if analyses and not reanalysis:
        raise RuntimeError("an analysis already exists; use --reanalyze --reason to create a new revision")
    if reanalysis and not (reason and reason.strip()):
        raise ValueError("--reason is required with --reanalyze")
    raw_manifest = json.loads((raw_dir / "run-manifest.json").read_text(encoding="utf-8"))
    result = json.loads((raw_dir / "artifacts/result.json").read_text(encoding="utf-8"))
    prior = analyses[-1].name if analyses else None
    return _write_analysis_bundle(experiment_id=experiment_id, run_id=run_id, raw_dir=raw_dir, raw_manifest=raw_manifest, result=result, run_mode=str(raw_manifest.get("run_mode", "development")), reanalysis_reason=reason, prior_analysis=prior)
