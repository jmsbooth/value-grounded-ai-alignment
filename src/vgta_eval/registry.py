"""Append-only, lock-protected registries for research history."""

from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
from typing import Any, Iterator, Mapping

try:  # pragma: no cover - exercised on the Unix research host
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class RegistryError(ValueError):
    """Raised when an append-only registry would lose traceability."""


@contextmanager
def _registry_lock(path: Path) -> Iterator[None]:
    lock_path = path.parent / ".registry.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    if not file_path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RegistryError(f"invalid JSON in {file_path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise RegistryError(f"registry record must be an object: {file_path}:{line_number}")
        records.append(record)
    return records


def append_unique(path: str | Path, record: Mapping[str, Any], *, identity_field: str) -> dict[str, Any]:
    """Append one record, rejecting duplicate identities under an exclusive lock."""

    file_path = Path(path)
    if identity_field not in record or not str(record[identity_field]):
        raise RegistryError(f"record is missing identity field {identity_field}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    materialized = dict(record)
    with _registry_lock(file_path):
        existing = read_jsonl(file_path)
        identity = str(materialized[identity_field])
        if any(str(item.get(identity_field)) == identity for item in existing):
            raise RegistryError(f"duplicate {identity_field}: {identity}")
        with file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(materialized, sort_keys=True) + "\n")
            handle.flush()
        return materialized


def validate_registry(path: str | Path, *, identity_field: str) -> list[dict[str, Any]]:
    records = read_jsonl(path)
    identities = [str(record.get(identity_field, "")) for record in records]
    if any(not identity for identity in identities):
        raise RegistryError(f"{path} contains a record without {identity_field}")
    if len(identities) != len(set(identities)):
        raise RegistryError(f"{path} contains duplicate {identity_field} values")
    return records


def write_json(path: str | Path, value: Mapping[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")
