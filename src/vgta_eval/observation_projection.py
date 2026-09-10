"""Model-visible projection of a semantic world.

The projection is intentionally boring: it copies only observed facts and the
public policy.  Private identifiers, template names, and reference labels do
not cross this boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .semantic_worlds import PolicyRule, PublicFact, TypedEdge, TypedNode, World, public_world_facts


@dataclass(frozen=True)
class ProjectedObservation:
    domain: str
    policy_id: str
    policy_text: str
    question: str
    facts: tuple[PublicFact, ...]
    rules: tuple[PolicyRule, ...]
    nodes: tuple[TypedNode, ...]
    edges: tuple[TypedEdge, ...]


def project_world(world: World) -> ProjectedObservation:
    """Create the public observation used by both the oracle and the model."""

    return ProjectedObservation(
        domain=world.domain,
        policy_id=world.policy_id,
        policy_text=world.policy_text,
        question=world.question,
        facts=public_world_facts(world),
        rules=world.rules,
        nodes=world.nodes,
        edges=world.edges,
    )


def observation_from_mapping(value: Mapping[str, Any]) -> ProjectedObservation:
    """Parse a minimal observation mapping for oracle/metamorphic tests."""

    facts = tuple(
        PublicFact(
            fact_id=f"public-fact-{index:03d}",
            subject=str(item["subject"]),
            predicate=str(item["predicate"]),
            object=str(item["object"]),
            source=str(item.get("source", "policy-record")),
        )
        for index, item in enumerate(value.get("facts", ()))
    )
    rules = tuple(
        PolicyRule(
            rule_id=str(item["rule_id"]),
            text=str(item["text"]),
            required_facts=tuple(str(value) for value in item.get("required_facts", ())),
        )
        for item in value.get("rules", ())
    )
    nodes = tuple(TypedNode(f"node-{index:03d}", str(item["type"])) for index, item in enumerate(value.get("nodes", ())))
    edges = tuple(
        TypedEdge(
            source=str(item.get("source", "")),
            relation=str(item.get("relation", "")),
            target=str(item.get("target", "")),
        )
        for item in value.get("edges", ())
    )
    return ProjectedObservation(
        domain=str(value["domain"]),
        policy_id=str(value.get("policy_id", "")),
        policy_text=str(value.get("policy_text", "")),
        question=str(value.get("question", "")),
        facts=facts,
        rules=rules,
        nodes=nodes,
        edges=edges,
    )
