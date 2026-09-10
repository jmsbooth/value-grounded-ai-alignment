"""Right-padded causal-LM batches with explicit prompt/response masks."""

from __future__ import annotations

import json
from typing import Any, Iterable, Mapping

from vgta_eval.input_contracts import build_response_target
from vgta_eval.semantic_worlds import PrivateAnnotation, PublicExample

from .model_loader import ModelDependencyError


def _torch():
    try:
        import torch
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PyTorch is required for batching") from exc
    return torch


def _ids(tokenizer: Any, text: str) -> list[int]:
    encoded = tokenizer(text, add_special_tokens=True, truncation=False)
    return list(encoded["input_ids"])


def collate_examples(
    examples: Iterable[PublicExample],
    tokenizer: Any,
    *,
    annotations: Mapping[str, PrivateAnnotation] | None = None,
    structured: bool = False,
    max_length: int = 2048,
) -> dict[str, Any]:
    torch = _torch()
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    rows: list[tuple[list[int], list[int], list[int], list[int], PublicExample]] = []
    for example in examples:
        prompt = example.model_bytes(structured=structured).decode("utf-8")
        prompt_ids = _ids(tokenizer, prompt)
        response_ids: list[int] = []
        if annotations is not None:
            if example.public_id not in annotations:
                raise ValueError(f"missing private annotation for {example.public_id}")
            response_ids = _ids(tokenizer, json.dumps(build_response_target(annotations[example.public_id]), sort_keys=True))
            if len(prompt_ids) + len(response_ids) > max_length:
                raise ValueError(
                    f"response target for {example.public_id} would be truncated at max_length={max_length}; "
                    "increase the protocol context or shorten the public rendering"
                )
        input_ids = (prompt_ids + response_ids)[:max_length]
        prompt_len = min(len(prompt_ids), len(input_ids))
        response_mask = [0] * prompt_len + [1] * max(0, len(input_ids) - prompt_len)
        prompt_mask = [1] * prompt_len + [0] * max(0, len(input_ids) - prompt_len)
        labels = [-100] * prompt_len + input_ids[prompt_len:]
        rows.append((input_ids, labels, prompt_mask, response_mask, example))
    width = max((len(row[0]) for row in rows), default=1)
    ids = torch.full((len(rows), width), pad_id, dtype=torch.long)
    labels = torch.full((len(rows), width), -100, dtype=torch.long)
    attention = torch.zeros((len(rows), width), dtype=torch.long)
    prompt_mask = torch.zeros((len(rows), width), dtype=torch.bool)
    response_mask = torch.zeros((len(rows), width), dtype=torch.bool)
    for index, (row_ids, row_labels, row_prompt, row_response, _) in enumerate(rows):
        size = len(row_ids)
        ids[index, :size] = torch.tensor(row_ids, dtype=torch.long)
        labels[index, :size] = torch.tensor(row_labels, dtype=torch.long)
        attention[index, :size] = 1
        prompt_mask[index, :size] = torch.tensor(row_prompt, dtype=torch.bool)
        response_mask[index, :size] = torch.tensor(row_response, dtype=torch.bool)
    return {
        "input_ids": ids,
        "attention_mask": attention,
        "labels": labels,
        "prompt_mask": prompt_mask,
        "response_mask": response_mask,
        "response_token_count": int(response_mask.sum().item()),
        "prompt_token_count": int(prompt_mask.sum().item()),
        "public_ids": [row[4].public_id for row in rows],
    }
