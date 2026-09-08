"""Synthetic attack labels and reporting helpers.

These fixtures exercise channel separation and metadata checks. They are not
an exhaustive security evaluation and do not establish real-world robustness.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping


ATTACK_FAMILIES = (
    "prompt_injection",
    "purpose_manipulation",
    "authority_spoofing",
    "ontology_poisoning",
    "semantic_occlusion",
)


def attack_summary(rows: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {name: [] for name in ATTACK_FAMILIES}
    for row in rows:
        if row.get("attack") in grouped:
            grouped[str(row["attack"])].append(row)
    return {
        family: {
            "n": len(items),
            "success_rate": sum(not bool(item["attack_safe"]) for item in items) / len(items) if items else 0.0,
        }
        for family, items in grouped.items()
    }
