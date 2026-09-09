"""Compatibility checks for protocol, data, and scientific artifact versions."""

from __future__ import annotations

from typing import Mapping


REQUIRED_ARTIFACTS = (
    "protocol_version",
    "dataset_sha256",
    "ground_truth_sha256",
    "ontology_sha256",
    "verifier_sha256",
    "config_sha256",
    "attack_suite_sha256",
    "metric_suite_sha256",
)


class CompatibilityError(ValueError):
    """Raised when scientific artifacts cannot be compared safely."""


def validate_compatibility(actual: Mapping[str, object], expected: Mapping[str, object], *, run_mode: str = "development", allow_override: bool = False) -> None:
    missing = [key for key in REQUIRED_ARTIFACTS if key not in actual]
    mismatched = [key for key in REQUIRED_ARTIFACTS if key in actual and key in expected and actual[key] != expected[key]]
    if (missing or mismatched) and not (allow_override and run_mode == "development"):
        details = []
        if missing:
            details.append(f"missing={','.join(missing)}")
        if mismatched:
            details.append(f"mismatched={','.join(mismatched)}")
        raise CompatibilityError("incompatible scientific artifacts: " + "; ".join(details))
