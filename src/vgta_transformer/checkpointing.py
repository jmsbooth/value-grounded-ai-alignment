"""Checkpoint and reload helpers for adapter/head diagnostics."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_checkpoint(path: str | Path, model: Any, *, auxiliary_heads: Any | None = None, optimizer: Any | None = None, scheduler: Any | None = None, scaler: Any | None = None, random_state: Any | None = None, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
    import torch
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(directory / "adapter")
    if auxiliary_heads is not None:
        torch.save(auxiliary_heads.state_dict(), directory / "auxiliary-heads.pt")
    if optimizer is not None:
        torch.save(optimizer.state_dict(), directory / "optimizer.pt")
    if scheduler is not None:
        torch.save(scheduler.state_dict(), directory / "scheduler.pt")
    if scaler is not None:
        torch.save(scaler.state_dict(), directory / "scaler.pt")
    if random_state is not None:
        torch.save(random_state, directory / "random-state.pt")
    metadata_path = directory / "metadata.json"
    metadata_path.write_text(json.dumps(dict(metadata or {}), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hashes = {str(file.relative_to(directory)): _sha256(file) for file in directory.rglob("*") if file.is_file() and file.name != "checksums.json"}
    (directory / "checksums.json").write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return hashes


def load_training_state(path: str | Path, *, optimizer: Any | None = None, scheduler: Any | None = None, scaler: Any | None = None) -> dict[str, Any]:
    """Load mutable training state after a checksum-verified checkpoint."""

    import torch
    directory = Path(path)
    if not all(verify_checkpoint(directory).values()):
        raise ValueError(f"checkpoint verification failed: {directory}")
    for target, filename in ((optimizer, "optimizer.pt"), (scheduler, "scheduler.pt"), (scaler, "scaler.pt")):
        if target is not None and (directory / filename).exists():
            target.load_state_dict(torch.load(directory / filename, map_location="cpu", weights_only=False))
    return torch.load(directory / "random-state.pt", map_location="cpu", weights_only=False) if (directory / "random-state.pt").exists() else {}


def verify_checkpoint(path: str | Path) -> dict[str, bool]:
    directory = Path(path)
    expected = json.loads((directory / "checksums.json").read_text(encoding="utf-8"))
    return {name: (directory / name).exists() and _sha256(directory / name) == digest for name, digest in expected.items() if name != "checksums.json"}
