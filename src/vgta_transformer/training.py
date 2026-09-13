"""Tiny, observable training operations used by development diagnostics."""

from __future__ import annotations

from typing import Any, Mapping

from .losses import masked_cross_entropy, masked_cross_entropy_stats, total_loss, total_loss_stats
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
    weights = batch.get("response_weight_mask", batch["response_mask"].to(dtype=logits.dtype))[:, 1:]
    numerator, count = masked_cross_entropy_stats(logits, labels.clamp_min(0), weights * response_mask.to(dtype=weights.dtype))
    return numerator / count.clamp_min(1.0), count


def response_loss_stats_from_outputs(outputs: Any, batch: Mapping[str, Any]) -> tuple[Any, Any]:
    logits = outputs.logits[:, :-1]
    labels = batch["labels"][:, 1:]
    response_mask = batch["response_mask"][:, 1:]
    weights = batch.get("response_weight_mask", batch["response_mask"].to(dtype=logits.dtype))[:, 1:]
    return masked_cross_entropy_stats(logits, labels.clamp_min(0), weights * response_mask.to(dtype=weights.dtype))


def optimizer_step(model: Any, optimizer: Any, *, max_grad_norm: float = 1.0, auxiliary_heads: Any | None = None) -> float:
    """Clip and perform one explicit optimizer update; return the pre-clip norm."""

    torch = _torch()
    grad_norm = torch.nn.utils.clip_grad_norm_(trainable_parameters(model, auxiliary_heads), max_norm=max_grad_norm)
    if not torch.isfinite(grad_norm):
        raise FloatingPointError("non-finite gradient norm")
    optimizer.step()
    return float(grad_norm.detach().cpu())


def accumulated_response_step(model: Any, batches: list[Mapping[str, Any]], optimizer: Any, *, max_grad_norm: float = 1.0, scheduler: Any | None = None) -> dict[str, float]:
    """Run one token-weighted update over unequal-length microbatches."""

    torch = _torch()
    if not batches:
        raise ValueError("at least one microbatch is required")
    model.train()
    optimizer.zero_grad(set_to_none=True)
    total_tokens = float(sum(float(batch.get("response_weight_mask", batch["response_mask"].to(dtype=torch.float32))[:, 1:].mul(batch["response_mask"][:, 1:]).sum().item()) for batch in batches))
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
    if scheduler is not None:
        scheduler.step()
    if grad_norm == 0.0:
        raise FloatingPointError("zero gradient norm")
    return {"loss": objective_value, "gradient_norm": grad_norm, "response_token_count": total_tokens}


def tiny_train_step(model: Any, batch: Mapping[str, Any], optimizer: Any, *, auxiliary_heads: Any | None = None, auxiliary_targets: Mapping[str, Any] | None = None, auxiliary_weights: Mapping[str, float] | None = None, response_loss_coefficient: float = 1.0, auxiliary_masks: Mapping[str, Any] | None = None, scheduler: Any | None = None) -> dict[str, float]:
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
    loss, terms = total_loss(response_loss=response_loss * float(response_loss_coefficient), auxiliary_logits=heads_output, auxiliary_targets=auxiliary_targets, weights=auxiliary_weights)
    if not torch.isfinite(loss):
        raise FloatingPointError("non-finite training loss")
    loss.backward()
    grad_norm = optimizer_step(model, optimizer, auxiliary_heads=auxiliary_heads)
    if scheduler is not None:
        scheduler.step()
    if grad_norm == 0.0:
        raise FloatingPointError("zero gradient norm")
    return {"loss": float(loss.detach().cpu()), "gradient_norm": grad_norm, "response_token_count": float(response_token_count.detach().cpu()), **terms}


def accumulated_train_step(
    model: Any,
    batches: list[Mapping[str, Any]],
    optimizer: Any,
    *,
    auxiliary_heads: Any | None = None,
    auxiliary_targets: list[Mapping[str, Any]] | None = None,
    auxiliary_weights: Mapping[str, float] | None = None,
    auxiliary_masks: list[Mapping[str, Any]] | None = None,
    response_loss_coefficient: float = 1.0,
    max_grad_norm: float = 1.0,
    scheduler: Any | None = None,
) -> dict[str, float]:
    """Perform one update from one-example microbatches.

    Every response and auxiliary term is normalized by its global denominator;
    optimizer, clipping, and scheduler each run exactly once.  The runner is
    responsible for passing the same microbatch grouping to every arm.
    """

    torch = _torch()
    if not batches:
        raise ValueError("at least one microbatch is required")
    if auxiliary_targets is not None and len(auxiliary_targets) != len(batches):
        raise ValueError("one auxiliary target mapping is required per microbatch")
    model.train()
    optimizer.zero_grad(set_to_none=True)
    response_denominator = torch.tensor(0.0, device=batches[0]["input_ids"].device)
    aux_denominators: dict[str, Any] = {}
    for index, batch in enumerate(batches):
        weights = batch.get("response_weight_mask", batch["response_mask"].to(dtype=torch.float32))[:, 1:]
        response_denominator = response_denominator + weights.mul(batch["response_mask"][:, 1:]).sum()
        if auxiliary_heads is not None and auxiliary_targets is not None:
            for name, target in auxiliary_targets[index].items():
                mask = (auxiliary_masks[index] if auxiliary_masks is not None else {}).get(name)
                count = target.numel() if mask is None else mask.to(dtype=torch.float32).sum()
                aux_denominators[name] = aux_denominators.get(name, target.new_tensor(0.0)) + count
    if response_loss_coefficient != 0.0 and float(response_denominator.detach().cpu()) <= 0:
        raise ValueError("microbatches contain no supervised response tokens")
    metrics: dict[str, float] = {"response_token_count": float(response_denominator.detach().cpu()), "microbatch_count": float(len(batches))}
    totals: dict[str, float] = {}
    for index, batch in enumerate(batches):
        outputs = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], output_hidden_states=auxiliary_heads is not None, use_cache=False)
        response_numerator, _ = response_loss_stats_from_outputs(outputs, batch)
        heads_output = None
        if auxiliary_heads is not None:
            from .auxiliary_heads import pool_prompt_hidden
            heads_output = auxiliary_heads(pool_prompt_hidden(outputs.hidden_states[-1], batch["prompt_mask"]))
        combined = response_numerator / response_denominator.clamp_min(1.0) * float(response_loss_coefficient)
        totals["response"] = totals.get("response", 0.0) + float((response_numerator.detach() / response_denominator.clamp_min(1.0)).cpu())
        if heads_output is not None and auxiliary_targets is not None:
            from .losses import masked_bce_with_logits_stats
            for name, logits in heads_output.items():
                coefficient = float((auxiliary_weights or {}).get(name, 0.0))
                if coefficient == 0.0 or name not in auxiliary_targets[index]:
                    continue
                mask = (auxiliary_masks[index] if auxiliary_masks is not None else {}).get(name)
                numerator, denominator = masked_bce_with_logits_stats(logits, auxiliary_targets[index][name], mask)
                combined = combined + coefficient * numerator / aux_denominators[name].clamp_min(1.0)
                totals[name] = totals.get(name, 0.0) + float((numerator.detach() / aux_denominators[name].clamp_min(1.0)).cpu())
        if not torch.isfinite(combined):
            raise FloatingPointError("non-finite accumulated loss")
        combined.backward()
        del outputs, heads_output, combined
    grad_norm = optimizer_step(model, optimizer, max_grad_norm=max_grad_norm, auxiliary_heads=auxiliary_heads)
    if scheduler is not None:
        scheduler.step()
    if grad_norm == 0.0:
        raise FloatingPointError("zero gradient norm")
    metrics.update({"loss": float(sum(totals.values())), "gradient_norm": grad_norm, **totals})
    return metrics


def parameter_accounting(model: Any, auxiliary_heads: Any | None = None, optimizer: Any | None = None, before: Mapping[str, Any] | None = None) -> dict[str, int]:
    """Count total, frozen, adapter, auxiliary, optimizer, gradient, and change sets."""

    all_model = list(model.parameters())
    adapter = [value for name, value in model.named_parameters() if "lora_" in name]
    aux = list(auxiliary_heads.parameters()) if auxiliary_heads is not None else []
    trainable = [value for value in all_model + aux if value.requires_grad]
    optimizer_count = sum(value.numel() for group in (optimizer.param_groups if optimizer is not None else []) for value in group["params"])
    counts = {
        "total_model_parameters": sum(value.numel() for value in all_model),
        "frozen_model_parameters": sum(value.numel() for value in all_model if not value.requires_grad),
        "trainable_model_parameters": sum(value.numel() for value in all_model if value.requires_grad),
        "adapter_parameters": sum(value.numel() for value in adapter),
        "auxiliary_head_parameters": sum(value.numel() for value in aux),
        "optimizer_parameters": optimizer_count,
        "nonzero_gradient_parameters": sum(value.numel() for value in trainable if value.grad is not None and bool(torch_count_nonzero(value.grad))),
    }
    if before is not None:
        current = {name: value.detach() for name, value in list(model.named_parameters()) + (list(auxiliary_heads.named_parameters()) if auxiliary_heads is not None else []) if value.requires_grad}
        counts["changed_trainable_parameters"] = sum(value.numel() for name, value in current.items() if name in before and not bool(value.eq(before[name]).all()))
    return counts


def torch_count_nonzero(value: Any) -> int:
    return int(value.detach().ne(0).sum().cpu())
