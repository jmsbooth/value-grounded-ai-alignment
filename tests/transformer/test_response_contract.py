import json
from dataclasses import replace

import pytest

torch = pytest.importorskip("torch")

from vgta_eval.semantic_worlds import generate_v2_dataset
from vgta_transformer.collator import collate_examples
from vgta_transformer.response_contract import build_training_sequence, serialize_response_target


class OffsetTokenizer:
    pad_token_id = 0
    eos_token_id = 0
    bos_token_id = 1
    special_tokens_map = {"bos_token": "<bos>", "eos_token": "<eos>", "pad_token": "<eos>"}

    def __call__(self, text, *, add_special_tokens=False, truncation=False, return_offsets_mapping=False, **kwargs):
        del truncation, kwargs
        tokens = []
        offsets = []
        # Character-level tokens make the boundary assertions explicit and
        # also exercise repeated strings and punctuation safely.
        for index, char in enumerate(text):
            tokens.append((ord(char) % 89) + 2)
            offsets.append((index, index + 1))
        if add_special_tokens:
            tokens = [self.bos_token_id] + tokens + [self.eos_token_id]
            offsets = [(0, 0)] + offsets + [(0, 0)]
        result = {"input_ids": tokens}
        if return_offsets_mapping:
            result["offset_mapping"] = offsets
        return result

    def decode(self, ids, **kwargs):
        del kwargs
        return "".join(chr((int(value) - 2) % 89) for value in ids if value != self.eos_token_id)


def _fixture():
    dataset = generate_v2_dataset(profile="mini")
    example = replace(dataset.examples[0], public_input="Task: test", structured_input='{"representation":"test"}')
    return example, dataset.annotation_map()[dataset.examples[0].public_id]


def test_response_contract_appends_existing_eos_once_and_supervises_it():
    example, annotation = _fixture()
    tokenizer = OffsetTokenizer()
    sequence = build_training_sequence(example, annotation, tokenizer, structured=True, max_length=2048)
    assert sequence.response_ids[-1] == tokenizer.eos_token_id
    assert sequence.response_ids.count(tokenizer.eos_token_id) >= 1
    assert sequence.labels[-1] == tokenizer.eos_token_id
    assert sequence.response_mask[-1] == 1
    assert sequence.response_weights[-1] == 1.0
    assert len(sequence.input_ids) == len(sequence.labels) == len(sequence.response_mask)


def test_text_weights_cover_only_selected_serialized_field_values_and_not_eos():
    example, annotation = _fixture()
    tokenizer = OffsetTokenizer()
    plain = build_training_sequence(example, annotation, tokenizer, structured=True, max_length=2048)
    weighted = build_training_sequence(example, annotation, tokenizer, structured=True, max_length=2048, span_weight_fields=("relation_class",))
    assert weighted.response_weights[-1] == 1.0
    assert any(value == 2.0 for value in weighted.response_weights[len(weighted.prompt_ids):-1])
    assert sum(value == 2.0 for value in weighted.response_weights) < len(weighted.response_weights)
    assert all(value in {1.0, 2.0} for value in weighted.response_weights)
    assert plain.response_text == weighted.response_text
    assert json.loads(plain.response_text) == json.loads(serialize_response_target(annotation).text)


def test_padding_equal_to_eos_is_masked_by_position():
    example, annotation = _fixture()
    dataset = generate_v2_dataset(profile="mini")
    other = replace(dataset.examples[1], public_input="Task: a longer test", structured_input='{"representation":"test-2"}')
    annotations = dataset.annotation_map()
    batch = collate_examples((example, other), tokenizer=OffsetTokenizer(), annotations=annotations, structured=False, max_length=2048)
    for row, width in enumerate(batch["attention_mask"].sum(dim=1).tolist()):
        assert batch["response_mask"][row, int(width) - 1]
        assert not batch["response_mask"][row, int(width):].any()
    assert batch["input_ids"].shape[1] >= max(batch["attention_mask"].sum(dim=1).tolist())
