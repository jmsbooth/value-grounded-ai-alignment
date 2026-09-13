"""Masked response and auxiliary losses."""

from __future__ import annotations

from typing import Any, Mapping

from .model_loader import ModelDependencyError


def _imports():
    try:
        import torch
        import torch.nn.functional as F
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PyTorch is required for loss computation") from exc
    return torch, F


def masked_cross_entropy(logits: Any, targets: Any, mask: Any) -> Any:
    numerator, count = masked_cross_entropy_stats(logits, targets, mask)
    return numerator / count.clamp_min(1.0)


def masked_cross_entropy_stats(logits: Any, targets: Any, mask: Any) -> tuple[Any, Any]:
    """Return an unreduced numerator and supervised-token count for accumulation."""

    torch, F = _imports()
    losses = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), targets.reshape(-1), reduction="none")
    weights = mask.reshape(-1).to(dtype=losses.dtype)
    return (losses * weights).sum(), weights.sum()


def weighted_cross_entropy(logits: Any, targets: Any, weights: Any) -> Any:
    numerator, count = masked_cross_entropy_stats(logits, targets, weights)
    return numerator / count.clamp_min(1.0)


def masked_bce_with_logits(logits: Any, targets: Any, mask: Any | None = None) -> Any:
    numerator, count = masked_bce_with_logits_stats(logits, targets, mask)
    return numerator / count.clamp_min(1.0)


def masked_bce_with_logits_stats(logits: Any, targets: Any, mask: Any | None = None) -> tuple[Any, Any]:
    """Return an auxiliary numerator and valid-element denominator."""

    torch, F = _imports()
    losses = F.binary_cross_entropy_with_logits(logits, targets.to(dtype=logits.dtype), reduction="none")
    if mask is not None:
        weights = mask.to(dtype=losses.dtype)
        return (losses * weights).sum(), weights.sum()
    return losses.sum(), losses.new_tensor(losses.numel(), dtype=losses.dtype)


def auxiliary_loss_stats(logits: Any, targets: Any, mask: Any | None = None) -> tuple[Any, Any]:
    return masked_bce_with_logits_stats(logits, targets, mask)


def total_loss(*, response_loss: Any, auxiliary_logits: Mapping[str, Any] | None = None, auxiliary_targets: Mapping[str, Any] | None = None, weights: Mapping[str, float] | None = None) -> tuple[Any, dict[str, float]]:
    """Combine losses with explicit weights; zero-weight heads do not backpropagate."""

    terms: dict[str, Any] = {"response": response_loss}
    weights = dict(weights or {})
    if auxiliary_logits and auxiliary_targets:
        for name, logits in auxiliary_logits.items():
            if name not in auxiliary_targets or float(weights.get(name, 0.0)) == 0.0:
                continue
            target = auxiliary_targets[name]
            terms[name] = masked_bce_with_logits(logits, target)
    combined = terms["response"]
    for name, loss in terms.items():
        if name != "response":
            combined = combined + float(weights[name]) * loss
    return combined, {name: float(value.detach().cpu()) for name, value in terms.items()}


def total_loss_stats(
    *,
    response_numerator: Any,
    response_denominator: Any,
    auxiliary_logits: Mapping[str, Any] | None = None,
    auxiliary_targets: Mapping[str, Any] | None = None,
    auxiliary_masks: Mapping[str, Any] | None = None,
    weights: Mapping[str, float] | None = None,
    response_coefficient: float = 1.0,
) -> tuple[Any, dict[str, Any]]:
    """Combine globally-normalized response and auxiliary terms.

    The returned tensors retain their graphs.  Callers performing gradient
    accumulation should supply denominators computed across all microbatches.
    """

    terms: dict[str, Any] = {}
    combined = response_numerator / response_denominator.clamp_min(1.0) * float(response_coefficient)
    terms["response"] = response_numerator / response_denominator.clamp_min(1.0)
    weights = dict(weights or {})
    if auxiliary_logits and auxiliary_targets:
        for name, logits in auxiliary_logits.items():
            coefficient = float(weights.get(name, 0.0))
            if name not in auxiliary_targets or coefficient == 0.0:
                continue
            numerator, denominator = masked_bce_with_logits_stats(logits, auxiliary_targets[name], (auxiliary_masks or {}).get(name))
            terms[name] = (numerator, denominator, coefficient)
            combined = combined + coefficient * numerator / denominator.clamp_min(1.0)
    return combined, terms
