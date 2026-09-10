from vgta_transformer.model_loader import EXPECTED_CONFIG, MODEL_ID, REQUESTED_REVISION, RESOLVED_REVISION_SHA, resolve_model_revision


def test_model_revision_is_pinned_to_reviewed_sha():
    assert MODEL_ID == "EleutherAI/pythia-410m"
    assert REQUESTED_REVISION == "step143000"
    assert resolve_model_revision() == RESOLVED_REVISION_SHA
    assert EXPECTED_CONFIG["max_position_embeddings"] == 2048

