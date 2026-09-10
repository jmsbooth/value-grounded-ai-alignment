"""Fail-closed ordering guards for the Pythia phase."""

from __future__ import annotations

import json
from pathlib import Path


def require_semantic_gate(root: Path) -> None:
    path = root / "results/reports/te-v0.6.0-pythia/semantic-validity/semantic-audit.json"
    if not path.exists():
        raise RuntimeError("semantic gate is absent; run te-semantic-audit before loading Pythia")
    status = json.loads(path.read_text(encoding="utf-8")).get("status")
    if status != "SEMANTIC_DATASET_VALIDATED":
        raise RuntimeError(f"semantic gate is not passing: {status}")

