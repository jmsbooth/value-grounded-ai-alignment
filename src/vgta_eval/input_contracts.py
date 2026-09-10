"""Input/label boundary checks for the transformer phase."""

from __future__ import annotations

from typing import Any, Mapping

from .semantic_worlds import ACTION_CATALOGUE, PrivateAnnotation, PublicExample


FORBIDDEN_MODEL_KEYS = frozenset({
    "gold", "label", "labels", "target", "target_action", "candidate_id", "verdict",
    "world_id", "world_group_id", "template_id", "split", "annotation", "private",
    "useful", "permitted", "evidence_refs", "applicable_norm_ids",
})


class InputContractError(ValueError):
    """Raised when private reference information crosses the model boundary."""


def _forbidden_keys(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text.lower() in FORBIDDEN_MODEL_KEYS:
                found.append(f"{path}.{key_text}" if path else key_text)
            found.extend(_forbidden_keys(child, f"{path}.{key_text}" if path else key_text))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.extend(_forbidden_keys(child, f"{path}[{index}]"))
    return found


def validate_public_mapping(value: Mapping[str, Any]) -> None:
    forbidden = _forbidden_keys(value)
    if forbidden:
        raise InputContractError("private/reference fields in public input: " + ", ".join(forbidden))


def validate_public_example(example: PublicExample) -> None:
    validate_public_mapping({
        "public_input": example.public_input,
        "structured_input": example.structured_input,
        "action_catalogue": [{"id": cid, "description": description} for cid, description in ACTION_CATALOGUE],
    })
    if example.action_catalogue != ACTION_CATALOGUE:
        raise InputContractError("public action catalogue must be fixed across examples")
    if any(token in example.public_input.lower() for token in ("target_action", "gold label", "template_id", "world_id")):
        raise InputContractError("private identity or label text found in natural input")


def assert_annotation_is_private(annotation: PrivateAnnotation) -> None:
    if not annotation.public_id or not annotation.candidate_id:
        raise InputContractError("private annotation is incomplete")


def build_response_target(annotation: PrivateAnnotation) -> dict[str, Any]:
    """Return the fixed response target; this is never passed as model input."""

    return {
        "action": annotation.action,
        "candidate_id": annotation.candidate_id,
        "salient_values": list(annotation.salient_values),
        "relation_class": annotation.relation_class,
        "conflict_class": annotation.conflict_class,
        "applicable_norm_ids": list(annotation.applicable_norm_ids),
        "useful": annotation.useful,
        "permitted": annotation.permitted,
    }

