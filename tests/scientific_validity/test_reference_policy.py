from dataclasses import replace

from vgta_eval.observation_projection import project_world
from vgta_eval.reference_policy import interpret_observation
from vgta_eval.semantic_worlds import build_worlds


def test_oracle_is_template_invariant_and_fact_sensitive():
    worlds = build_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})
    world = worlds[0]
    baseline = interpret_observation(project_world(world))
    assert baseline.candidate_id == "candidate_01"
    assert interpret_observation(project_world(replace(world, template_id="arbitrary-name"))) == baseline
    changed = replace(world, facts=tuple(replace(fact, object="inactive") if fact.subject == "delegation" else fact for fact in world.facts))
    assert interpret_observation(project_world(changed)).candidate_id == "candidate_03"


def test_oracle_has_explicit_unknown_path():
    world = build_worlds(group_counts={"train": 1, "validation": 1, "calibration": 1, "open-dev": 1, "locked-engineering-eval": 1})[0]
    observation = project_world(world)
    observation = replace(observation, facts=tuple(fact for fact in observation.facts if fact.subject != "evidence"))
    decision = interpret_observation(observation)
    assert decision.status == "unknown"
    assert decision.candidate_id == "candidate_04"

