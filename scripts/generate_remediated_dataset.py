#!/usr/bin/env python3
"""Materialize the split-remediated harness dataset."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.scenario_generator import REMEDIATED_DATASET_VERSION, write_remediated_dataset


def main() -> int:
    target = ROOT / "experiments/datasets" / REMEDIATED_DATASET_VERSION
    manifest = write_remediated_dataset(target)
    print(json.dumps({"dataset": REMEDIATED_DATASET_VERSION, "path": str(target.relative_to(ROOT)), "manifest": manifest}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
