#!/usr/bin/env python3
"""Execute reference, truth-table, and mutation checks for candidate scoring."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vgta_eval.candidate_evaluator import evaluate_candidate
from vgta_eval.evidence_receipts import make_receipt, sha256_file, write_receipt
from vgta_eval.observation_projection import project_world
from vgta_eval.prediction_scoring import score_prediction
from vgta_eval.reference_policy import interpret_observation
from vgta_eval.semantic_worlds import ACTION_CATALOGUE


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    from vgta_eval.input_contracts import build_response_target
    from vgta_eval.semantic_worlds import generate_v2_dataset
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-independent-score")
    output_dir = args.output_dir or ROOT / "results/raw/te-v0.6.2-pythia-correction/independent-scoring" / run_id
    dataset = generate_v2_dataset(profile="mini")
    rows = []
    truth_table = []
    open_examples = dataset.by_split("open-dev")
    world_map = {world.world_id: world for world in dataset.worlds}
    annotations = dataset.annotation_map()
    for example in open_examples:
        world = world_map[example.public_id.removeprefix("public-")]
        observation = project_world(world)
        target = build_response_target(annotations[example.public_id])
        raw = json.dumps(target, sort_keys=True, separators=(",", ":"))
        scored = score_prediction(example, observation, raw)
        rows.append(scored)
        for candidate_id, _ in ACTION_CATALOGUE:
            verdict = evaluate_candidate(interpret_observation, observation, ACTION_CATALOGUE, candidate_id)
            truth_table.append({"public_id": example.public_id, "candidate_id": candidate_id, "permission": verdict.permission, "utility": verdict.utility, "authoritative_candidate_id": verdict.authoritative_candidate_id})
        mutated = json.loads(raw)
        mutated["permitted"] = not mutated["permitted"]
        mutated["useful"] = not mutated["useful"]
        mutated_row = score_prediction(example, observation, json.dumps(mutated, sort_keys=True, separators=(",", ":")))
        assert mutated_row["evaluator"] == scored["evaluator"], "evaluator changed when model claims changed"
    result = {"protocol": "te-v0.6.2-pythia-correction", "experiment_id": "independent-scoring", "run_id": run_id, "status": "INDEPENDENT_SCORING_VALIDATED", "rows": rows, "truth_table": truth_table, "mutation_tests": {"claim_flip_invariant": True, "candidate_catalogue_fixed": True}, "locked_data_read_or_scored": False}
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "result.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, default=list) + "\n", encoding="utf-8")
    receipt = make_receipt(producer_kind="semantic_audit", protocol=result["protocol"], status=result["status"], experiment_id=result["experiment_id"], run_id=run_id, result_sha256=sha256_file(output), row_count=len(rows), truth_table_rows=len(truth_table), locked_data_read_or_scored=False)
    write_receipt(output_dir / "evidence-receipt.json", receipt)
    print(json.dumps({"status": result["status"], "run_id": run_id, "rows": len(rows), "receipt_digest": receipt["receipt_digest"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
