#!/usr/bin/env python3
"""Dependency-light Pythia phase preflight."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import importlib.metadata
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.evidence_receipts import make_receipt, write_receipt
from vgta_transformer.model_loader import EXPECTED_CONFIG, MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()


def collect() -> dict[str, object]:
    total, used, free = shutil.disk_usage(ROOT)
    modules = {name: importlib.util.find_spec(name) is not None for name in ("torch", "transformers", "peft", "safetensors", "psutil")}
    package_names = ("torch", "transformers", "peft", "safetensors", "psutil", "accelerate", "tokenizers", "numpy", "PyYAML", "pytest")
    resolved_packages = {}
    for package in package_names:
        try:
            resolved_packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            resolved_packages[package] = None
    environment_digest = hashlib.sha256(json.dumps(resolved_packages, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "protocol": "te-v0.6.0-pythia",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repo": {"head": _git("rev-parse", "HEAD"), "branch": _git("branch", "--show-current"), "worktree_clean": not bool(_git("status", "--porcelain"))},
        "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "processor": platform.processor(), "python": platform.python_version(), "cpu_count": os.cpu_count()},
        "memory_and_disk": {"disk_free_bytes": free, "disk_total_bytes": total, "disk_free_gib": round(free / 2**30, 3)},
        "accelerators": {"cuda_available": False, "mps_possible": platform.system() == "Darwin" and platform.machine() == "arm64"},
        "dependencies": modules,
        "resolved_packages": resolved_packages,
        "environment_digest": environment_digest,
        "model": {"model_id": MODEL_ID, "requested_revision": REQUESTED_REVISION, "resolved_revision_sha": RESOLVED_REVISION_SHA, "expected_config": EXPECTED_CONFIG, "cache_configured": bool(os.environ.get("VGTA_PYTHIA_CACHE"))},
        "constraints": {"paid_compute": False, "external_upload": False, "publish": False, "push": False, "locked_run": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/reports/te-v0.6.0-pythia/preflight")
    args = parser.parse_args()
    report = collect()
    report["status"] = "PREFLIGHT_RECORDED"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "preflight.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_receipt(args.output_dir / "evidence-receipt.json", make_receipt(
        producer_kind="preflight", protocol="te-v0.6.0-pythia", status="PREFLIGHT_RECORDED",
        model_revision_sha=RESOLVED_REVISION_SHA, dependencies=report["dependencies"], environment_digest=report["environment_digest"], disk_free_gib=report["memory_and_disk"]["disk_free_gib"],
    ))
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
