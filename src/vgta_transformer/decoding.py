"""Deterministic model decoding and fixed-schema response parsing."""

from __future__ import annotations

import json
from typing import Any


def generate_greedy(model: Any, tokenizer: Any, text: str, *, max_new_tokens: int = 96, device: str = "cpu") -> str:
    encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048)
    encoded = {key: value.to(device) for key, value in encoded.items()}
    output = model.generate(**encoded, do_sample=False, max_new_tokens=max_new_tokens, pad_token_id=tokenizer.pad_token_id)
    prompt_length = encoded["input_ids"].shape[1]
    return tokenizer.decode(output[0][prompt_length:], skip_special_tokens=True)


def parse_response(raw_text: str) -> dict[str, Any] | None:
    start, end = raw_text.find("{"), raw_text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(raw_text[start:end + 1])
    except json.JSONDecodeError:
        return None
    required = {"action", "candidate_id", "salient_values", "relation_class", "conflict_class", "applicable_norm_ids", "useful", "permitted"}
    if not isinstance(value, dict) or not required.issubset(value):
        return None
    return value
