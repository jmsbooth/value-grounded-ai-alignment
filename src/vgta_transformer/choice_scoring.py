"""Fixed-continuation likelihood scoring, separate from free generation."""

from __future__ import annotations

from typing import Any, Iterable


def score_continuations(model: Any, tokenizer: Any, prompt: str, continuations: Iterable[str], *, device: str = "cpu") -> dict[str, float]:
    import torch
    scores: dict[str, float] = {}
    model.eval()
    with torch.no_grad():
        for continuation in continuations:
            encoded = tokenizer(prompt + continuation, return_tensors="pt", truncation=True, max_length=2048)
            encoded = {key: value.to(device) for key, value in encoded.items()}
            logits = model(**encoded, use_cache=False).logits[:, :-1]
            token_ids = encoded["input_ids"][:, 1:]
            log_probs = logits.log_softmax(-1).gather(-1, token_ids.unsqueeze(-1)).squeeze(-1)
            scores[continuation] = float(log_probs.sum().cpu())
    return scores

