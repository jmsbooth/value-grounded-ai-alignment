"""Single source of truth for corrected v0.6.2 arm fidelity."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VariantSpec:
    name: str
    input_mode: str
    auxiliary_heads: tuple[str, ...]
    auxiliary_weights: dict[str, float]
    span_weight_fields: tuple[str, ...]
    shuffled_targets: tuple[str, ...]

    @property
    def structured(self) -> bool:
        return self.input_mode == "exact-b-structured"

    @property
    def fingerprint(self) -> str:
        value = {"name": self.name, "input_mode": self.input_mode, "auxiliary_heads": self.auxiliary_heads, "auxiliary_weights": self.auxiliary_weights, "span_weight_fields": self.span_weight_fields, "shuffled_targets": self.shuffled_targets}
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_variant_specs(path: str | Path) -> dict[str, VariantSpec]:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyYAML is required to load a protocol variant plan") from exc
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    result: dict[str, VariantSpec] = {}
    for name, value in raw.get("variants", {}).items():
        result[name] = VariantSpec(
            name=name,
            input_mode=str(value["input_mode"]),
            auxiliary_heads=tuple(value.get("auxiliary_heads", ())),
            auxiliary_weights={str(k): float(v) for k, v in value.get("auxiliary_weights", {}).items()},
            span_weight_fields=tuple(value.get("span_weight_fields", ())),
            shuffled_targets=tuple(value.get("shuffled_targets", ())),
        )
    if len(result) != 8:
        raise ValueError(f"v0.6.2 requires eight declared arms, found {len(result)}")
    return result
