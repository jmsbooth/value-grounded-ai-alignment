"""Transparent synthetic action-selection model used for repository examples."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .verifier import CandidateAction, RuleBasedVerifier


@dataclass(frozen=True)
class ScenarioAction:
    name: str
    task_utility: float
    value_features: Mapping[str, float]
    candidate: CandidateAction


@dataclass(frozen=True)
class Scenario:
    name: str
    actions: tuple[ScenarioAction, ...]
    value_weights: Mapping[str, float]
    expected_safe_action: str


@dataclass(frozen=True)
class Decision:
    selected_action: str
    score: float
    verifier_permitted: bool
    verifier_reasons: tuple[str, ...]


def score_action(action: ScenarioAction, value_weights: Mapping[str, float]) -> float:
    value_term = sum(
        value_weights.get(feature, 0.0) * magnitude
        for feature, magnitude in action.value_features.items()
    )
    return action.task_utility + value_term


def choose_action(
    scenario: Scenario,
    method: str = "vga_toy",
    verify: bool = True,
) -> Decision:
    if method not in {"baseline", "vga_toy"}:
        raise ValueError("method must be 'baseline' or 'vga_toy'")
    verifier = RuleBasedVerifier()
    ranked = sorted(
        scenario.actions,
        key=lambda action: (
            score_action(action, scenario.value_weights)
            if method == "vga_toy"
            else action.task_utility
        ),
        reverse=True,
    )
    for action in ranked:
        result = verifier.verify(action.candidate)
        if not verify or result.permitted:
            return Decision(
                selected_action=action.name,
                score=score_action(action, scenario.value_weights)
                if method == "vga_toy"
                else action.task_utility,
                verifier_permitted=result.permitted,
                verifier_reasons=result.reasons,
            )
    raise RuntimeError("no candidate action passed the toy verifier")
