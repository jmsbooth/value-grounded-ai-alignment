#!/usr/bin/env python3
"""Capture final source/protected-paper state and fail on paper drift."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.transformer.preflight_development import collect


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", type=Path, default=ROOT / "docs/experiments/te-v0.6.1-pythia-development/preflight.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/experiments/te-v0.6.1-pythia-development/final-state.json")
    args = parser.parse_args()
    start = json.loads(args.preflight.read_text(encoding="utf-8"))
    end = collect(args.output.parent)
    start_digest = start["protected_paper_tree"]["tree_digest"]
    end_digest = end["protected_paper_tree"]["tree_digest"]
    check = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True, check=False)
    result = {"protocol": "te-v0.6.1-pythia-development", "status": "FROZEN_ARTIFACTS_VERIFIED" if start_digest == end_digest and check.returncode == 0 else "FROZEN_ARTIFACTS_DRIFTED", "start_paper_tree_digest": start_digest, "end_paper_tree_digest": end_digest, "paper_tree_unchanged": start_digest == end_digest, "diff_check": check.returncode == 0, "final_source_state": end}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "paper_tree_unchanged": result["paper_tree_unchanged"], "diff_check": result["diff_check"]}, sort_keys=True))
    return 0 if result["status"] == "FROZEN_ARTIFACTS_VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
