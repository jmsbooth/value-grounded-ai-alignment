"""Cluster-aware analysis helpers for paired model outputs."""

from __future__ import annotations

from collections import defaultdict
import hashlib
from typing import Any, Iterable, Mapping

import numpy as np


def raw_denominators(rows: Iterable[Mapping[str, Any]], *, keys: tuple[str, ...] = ("variant", "seed", "split", "attack")) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        key = "|".join(str(row.get(name, "none")) for name in keys)
        counts[key] += 1
    return dict(sorted(counts.items()))


def clustered_bootstrap_delta(
    rows: Iterable[Mapping[str, Any]],
    *,
    left_variant: str,
    right_variant: str,
    score_key: str = "correct",
    cluster_key: str = "world_group_id",
    resamples: int = 2000,
    seed: int = 20260909,
) -> dict[str, Any]:
    """Bootstrap paired cluster means, preserving all rows within a world group."""

    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        variant = str(row.get("variant", ""))
        if variant not in {left_variant, right_variant}:
            continue
        grouped[str(row[cluster_key])][variant].append(float(row[score_key]))
    paired = [(np.mean(values[left_variant]), np.mean(values[right_variant])) for values in grouped.values() if left_variant in values and right_variant in values]
    if not paired:
        return {"left_variant": left_variant, "right_variant": right_variant, "clusters": 0, "delta": None, "ci95": None, "status": "insufficient_paired_clusters"}
    observed = float(np.mean([right - left for left, right in paired]))
    rng = np.random.default_rng(seed)
    samples = np.asarray([right - left for left, right in paired])
    indices = rng.integers(0, len(samples), size=(resamples, len(samples)))
    boot = samples[indices].mean(axis=1)
    return {
        "left_variant": left_variant,
        "right_variant": right_variant,
        "clusters": len(paired),
        "delta": observed,
        "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
        "bootstrap_resamples": resamples,
        "bootstrap_seed": seed,
        "unit_of_inference": cluster_key,
        "status": "complete",
    }


def analysis_input_digest(rows: Iterable[Mapping[str, Any]]) -> str:
    lines = ["|".join(f"{key}={row.get(key, '')}" for key in sorted(row)) for row in rows]
    return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()

