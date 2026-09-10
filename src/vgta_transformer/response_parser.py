"""Strict response extraction and parsing for the v0.6.1 development path."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping, Sequence

from vgta_eval.semantic_worlds import ACTION_CATALOGUE, VALUE_DEFINITIONS


ERROR_TAXONOMY = (
    "empty_output",
    "not_json",
    "markdown_or_extra_prose",
    "invalid_json_syntax",
    "multiple_json_values_or_trailing_content",
    "missing_required_fields",
    "additional_disallowed_fields",
    "invalid_enum_or_type",
    "invalid_public_reference",
    "truncated_generation",
    "schema_valid",
)
REQUIRED_FIELDS = frozenset({
    "action", "candidate_id", "salient_values", "relation_class", "conflict_class",
    "applicable_norm_ids", "useful", "permitted",
})
ALLOWED_FIELDS = REQUIRED_FIELDS
ACTION_BY_ID = dict(ACTION_CATALOGUE)
ID_BY_ACTION = {description: candidate_id for candidate_id, description in ACTION_CATALOGUE}
VALUE_IDS = frozenset(value_id for value_id, _ in VALUE_DEFINITIONS)
RELATION_CLASSES = frozenset({
    "policy_compliance", "consent_scope", "delegation_status",
    "recipient_authorization", "evidence_freshness", "requires_evidence",
    "policy_prohibition",
})
CONFLICT_CLASSES = frozenset({"no_conflict", "resolvable_conflict", "unresolved_conflict"})


class DuplicateKeyError(ValueError):
    pass


@dataclass(frozen=True)
class ParseResult:
    valid: bool
    value: dict[str, Any] | None
    primary_error: str
    syntax_valid: bool
    schema_valid: bool
    public_reference_valid: bool
    detail: str | None = None


def extract_continuation_ids(generated_ids: Any, input_width: int | Sequence[int]) -> list[list[int]]:
    """Slice model continuations by tensor width, including batch padding."""

    if hasattr(generated_ids, "detach"):
        tensor = generated_ids.detach().cpu()
        rows = tensor.tolist()
    else:
        rows = generated_ids
    if not rows:
        return []
    if isinstance(rows[0], int):
        rows = [rows]
    widths = [int(input_width)] * len(rows) if isinstance(input_width, int) else [int(v) for v in input_width]
    if len(widths) != len(rows):
        raise ValueError("one input width is required for every generated row")
    return [list(row[width:]) for row, width in zip(rows, widths)]


def decode_continuation(tokenizer: Any, generated_ids: Any, input_width: int | Sequence[int]) -> list[str]:
    continuations = extract_continuation_ids(generated_ids, input_width)
    return [tokenizer.decode(ids, skip_special_tokens=True) for ids in continuations]


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate key: {key}")
        value[key] = item
    return value


def _error(primary_error: str, detail: str | None = None, *, syntax_valid: bool = False) -> ParseResult:
    return ParseResult(False, None, primary_error, syntax_valid, False, False, detail)


def _reference_sets(public_reference: Mapping[str, Any] | None) -> tuple[set[str], set[str], set[str]]:
    ref = public_reference or {}
    candidates = ref.get("candidate_ids", tuple(ACTION_BY_ID))
    actions = ref.get("actions", tuple(ID_BY_ACTION))
    norms = ref.get("norm_ids", (f"norm_{index:02d}" for index in range(1, 6)))
    return set(str(value) for value in candidates), set(str(value) for value in actions), set(str(value) for value in norms)


def strict_parse(raw_text: str, *, public_reference: Mapping[str, Any] | None = None, stopped_at_token_cap: bool = False) -> ParseResult:
    """Parse exactly one complete public-schema JSON object without repair."""

    stripped = raw_text.strip()
    if not stripped:
        return _error("empty_output")
    if not stripped.startswith("{"):
        if "{" in stripped or stripped.startswith("```"):
            return _error("markdown_or_extra_prose", "object was not the first top-level value")
        return _error("not_json")
    decoder = json.JSONDecoder(object_pairs_hook=_pairs)
    try:
        value, end = decoder.raw_decode(stripped)
    except DuplicateKeyError as exc:
        return _error("additional_disallowed_fields", str(exc), syntax_valid=True)
    except json.JSONDecodeError as exc:
        if stopped_at_token_cap and not stripped.endswith("}"):
            return _error("truncated_generation", str(exc))
        return _error("invalid_json_syntax", str(exc))
    remainder = stripped[end:].strip()
    if remainder:
        return _error("multiple_json_values_or_trailing_content", "non-whitespace followed the first JSON value", syntax_valid=True)
    if not isinstance(value, dict):
        return _error("invalid_enum_or_type", "top-level response must be an object", syntax_valid=True)
    missing = sorted(REQUIRED_FIELDS - set(value))
    if missing:
        return _error("missing_required_fields", ", ".join(missing), syntax_valid=True)
    extra = sorted(set(value) - ALLOWED_FIELDS)
    if extra:
        return _error("additional_disallowed_fields", ", ".join(extra), syntax_valid=True)
    if not isinstance(value["action"], str) or not isinstance(value["candidate_id"], str):
        return _error("invalid_enum_or_type", "action and candidate_id must be strings", syntax_valid=True)
    if not isinstance(value["salient_values"], list) or not all(isinstance(item, str) for item in value["salient_values"]):
        return _error("invalid_enum_or_type", "salient_values must be a string array", syntax_valid=True)
    if not isinstance(value["applicable_norm_ids"], list) or not all(isinstance(item, str) for item in value["applicable_norm_ids"]):
        return _error("invalid_enum_or_type", "applicable_norm_ids must be a string array", syntax_valid=True)
    if not isinstance(value["relation_class"], str) or value["relation_class"] not in RELATION_CLASSES:
        return _error("invalid_enum_or_type", "unknown relation_class", syntax_valid=True)
    if not isinstance(value["conflict_class"], str) or value["conflict_class"] not in CONFLICT_CLASSES:
        return _error("invalid_enum_or_type", "unknown conflict_class", syntax_valid=True)
    if not isinstance(value["useful"], bool) or not isinstance(value["permitted"], bool):
        return _error("invalid_enum_or_type", "useful and permitted must be booleans", syntax_valid=True)
    candidate_ids, actions, norm_ids = _reference_sets(public_reference)
    if value["candidate_id"] not in candidate_ids or value["action"] not in actions or value["candidate_id"] != ID_BY_ACTION.get(value["action"]):
        return _error("invalid_public_reference", "action/candidate does not match the public catalogue", syntax_valid=True)
    if any(item not in VALUE_IDS for item in value["salient_values"]):
        return _error("invalid_enum_or_type", "unknown salient value", syntax_valid=True)
    if any(item not in norm_ids for item in value["applicable_norm_ids"]):
        return _error("invalid_public_reference", "norm reference is absent from the public policy", syntax_valid=True)
    return ParseResult(True, value, "schema_valid", True, True, True)


def parser_reference(example: Any) -> dict[str, Any]:
    return {
        "candidate_ids": [candidate_id for candidate_id, _ in example.action_catalogue],
        "actions": [description for _, description in example.action_catalogue],
        "norm_ids": [f"norm_{index:02d}" for index in range(1, 6)],
    }
