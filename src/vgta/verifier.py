"""Independent action-verification interfaces and a tiny transparent fixture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CandidateAction:
    name: str
    authorized: bool = True
    consent_obtained: bool = True
    touches_private_data: bool = False
    coercive: bool = False
    predicted_harm: float = 0.0
    semantic_completeness: float = 1.0


@dataclass(frozen=True)
class VerificationResult:
    permitted: bool
    reasons: tuple[str, ...]


class ConstraintVerifier(Protocol):
    def verify(self, action: CandidateAction) -> VerificationResult:
        ...


class RuleBasedVerifier:
    """Small deterministic fixture; not an SMT solver or production control."""

    def verify(self, action: CandidateAction) -> VerificationResult:
        reasons: list[str] = []
        if not action.authorized:
            reasons.append("authorization is absent")
        if action.touches_private_data and not action.consent_obtained:
            reasons.append("private-data action lacks consent")
        if action.coercive:
            reasons.append("action is marked coercive")
        if action.predicted_harm > 0.8:
            reasons.append("predicted harm exceeds toy threshold")
        if not 0.0 <= action.semantic_completeness <= 1.0:
            reasons.append("action semantic completeness is outside [0, 1]")
        elif action.semantic_completeness < 1.0:
            reasons.append("action semantic state is incomplete")
        return VerificationResult(permitted=not reasons, reasons=tuple(reasons))
