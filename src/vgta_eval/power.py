"""Conservative sample-size planning for future confirmatory comparisons."""

from __future__ import annotations

from statistics import NormalDist
from typing import Any, Sequence


def required_scenarios(effect: float, *, baseline: float = 0.5, alpha: float = 0.05, power: float = 0.8) -> int:
    if not 0.0 < effect < 1.0:
        raise ValueError("effect must be a positive proportion less than one")
    if not 0.0 < baseline < 1.0:
        raise ValueError("baseline must be between zero and one")
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    z_power = NormalDist().inv_cdf(power)
    alternative = min(0.999, baseline + effect)
    pooled = 2.0 * baseline * (1.0 - baseline)
    separate = baseline * (1.0 - baseline) + alternative * (1.0 - alternative)
    n = ((z_alpha * (pooled ** 0.5) + z_power * (separate ** 0.5)) / effect) ** 2
    return max(1, int(n + 0.999))


def power_plan(effects: Sequence[float] = (0.03, 0.05, 0.10), *, seeds: Sequence[int] = (3, 5)) -> dict[str, Any]:
    rows = []
    for effect in effects:
        scenarios = required_scenarios(effect)
        rows.append({"minimum_effect": effect, "required_scenarios_per_variant": scenarios, "seeds": list(seeds), "total_evaluations_per_variant": scenarios * len(seeds)})
    return {"assumptions": {"baseline": 0.5, "alpha": 0.05, "power": 0.8, "two_sided": True, "method": "normal approximation for independent binary proportions; planning only"}, "recommendations": rows}
