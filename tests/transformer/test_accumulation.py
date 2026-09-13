import copy
from dataclasses import replace

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("peft")

from transformers import GPTNeoXConfig, GPTNeoXForCausalLM

from vgta_eval.semantic_worlds import generate_v2_dataset
from vgta_transformer.adaptation import add_lora
from vgta_transformer.collator import collate_examples
from vgta_transformer.training import accumulated_train_step, tiny_train_step


class Tokenizer:
    pad_token_id = 0
    eos_token_id = 0

    def __call__(self, text, *, add_special_tokens=False, truncation=False, **kwargs):
        del truncation, kwargs
        return {"input_ids": [((ord(char) % 90) + 1) for char in text] + ([self.eos_token_id] if add_special_tokens else [])}


def model():
    return add_lora(GPTNeoXForCausalLM(GPTNeoXConfig(num_hidden_layers=1, hidden_size=32, intermediate_size=64, num_attention_heads=4, vocab_size=97, max_position_embeddings=512)))


def test_one_update_microbatch_objective_matches_full_batch():
    dataset = generate_v2_dataset(profile="mini")
    annotations = dataset.annotation_map()
    tokenizer = Tokenizer()
    examples = dataset.by_split("train")[:2]
    examples = tuple(replace(example, public_input=f"Task: {index}", structured_input='{"representation":"test"}') for index, example in enumerate(examples))
    full = collate_examples(examples, tokenizer, annotations=annotations, structured=True, max_length=512)
    singles = [collate_examples((example,), tokenizer, annotations=annotations, structured=True, max_length=512) for example in examples]
    first, second = model(), model()
    second.load_state_dict(copy.deepcopy(first.state_dict()))
    opt_first = torch.optim.AdamW([value for value in first.parameters() if value.requires_grad], lr=1e-3, weight_decay=0.0)
    opt_second = torch.optim.AdamW([value for value in second.parameters() if value.requires_grad], lr=1e-3, weight_decay=0.0)
    torch.manual_seed(7)
    tiny_train_step(first, full, opt_first)
    torch.manual_seed(7)
    accumulated_train_step(second, singles, opt_second)
    for left, right in zip(first.parameters(), second.parameters()):
        assert torch.allclose(left, right, atol=1e-6, rtol=1e-5)


def test_accumulation_records_one_optimizer_update_and_partial_batch():
    dataset = generate_v2_dataset(profile="mini")
    annotations = dataset.annotation_map()
    example = replace(dataset.by_split("train")[0], public_input="Task: test", structured_input='{"representation":"test"}')
    batch = collate_examples((example,), Tokenizer(), annotations=annotations, structured=True, max_length=512)
    target = model()
    optimizer = torch.optim.AdamW([value for value in target.parameters() if value.requires_grad], lr=1e-3)
    metrics = accumulated_train_step(target, [batch], optimizer)
    assert metrics["microbatch_count"] == 1
    assert metrics["response_token_count"] > 0
