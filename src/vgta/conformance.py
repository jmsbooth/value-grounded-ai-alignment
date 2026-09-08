"""Empirical conformance probes for a derived axiological module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ConformanceResult:
    """A descriptive relation-recovery result, not a semantic proof."""

    conforms: bool
    relation_recovery: float
    tested_relations: int
    missing_relations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


def evaluate_conformance(
    canonical_relations: Iterable[str],
    neural_relations: Iterable[str],
    *,
    minimum_recovery: float = 1.0,
) -> ConformanceResult:
    """Compare relation labels recovered by a module with canonical labels.

    This deliberately small probe is useful for deterministic interface tests.
    Empirical work must replace it with held-out relation probes, graph
    completion controls, concept-direction stability, behavior probes, and
    representation-drift tests.
    """

    canonical = set(canonical_relations)
    neural = set(neural_relations)
    if not 0.0 <= minimum_recovery <= 1.0:
        raise ValueError("minimum_recovery must be between zero and one")
    if not canonical:
        return ConformanceResult(
            conforms=not neural,
            relation_recovery=1.0 if not neural else 0.0,
            tested_relations=0,
            missing_relations=(),
            notes=("empty canonical relation set; no semantic conclusion",),
        )
    recovered = canonical.intersection(neural)
    recovery = len(recovered) / len(canonical)
    missing = tuple(sorted(canonical - neural))
    return ConformanceResult(
        conforms=recovery >= minimum_recovery and not (neural - canonical),
        relation_recovery=recovery,
        tested_relations=len(canonical),
        missing_relations=missing,
        notes=("relation-recovery interface only; not a proof of meaning",),
    )
