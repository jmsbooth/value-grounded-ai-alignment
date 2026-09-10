import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
pytest.importorskip("peft")

from transformers import GPTNeoXConfig, GPTNeoXForCausalLM
from vgta_transformer.adaptation import add_lora, trainable_parameter_count


def test_tiny_gpt_neox_uses_actual_lora_targets():
    config = GPTNeoXConfig(num_hidden_layers=1, hidden_size=32, intermediate_size=64, num_attention_heads=4, vocab_size=97, max_position_embeddings=32)
    model = add_lora(GPTNeoXForCausalLM(config))
    assert trainable_parameter_count(model) > 0
    assert "query_key_value" in model._vgta_lora_targets
    assert all(not parameter.requires_grad for name, parameter in model.named_parameters() if "lora_" not in name)

