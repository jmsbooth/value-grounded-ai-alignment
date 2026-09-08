"""Episode-level semantic state boundary for future reasoning experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class SemanticState:
    goal: str | None = None
    entities: list[str] = field(default_factory=list)
    relationships: list[dict[str, str]] = field(default_factory=list)
    current_purpose: str | None = None
    affected_moral_patients: list[str] = field(default_factory=list)
    relevant_values: list[str] = field(default_factory=list)
    applicable_norms: list[str] = field(default_factory=list)
    known_constraints: list[str] = field(default_factory=list)
    uncertainty: dict[str, float] = field(default_factory=dict)
    potential_harms: list[str] = field(default_factory=list)
    capabilities_affected: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
