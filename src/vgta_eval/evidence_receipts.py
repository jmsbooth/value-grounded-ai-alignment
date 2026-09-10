"""Small, machine-readable provenance receipts for new experiment outputs."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


PRODUCER_KINDS = frozenset({
    "known_fixture",
    "semantic_audit",
    "preflight",
    "model_smoke",
    "training_diagnostic",
    "model_prediction",
    "analysis",
    "gate",
    "historical_qualification",
})


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def make_receipt(*, producer_kind: str, protocol: str, status: str, **payload: Any) -> dict[str, Any]:
    if producer_kind not in PRODUCER_KINDS:
        raise ValueError(f"unsupported producer_kind: {producer_kind}")
    receipt = {
        "receipt_version": "evidence-receipt-v1",
        "producer_kind": producer_kind,
        "protocol": protocol,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        **payload,
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt


def write_receipt(path: str | Path, receipt: Mapping[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(dict(receipt), indent=2, sort_keys=True) + "\n", encoding="utf-8")

