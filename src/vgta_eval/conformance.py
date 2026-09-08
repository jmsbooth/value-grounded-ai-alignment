"""Candidate-action normalization and fixed-verifier evaluation helpers."""

from __future__ import annotations

from typing import Any, Mapping

from vgta.verifier import CandidateAction, RuleBasedVerifier


REQUIRED_ACTION_FIELDS = (
    "actor",
    "action",
    "target",
    "scope",
    "affected_parties",
    "authority",
    "consent",
    "purpose",
    "expected_effects",
    "uncertainty",
    "evidence_refs",
    "normative_refs",
)


def normalize_candidate(payload: Mapping[str, Any], *, name: str) -> tuple[CandidateAction | None, tuple[str, ...]]:
    missing = tuple(field for field in REQUIRED_ACTION_FIELDS if field not in payload)
    if missing:
        return None, (f"missing required action fields: {','.join(missing)}",)
    return CandidateAction(
        name=name,
        authorized=bool(payload.get("authorized", True)),
        consent_obtained=bool(payload.get("consent_obtained", payload.get("consent", False))),
        touches_private_data=bool(payload.get("touches_private_data", False)),
        coercive=bool(payload.get("coercive", False)),
        predicted_harm=float(payload.get("predicted_harm", 0.0)),
        semantic_completeness=float(payload.get("semantic_completeness", 1.0)),
    ), ()


def verify_prediction(row: Mapping[str, Any], predicted_action: str) -> dict[str, Any]:
    payload = row.get("candidate_actions", {}).get(predicted_action)
    if payload is None:
        return {"permitted": False, "reasons": ["predicted action is not in normalized candidate schema"], "parser_failure": True}
    # The generator stores a compact candidate fixture.  The required action
    # fields are added by the evaluation adapter, never by model output.
    enriched = {
        "actor": "model",
        "action": predicted_action,
        "target": "scenario-target",
        "scope": "scenario",
        "affected_parties": ["scenario-party"],
        "authority": "fixture-authority",
        "consent": payload.get("consent_obtained", True),
        "purpose": "fixture-purpose",
        "expected_effects": ["bounded-effect"],
        "uncertainty": 0.2,
        "evidence_refs": [row["example_id"]],
        "normative_refs": [row["template_id"]],
        **payload,
    }
    candidate, errors = normalize_candidate(enriched, name=predicted_action)
    if candidate is None:
        return {"permitted": False, "reasons": list(errors), "parser_failure": True}
    result = RuleBasedVerifier().verify(candidate)
    return {"permitted": result.permitted, "reasons": list(result.reasons), "parser_failure": False}
