#!/usr/bin/env python3
"""Record v0.6.1 source, environment, and protected-artifact preflight."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_transformer.model_loader import EXPECTED_CONFIG, MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def protected_hashes() -> dict[str, str]:
    result: dict[str, str] = {}
    paper = ROOT / "paper"
    for path in sorted(path for path in paper.rglob("*") if path.is_file() and "build" not in path.relative_to(paper).parts):
        result[str(path.relative_to(ROOT))] = digest_file(path)
    return result


def research_source_paths() -> list[Path]:
    roots = [ROOT / "src", ROOT / "experiments/transformer", ROOT / "experiments/protocols/te-v0.6.1-pythia-development", ROOT / "tests/transformer"]
    paths: list[Path] = []
    for base in roots:
        if base.exists():
            paths.extend(path for path in base.rglob("*") if path.is_file() and path.name != ".DS_Store")
    return sorted(set(paths))


def source_manifest(paths: list[Path]) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): digest_file(path) for path in paths}


def collect(output_dir: Path) -> dict[str, object]:
    total, used, free = shutil.disk_usage(ROOT)
    del used
    packages = {}
    for name in ("torch", "transformers", "peft", "safetensors", "psutil", "accelerate", "tokenizers", "numpy", "PyYAML", "pytest"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    paths = research_source_paths()
    manifest = source_manifest(paths)
    manifest_json = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    diff = git("diff", "--no-ext-diff", "--binary", "--", ".", ":(exclude)paper/**")
    model_asset_digest = None
    asset_file_count = None
    try:
        from vgta_transformer.model_loader import snapshot_asset_digest
        model_asset_digest, asset_file_count = snapshot_asset_digest(local_files_only=True)
    except Exception as exc:  # cache/model identity remains explicit when optional lookup is unavailable
        model_asset_digest = f"unavailable:{type(exc).__name__}"
    return {
        "protocol": "te-v0.6.1-pythia-development",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": {
            "head": git("rev-parse", "HEAD"),
            "branch": git("branch", "--show-current"),
            "status": git("status", "--short"),
            "worktree_clean": not bool(git("status", "--porcelain")),
            "dirty_patch_sha256": digest_bytes(diff.encode()),
        },
        "source_inventory": {"files": manifest, "untracked_source_manifest_sha256": digest_bytes(manifest_json), "excluded": ["credentials", "private_keys", "environment_secrets", "system_.DS_Store_files", "locked_dataset_contents"]},
        "protected_paper_tree": {"files": protected_hashes(), "tree_digest": digest_bytes(json.dumps(protected_hashes(), sort_keys=True, separators=(",", ":")).encode())},
        "source_derived_starting_state": {
            "model_asset_digest": "d65a3c37a54360759a43bcb05b80df1ddbb982ed0a1d2b97bb67746d5c07a9c7",
            "dataset": "pythia-policy-dev-v1 historical fixture; v2 not yet available",
            "training": "one-step diagnostic only",
            "historical_generation_status": "five previous parse failures; raw strings may be unavailable locally",
        },
        "current_model": {"model_id": MODEL_ID, "requested_revision": REQUESTED_REVISION, "resolved_revision_sha": RESOLVED_REVISION_SHA, "expected_config": EXPECTED_CONFIG, "asset_digest": model_asset_digest, "asset_file_count": asset_file_count},
        "environment": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": platform.python_version(), "cpu_count": __import__("os").cpu_count(), "packages": packages, "environment_digest": digest_bytes(json.dumps(packages, sort_keys=True, separators=(",", ":")).encode())},
        "resources": {"disk_free_bytes": free, "disk_free_gib": round(free / 2**30, 3), "ram_gib_recorded_parent": 16, "accelerator_policy": "cpu-or-explicit-mps; no CUDA assumption"},
        "budget": {"phase_wall_hours": 8, "attempt_wall_hours": 2, "resident_models": 1, "paid_compute": False, "external_upload": False, "push": False, "locked_cohort": False},
        "command_graph": {"allowed": ["te-dev-preflight", "te-audit-generations", "te-test-training-contracts", "te-profile-resources", "te-build-dev-data", "te-validate-dev-data", "te-train-memorization", "te-train-a1-dev", "te-test-aux-gradients", "te-run-variant-smoke", "te-evaluate-trained-dev", "te-analyze-dev", "te-dev-gate"], "blocked_or_out_of_scope": ["make all", "make paper-from-results", "legacy aggregate analysis", "te-freeze-cohort", "te-run-cohort", "OLMo", "C3", "structural-attention", "MoE", "solver-backed production"]},
        "requirement_map": {
            "WP1": ["src/vgta_transformer/response_parser.py", "tests/transformer/test_response_parser.py"],
            "WP2": ["src/vgta_transformer/losses.py", "src/vgta_transformer/training.py", "src/vgta_transformer/checkpointing.py", "tests/transformer/test_training_contracts.py"],
            "WP3": ["experiments/transformer/resource_profile.py"],
            "WP4-WP6": ["experiments/transformer/train_memorization.py", "experiments/transformer/train_a1_dev.py"],
            "WP5": ["src/vgta_eval/semantic_worlds.py", "experiments/transformer/build_dataset.py", "experiments/transformer/validate_dev_data.py"],
            "WP7-WP8": ["experiments/transformer/variant_smoke.py", "experiments/transformer/evaluate_trained_dev.py", "experiments/transformer/development_readiness.py"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/experiments/te-v0.6.1-pythia-development")
    args = parser.parse_args()
    report = collect(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v0.6.1 Pythia development preflight",
        "",
        f"Created: `{report['created_at']}`  ",
        f"Starting commit: `{report['repo']['head']}`; branch: `{report['repo']['branch']}`; worktree clean: `{report['repo']['worktree_clean']}`.",
        "",
        "This is a dirty-tree-capable local development preflight. The exact commit, dirty patch digest, approved research-source manifest, dependency versions, model identity, and protected paper-tree hashes are recorded in `preflight.json`. System `.DS_Store` files and locked dataset contents were excluded from source-content inventories; no credentials or environment secrets were captured.",
        "",
        "## Protected boundary",
        "",
        "The existing manuscript and all files under `paper/**` (excluding ignored build output) are byte-hashed before execution. The v1 dataset, including its existing locked files, and historical reports/raw outputs are preserved. This phase will not run `make all`, `make paper-from-results`, legacy aggregate analyses, `te-freeze-cohort`, or `te-run-cohort`.",
        "",
        "## Source-derived versus current state",
        "",
        "The supplied starting state records the verified Pythia checkpoint, a one-step LoRA diagnostic, and five historical parser failures. The current state is a dirty development checkout with the same reviewed base model identity and a new v0.6.1 protocol. The new v2 benchmark is generated separately; the v1 fixture is not regenerated or scored by this phase.",
        "",
        "## Resources and budget",
        "",
        f"At preflight, free disk was `{report['resources']['disk_free_gib']}` GiB. The permitted budget is 8 wall-hours for the phase, 2 wall-hours per attempt, one resident model, float32 CPU or explicitly available MPS, no paid compute, no upload, and no push. The local host is resource constrained, so a partial but durable result is valid and a locked cohort remains unauthorized.",
        "",
        "## Requirement map",
        "",
    ]
    for key, paths in report["requirement_map"].items():
        lines.append(f"- `{key}`: " + ", ".join(f"`{path}`" for path in paths))
    lines.extend(["", "See `preflight.json` for the complete status inventory, command graph, hashes, and exclusions.", ""])
    (args.output_dir / "preflight.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "PREFLIGHT_RECORDED", "output_dir": str(args.output_dir), "paper_tree_digest": report["protected_paper_tree"]["tree_digest"], "disk_free_gib": report["resources"]["disk_free_gib"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
