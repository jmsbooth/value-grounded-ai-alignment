"""Governed canonical axiology and its non-authoritative neural derivative.

The repository does not train a neural module. These types make the authority
boundary explicit so future experiments cannot accidentally treat a learned
representation as the canonical source of values.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class CanonicalAxiology:
    """External, versioned, provenance-bearing axiological source."""

    version: str
    ontology_format: str = "typed-graph"
    source: str = "governed-external-source"
    provenance: tuple[str, ...] = ()
    content_identifier_method: str = "deployment-assigned-digest"
    content_digest: str | None = None
    immutable_in_deployment: bool = True

    def __post_init__(self) -> None:
        if not self.version:
            raise ValueError("version must not be empty")
        if not self.content_identifier_method:
            raise ValueError("content_identifier_method must not be empty")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def compile(
        self,
        module_id: str = "axiological-module-interface",
        feature_names: Sequence[str] = (),
    ) -> "AxiologicalNeuralModule":
        return compile_axiology(self, module_id=module_id, feature_names=feature_names)


@dataclass(frozen=True)
class AxiologicalNeuralModule:
    """Derived learned or hybrid module; never the canonical authority."""

    version: str
    module_id: str
    feature_names: tuple[str, ...] = ()
    compiled_from_digest: str | None = None
    training_status: str = "interface-only"
    authoritative: bool = False

    def __post_init__(self) -> None:
        if not self.version or not self.module_id:
            raise ValueError("version and module_id must not be empty")
        if self.authoritative:
            raise ValueError("AxiologicalNeuralModule cannot be authoritative")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def compile_axiology(
    canonical: CanonicalAxiology,
    module_id: str = "axiological-module-interface",
    feature_names: Sequence[str] = (),
) -> AxiologicalNeuralModule:
    """Create a provenance-linked module record without pretending to train it."""

    return AxiologicalNeuralModule(
        version=canonical.version,
        module_id=module_id,
        feature_names=tuple(feature_names),
        compiled_from_digest=canonical.content_digest,
    )
