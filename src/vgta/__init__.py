"""Small, dependency-free interfaces for the VGA research scaffold.

The package intentionally does not implement a full Transformer.  It exposes
the boundaries that a future experimental implementation would need to make
explicit: ontology loading, semantic bias construction, expert routing,
episode state, and independent action verification.
"""

from .ontology import Ontology, Triple, parse_turtle
from .canonical import AxiologicalNeuralModule, CanonicalAxiology, compile_axiology
from .conformance import ConformanceResult, evaluate_conformance
from .normative import (
    NormativeAssertion,
    NormativeAuthority,
    NormativeConflict,
    authority_function,
    classify_conflict,
    resolve_conflict,
)
from .semantic_state import SemanticState
from .verifier import CandidateAction, RuleBasedVerifier, VerificationResult

__all__ = [
    "CandidateAction",
    "AxiologicalNeuralModule",
    "CanonicalAxiology",
    "ConformanceResult",
    "NormativeAssertion",
    "NormativeAuthority",
    "NormativeConflict",
    "Ontology",
    "RuleBasedVerifier",
    "SemanticState",
    "Triple",
    "VerificationResult",
    "authority_function",
    "classify_conflict",
    "compile_axiology",
    "evaluate_conformance",
    "parse_turtle",
    "resolve_conflict",
]

__version__ = "0.3.0-preprint"
