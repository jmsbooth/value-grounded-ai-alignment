"""The v0.6.2 teacher-forcing and tokenizer contract.

This module is deliberately independent of the model implementation.  It
owns the byte-stable response serialization, explicit EOS construction, and
the character-to-token map used by the text-weighted controls.  Inference and
training must call the same prompt tokenizer policy.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping, Sequence

from vgta_eval.input_contracts import build_response_target
from vgta_eval.semantic_worlds import PrivateAnnotation, PublicExample


@dataclass(frozen=True)
class ResponseSerialization:
    text: str
    value_spans: Mapping[str, tuple[tuple[int, int], ...]]


@dataclass(frozen=True)
class TrainingSequence:
    prompt_ids: tuple[int, ...]
    response_ids: tuple[int, ...]
    input_ids: tuple[int, ...]
    labels: tuple[int, ...]
    prompt_mask: tuple[int, ...]
    response_mask: tuple[int, ...]
    response_weights: tuple[float, ...]
    response_text: str | None
    response_value_spans: Mapping[str, tuple[tuple[int, int], ...]]
    truncated: bool


def serialize_response_target(annotation: PrivateAnnotation) -> ResponseSerialization:
    """Serialize one response without tokenizer-added BOS/EOS or whitespace drift."""

    value = build_response_target(annotation)
    spans: dict[str, list[tuple[int, int]]] = {}

    def render(node: Any, path: str = "") -> str:
        if isinstance(node, dict):
            parts: list[str] = ["{"]  # Include the brace in absolute value offsets.
            for index, key in enumerate(sorted(node)):
                if index:
                    parts.append(",")
                parts.extend((json.dumps(str(key), ensure_ascii=False), ":"))
                child_path = f"{path}.{key}" if path else str(key)
                value_start = sum(len(part) for part in parts)
                child = render(node[key], child_path)
                parts.append(child)
                value_end = sum(len(part) for part in parts)
                if key in {"salient_values", "relation_class", "applicable_norm_ids", "conflict_class"}:
                    spans.setdefault(key, []).append((value_start, value_end))
            return "".join(parts) + "}"
        if isinstance(node, list):
            return "[" + ",".join(render(item, path) for item in node) + "]"
        return json.dumps(node, ensure_ascii=False, separators=(",", ":"))

    text = render(value)
    return ResponseSerialization(text=text, value_spans={key: tuple(value) for key, value in spans.items()})


def _as_list(value: Any) -> list[Any]:
    if hasattr(value, "detach"):
        value = value.detach().cpu().tolist()
    if isinstance(value, tuple):
        value = list(value)
    if value and isinstance(value[0], list):
        return list(value[0])
    return list(value or [])


def _tokenize(tokenizer: Any, text: str, *, offsets: bool = False) -> dict[str, Any]:
    """Tokenize without automatic specials; this is an intentional hard boundary."""

    kwargs: dict[str, Any] = {"add_special_tokens": False, "truncation": False}
    if offsets:
        kwargs["return_offsets_mapping"] = True
    try:
        encoded = tokenizer(text, **kwargs)
    except (TypeError, ValueError) as exc:
        if offsets:
            raise ValueError("the v0.6.2 text-weighted contract requires tokenizer offsets") from exc
        raise
    if not isinstance(encoded, Mapping):
        raise TypeError("tokenizer must return a mapping")
    return dict(encoded)


def tokenizer_special_audit(tokenizer: Any, text: str) -> dict[str, Any]:
    """Record both special-token modes so automatic EOS cannot be hidden."""

    audit: dict[str, Any] = {
        "special_tokens_map": dict(getattr(tokenizer, "special_tokens_map", {}) or {}),
        "bos_token_id": getattr(tokenizer, "bos_token_id", None),
        "eos_token_id": getattr(tokenizer, "eos_token_id", None),
        "pad_token_id": getattr(tokenizer, "pad_token_id", None),
    }
    for mode in (False, True):
        encoded = tokenizer(text, add_special_tokens=mode, truncation=False)
        audit[f"add_special_tokens_{str(mode).lower()}"] = _as_list(encoded["input_ids"])
    return audit


def _selected_weight_mask(tokenizer: Any, serialization: ResponseSerialization, selected_fields: Iterable[str]) -> tuple[float, ...]:
    selected = set(selected_fields)
    if not selected:
        return tuple(1.0 for _ in _as_list(_tokenize(tokenizer, serialization.text)["input_ids"]))
    encoded = _tokenize(tokenizer, serialization.text, offsets=True)
    offsets = _as_list(encoded.get("offset_mapping"))
    spans = [span for field, field_spans in serialization.value_spans.items() if field in selected for span in field_spans]
    weights: list[float] = []
    for start_end in offsets:
        start, end = (int(start_end[0]), int(start_end[1]))
        # Some tokenizers return (0, 0) for special tokens.  There are no
        # special tokens in this call, but retain the ordinary weight safely.
        overlap = end > start and any(start < span_end and end > span_start for span_start, span_end in spans)
        weights.append(2.0 if overlap else 1.0)
    if len(weights) != len(_as_list(encoded["input_ids"])):
        raise ValueError("tokenizer offset mapping width does not match token width")
    return tuple(weights)


def build_training_sequence(
    example: PublicExample,
    annotation: PrivateAnnotation | None,
    tokenizer: Any,
    *,
    structured: bool,
    max_length: int,
    span_weight_fields: Iterable[str] = (),
) -> TrainingSequence:
    """Build the exact prompt + response + one explicit EOS sequence."""

    prompt = example.model_bytes(structured=structured).decode("utf-8")
    prompt_ids = tuple(int(value) for value in _as_list(_tokenize(tokenizer, prompt)["input_ids"]))
    response_ids: tuple[int, ...] = ()
    response_text: str | None = None
    response_value_spans: Mapping[str, tuple[tuple[int, int], ...]] = {}
    response_weights: tuple[float, ...] = ()
    if annotation is not None:
        if annotation.public_id != example.public_id:
            raise ValueError("annotation/example identity mismatch")
        serialization = serialize_response_target(annotation)
        response_text = serialization.text
        response_value_spans = serialization.value_spans
        response_tokens = tuple(int(value) for value in _as_list(_tokenize(tokenizer, response_text)["input_ids"]))
        eos_id = getattr(tokenizer, "eos_token_id", None)
        if eos_id is None:
            raise ValueError("v0.6.2 requires a tokenizer eos_token_id")
        if response_tokens and response_tokens[-1] == int(eos_id):
            raise ValueError("response tokenizer unexpectedly supplied EOS with add_special_tokens=False")
        response_ids = response_tokens + (int(eos_id),)
        response_weights = _selected_weight_mask(tokenizer, serialization, span_weight_fields) + (1.0,)
        if len(response_weights) != len(response_ids):
            raise ValueError("response weight width does not include exactly one EOS")
    total = len(prompt_ids) + len(response_ids)
    if total > max_length:
        raise ValueError(
            f"response target for {example.public_id} exceeds max_length={max_length} "
            f"with prompt={len(prompt_ids)} response_plus_eos={len(response_ids)}"
        )
    input_ids = prompt_ids + response_ids
    labels = tuple([-100] * len(prompt_ids) + list(response_ids))
    prompt_mask = tuple([1] * len(prompt_ids) + [0] * len(response_ids))
    response_mask = tuple([0] * len(prompt_ids) + [1] * len(response_ids))
    weights = tuple([1.0] * len(prompt_ids) + list(response_weights))
    return TrainingSequence(
        prompt_ids=prompt_ids,
        response_ids=response_ids,
        input_ids=input_ids,
        labels=labels,
        prompt_mask=prompt_mask,
        response_mask=response_mask,
        response_weights=weights,
        response_text=response_text,
        response_value_spans=response_value_spans,
        truncated=False,
    )


def audit_tokenizer_contract(
    examples: Sequence[PublicExample],
    annotations: Mapping[str, PrivateAnnotation],
    tokenizer: Any,
    *,
    structured: bool,
    max_length: int,
) -> dict[str, Any]:
    """Return an auditable, JSON-serializable receipt for a real tokenizer."""

    rows: list[dict[str, Any]] = []
    for example in examples:
        annotation = annotations[example.public_id]
        sequence = build_training_sequence(example, annotation, tokenizer, structured=structured, max_length=max_length)
        prompt = example.model_bytes(structured=structured).decode("utf-8")
        rows.append({
            "public_id": example.public_id,
            "prompt_sha256": __import__("hashlib").sha256(prompt.encode("utf-8")).hexdigest(),
            "response_sha256": __import__("hashlib").sha256((sequence.response_text or "").encode("utf-8")).hexdigest(),
            "prompt_text": prompt,
            "response_text": sequence.response_text,
            "prompt_ids": list(sequence.prompt_ids),
            "response_ids_including_eos": list(sequence.response_ids),
            "input_ids": list(sequence.input_ids),
            "labels": list(sequence.labels),
            "prompt_mask": list(sequence.prompt_mask),
            "response_mask": list(sequence.response_mask),
            "response_weights": list(sequence.response_weights),
            "supervised_token_count": sum(sequence.response_mask),
            "eos_id": getattr(tokenizer, "eos_token_id", None),
            "special_audit": tokenizer_special_audit(tokenizer, prompt),
        })
    return {
        "contract": "te-v0.6.2-response-eos-v1",
        "structured": structured,
        "max_length": max_length,
        "row_count": len(rows),
        "rows": rows,
    }
