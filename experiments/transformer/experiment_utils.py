"""Shared bounded-training utilities for the v0.6.1 experiment runners."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import random
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import numpy as np

from vgta_eval.evidence_receipts import canonical_digest
from vgta_eval.semantic_worlds import ACTION_CATALOGUE, VALUE_DEFINITIONS, PrivateAnnotation, PublicExample, SemanticDataset, generate_v2_dataset
from vgta_transformer.adaptation import add_lora
from vgta_transformer.auxiliary_heads import AuxiliaryHeads
from vgta_transformer.checkpointing import save_checkpoint
from vgta_transformer.collator import collate_examples
from vgta_transformer.model_loader import load_base_model, load_tokenizer, model_load_info
from vgta_transformer.response_parser import parser_reference, strict_parse


ROOT = Path(__file__).resolve().parents[2]
RELATION_CLASSES = ("policy_compliance", "consent_scope", "delegation_status", "recipient_authorization", "evidence_freshness", "requires_evidence", "policy_prohibition")
CONFLICT_CLASSES = ("no_conflict", "resolvable_conflict", "unresolved_conflict")


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)


def random_state() -> dict[str, Any]:
    import torch
    return {"python": random.getstate(), "numpy": np.random.get_state(), "torch": torch.get_rng_state()}


def dataset_for_profile(profile: str = "mini") -> SemanticDataset:
    return generate_v2_dataset(profile=profile)


def examples_for(dataset: SemanticDataset, split: str, limit: int | None = None) -> tuple[PublicExample, ...]:
    values = dataset.by_split(split)
    return values if limit is None else values[:limit]


def target_for(annotation: PrivateAnnotation) -> dict[str, Any]:
    from vgta_eval.input_contracts import build_response_target
    return build_response_target(annotation)


def auxiliary_target_tensors(annotations: Iterable[PrivateAnnotation], *, device: str = "cpu") -> dict[str, Any]:
    import torch
    rows = list(annotations)
    values = torch.zeros((len(rows), len(VALUE_DEFINITIONS)), dtype=torch.float32, device=device)
    relation = torch.zeros((len(rows), len(RELATION_CLASSES)), dtype=torch.float32, device=device)
    norms = torch.zeros((len(rows), 5), dtype=torch.float32, device=device)
    conflict = torch.zeros((len(rows), len(CONFLICT_CLASSES)), dtype=torch.float32, device=device)
    value_index = {name: index for index, (name, _) in enumerate(VALUE_DEFINITIONS)}
    relation_index = {name: index for index, name in enumerate(RELATION_CLASSES)}
    conflict_index = {name: index for index, name in enumerate(CONFLICT_CLASSES)}
    for row, annotation in enumerate(rows):
        for value in annotation.salient_values:
            if value in value_index:
                values[row, value_index[value]] = 1.0
        if annotation.relation_class in relation_index:
            relation[row, relation_index[annotation.relation_class]] = 1.0
        for norm in annotation.applicable_norm_ids:
            number = int(norm.rsplit("_", 1)[-1]) - 1
            if 0 <= number < 5:
                norms[row, number] = 1.0
        if annotation.conflict_class in conflict_index:
            conflict[row, conflict_index[annotation.conflict_class]] = 1.0
    return {"values": values, "relation": relation, "norms": norms, "conflict": conflict}


def head_for_variant(variant: str, hidden_size: int) -> tuple[Any | None, tuple[str, ...]]:
    import torch
    active = {
        "A1": (), "B": (), "C1": ("values", "relation"), "C2": ("values", "relation", "norms", "conflict"),
        "B-TEXT-A": (), "C1-TEXT-N": ("values", "relation"), "C1-SHAM": ("values", "relation"), "C2-SHAM": ("values", "relation", "norms", "conflict"),
    }[variant]
    if not active:
        return None, active
    return AuxiliaryHeads(hidden_size, value_count=4, relation_count=len(RELATION_CLASSES), norm_count=5, conflict_count=len(CONFLICT_CLASSES)), active


def optimizer_for(model: Any, heads: Any | None, *, learning_rate: float, weight_decay: float) -> Any:
    import torch
    params = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if heads is not None:
        params.extend(parameter for parameter in heads.parameters() if parameter.requires_grad)
    return torch.optim.AdamW(params, lr=learning_rate, betas=(0.9, 0.999), eps=1e-8, weight_decay=weight_decay)


def build_model(seed: int, *, device: str = "cpu", variant: str = "A1") -> tuple[Any, Any, Any | None, tuple[str, ...]]:
    seed_everything(seed)
    tokenizer = load_tokenizer(local_files_only=True)
    model = add_lora(load_base_model(local_files_only=True, device=device))
    heads, active = head_for_variant(variant, model.config.hidden_size)
    if heads is not None:
        heads.to(device)
    return model, tokenizer, heads, active


def batch_for(example: PublicExample, annotation: PrivateAnnotation, tokenizer: Any, *, structured: bool, device: str = "cpu", max_length: int = 2048) -> dict[str, Any]:
    batch = collate_examples((example,), tokenizer, annotations={example.public_id: annotation}, structured=structured, max_length=max_length)
    return {key: value.to(device) if hasattr(value, "to") else value for key, value in batch.items()}


def evaluate_nll(model: Any, tokenizer: Any, examples: Iterable[PublicExample], annotations: Mapping[str, PrivateAnnotation], *, structured: bool, device: str = "cpu") -> dict[str, float]:
    import torch
    from vgta_transformer.training import response_loss_from_outputs
    examples = tuple(examples)
    model.eval()
    numerator = 0.0
    count = 0.0
    with torch.no_grad():
        for offset in range(0, len(examples), 8):
            chunk = examples[offset:offset + 8]
            batch = collate_examples(chunk, tokenizer, annotations={example.public_id: annotations[example.public_id] for example in chunk}, structured=structured, max_length=2048)
            batch = {key: value.to(device) if hasattr(value, "to") else value for key, value in batch.items()}
            output = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], use_cache=False)
            loss, tokens = response_loss_from_outputs(output, batch)
            numerator += float(loss.detach().cpu()) * float(tokens.detach().cpu())
            count += float(tokens.detach().cpu())
    return {"response_nll": numerator / max(1.0, count), "response_tokens": count, "examples": float(len(examples))}


def public_reference(example: PublicExample) -> dict[str, Any]:
    ref = parser_reference(example)
    ref["norm_ids"] = sorted(set(re.findall(r"norm_[0-9]{2}", example.model_bytes(structured=True).decode("utf-8"))))
    return ref


def generate_record(model: Any, tokenizer: Any, example: PublicExample, annotation: PrivateAnnotation, *, structured: bool, max_new_tokens: int = 256, device: str = "cpu", attack: str | None = None) -> dict[str, Any]:
    prompt = example.model_bytes(structured=structured).decode("utf-8")
    return generate_record_for_prompt(model, tokenizer, example, annotation, prompt=prompt, max_new_tokens=max_new_tokens, device=device, attack=attack, structured=structured)


def generate_record_for_prompt(model: Any, tokenizer: Any, example: PublicExample, annotation: PrivateAnnotation, *, prompt: str, max_new_tokens: int = 256, device: str = "cpu", attack: str | None = None, structured: bool = False) -> dict[str, Any]:
    import torch
    encoded = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    encoded = {key: value.to(device) for key, value in encoded.items()}
    model.eval()
    with torch.no_grad():
        generated = model.generate(**encoded, do_sample=False, max_new_tokens=max_new_tokens, pad_token_id=tokenizer.pad_token_id, use_cache=True)
    input_width = int(encoded["input_ids"].shape[1])
    continuation_ids = generated[0, input_width:].detach().cpu().tolist()
    raw = tokenizer.decode(continuation_ids, skip_special_tokens=True)
    result = strict_parse(raw, public_reference=public_reference(example), stopped_at_token_cap=len(continuation_ids) >= max_new_tokens)
    predicted = result.value.get("candidate_id") if result.valid and result.value else None
    return {
        "public_id": example.public_id,
        "world_group_id": example.world_group_id,
        "split": example.split,
        "variant": None,
        "seed": None,
        "attack": attack,
        "structured_input": structured,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_token_count": input_width,
        "prompt_token_ids": encoded["input_ids"][0].detach().cpu().tolist(),
        "generated_token_ids": continuation_ids,
        "generated_token_count": len(continuation_ids),
        "generation_cap": max_new_tokens,
        "stop_reason": "token_cap" if len(continuation_ids) >= max_new_tokens else "eos_or_model_stop",
        "raw_model_output": raw,
        "parser": result.__dict__,
        "parse_success": result.valid,
        "predicted_candidate_id": predicted,
        "expected_candidate_id": annotation.candidate_id,
        "policy_assessable": result.valid,
        "policy_permitted": (result.valid and bool(result.value.get("permitted"))) if result.valid and result.value else None,
        "task_correct": predicted == annotation.candidate_id if predicted is not None else None,
        "uncertainty_or_missing_evidence_expected": bool(annotation.required_information),
        "mock_enforcement": "allow" if result.valid and result.value.get("permitted") else "fail_closed_block",
        "enforcement_is_not_model_safety_evidence": True,
    }


def save_model_checkpoint(path: Path, model: Any, heads: Any | None, optimizer: Any, *, metadata: Mapping[str, Any]) -> dict[str, str]:
    return save_checkpoint(path, model, auxiliary_heads=heads, optimizer=optimizer, random_state=random_state(), metadata=dict(metadata))


def reload_checkpoint(path: Path, *, device: str = "cpu", hidden_size: int = 1024, variant: str = "A1") -> tuple[Any, Any, Any | None, tuple[str, ...]]:
    """Reload an adapter checkpoint onto the exact pinned base model."""

    import torch
    from peft import PeftModel
    from vgta_transformer.checkpointing import verify_checkpoint
    if not all(verify_checkpoint(path).values()):
        raise ValueError(f"refusing to load unverified checkpoint: {path}")
    tokenizer = load_tokenizer(local_files_only=True)
    base = load_base_model(local_files_only=True, device=device)
    model = PeftModel.from_pretrained(base, path / "adapter", is_trainable=False)
    heads, active = head_for_variant(variant, hidden_size)
    if heads is not None:
        heads.load_state_dict(torch.load(path / "auxiliary-heads.pt", map_location=device, weights_only=False))
        heads.to(device)
    return model, tokenizer, heads, active


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config_digest(protocol_root: Path) -> str:
    files = {str(path.relative_to(protocol_root)): file_digest(path) for path in sorted(protocol_root.iterdir()) if path.is_file()}
    return canonical_digest(files)
