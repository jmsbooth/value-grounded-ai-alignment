"""Optional pretrained-Transformer integration for the Pythia phase.

Importing this package does not import PyTorch or download model weights.
"""

from .model_loader import MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA

__all__ = ["MODEL_ID", "REQUESTED_REVISION", "RESOLVED_REVISION_SHA"]

