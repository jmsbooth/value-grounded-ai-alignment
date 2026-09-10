import json

import pytest

torch = pytest.importorskip("torch")

from vgta_transformer.response_parser import decode_continuation, strict_parse


VALID = {
    "action": "allow the requested operation",
    "candidate_id": "candidate_01",
    "salient_values": ["agency", "privacy"],
    "relation_class": "policy_compliance",
    "conflict_class": "no_conflict",
    "applicable_norm_ids": ["norm_01", "norm_02"],
    "useful": True,
    "permitted": True,
}


def test_strict_parser_accepts_only_complete_public_schema():
    result = strict_parse(json.dumps(VALID, sort_keys=True))
    assert result.valid and result.primary_error == "schema_valid"


@pytest.mark.parametrize(
    ("raw", "error"),
    [
        ("", "empty_output"),
        ("not an answer", "not_json"),
        ("Here is the answer: " + json.dumps(VALID), "markdown_or_extra_prose"),
        ('{"action":', "invalid_json_syntax"),
        (json.dumps(VALID) + "\n{}", "multiple_json_values_or_trailing_content"),
        (json.dumps({key: value for key, value in VALID.items() if key != "useful"}), "missing_required_fields"),
        (json.dumps({**VALID, "private": True}), "additional_disallowed_fields"),
        (json.dumps({**VALID, "useful": "yes"}), "invalid_enum_or_type"),
        (json.dumps({**VALID, "candidate_id": "private-answer"}), "invalid_public_reference"),
    ],
)
def test_one_fault_mutations_have_explicit_primary_error(raw, error):
    assert strict_parse(raw).primary_error == error


def test_duplicate_keys_are_not_silently_accepted():
    raw = '{"action":"allow the requested operation","action":"decline the requested operation"}'
    assert strict_parse(raw).primary_error == "additional_disallowed_fields"


def test_cap_termination_is_retained_as_a_distinct_diagnostic():
    assert strict_parse('{"action":', stopped_at_token_cap=True).primary_error == "truncated_generation"


def test_continuation_extraction_uses_actual_padded_tensor_width():
    # The first prompt occupies three tokens and is right-padded to the
    # actual four-token generation-call width. Both rows must slice at four.
    generated = torch.tensor([[10, 11, 12, 0, 91, 92], [20, 21, 22, 23, 81, 82]])
    assert decode_continuation(_Tokenizer(), generated, [4, 4]) == ["91 92", "81 82"]


class _Tokenizer:
    def decode(self, ids, *, skip_special_tokens=True):
        return " ".join(str(value) for value in ids)
