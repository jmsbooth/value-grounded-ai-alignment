"""Variant aliasing for blinded metric generation."""

from __future__ import annotations

from pathlib import Path
import secrets
from typing import Any, Mapping, Sequence

from .reporting import immutable_json_write


def make_variant_map(variants: Sequence[str], *, seed: int = 1729) -> dict[str, str]:
    del seed  # aliases are deliberately opaque; deterministic fixtures may pass explicit aliases.
    aliases = [f"VX-{index:02d}" for index in range(1, len(variants) + 1)]
    shuffled = list(aliases)
    secrets.SystemRandom().shuffle(shuffled)
    return {str(variant): shuffled[index] for index, variant in enumerate(variants)}


def blind_rows(rows: Sequence[Mapping[str, Any]], variant_map: Mapping[str, str]) -> list[dict[str, Any]]:
    blinded = []
    for row in rows:
        variant = str(row.get("variant", ""))
        if variant not in variant_map:
            raise ValueError(f"variant is not in blinding map: {variant}")
        copy = dict(row)
        copy["variant"] = variant_map[variant]
        blinded.append(copy)
    return blinded


def audit_blind_rows(rows: Sequence[Mapping[str, Any]], *, aliases: Sequence[str]) -> dict[str, Any]:
    alias_set = set(aliases)
    leaked_fields = ["model_variant", "variant_name", "architecture"]
    leaks = [{"field": field, "row": index} for index, row in enumerate(rows) for field in leaked_fields if field in row]
    invalid_aliases = sorted({str(row.get("variant")) for row in rows if row.get("variant") not in alias_set})
    return {"leaks": leaks, "invalid_aliases": invalid_aliases, "passed": not leaks and not invalid_aliases}


def write_variant_map(path: str | Path, variant_map: Mapping[str, str]) -> None:
    immutable_json_write(path, {"variant_map": dict(variant_map), "purpose": "sealed unblinding map; not used during raw metric generation"})
