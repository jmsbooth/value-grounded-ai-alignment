#!/usr/bin/env python3
"""Emit an executable training-contract receipt from the isolated test suite."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results/reports/te-v0.6.1-pythia-development/training-contracts.json")
    args = parser.parse_args()
    command = [sys.executable, "-m", "pytest", "-q", "tests/transformer/test_training_contracts.py", "tests/transformer/test_response_parser.py"]
    completed = subprocess.run(command, cwd=ROOT, env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")}, capture_output=True, text=True, check=False)
    result = {
        "protocol": "te-v0.6.1-pythia-development",
        "experiment_id": "training-contract-tests",
        "status": "TRAINING_CONTRACT_VALIDATED" if completed.returncode == 0 else "TRAINING_CONTRACT_REJECTED",
        "command": command,
        "return_code": completed.returncode,
        "test_output": completed.stdout + completed.stderr,
        "checks": {
            "manual_response_loss": completed.returncode == 0,
            "continuation_extraction_and_parser": completed.returncode == 0,
            "optimizer_and_auxiliary_contracts": completed.returncode == 0,
            "checkpoint_and_random_state": completed.returncode == 0,
        },
        "backend": "isolated-or-current-python",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "return_code": completed.returncode}, sort_keys=True))
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
