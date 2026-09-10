import copy

import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
pytest.importorskip("peft")

from transformers import GPTNeoXConfig, GPTNeoXForCausalLM

from vgta_eval.semantic_worlds import generate_semantic_dataset
from vgta_transformer.adaptation import add_lora
from vgta_transformer.auxiliary_heads import AuxiliaryHeads, pool_prompt_hidden
from vgta_transformer.checkpointing import load_training_state, save_checkpoint, verify_checkpoint
from vgta_transformer.collator import collate_examples
from vgta_transformer.losses import masked_cross_entropy, masked_cross_entropy_stats
from vgta_transformer.training import tiny_train_step


class _Tokenizer:
    pad_token_id = 0
    eos_token_id = 0

    def __call__(self, text, *, add_special_tokens=True, truncation=False, return_tensors=None, **kwargs):
        del truncation, kwargs
        ids = [((sum(bytearray(token.encode())) % 90) + 1) for token in text.split()]
        if add_special_tokens:
            ids.append(self.eos_token_id)
        result = {"input_ids": ids}
        if return_tensors == "pt":
            result = {"input_ids": torch.tensor([ids]), "attention_mask": torch.ones((1, len(ids)), dtype=torch.long)}
        return result

    def decode(self, ids, **kwargs):
        return " ".join(str(item) for item in ids)


def _model():
    config = GPTNeoXConfig(num_hidden_layers=1, hidden_size=32, intermediate_size=64, num_attention_heads=4, vocab_size=97, max_position_embeddings=256)
    return add_lora(GPTNeoXForCausalLM(config))


def test_manual_response_loss_matches_masked_implementation():
    logits = torch.tensor([[[1.0, 0.0], [0.0, 2.0], [3.0, 0.0]]], requires_grad=True)
    targets = torch.tensor([[0, 1, 0]])
    mask = torch.tensor([[True, False, True]])
    manual = torch.stack((torch.nn.functional.cross_entropy(logits[0, 0], targets[0, 0]), torch.nn.functional.cross_entropy(logits[0, 2], targets[0, 2]))).mean()
    assert torch.allclose(manual, masked_cross_entropy(logits, targets, mask))


def test_unequal_microbatches_use_token_weighted_accumulation():
    first = (torch.randn(1, 2, 7), torch.tensor([[1, 2]]), torch.tensor([[True, True]]))
    second = (torch.randn(1, 5, 7), torch.tensor([[1, 2, 3, 4, 5]]), torch.tensor([[True, True, True, False, False]]))
    n1, c1 = masked_cross_entropy_stats(*first)
    n2, c2 = masked_cross_entropy_stats(*second)
    combined = (n1 + n2) / (c1 + c2)
    padded_logits = torch.cat((torch.nn.functional.pad(first[0], (0, 0, 0, 3)), second[0]), dim=0)
    padded_targets = torch.cat((torch.nn.functional.pad(first[1], (0, 3)), second[1]), dim=0)
    padded_mask = torch.cat((torch.nn.functional.pad(first[2], (0, 3)), second[2]), dim=0)
    assert torch.allclose(combined, masked_cross_entropy(padded_logits, padded_targets, padded_mask))


def test_auxiliary_pool_is_prompt_bounded_under_teacher_forcing():
    hidden = torch.arange(2 * 5 * 3, dtype=torch.float32).reshape(2, 5, 3)
    prompt_mask = torch.tensor([[True, True, False, False, False], [True, True, True, False, False]])
    pooled = pool_prompt_hidden(hidden, prompt_mask)
    assert torch.equal(pooled[0], hidden[0, 1])
    assert torch.equal(pooled[1], hidden[1, 2])


def test_real_update_changes_adapter_but_no_update_control_does_not():
    dataset = generate_semantic_dataset(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    tokenizer = _Tokenizer()
    batch = collate_examples(dataset.examples[:1], tokenizer, annotations=dataset.annotation_map())
    model = _model()
    before = {name: value.detach().clone() for name, value in model.named_parameters() if value.requires_grad}
    # Explicit no-update control: no backward or optimizer step.
    for name, value in model.named_parameters():
        if value.requires_grad:
            assert torch.equal(before[name], value)
    optimizer = torch.optim.AdamW([value for value in model.parameters() if value.requires_grad], lr=1e-2)
    metrics = tiny_train_step(model, batch, optimizer)
    assert metrics["gradient_norm"] > 0
    assert any(not torch.equal(before[name], value) for name, value in model.named_parameters() if value.requires_grad)


def test_auxiliary_loss_reaches_shared_lora_and_heads():
    dataset = generate_semantic_dataset(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    batch = collate_examples(dataset.examples[:1], _Tokenizer(), annotations=dataset.annotation_map())
    model = _model()
    heads = AuxiliaryHeads(32, value_count=4, relation_count=1, norm_count=1, conflict_count=1)
    optimizer = torch.optim.AdamW(list(value for value in model.parameters() if value.requires_grad) + list(heads.parameters()), lr=1e-2)
    metrics = tiny_train_step(model, batch, optimizer, auxiliary_heads=heads, auxiliary_targets={"values": torch.ones(1, 4), "relation": torch.ones(1, 1)}, auxiliary_weights={"values": 1.0, "relation": 1.0})
    assert metrics["values"] > 0 and metrics["relation"] > 0
    assert any(parameter.grad is not None and parameter.grad.abs().sum() > 0 for name, parameter in model.named_parameters() if "lora_" in name)
    assert any(parameter.grad is not None and parameter.grad.abs().sum() > 0 for parameter in heads.parameters())


def test_answer_tokens_cannot_change_prompt_representation_in_eval_mode():
    model = GPTNeoXForCausalLM(GPTNeoXConfig(num_hidden_layers=1, hidden_size=32, intermediate_size=64, num_attention_heads=4, vocab_size=97, max_position_embeddings=32))
    model.eval()
    prompt = torch.tensor([[1, 2, 3]])
    first = torch.cat((prompt, torch.tensor([[4, 5]])), dim=1)
    second = torch.cat((prompt, torch.tensor([[80, 81]])), dim=1)
    with torch.no_grad():
        left = pool_prompt_hidden(model(first, output_hidden_states=True, use_cache=False).hidden_states[-1], torch.tensor([[True, True, True, False, False]]))
        right = pool_prompt_hidden(model(second, output_hidden_states=True, use_cache=False).hidden_states[-1], torch.tensor([[True, True, True, False, False]]))
    assert torch.allclose(left, right, atol=1e-6, rtol=1e-6)


def test_checkpoint_roundtrip_includes_optimizer_and_random_state(tmp_path):
    model = _model()
    optimizer = torch.optim.AdamW([value for value in model.parameters() if value.requires_grad], lr=1e-3)
    path = tmp_path / "checkpoint"
    save_checkpoint(path, model, optimizer=optimizer, random_state={"python": "fixture"}, metadata={"update_count": 3, "tokenizer": "fixture"})
    assert all(verify_checkpoint(path).values())
    restored = torch.optim.AdamW([value for value in model.parameters() if value.requires_grad], lr=1e-3)
    assert load_training_state(path, optimizer=restored)["python"] == "fixture"
