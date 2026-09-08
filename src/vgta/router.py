"""Interface boundary for ontology-conditioned sparse expert routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class RoutingContext:
    values: tuple[str, ...] = ()
    norms: tuple[str, ...] = ()
    purpose: str | None = None


class OntologyConditionedRouter:
    """Future MoE router interface; no routing policy is silently invented."""

    def __init__(self, experts: Sequence[str]):
        if not experts or len(set(experts)) != len(experts):
            raise ValueError("experts must be a non-empty sequence of unique names")
        self.experts = tuple(experts)

    def route(
        self,
        hidden_state: Sequence[float],
        context: RoutingContext,
        k: int = 2,
    ) -> tuple[str, ...]:
        del hidden_state, context, k
        raise NotImplementedError(
            "Ontology-conditioned routing requires a trained experimental model"
        )
