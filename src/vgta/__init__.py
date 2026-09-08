"""Small, dependency-free interfaces for the VGA research scaffold.

The package intentionally does not implement a full Transformer.  It exposes
the boundaries that a future experimental implementation would need to make
explicit: ontology loading, semantic bias construction, expert routing,
episode state, and independent action verification.
"""

from .ontology import Ontology, Triple, parse_turtle
from .semantic_state import SemanticState
from .verifier import CandidateAction, RuleBasedVerifier, VerificationResult

__all__ = [
    "CandidateAction",
    "Ontology",
    "RuleBasedVerifier",
    "SemanticState",
    "Triple",
    "VerificationResult",
    "parse_turtle",
]

__version__ = "0.1.0"
