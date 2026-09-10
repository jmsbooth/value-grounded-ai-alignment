import pytest

torch = pytest.importorskip("torch")

from vgta_transformer.losses import masked_cross_entropy, total_loss


def test_prompt_tokens_are_excluded_from_response_loss():
    logits = torch.zeros((1, 3, 4), requires_grad=True)
    targets = torch.tensor([[0, 1, 2]])
    prompt_mask = torch.tensor([[0, 0, 1]], dtype=torch.bool)
    loss = masked_cross_entropy(logits, targets, prompt_mask)
    loss.backward()
    assert torch.equal(logits.grad[0, :2], torch.zeros_like(logits.grad[0, :2]))
    assert logits.grad[0, 2].abs().sum() > 0


def test_zero_weight_auxiliary_term_is_not_added():
    response = torch.tensor(2.0, requires_grad=True)
    auxiliary = torch.zeros((1, 2), requires_grad=True)
    target = torch.ones((1, 2))
    combined, terms = total_loss(response_loss=response, auxiliary_logits={"values": auxiliary}, auxiliary_targets={"values": target}, weights={"values": 0.0})
    assert combined is response
    assert "values" not in terms

