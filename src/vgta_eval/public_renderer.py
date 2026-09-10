"""Stable natural-language and typed renderings for semantic observations."""

from __future__ import annotations

import json
from typing import Any

from .observation_projection import ProjectedObservation
from .semantic_worlds import ACTION_CATALOGUE


def render_natural(observation: ProjectedObservation) -> str:
    fact_lines = "; ".join(
        f"{fact.subject} {fact.predicate}={fact.object}" for fact in observation.facts
    )
    return "\n".join((
        "Task: apply the public operational policy to the observed world.",
        f"Policy: {' '.join(observation.policy_text.split())}",
        f"Observed facts: {fact_lines}.",
        f"Question: {observation.question}",
        "Choose one candidate and return the requested structured response fields.",
        "Candidate actions: " + "; ".join(f"{cid}: {description}" for cid, description in ACTION_CATALOGUE),
        "Public normative rule IDs: " + ", ".join(rule.rule_id for rule in observation.rules) + ".",
        "Generic values: agency, privacy, accountability, and scope are policy concepts; infer their relevance from the observed facts.",
    ))


def render_structured(observation: ProjectedObservation) -> str:
    def node_type(node_id: str) -> str:
        for node in observation.nodes:
            if node.node_id == node_id:
                return node.node_type
        return "unknown"

    value: dict[str, Any] = {
        "representation": "typed-public-observation-v1",
        "domain": observation.domain,
        "policy_id": observation.policy_id,
        "policy": observation.policy_text,
        "rules": [
            {"rule_id": rule.rule_id, "text": rule.text, "required_facts": list(rule.required_facts)}
            for rule in observation.rules
        ],
        "facts": [
            {"subject": fact.subject, "predicate": fact.predicate, "object": fact.object, "source": fact.source}
            for fact in observation.facts
        ],
        "graph": {
            "nodes": [{"type": node.node_type} for node in observation.nodes],
            "edges": [
                {"relation": edge.relation, "source_type": node_type(edge.source), "target_type": node_type(edge.target)}
                for edge in observation.edges
            ],
        },
        "question": observation.question,
        "candidate_actions": [{"id": cid, "description": description} for cid, description in ACTION_CATALOGUE],
    }
    return json.dumps(value, sort_keys=True)
