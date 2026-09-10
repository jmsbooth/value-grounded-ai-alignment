"""Optional readout heads for values, relations, norms, and conflicts."""

from __future__ import annotations

from typing import Any, Mapping

from .model_loader import ModelDependencyError


def _torch():
    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("PyTorch is required for auxiliary heads") from exc
    return torch, nn


class AuxiliaryHeads:
    """A torch module created lazily so importing the repository stays light."""

    def __new__(cls, hidden_size: int, *, value_count: int, relation_count: int, norm_count: int, conflict_count: int):
        torch, nn = _torch()

        class _Heads(nn.Module):
            def __init__(self):
                super().__init__()
                self.values = nn.Linear(hidden_size, value_count)
                self.relation = nn.Linear(hidden_size, relation_count)
                self.norms = nn.Linear(hidden_size, norm_count)
                self.conflict = nn.Linear(hidden_size, conflict_count)

            def forward(self, hidden: Any) -> Mapping[str, Any]:
                return {
                    "values": self.values(hidden),
                    "relation": self.relation(hidden),
                    "norms": self.norms(hidden),
                    "conflict": self.conflict(hidden),
                }

        return _Heads()


def pool_last_hidden(last_hidden: Any, attention_mask: Any) -> Any:
    torch, _ = _torch()
    lengths = attention_mask.long().sum(dim=1).clamp_min(1) - 1
    batch = torch.arange(last_hidden.shape[0], device=last_hidden.device)
    return last_hidden[batch, lengths]


def pool_prompt_hidden(last_hidden: Any, prompt_mask: Any) -> Any:
    """Pool the last prompt token, excluding teacher-forced response tokens."""

    torch, _ = _torch()
    lengths = prompt_mask.long().sum(dim=1).clamp_min(1) - 1
    batch = torch.arange(last_hidden.shape[0], device=last_hidden.device)
    return last_hidden[batch, lengths]
