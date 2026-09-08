"""Dependency-free statistical summaries for synthetic experiments."""

from __future__ import annotations

import random
from statistics import mean
from typing import Sequence


def bootstrap_mean_ci(
    values: Sequence[float],
    iterations: int = 2000,
    seed: int = 1729,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Percentile bootstrap interval for a bounded synthetic summary."""

    if not values:
        raise ValueError("values must not be empty")
    if iterations < 100:
        raise ValueError("iterations must be at least 100")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between zero and one")
    rng = random.Random(seed)
    sample = tuple(float(value) for value in values)
    estimates = [
        mean(rng.choice(sample) for _ in sample) for _ in range(iterations)
    ]
    estimates.sort()
    lower_index = int((1.0 - confidence) / 2.0 * iterations)
    upper_index = int((1.0 - (1.0 - confidence) / 2.0) * iterations) - 1
    return estimates[lower_index], estimates[upper_index]


def proportion_summary(values: Sequence[bool]) -> dict[str, float | int | list[float]]:
    """Summarize binary outcomes without implying population-level evidence."""

    if not values:
        raise ValueError("values must not be empty")
    numeric = [1.0 if value else 0.0 for value in values]
    interval = bootstrap_mean_ci(numeric)
    proportion = mean(numeric)
    return {
        "n": len(values),
        "proportion": proportion,
        "bootstrap_95_ci": [interval[0], interval[1]],
    }


def useful_conformance_rate(useful: Sequence[bool], conforming: Sequence[bool]) -> float:
    """Compute UCR; callers must define eligibility and usefulness in advance."""

    if len(useful) != len(conforming):
        raise ValueError("useful and conforming must have equal length")
    if not useful:
        raise ValueError("useful and conforming must not be empty")
    eligible = [is_useful and is_conforming for is_useful, is_conforming in zip(useful, conforming)]
    return sum(eligible) / len(eligible)
