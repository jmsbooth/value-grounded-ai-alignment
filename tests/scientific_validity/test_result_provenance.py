import pytest

from vgta_eval.evidence_receipts import make_receipt


def test_receipts_require_known_producer_class():
    receipt = make_receipt(producer_kind="semantic_audit", protocol="hv-v0.5.2-semantic-validity", status="SEMANTIC_DATASET_VALIDATED")
    assert receipt["receipt_version"] == "evidence-receipt-v1"
    assert len(receipt["receipt_digest"]) == 64
    with pytest.raises(ValueError):
        make_receipt(producer_kind="invented", protocol="x", status="x")

