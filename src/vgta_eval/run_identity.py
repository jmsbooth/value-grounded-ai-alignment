"""Collision-resistant identities for immutable research artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
import re
import secrets
from pathlib import Path


RUN_ID_PATTERN = re.compile(r"^\d{8}T\d{6}Z-[0-9a-f]{6,32}$")
ANALYSIS_PATTERN = re.compile(r"^analysis-r(\d{3,})$")


def utc_timestamp(value: datetime | None = None) -> str:
    """Return a second-resolution UTC timestamp suitable for an artifact ID."""

    current = value or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def new_run_id(*, now: datetime | None = None, suffix: str | None = None) -> str:
    """Create a run ID without relying on a count of existing files."""

    token = suffix or secrets.token_hex(3)
    if not re.fullmatch(r"[0-9a-f]{6,32}", token):
        raise ValueError("run suffix must be 6-32 lowercase hexadecimal characters")
    run_id = f"{utc_timestamp(now)}-{token}"
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError(f"invalid generated run ID: {run_id}")
    return run_id


def validate_run_id(run_id: str) -> str:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError(f"invalid run ID: {run_id}")
    return run_id


def reserve_run_directory(parent: str | Path, *, prefix: str = "", now: datetime | None = None) -> tuple[str, Path]:
    """Atomically reserve a unique run directory under ``parent``."""

    root = Path(parent)
    root.mkdir(parents=True, exist_ok=True)
    for _ in range(32):
        run_id = new_run_id(now=now)
        candidate = root / f"{prefix}{run_id}"
        try:
            candidate.mkdir()
        except FileExistsError:
            continue
        return run_id, candidate
    raise RuntimeError("could not reserve a unique run directory after 32 attempts")


def analysis_name(revision: int) -> str:
    if revision < 1:
        raise ValueError("analysis revision must be positive")
    return f"analysis-r{revision:03d}"


def parse_analysis_revision(name: str) -> int:
    match = ANALYSIS_PATTERN.fullmatch(name)
    if not match:
        raise ValueError(f"invalid analysis directory name: {name}")
    return int(match.group(1))


def next_analysis_revision(parent: str | Path) -> int:
    root = Path(parent)
    revisions = []
    if root.exists():
        for child in root.iterdir():
            if child.is_dir() and ANALYSIS_PATTERN.fullmatch(child.name):
                revisions.append(parse_analysis_revision(child.name))
    return max(revisions, default=0) + 1


def make_report_id(protocol: str, experiment: str, run_id: str, revision: int) -> str:
    """Return the globally unique, human-readable report identity."""

    validate_run_id(run_id)
    if revision < 1:
        raise ValueError("analysis revision must be positive")
    for value, label in ((protocol, "protocol"), (experiment, "experiment")):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
            raise ValueError(f"invalid {label} identifier: {value}")
    return f"{protocol}__{experiment}__{run_id}__a{revision:03d}"
