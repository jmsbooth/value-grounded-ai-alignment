"""Metadata-first normative assertions and conflict states."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NormativeAuthority:
    source: str
    authority: str
    jurisdiction: str
    precedence: int = 0
    confidence: float = 1.0
    version: str = "unversioned"


@dataclass(frozen=True)
class NormativeAssertion:
    identifier: str
    proposition: str
    authority: NormativeAuthority
    effective_from: str | None = None
    effective_until: str | None = None
    scope: str | None = None
    exceptions: tuple[str, ...] = ()
    truth_claim: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "identifier": self.identifier,
            "proposition": self.proposition,
            "authority": self.authority.__dict__,
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "scope": self.scope,
            "exceptions": list(self.exceptions),
            "truth_claim": self.truth_claim,
        }


@dataclass(frozen=True)
class NormativeConflict:
    left: str
    right: str
    reason: str
    state: str = "unresolved"
    options: tuple[str, ...] = (
        "precedence",
        "context_required",
        "authorized_profile",
        "abstain",
        "escalate",
        "uncertain",
    )
    notes: tuple[str, ...] = field(default_factory=tuple)


def authority_function(assertion: NormativeAssertion) -> NormativeAuthority:
    """Expose Auth(n) as metadata; it is not a scalar moral-weight function."""

    return assertion.authority


def classify_conflict(
    left: NormativeAssertion,
    right: NormativeAssertion,
) -> NormativeConflict:
    """Return a conflict state without converting authority into moral weight."""

    same_scope = left.scope is not None and left.scope == right.scope
    same_jurisdiction = left.authority.jurisdiction == right.authority.jurisdiction
    reason = "propositions are marked as incompatible"
    if not same_scope or not same_jurisdiction:
        reason += "; applicability context is required"
    return NormativeConflict(
        left=left.identifier,
        right=right.identifier,
        reason=reason,
        notes=("authority metadata resolves governed applicability, not moral truth",),
    )


def resolve_conflict(
    conflict: NormativeConflict,
    *,
    context_available: bool = False,
    authorized_profile_available: bool = False,
    human_escalation_available: bool = True,
) -> str:
    """Select a governance outcome from explicit state, never a scalar score."""

    if context_available:
        return "context_required"
    if authorized_profile_available:
        return "authorized_profile"
    if human_escalation_available:
        return "escalate"
    return "abstain" if conflict.state == "unresolved" else "uncertain"
