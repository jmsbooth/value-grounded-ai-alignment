"""Small-sample statistical summaries used by the preregistered pilot."""

from __future__ import annotations

import random
from statistics import mean, pstdev
from typing import Callable, Sequence


def bootstrap_ci(values: Sequence[float], *, iterations: int = 4000, seed: int = 1729, confidence: float = 0.95) -> tuple[float, float]:
    if not values:
        raise ValueError("values must not be empty")
    rng = random.Random(seed)
    sample = tuple(float(value) for value in values)
    estimates = [mean(rng.choice(sample) for _ in sample) for _ in range(iterations)]
    estimates.sort()
    tail = (1.0 - confidence) / 2.0
    return estimates[int(tail * iterations)], estimates[max(0, int((1.0 - tail) * iterations) - 1)]


def paired_bootstrap_difference(left: Sequence[float], right: Sequence[float], *, iterations: int = 4000, seed: int = 1729) -> tuple[float, tuple[float, float], float]:
    if len(left) != len(right) or not left:
        raise ValueError("paired inputs must have equal non-zero length")
    differences = [float(a) - float(b) for a, b in zip(left, right)]
    interval = bootstrap_ci(differences, iterations=iterations, seed=seed)
    return mean(differences), interval, _standardized_effect(differences)


def _standardized_effect(values: Sequence[float]) -> float:
    deviation = pstdev(values)
    return mean(values) / deviation if deviation else (0.0 if not mean(values) else float("inf"))


def summarize_seed_values(values: Sequence[float]) -> dict[str, float | int | list[float]]:
    interval = bootstrap_ci(values)
    return {
        "n_seeds": len(values),
        "mean": mean(values),
        "seed_stddev": pstdev(values) if len(values) > 1 else 0.0,
        "bootstrap_95_ci": [interval[0], interval[1]],
    }
