"""Calibration and selective-prediction metrics with bounded inputs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np


def _probabilities(rows: Sequence[Mapping[str, Any]]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not rows:
        raise ValueError("rows must not be empty")
    probabilities = np.asarray([row["action_probabilities"] for row in rows], dtype=float)
    if probabilities.ndim != 2 or np.any(probabilities < 0.0) or np.any(probabilities.sum(axis=1) <= 0.0):
        raise ValueError("action probabilities must be a nonnegative 2-D array with positive row sums")
    probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
    labels = np.asarray([int(row["target_action_index"]) for row in rows], dtype=int)
    predicted = np.argmax(probabilities, axis=1)
    return probabilities, labels, predicted


def brier_score(rows: Sequence[Mapping[str, Any]]) -> float:
    probabilities, labels, _ = _probabilities(rows)
    one_hot = np.zeros_like(probabilities)
    one_hot[np.arange(len(labels)), labels] = 1.0
    return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))


def expected_calibration_error(rows: Sequence[Mapping[str, Any]], bins: int = 10) -> float:
    if bins < 1:
        raise ValueError("bins must be positive")
    probabilities, labels, predicted = _probabilities(rows)
    confidence = np.max(probabilities, axis=1)
    correct = predicted == labels
    error = 0.0
    for lower, upper in zip(np.linspace(0.0, 1.0, bins, endpoint=False), np.linspace(0.0, 1.0, bins + 1)[1:]):
        selected = (confidence >= lower) & ((confidence < upper) if upper < 1.0 else (confidence <= upper))
        if np.any(selected):
            error += float(np.sum(selected)) / len(rows) * abs(float(np.mean(confidence[selected])) - float(np.mean(correct[selected])))
    return error


def risk_coverage(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, float]]:
    probabilities, labels, predicted = _probabilities(rows)
    confidence = np.max(probabilities, axis=1)
    order = np.argsort(-confidence)
    output = []
    for count in range(1, len(rows) + 1):
        selected = order[:count]
        output.append({"coverage": count / len(rows), "risk": float(1.0 - np.mean(predicted[selected] == labels[selected])), "selective_accuracy": float(np.mean(predicted[selected] == labels[selected]))})
    return output


def calibration_summary(rows: Sequence[Mapping[str, Any]], *, bins: int = 10, abstention_threshold: float = 0.5) -> dict[str, Any]:
    probabilities, labels, predicted = _probabilities(rows)
    confidence = np.max(probabilities, axis=1)
    selected = confidence >= abstention_threshold
    return {
        "n": len(rows),
        "brier_score": brier_score(rows),
        "ece": expected_calibration_error(rows, bins=bins),
        "selective_accuracy_at_threshold": float(np.mean(predicted[selected] == labels[selected])) if np.any(selected) else 0.0,
        "abstention_rate": float(1.0 - np.mean(selected)),
        "false_confidence_rate": float(np.mean((predicted != labels) & (confidence >= 0.8))),
        "risk_coverage": risk_coverage(rows),
    }


def calibration_self_test() -> dict[str, Any]:
    rows = [{"action_probabilities": [0.9, 0.1], "target_action_index": 0}, {"action_probabilities": [0.6, 0.4], "target_action_index": 1}]
    summary = calibration_summary(rows, bins=2)
    if not (0.0 <= summary["brier_score"] <= 2.0 and 0.0 <= summary["ece"] <= 1.0 and len(summary["risk_coverage"]) == 2):
        raise AssertionError("calibration self-test produced invalid bounded metrics")
    return summary
