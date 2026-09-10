"""Exact, offline-by-default loading for EleutherAI Pythia-410M."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


MODEL_ID = "EleutherAI/pythia-410m"
REQUESTED_REVISION = "step143000"
RESOLVED_REVISION_SHA = "bba6a464f54bbf08fc174cfb351d9794d58af21d"
EXPECTED_CONFIG = {
    "model_type": "gpt_neox",
    "architectures": ("GPTNeoXForCausalLM",),
    "num_hidden_layers": 24,
    "hidden_size": 1024,
    "num_attention_heads": 16,
    "intermediate_size": 4096,
    "max_position_embeddings": 2048,
}


class ModelDependencyError(RuntimeError):
    """Raised when optional Transformer dependencies are not installed."""


class ModelIntegrityError(RuntimeError):
    """Raised when a loaded model is not the requested Pythia checkpoint."""


@dataclass(frozen=True)
class ModelLoadInfo:
    model_id: str
    requested_revision: str
    resolved_revision_sha: str
    config: dict[str, Any]
    device: str
    local_files_only: bool


def _imports():
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, GPTNeoXForCausalLM
    except ImportError as exc:  # pragma: no cover - exercised in dependency-light CI
        raise ModelDependencyError("install the isolated Pythia environment to use model integration") from exc
    return torch, AutoModelForCausalLM, AutoTokenizer, GPTNeoXForCausalLM


def resolve_model_revision(*, model_id: str = MODEL_ID, revision: str = REQUESTED_REVISION) -> str:
    """Return the reviewed immutable revision; resolution is intentionally explicit."""

    if model_id == MODEL_ID and revision == REQUESTED_REVISION:
        return RESOLVED_REVISION_SHA
    raise ModelIntegrityError("unreviewed model or revision; add an explicit protocol update before use")


def _validate_config(config: Any) -> dict[str, Any]:
    actual = {
        "model_type": str(getattr(config, "model_type", "")),
        "architectures": tuple(getattr(config, "architectures", ()) or ()),
        "num_hidden_layers": int(getattr(config, "num_hidden_layers", -1)),
        "hidden_size": int(getattr(config, "hidden_size", -1)),
        "num_attention_heads": int(getattr(config, "num_attention_heads", -1)),
        "intermediate_size": int(getattr(config, "intermediate_size", -1)),
        "max_position_embeddings": int(getattr(config, "max_position_embeddings", -1)),
    }
    if actual != EXPECTED_CONFIG:
        raise ModelIntegrityError(f"unexpected Pythia configuration: {actual}")
    if "GPTNeoXForCausalLM" not in actual["architectures"]:
        raise ModelIntegrityError("generic causal-LM architecture is not accepted")
    return actual


def load_tokenizer(*, cache_dir: str | Path | None = None, local_files_only: bool = True):
    _, _, AutoTokenizer, _ = _imports()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        revision=resolve_model_revision(),
        cache_dir=str(cache_dir) if cache_dir else None,
        local_files_only=local_files_only,
        trust_remote_code=False,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def load_base_model(*, cache_dir: str | Path | None = None, local_files_only: bool = True, device: str = "cpu"):
    torch, AutoModelForCausalLM, _, GPTNeoXForCausalLM = _imports()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=resolve_model_revision(),
        cache_dir=str(cache_dir) if cache_dir else None,
        local_files_only=local_files_only,
        trust_remote_code=False,
        dtype=torch.float32,
    )
    if not isinstance(model, GPTNeoXForCausalLM):
        raise ModelIntegrityError(f"loaded type {type(model).__name__}, expected GPTNeoXForCausalLM")
    _validate_config(model.config)
    if device not in {"cpu", "mps"}:
        raise ValueError("Pythia phase permits only cpu or explicit mps")
    if device == "mps" and not torch.backends.mps.is_available():
        raise ModelDependencyError("MPS requested but unavailable on this host")
    return model.to(device)


def model_load_info(model: Any, *, device: str, local_files_only: bool) -> ModelLoadInfo:
    config = _validate_config(model.config)
    return ModelLoadInfo(MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA, config, device, local_files_only)


def file_hashes(root: str | Path) -> dict[str, str]:
    """Hash an already-downloaded model directory without downloading anything."""

    root = Path(root)
    hashes: dict[str, str] = {}
    if not root.exists():
        return hashes
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        hashes[str(path.relative_to(root))] = digest.hexdigest()
    return hashes


def config_digest(model: Any) -> str:
    return hashlib.sha256(json.dumps(_validate_config(model.config), sort_keys=True).encode()).hexdigest()


def snapshot_asset_digest(*, local_files_only: bool = True) -> tuple[str, int]:
    """Return a digest over the verified local Hub snapshot without exposing its path."""

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:  # pragma: no cover
        raise ModelDependencyError("huggingface_hub is required to hash model assets") from exc
    snapshot = snapshot_download(MODEL_ID, revision=resolve_model_revision(), local_files_only=local_files_only)
    hashes = file_hashes(snapshot)
    if not hashes:
        raise ModelIntegrityError("verified model snapshot contains no files")
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return digest, len(hashes)
