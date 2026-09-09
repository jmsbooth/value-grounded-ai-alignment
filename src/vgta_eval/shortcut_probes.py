"""Small, dependency-light shortcut baselines for the synthetic benchmark."""

from __future__ import annotations

from collections import Counter
from math import log
from typing import Any, Mapping, Sequence

import numpy as np


def _label(row: Mapping[str, Any]) -> str:
    return str(row["labels"]["action"])


def _tokens(row: Mapping[str, Any], mode: str) -> list[str]:
    if mode == "surface":
        return [f"surface:{token}" for token in row.get("feature_groups", {}).get("surface", ())]
    if mode == "metadata":
        return [f"metadata:{row.get('family', '')}", f"metadata:{row.get('template_id', '')}", f"metadata:{row.get('transform', '')}"]
    if mode == "topology":
        return [f"topology:{token}" for token in row.get("topology_edges", ())]
    return []


def _vectorize(train: Sequence[Mapping[str, Any]], rows: Sequence[Mapping[str, Any]], mode: str, *, tfidf: bool = False) -> tuple[np.ndarray, list[str]]:
    vocabulary = sorted({token for row in train for token in _tokens(row, mode)})
    index = {token: position for position, token in enumerate(vocabulary)}
    matrix = np.zeros((len(rows), len(vocabulary)), dtype=float)
    for row_index, row in enumerate(rows):
        counts = Counter(_tokens(row, mode))
        for token, count in counts.items():
            if token in index:
                matrix[row_index, index[token]] = float(count)
    if tfidf and vocabulary:
        document_frequency = np.count_nonzero(matrix > 0.0, axis=0)
        matrix *= np.log((1.0 + len(rows)) / (1.0 + document_frequency)) + 1.0
    return matrix, vocabulary


def _linear_fit(train_x: np.ndarray, train_y: np.ndarray, class_count: int, seed: int = 11, epochs: int = 80) -> np.ndarray:
    rng = np.random.default_rng(seed)
    weights = rng.normal(0.0, 0.02, size=(class_count, train_x.shape[1] + 1))
    for _ in range(epochs):
        for index in rng.permutation(len(train_x)):
            x = np.concatenate(([1.0], train_x[index]))
            logits = weights @ x
            logits -= np.max(logits)
            probabilities = np.exp(logits)
            probabilities /= np.sum(probabilities)
            probabilities[int(train_y[index])] -= 1.0
            weights -= 0.05 * probabilities[:, None] * x[None, :]
    return weights


def _accuracy(rows: Sequence[Mapping[str, Any]], predictions: Sequence[str], *, family: str | None = None) -> float:
    selected = [(row, prediction) for row, prediction in zip(rows, predictions) if family is None or row.get("family") == family]
    return sum(_label(row) == prediction for row, prediction in selected) / len(selected) if selected else 0.0


def run_shortcut_probes(train: Sequence[Mapping[str, Any]], evaluation: Sequence[Mapping[str, Any]], *, seed: int = 11) -> dict[str, Any]:
    labels = sorted({_label(row) for row in train})
    label_index = {label: index for index, label in enumerate(labels)}
    majority = Counter(_label(row) for row in train).most_common(1)[0][0]
    results: dict[str, Any] = {"majority": {"overall_accuracy": _accuracy(evaluation, [majority] * len(evaluation))}}
    for name, mode, tfidf in (("bag_of_words", "surface", False), ("tfidf_logistic", "surface", True), ("metadata_only", "metadata", False), ("sequence_length_only", "length", False), ("topology_summary", "topology", False)):
        if mode == "length":
            train_x = np.asarray([[len(str(row.get("surface", "")).split())] for row in train], dtype=float)
            eval_x = np.asarray([[len(str(row.get("surface", "")).split())] for row in evaluation], dtype=float)
        else:
            train_x, _ = _vectorize(train, train, mode, tfidf=tfidf)
            eval_x, _ = _vectorize(train, evaluation, mode, tfidf=tfidf)
        weights = _linear_fit(train_x, np.asarray([label_index[_label(row)] for row in train]), len(labels), seed=seed)
        logits = np.c_[np.ones(len(eval_x)), eval_x] @ weights.T
        predictions = [labels[int(index)] for index in np.argmax(logits, axis=1)]
        results[name] = {"overall_accuracy": _accuracy(evaluation, predictions), "structural_ood_accuracy": _accuracy(evaluation, predictions, family="structural_ood"), "predictions": len(predictions)}
    surface_ood = results["bag_of_words"]["structural_ood_accuracy"]
    return {"baselines": results, "gate": {"surface_baseline_not_trivial": surface_ood < 0.9, "surface_structural_ood_accuracy": surface_ood, "passed": surface_ood < 0.9}, "labels": labels}
