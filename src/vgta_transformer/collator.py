"""Right-padded causal-LM batches with explicit prompt/response masks."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from vgta_eval.semantic_worlds import PrivateAnnotation, PublicExample

from .model_loader import ModelDependencyError
from .response_contract import build_training_sequence


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PyTorch is required for batching") from exc
    return torch


def collate_examples(
    examples: Iterable[PublicExample],
    tokenizer: Any,
    *,
    annotations: Mapping[str, PrivateAnnotation] | None = None,
    structured: bool = False,
    max_length: int = 2048,
    span_weight_fields: Iterable[str] = (),
) -> dict[str, Any]:
    torch = _torch()
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    rows: list[tuple[Any, PublicExample]] = []
    for example in examples:
        annotation = None
        if annotations is not None:
            if example.public_id not in annotations:
                raise ValueError(f"missing private annotation for {example.public_id}")
            annotation = annotations[example.public_id]
        sequence = build_training_sequence(example, annotation, tokenizer, structured=structured, max_length=max_length, span_weight_fields=span_weight_fields)
        rows.append((sequence, example))
    width = max((len(row[0].input_ids) for row in rows), default=1)
    ids = torch.full((len(rows), width), pad_id, dtype=torch.long)
    labels = torch.full((len(rows), width), -100, dtype=torch.long)
    attention = torch.zeros((len(rows), width), dtype=torch.long)
    prompt_mask = torch.zeros((len(rows), width), dtype=torch.bool)
    response_mask = torch.zeros((len(rows), width), dtype=torch.bool)
    response_weights = torch.zeros((len(rows), width), dtype=torch.float32)
    for index, (sequence, _) in enumerate(rows):
        size = len(sequence.input_ids)
        ids[index, :size] = torch.tensor(sequence.input_ids, dtype=torch.long)
        labels[index, :size] = torch.tensor(sequence.labels, dtype=torch.long)
        attention[index, :size] = 1
        prompt_mask[index, :size] = torch.tensor(sequence.prompt_mask, dtype=torch.bool)
        response_mask[index, :size] = torch.tensor(sequence.response_mask, dtype=torch.bool)
        response_weights[index, :size] = torch.tensor(sequence.response_weights, dtype=torch.float32)
    return {
        "input_ids": ids,
        "attention_mask": attention,
        "labels": labels,
        "prompt_mask": prompt_mask,
        "response_mask": response_mask,
        "response_weight_mask": response_weights,
        "response_token_count": int(response_mask.sum().item()),
        "response_weight_sum": float((response_weights * response_mask).sum().item()),
        "prompt_token_count": int(prompt_mask.sum().item()),
        "public_ids": [row[1].public_id for row in rows],
    }
