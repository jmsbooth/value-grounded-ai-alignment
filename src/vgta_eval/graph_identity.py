"""Canonical identity and metamorphic operations for typed policy graphs."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import itertools
import json
from typing import Iterable, Sequence

from .semantic_worlds import TypedEdge, TypedNode


@dataclass(frozen=True)
class TypedGraph:
    nodes: tuple[TypedNode, ...]
    edges: tuple[TypedEdge, ...]


@dataclass(frozen=True)
class GraphChunks:
    prefix: TypedGraph
    suffix: TypedGraph
    cross_edges: tuple[TypedEdge, ...]
    full_identity: str


def _graph(graph_or_nodes: TypedGraph | Sequence[TypedNode], edges: Sequence[TypedEdge] | None = None) -> TypedGraph:
    if isinstance(graph_or_nodes, TypedGraph):
        return graph_or_nodes
    return TypedGraph(tuple(graph_or_nodes), tuple(edges or ()))


def graph_content_hash(graph_or_nodes: TypedGraph | Sequence[TypedNode], edges: Sequence[TypedEdge] | None = None) -> str:
    graph = _graph(graph_or_nodes, edges)
    payload = {
        "nodes": sorted((node.node_id, node.node_type) for node in graph.nodes),
        "edges": sorted((edge.source, edge.relation, edge.target) for edge in graph.edges),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _canonical_fingerprint(graph: TypedGraph, *, preserve_relations: bool) -> str:
    if len(graph.nodes) > 9:
        raise ValueError("canonical graph fingerprint is bounded to nine nodes")
    node_by_id = {node.node_id: node for node in graph.nodes}
    if len(node_by_id) != len(graph.nodes) or any(edge.source not in node_by_id or edge.target not in node_by_id for edge in graph.edges):
        raise ValueError("graph contains duplicate or unknown node identifiers")
    by_type: dict[str, list[str]] = {}
    for node in graph.nodes:
        by_type.setdefault(node.node_type, []).append(node.node_id)
    type_order = sorted(by_type)
    permutation_groups = [list(itertools.permutations(by_type[node_type])) for node_type in type_order]
    forms: list[str] = []
    for choices in itertools.product(*permutation_groups):
        mapping: dict[str, str] = {}
        cursor = 0
        ordered_nodes: list[tuple[str, str]] = []
        for node_type, chosen in zip(type_order, choices):
            for new_index, old_id in enumerate(chosen):
                mapping[old_id] = f"{node_type}#{new_index}"
                ordered_nodes.append((f"{node_type}#{new_index}", node_type))
            cursor += len(chosen)
        del cursor
        mapped_edges = []
        for edge in graph.edges:
            mapped = [mapping[edge.source], mapping[edge.target]]
            mapped_edges.append((*mapped, edge.relation) if preserve_relations else tuple(mapped))
        forms.append(json.dumps({"nodes": sorted(ordered_nodes), "edges": sorted(mapped_edges)}, separators=(",", ":")))
    return hashlib.sha256(min(forms).encode()).hexdigest()


def unlabeled_structure_fingerprint(graph_or_nodes: TypedGraph | Sequence[TypedNode], edges: Sequence[TypedEdge] | None = None) -> str:
    """Fingerprint directed topology while ignoring node IDs and relation labels."""

    return _canonical_fingerprint(_graph(graph_or_nodes, edges), preserve_relations=False)


def typed_relation_fingerprint(graph_or_nodes: TypedGraph | Sequence[TypedNode], edges: Sequence[TypedEdge] | None = None) -> str:
    """Fingerprint topology plus typed relation labels, ignoring node IDs."""

    return _canonical_fingerprint(_graph(graph_or_nodes, edges), preserve_relations=True)


def rename_nodes(graph: TypedGraph, names: Iterable[str]) -> TypedGraph:
    names = tuple(names)
    if len(names) != len(graph.nodes) or len(set(names)) != len(names):
        raise ValueError("replacement names must be unique and cover every node")
    mapping = {node.node_id: name for node, name in zip(graph.nodes, names)}
    return TypedGraph(
        nodes=tuple(TypedNode(mapping[node.node_id], node.node_type) for node in graph.nodes),
        edges=tuple(TypedEdge(mapping[edge.source], edge.relation, mapping[edge.target]) for edge in graph.edges),
    )


def reorder_edges(graph: TypedGraph) -> TypedGraph:
    return TypedGraph(graph.nodes, tuple(reversed(graph.edges)))


def split_prefix_graph(graph: TypedGraph, prefix_size: int) -> tuple[TypedGraph, TypedGraph]:
    """Split serialized node/edge prefixes without changing the full graph."""

    if not 0 < prefix_size < len(graph.nodes):
        raise ValueError("prefix_size must leave nodes on both sides")
    left_nodes = graph.nodes[:prefix_size]
    right_nodes = graph.nodes[prefix_size:]
    left_ids = {node.node_id for node in left_nodes}
    right_ids = {node.node_id for node in right_nodes}
    left_edges = tuple(edge for edge in graph.edges if edge.source in left_ids and edge.target in left_ids)
    right_edges = tuple(edge for edge in graph.edges if edge.source in right_ids and edge.target in right_ids)
    return TypedGraph(left_nodes, left_edges), TypedGraph(right_nodes, right_edges)


def split_graph_chunks(graph: TypedGraph, prefix_size: int) -> GraphChunks:
    """Split a graph for transport while retaining cross-boundary edges."""

    if not 0 < prefix_size < len(graph.nodes):
        raise ValueError("prefix_size must leave nodes on both sides")
    left_nodes = graph.nodes[:prefix_size]
    right_nodes = graph.nodes[prefix_size:]
    left_ids = {node.node_id for node in left_nodes}
    right_ids = {node.node_id for node in right_nodes}
    left_edges = tuple(edge for edge in graph.edges if edge.source in left_ids and edge.target in left_ids)
    right_edges = tuple(edge for edge in graph.edges if edge.source in right_ids and edge.target in right_ids)
    cross_edges = tuple(edge for edge in graph.edges if (edge.source in left_ids) != (edge.target in left_ids))
    return GraphChunks(TypedGraph(left_nodes, left_edges), TypedGraph(right_nodes, right_edges), cross_edges, graph_content_hash(graph))


def merge_graph_chunks(chunks: GraphChunks) -> TypedGraph:
    graph = TypedGraph(chunks.prefix.nodes + chunks.suffix.nodes, chunks.prefix.edges + chunks.suffix.edges + chunks.cross_edges)
    if graph_content_hash(graph) != chunks.full_identity:
        raise ValueError("graph chunks failed identity check")
    return graph


def exact_graph_equivalent(left: TypedGraph, right: TypedGraph) -> bool:
    return typed_relation_fingerprint(left) == typed_relation_fingerprint(right)
