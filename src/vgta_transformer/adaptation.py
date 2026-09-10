"""LoRA adaptation constrained to modules present in GPT-NeoX."""

from __future__ import annotations

from typing import Any

from .model_loader import ModelDependencyError


def _imports():
    try:
        from peft import LoraConfig, TaskType, get_peft_model
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PEFT is required for LoRA adaptation") from exc
    return LoraConfig, TaskType, get_peft_model


def inspect_target_modules(model: Any) -> tuple[str, ...]:
    names = {name.rsplit(".", 1)[-1] for name, module in model.named_modules() if module.__class__.__name__ in {"Linear", "Conv1D"}}
    preferred = tuple(name for name in ("query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h") if name in names)
    if "query_key_value" not in preferred or "dense" not in preferred:
        raise ValueError(f"expected GPT-NeoX attention/MLP targets not found; observed {sorted(names)[:30]}")
    return preferred


def add_lora(model: Any, *, rank: int = 8, alpha: int = 16, dropout: float = 0.0) -> Any:
    if (rank, alpha, dropout) != (8, 16, 0.0):
        raise ValueError("protocol LoRA configuration is fixed at rank=8, alpha=16, dropout=0")
    LoraConfig, TaskType, get_peft_model = _imports()
    targets = inspect_target_modules(model)
    config = LoraConfig(
        r=rank,
        lora_alpha=alpha,
        lora_dropout=dropout,
        target_modules=list(targets),
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    adapted = get_peft_model(model, config)
    adapted.use_cache = False
    adapted.config.use_cache = False
    adapted._vgta_lora_targets = targets
    return adapted


def trainable_parameter_count(model: Any) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)

