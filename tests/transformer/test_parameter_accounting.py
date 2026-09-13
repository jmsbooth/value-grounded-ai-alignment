import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("peft")

from transformers import GPTNeoXConfig, GPTNeoXForCausalLM

from vgta_transformer.adaptation import add_lora
from vgta_transformer.auxiliary_heads import AuxiliaryHeads
from vgta_transformer.training import parameter_accounting


def test_accounting_separates_frozen_base_adapter_and_auxiliary_parameters():
    model = add_lora(GPTNeoXForCausalLM(GPTNeoXConfig(num_hidden_layers=1, hidden_size=32, intermediate_size=64, num_attention_heads=4, vocab_size=97, max_position_embeddings=32)))
    heads = AuxiliaryHeads(32, value_count=4, relation_count=2, norm_count=2, conflict_count=2)
    optimizer = torch.optim.AdamW([value for value in model.parameters() if value.requires_grad] + list(heads.parameters()), lr=1e-3)
    counts = parameter_accounting(model, heads, optimizer)
    assert counts["total_model_parameters"] > counts["trainable_model_parameters"]
    assert counts["adapter_parameters"] == counts["trainable_model_parameters"]
    assert counts["auxiliary_head_parameters"] > 0
    assert counts["optimizer_parameters"] == counts["trainable_model_parameters"] + counts["auxiliary_head_parameters"]
