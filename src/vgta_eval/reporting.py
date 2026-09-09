"""Provenance, immutable output, and report-path helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Any, Mapping

from .run_identity import analysis_name, make_report_id, next_analysis_revision


class ImmutableArtifactError(RuntimeError):
    """Raised when code attempts to replace an existing evidence artifact."""


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_output(root: str | Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=Path(root), text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def working_tree_clean(root: str | Path) -> bool:
    return git_output(root, "status", "--porcelain", "--untracked-files=all") == ""


def working_tree_patch_sha256(root: str | Path) -> str | None:
    root_path = Path(root)
    if working_tree_clean(root_path):
        return None
    tracked = subprocess.run(["git", "diff", "--binary", "HEAD", "--"], cwd=root_path, capture_output=True, check=False).stdout
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root_path, capture_output=True, text=True, check=False).stdout.splitlines()
    digest = hashlib.sha256()
    digest.update(tracked)
    for relative in sorted(untracked):
        path = root_path / relative
        if path.is_file():
            digest.update(relative.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def immutable_write(path: str | Path, content: str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8")
        if existing != content:
            raise ImmutableArtifactError(f"refusing to overwrite immutable artifact: {file_path}")
        return
    file_path.write_text(content, encoding="utf-8")


def immutable_json_write(path: str | Path, value: Mapping[str, Any]) -> None:
    immutable_write(path, json.dumps(dict(value), indent=2, sort_keys=True) + "\n")


def analysis_parent(root: str | Path, protocol: str, experiment: str, run_id: str) -> Path:
    return Path(root) / "results/analyses" / protocol / experiment / run_id


def report_parent(root: str | Path, protocol: str, experiment: str, run_id: str, revision: int) -> Path:
    return Path(root) / "results/reports" / protocol / experiment / run_id / analysis_name(revision)


def allocate_analysis(root: str | Path, protocol: str, experiment: str, run_id: str) -> tuple[int, Path]:
    parent = analysis_parent(root, protocol, experiment, run_id)
    parent.mkdir(parents=True, exist_ok=True)
    for _ in range(32):
        revision = next_analysis_revision(parent)
        directory = parent / analysis_name(revision)
        try:
            directory.mkdir()
        except FileExistsError:
            continue
        return revision, directory
    raise RuntimeError("could not allocate an analysis revision")


def make_manifest(
    *,
    root: str | Path,
    protocol: str,
    experiment: str,
    run_id: str,
    revision: int,
    raw_manifest_path: str | Path,
    dataset_sha256: str | None,
    ground_truth_sha256: str | None,
    ontology_sha256: str | None,
    verifier_sha256: str | None,
    config_sha256: str | None,
    analysis_code_sha256: str | None,
    evidence_tier: str,
    dataset_version: str | None = None,
    dataset_path: str | None = None,
    attack_suite_sha256: str | None = None,
    metric_suite_sha256: str | None = None,
    status: str = "complete",
    prior_analysis: str | None = None,
    reason_for_reanalysis: str | None = None,
) -> dict[str, Any]:
    root_path = Path(root)
    report_id = make_report_id(protocol, experiment, run_id, revision)
    clean = working_tree_clean(root_path)
    raw_path = Path(raw_manifest_path)
    manifest = {
        "report_id": report_id,
        "protocol_version": protocol,
        "experiment_id": experiment,
        "run_id": run_id,
        "analysis_revision": revision,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_output(root_path, "rev-parse", "HEAD"),
        "working_tree_clean": clean,
        "working_tree_patch_sha256": None if clean else working_tree_patch_sha256(root_path),
        "dataset_sha256": dataset_sha256,
        "ground_truth_sha256": ground_truth_sha256,
        "ontology_sha256": ontology_sha256,
        "verifier_sha256": verifier_sha256,
        "config_sha256": config_sha256,
        "attack_suite_sha256": attack_suite_sha256,
        "metric_suite_sha256": metric_suite_sha256,
        "analysis_code_sha256": analysis_code_sha256,
        "raw_manifest_sha256": sha256_file(raw_path),
        "evidence_tier": evidence_tier,
        "status": status,
    }
    if dataset_version is not None:
        manifest["dataset_version"] = dataset_version
    if dataset_path is not None:
        manifest["dataset_path"] = dataset_path
    if prior_analysis is not None:
        manifest["prior_analysis"] = prior_analysis
    if reason_for_reanalysis is not None:
        manifest["reason_for_reanalysis"] = reason_for_reanalysis
    return manifest
