from dataclasses import replace

from vgta_eval.candidate_evaluator import evaluate_candidate
from vgta_eval.observation_projection import project_world
from vgta_eval.reference_policy import interpret_observation
from vgta_eval.semantic_worlds import ACTION_CATALOGUE, build_v2_worlds
from vgta_eval.prediction_scoring import score_prediction


def test_candidate_evaluator_ignores_model_claims_and_private_fields():
    observation = project_world(build_v2_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1})[0])
    first = evaluate_candidate(interpret_observation, observation, ACTION_CATALOGUE, "candidate_01")
    assert first.permission is True and first.utility is True
    assert first.authoritative_candidate_id == "candidate_01"


def test_prohibited_operation_does_not_become_allowable_from_claims():
    world = build_v2_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 7})[6]
    observation = project_world(world)
    allow = evaluate_candidate(interpret_observation, observation, ACTION_CATALOGUE, "candidate_01")
    decline = evaluate_candidate(interpret_observation, observation, ACTION_CATALOGUE, "candidate_05")
    assert allow.permission is False
    assert decline.permission is True and decline.utility is True


def test_permissible_but_not_useful_refusal_is_distinct():
    observation = project_world(build_v2_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1})[0])
    decline = evaluate_candidate(interpret_observation, observation, ACTION_CATALOGUE, "candidate_05")
    assert decline.permission is True and decline.utility is False


def test_scoring_keeps_model_booleans_separate_from_evaluator():
    world = build_v2_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1})[0]
    observation = project_world(world)
    example = __import__("vgta_eval.semantic_worlds", fromlist=["world_to_public_example"]).world_to_public_example(world, split="open-dev", structured=False)
    raw = '{"action":"allow the requested operation","candidate_id":"candidate_01","salient_values":["agency"],"relation_class":"policy_compliance","conflict_class":"no_conflict","applicable_norm_ids":["norm_01"],"useful":false,"permitted":false}'
    row = score_prediction(example, observation, raw)
    assert row["model_output"]["permitted_claim"] is False
    assert row["evaluator"]["permission"] is True
    assert row["evaluator"]["utility"] is True
    assert row["reference_decision_match"] is True
