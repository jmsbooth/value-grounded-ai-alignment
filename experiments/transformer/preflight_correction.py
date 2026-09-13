#!/usr/bin/env python3
"""Record the v0.6.2 starting boundary and protected historical hashes."""

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

PROTOCOL = "te-v0.6.2-pythia-correction"
BASE_COMMIT = "0598a9795b5cb2721d26e9c0950377bae52676c0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_hash(root: Path, *, exclude_parts: set[str] | None = None) -> dict[str, str]:
    exclude_parts = exclude_parts or set()
    if not root.exists():
        return {}
    return {
        str(path.relative_to(ROOT)): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not (set(path.relative_to(root).parts) & exclude_parts) and path.name != ".DS_Store"
    }


def digest_mapping(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=list).encode()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def collect() -> dict[str, object]:
    total, used, free = shutil.disk_usage(ROOT)
    del total, used
    packages: dict[str, str | None] = {}
    for name in ("torch", "transformers", "peft", "safetensors", "psutil", "accelerate", "tokenizers", "numpy", "PyYAML", "pytest"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    paper = tree_hash(ROOT / "paper", exclude_parts={"build"})
    historical = {
        "docs": tree_hash(ROOT / "docs/experiments/te-v0.6.1-pythia-development"),
        "raw": tree_hash(ROOT / "results/raw/te-v0.6.1-pythia-development"),
        "reports": tree_hash(ROOT / "results/reports/te-v0.6.1-pythia-development"),
    }
    try:
        from vgta_transformer.model_loader import EXPECTED_CONFIG, MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA, snapshot_asset_digest
        asset_digest, asset_count = snapshot_asset_digest(local_files_only=True)
        model = {"model_id": MODEL_ID, "requested_revision": REQUESTED_REVISION, "resolved_revision_sha": RESOLVED_REVISION_SHA, "expected_config": EXPECTED_CONFIG, "asset_digest": asset_digest, "asset_file_count": asset_count}
    except Exception as exc:
        model = {"error": f"{type(exc).__name__}: {exc}"}
    return {
        "protocol": PROTOCOL,
        "spec_id": "VGA-SDD-TE-0062",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reviewed_parent_commit": BASE_COMMIT,
        "repo": {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"), "status": git("status", "--short"), "worktree_clean": not bool(git("status", "--porcelain"))},
        "model": model,
        "environment": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": platform.python_version(), "cpu_count": __import__("os").cpu_count(), "packages": packages, "environment_digest": digest_mapping(packages)},
        "resources": {"disk_free_bytes": free, "disk_free_gib": round(free / 2**30, 3), "ram_gib": round(__import__("psutil").virtual_memory().total / 2**30, 3) if packages.get("psutil") else None, "accelerator_policy": "cpu-or-explicit-mps", "unsafe_mps_watermark_override": False},
        "protected": {"paper": paper, "paper_tree_digest": digest_mapping(paper), "historical": historical, "historical_tree_digests": {key: digest_mapping(value) for key, value in historical.items()}},
        "exclusions": ["locked dataset contents", "credentials", "private keys", "environment secrets", "system .DS_Store files"],
        "authorization": {"locked_cohort": False, "external_upload": False, "push": False, "manuscript_regeneration": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/experiments/te-v0.6.2-pythia-correction")
    args = parser.parse_args()
    report = collect()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    text = f"""# v0.6.2 Pythia correction preflight

Created: `{report['created_at']}`  
Reviewed parent commit: `{BASE_COMMIT}`  
Observed starting commit: `{report['repo']['head']}`  
Worktree clean at capture: `{report['repo']['worktree_clean']}`

This receipt records the Pythia identity, runtime packages, local resource
boundary, and byte hashes for the frozen manuscript plus v0.6.1 documents,
raw outputs, and reports. These historical artifacts are protected inputs and
must not be regenerated or overwritten. Locked dataset contents, secrets, and
system `.DS_Store` files are excluded.

Free disk at capture: `{report['resources']['disk_free_gib']}` GiB. RAM:
`{report['resources']['ram_gib']}` GiB. The correction phase permits one
resident model, fresh child attempts, CPU or explicit MPS, float32, and no
unsafe MPS watermark override. Locked execution, upload, push, and manuscript
regeneration remain unauthorized.

See `preflight.json` for the complete hash manifests and environment receipt.
"""
    (args.output_dir / "preflight-inventory.md").write_text(text, encoding="utf-8")
    print(json.dumps({"status": "CORRECTION_PREFLIGHT_RECORDED", "paper_tree_digest": report["protected"]["paper_tree_digest"], "disk_free_gib": report["resources"]["disk_free_gib"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
