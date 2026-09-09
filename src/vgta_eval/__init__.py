"""Reproducible, small-scale empirical evaluation components for VGA.

The first executable release is a mechanism-validation proxy: a shared
NumPy multilayer perceptron with explicit semantic channels, not a
Transformer.  Results are therefore evidence about this controlled proxy and
its generated benchmark, not about frontier language models.
"""

from .metrics import metric_summary
from .model import MODEL_VARIANT_GROUPS, SmallSemanticModel
from .scenario_generator import generate_dataset, generate_remediated_dataset, load_dataset, write_dataset, write_remediated_dataset

__all__ = [
    "MODEL_VARIANT_GROUPS",
    "SmallSemanticModel",
    "generate_dataset",
    "generate_remediated_dataset",
    "load_dataset",
    "metric_summary",
    "write_dataset",
    "write_remediated_dataset",
]
