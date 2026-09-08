"""A small shared semantic-channel model for mechanism validation.

This is intentionally not a Transformer.  It is a transparent, fixed-size
multitask MLP used to test whether the proposed channel separation and
auxiliary objectives produce measurable differences before larger training is
attempted.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


MODEL_VARIANT_GROUPS: dict[str, tuple[str, ...]] = {
    "A1": ("surface",),
    "B": ("surface", "ontology", "purpose", "world"),
    "C1": ("surface", "ontology", "purpose", "world", "axiological"),
    "C2": ("surface", "ontology", "purpose", "world", "axiological", "normative"),
}


@dataclass(frozen=True)
class ModelConfig:
    hidden_dim: int = 24
    epochs: int = 90
    learning_rate: float = 0.08
    l2: float = 1.0e-4
    value_loss_weight: float = 0.45
    relation_loss_weight: float = 0.45
    conflict_loss_weight: float = 0.55
    purpose_loss_weight: float = 0.15
    capability_loss_weight: float = 0.20


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exp = np.exp(shifted)
    return exp / np.sum(exp)


def _sigmoid(logits: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(logits, -40.0, 40.0)))


class SmallSemanticModel:
    """Shared MLP with action and semantic diagnostic heads."""

    HEADS = ("action", "relation", "conflict", "purpose", "capability")

    def __init__(self, feature_names: Sequence[str], labels: Mapping[str, Sequence[str]], config: ModelConfig, seed: int):
        self.feature_names = tuple(feature_names)
        self.feature_index = {name: index for index, name in enumerate(self.feature_names)}
        self.labels = {key: tuple(value) for key, value in labels.items()}
        self.label_index = {key: {value: index for index, value in enumerate(values)} for key, values in self.labels.items()}
        self.config = config
        self.seed = seed
        rng = np.random.default_rng(seed)
        input_dim = len(self.feature_names)
        hidden_dim = config.hidden_dim
        self.W = rng.normal(0.0, 0.08, size=(hidden_dim, input_dim))
        self.b = np.zeros(hidden_dim)
        self.heads: dict[str, np.ndarray] = {}
        self.head_bias: dict[str, np.ndarray] = {}
        for head in self.HEADS:
            rows = len(self.labels[head])
            self.heads[head] = rng.normal(0.0, 0.08, size=(rows, hidden_dim))
            self.head_bias[head] = np.zeros(rows)
        self.heads["value"] = rng.normal(0.0, 0.08, size=(len(self.labels["value"]), hidden_dim))
        self.head_bias["value"] = np.zeros(len(self.labels["value"]))

    def clone(self) -> "SmallSemanticModel":
        return deepcopy(self)

    @property
    def parameter_count(self) -> int:
        return int(self.W.size + self.b.size + sum(value.size for value in self.heads.values()) + sum(value.size for value in self.head_bias.values()))

    def _vectorize(self, record: Mapping[str, Any], groups: Sequence[str]) -> np.ndarray:
        vector = np.zeros(len(self.feature_names), dtype=float)
        feature_groups = record["feature_groups"]
        for group in groups:
            for feature in feature_groups.get(group, ()):
                index = self.feature_index.get(feature)
                if index is not None:
                    vector[index] = 1.0
        return vector

    def _hidden(self, record: Mapping[str, Any], groups: Sequence[str]) -> tuple[np.ndarray, np.ndarray]:
        x = self._vectorize(record, groups)
        z = self.W @ x + self.b
        return x, np.tanh(z)

    def predict(self, record: Mapping[str, Any], groups: Sequence[str]) -> dict[str, Any]:
        _, hidden = self._hidden(record, groups)
        output: dict[str, Any] = {}
        action_prob = _softmax(self.heads["action"] @ hidden + self.head_bias["action"])
        output["action_probabilities"] = action_prob.tolist()
        output["action"] = self.labels["action"][int(np.argmax(action_prob))]
        output["action_confidence"] = float(np.max(action_prob))
        relation_prob = _softmax(self.heads["relation"] @ hidden + self.head_bias["relation"])
        output["relation"] = self.labels["relation"][int(np.argmax(relation_prob))]
        conflict_prob = _softmax(self.heads["conflict"] @ hidden + self.head_bias["conflict"])
        output["conflict"] = self.labels["conflict"][int(np.argmax(conflict_prob))]
        purpose_prob = _softmax(self.heads["purpose"] @ hidden + self.head_bias["purpose"])
        output["purpose"] = self.labels["purpose"][int(np.argmax(purpose_prob))]
        capability_prob = _softmax(self.heads["capability"] @ hidden + self.head_bias["capability"])
        output["capability"] = self.labels["capability"][int(np.argmax(capability_prob))]
        value_prob = _sigmoid(self.heads["value"] @ hidden + self.head_bias["value"])
        output["values"] = [label for label, probability in zip(self.labels["value"], value_prob) if probability >= 0.5]
        if not output["values"]:
            output["values"] = [self.labels["value"][int(np.argmax(value_prob))]]
        output["value_probabilities"] = value_prob.tolist()
        return output

    def _targets(self, record: Mapping[str, Any]) -> dict[str, Any]:
        labels = record["labels"]
        return {
            "action": self.label_index["action"][labels["action"]],
            "relation": self.label_index["relation"][labels["relation"]],
            "conflict": self.label_index["conflict"][labels["conflict"]],
            "purpose": self.label_index["purpose"][labels["purpose"]],
            "capability": self.label_index["capability"][labels["capability"]] if labels.get("capability") else None,
            "value": np.asarray([1.0 if label in labels["values"] else 0.0 for label in self.labels["value"]]),
        }

    def fit(
        self,
        records: Sequence[Mapping[str, Any]],
        groups: Sequence[str],
        *,
        tasks: Mapping[str, float] | None = None,
        freeze_groups: Sequence[str] = (),
    ) -> dict[str, float]:
        if not records:
            raise ValueError("records must not be empty")
        weights = {
            "action": 1.0,
            "value": self.config.value_loss_weight,
            "relation": self.config.relation_loss_weight,
            "conflict": self.config.conflict_loss_weight,
            "purpose": self.config.purpose_loss_weight,
            "capability": self.config.capability_loss_weight,
        }
        if tasks is not None:
            weights.update(tasks)
        frozen_indices = {
            self.feature_index[feature]
            for group in freeze_groups
            for feature in self.feature_names
            if feature.startswith(f"{group}:") and feature in self.feature_index
        }
        rng = np.random.default_rng(self.seed + len(records) + int(self.config.epochs))
        losses: list[float] = []
        for _ in range(self.config.epochs):
            order = rng.permutation(len(records))
            epoch_loss = 0.0
            for position in order:
                record = records[int(position)]
                x, hidden = self._hidden(record, groups)
                targets = self._targets(record)
                grad_hidden = np.zeros_like(hidden)
                gradients: dict[str, np.ndarray] = {}
                bias_gradients: dict[str, np.ndarray] = {}
                record_loss = 0.0
                for head in ("action", "relation", "conflict", "purpose", "capability"):
                    weight = weights[head]
                    target = targets[head]
                    if weight <= 0.0 or target is None:
                        continue
                    probability = _softmax(self.heads[head] @ hidden + self.head_bias[head])
                    gradient_logits = probability.copy()
                    gradient_logits[int(target)] -= 1.0
                    gradients[head] = weight * np.outer(gradient_logits, hidden) + self.config.l2 * self.heads[head]
                    bias_gradients[head] = weight * gradient_logits
                    grad_hidden += weight * (self.heads[head].T @ gradient_logits)
                    record_loss += weight * -np.log(max(float(probability[int(target)]), 1.0e-12))
                if weights["value"] > 0.0:
                    probability = _sigmoid(self.heads["value"] @ hidden + self.head_bias["value"])
                    gradient_logits = weights["value"] * (probability - targets["value"])
                    gradients["value"] = np.outer(gradient_logits, hidden) + self.config.l2 * self.heads["value"]
                    bias_gradients["value"] = gradient_logits
                    grad_hidden += self.heads["value"].T @ gradient_logits
                    record_loss += weights["value"] * float(np.mean(-(targets["value"] * np.log(np.maximum(probability, 1.0e-12)) + (1.0 - targets["value"]) * np.log(np.maximum(1.0 - probability, 1.0e-12)))))
                grad_z = grad_hidden * (1.0 - hidden * hidden)
                grad_W = np.outer(grad_z, x) + self.config.l2 * self.W
                if frozen_indices:
                    grad_W[:, sorted(frozen_indices)] = 0.0
                learning_rate = self.config.learning_rate / max(1.0, len(records) ** 0.15)
                self.W -= learning_rate * grad_W
                self.b -= learning_rate * grad_z
                for head, gradient in gradients.items():
                    self.heads[head] -= learning_rate * gradient
                    self.head_bias[head] -= learning_rate * bias_gradients[head]
                epoch_loss += record_loss
            losses.append(epoch_loss / len(records))
        return {"initial_loss": losses[0], "final_loss": losses[-1], "epochs": float(self.config.epochs)}


def feature_vocabulary(records: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    features: set[str] = set()
    for record in records:
        for values in record["feature_groups"].values():
            features.update(values)
    return tuple(sorted(features))
