"""Conceptual API for ontology-derived attention bias.

The function returns a dense bias matrix, but does not execute attention.  A
future implementation can add this matrix to the scaled dot-product logits
described in the paper after independently validating its semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class AttentionBiasConfig:
    alpha: float = 0.25
    beta: float = 0.25
    gamma: float = 0.25


def ontology_attention_bias(
    tokens: Sequence[str],
    axiological_relevance: Mapping[str, float],
    normative_relevance: Mapping[str, float],
    purpose_relevance: Mapping[str, float],
    config: AttentionBiasConfig = AttentionBiasConfig(),
) -> tuple[tuple[float, ...], ...]:
    """Build a conceptual row-shared ontology bias matrix.

    Each key token receives a bias from three independently supplied semantic
    relevance channels.  This is intentionally explicit and deterministic;
    it does not infer moral relevance from text and does not claim that a
    scalar bias is an adequate representation of value.
    """

    if not tokens:
        return ()
    values = tuple(
        config.alpha * axiological_relevance.get(token, 0.0)
        + config.beta * normative_relevance.get(token, 0.0)
        + config.gamma * purpose_relevance.get(token, 0.0)
        for token in tokens
    )
    return tuple(values for _ in tokens)
