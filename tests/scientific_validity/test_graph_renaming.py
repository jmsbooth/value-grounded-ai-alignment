from dataclasses import replace

from vgta_eval.graph_identity import TypedGraph, graph_content_hash, merge_graph_chunks, rename_nodes, reorder_edges, split_graph_chunks, typed_relation_fingerprint, unlabeled_structure_fingerprint
from vgta_eval.semantic_worlds import TypedEdge, TypedNode


def _graph():
    return TypedGraph(
        (TypedNode("a", "actor"), TypedNode("b", "actor"), TypedNode("r", "record")),
        (TypedEdge("a", "requests", "r"), TypedEdge("r", "owned_by", "b")),
    )


def test_node_renaming_and_edge_order_do_not_change_graph_identity():
    graph = _graph()
    renamed = rename_nodes(graph, ("owner-7", "requester-9", "record-2"))
    assert unlabeled_structure_fingerprint(graph) == unlabeled_structure_fingerprint(renamed)
    assert typed_relation_fingerprint(graph) == typed_relation_fingerprint(renamed)
    assert graph_content_hash(graph) == graph_content_hash(reorder_edges(graph))


def test_topology_and_relation_changes_are_detectable():
    graph = _graph()
    branch = TypedGraph(graph.nodes, (TypedEdge("a", "requests", "r"), TypedEdge("a", "owned_by", "b")))
    relabeled = TypedGraph(graph.nodes, (TypedEdge("a", "targets", "r"), TypedEdge("r", "owned_by", "b")))
    assert unlabeled_structure_fingerprint(graph) != unlabeled_structure_fingerprint(branch)
    assert unlabeled_structure_fingerprint(graph) == unlabeled_structure_fingerprint(relabeled)
    assert typed_relation_fingerprint(graph) != typed_relation_fingerprint(relabeled)


def test_prefix_suffix_transport_preserves_full_identity():
    graph = _graph()
    chunks = split_graph_chunks(graph, 1)
    assert graph_content_hash(merge_graph_chunks(chunks)) == graph_content_hash(graph)
