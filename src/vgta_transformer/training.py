"""Tiny, observable training operations used by development diagnostics."""

from __future__ import annotations

from typing import Any, Mapping

from .losses import masked_cross_entropy, masked_cross_entropy_stats, total_loss
from .model_loader import ModelDependencyError


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PyTorch is required for training") from exc
    return torch


def trainable_parameters(model: Any, auxiliary_heads: Any | None = None):
    parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if auxiliary_heads is not None:
        parameters.extend(parameter for parameter in auxiliary_heads.parameters() if parameter.requires_grad)
    return parameters


def response_loss_from_outputs(outputs: Any, batch: Mapping[str, Any]) -> tuple[Any, Any]:
    """Compute next-token response loss and its exact supervised-token count."""

    logits = outputs.logits[:, :-1]
    labels = batch["labels"][:, 1:]
    response_mask = batch["response_mask"][:, 1:]
    numerator, count = masked_cross_entropy_stats(logits, labels.clamp_min(0), response_mask)
    return numerator / count.clamp_min(1.0), count


def optimizer_step(model: Any, optimizer: Any, *, max_grad_norm: float = 1.0, auxiliary_heads: Any | None = None) -> float:
    """Clip and perform one explicit optimizer update; return the pre-clip norm."""

    torch = _torch()
    grad_norm = torch.nn.utils.clip_grad_norm_(trainable_parameters(model, auxiliary_heads), max_norm=max_grad_norm)
    if not torch.isfinite(grad_norm):
        raise FloatingPointError("non-finite gradient norm")
    optimizer.step()
    return float(grad_norm.detach().cpu())


def accumulated_response_step(model: Any, batches: list[Mapping[str, Any]], optimizer: Any, *, max_grad_norm: float = 1.0) -> dict[str, float]:
    """Run one token-weighted update over unequal-length microbatches."""

    torch = _torch()
    if not batches:
        raise ValueError("at least one microbatch is required")
    model.train()
    optimizer.zero_grad(set_to_none=True)
    total_tokens = float(sum(int(batch["response_mask"][:, 1:].sum().item()) for batch in batches))
    if total_tokens <= 0:
        raise ValueError("microbatches contain no supervised response tokens")
    objective_value = 0.0
    for batch in batches:
        outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], use_cache=False)
        loss, count = response_loss_from_outputs(outputs, batch)
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite accumulated loss")
        (loss * count / total_tokens).backward()
        objective_value += float(loss.detach().cpu()) * float(count.detach().cpu()) / total_tokens
    grad_norm = optimizer_step(model, optimizer, max_grad_norm=max_grad_norm)
    if grad_norm == 0.0:
        raise FloatingPointError("zero gradient norm")
    return {"loss": objective_value, "gradient_norm": grad_norm, "response_token_count": total_tokens}


def tiny_train_step(model: Any, batch: Mapping[str, Any], optimizer: Any, *, auxiliary_heads: Any | None = None, auxiliary_targets: Mapping[str, Any] | None = None, auxiliary_weights: Mapping[str, float] | None = None) -> dict[str, float]:
    torch = _torch()
    model.train()
    optimizer.zero_grad(set_to_none=True)
    outputs = model(
        input_ids=batch["input_ids"],
        attention_mask=batch["attention_mask"],
        output_hidden_states=auxiliary_heads is not None,
        use_cache=False,
    )
    response_loss, response_token_count = response_loss_from_outputs(outputs, batch)
    heads_output = None
    if auxiliary_heads is not None:
        from .auxiliary_heads import pool_prompt_hidden
        heads_output = auxiliary_heads(pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]))
    loss, terms = total_loss(response_loss=response_loss, auxiliary_logits=heads_output, auxiliary_targets=auxiliary_targets, weights=auxiliary_weights)
    if not torch.isfinite(loss):
        raise FloatingPointError("non-finite training loss")
    loss.backward()
    grad_norm = optimizer_step(model, optimizer, auxiliary_heads=auxiliary_heads)
    if grad_norm == 0.0:
        raise FloatingPointError("zero gradient norm")
    return {"loss": float(loss.detach().cpu()), "gradient_norm": grad_norm, "response_token_count": float(response_token_count.detach().cpu()), **terms}
