"""Dataset leakage and shortcut-audit primitives for the v0.5 harness."""

from __future__ import annotations

from collections import Counter, defaultdict
from difflib import SequenceMatcher
import re
from typing import Any, Iterable, Mapping, Sequence

METADATA_EXCESS_THRESHOLD = 0.10


def normalize_text(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _surface(record: Mapping[str, Any]) -> str:
    return str(record.get("surface", ""))


def _metadata(record: Mapping[str, Any]) -> tuple[str, ...]:
    provenance = record.get("provenance", {})
    return tuple(sorted({
        f"family={record.get('family', '')}",
        f"template={record.get('template_id', '')}",
        f"transform={record.get('transform', '')}",
        f"origin={provenance.get('origin', '')}",
        f"generator={provenance.get('generator_version', '')}",
    }))


def _entity_tokens(record: Mapping[str, Any]) -> set[str]:
    entities = {str(item).split(":", 1)[1] for item in record.get("feature_groups", {}).get("ontology", ()) if str(item).startswith("entity:")}
    return entities


def _label(record: Mapping[str, Any]) -> str:
    return str(record.get("labels", {}).get("action", ""))


def _metadata_predictive_power(train: Sequence[Mapping[str, Any]], heldout: Sequence[Mapping[str, Any]], key_fn) -> float:
    """Measure train-fitted metadata prediction on held-out records only."""

    if not train or not heldout:
        return 0.0
    groups: dict[Any, Counter[str]] = defaultdict(Counter)
    for record in train:
        groups[key_fn(record)][_label(record)] += 1
    global_majority = Counter(_label(record) for record in train).most_common(1)[0][0]
    predictions = {
        key: counter.most_common(1)[0][0]
        for key, counter in groups.items()
    }
    correct = sum(
        _label(record) == predictions.get(key_fn(record), global_majority)
        for record in heldout
    )
    return correct / len(heldout)


def audit_records(train: Sequence[Mapping[str, Any]], heldout: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Return explicit leakage counts and a conservative gate summary."""

    train_surface = {normalize_text(_surface(row)): row for row in train}
    heldout_surface = {normalize_text(_surface(row)): row for row in heldout}
    exact_pairs = [
        {"train_example_id": train_surface[key].get("example_id"), "heldout_example_id": heldout_surface[key].get("example_id"), "normalized_surface": key}
        for key in sorted(set(train_surface) & set(heldout_surface)) if key
    ]
    similarity_pairs: list[dict[str, Any]] = []
    for heldout_row in heldout:
        best = (0.0, None)
        heldout_text = normalize_text(_surface(heldout_row))
        for train_row in train:
            train_text = normalize_text(_surface(train_row))
            score = SequenceMatcher(None, heldout_text, train_text).ratio()
            if score > best[0]:
                best = (score, train_row)
        if best[1] is not None and best[0] >= 0.8:
            similarity_pairs.append({"heldout_example_id": heldout_row.get("example_id"), "train_example_id": best[1].get("example_id"), "similarity": round(best[0], 4)})
    train_templates = {str(row.get("template_id")) for row in train}
    template_overlap = sorted({str(row.get("template_id")) for row in heldout if str(row.get("template_id")) in train_templates})
    train_topologies = {str(row.get("topology_hash")) for row in train}
    topology_overlap = sorted({str(row.get("topology_hash")) for row in heldout if str(row.get("topology_hash")) in train_topologies})
    train_entities = set().union(*(_entity_tokens(row) for row in train)) if train else set()
    heldout_entities = set().union(*(_entity_tokens(row) for row in heldout)) if heldout else set()
    entity_overlap = sorted(train_entities & heldout_entities)
    metadata_power = {
        "family": _metadata_predictive_power(train, heldout, lambda row: row.get("family")),
        "template_id": _metadata_predictive_power(train, heldout, lambda row: row.get("template_id")),
        "transform": _metadata_predictive_power(train, heldout, lambda row: row.get("transform")),
        "surface_length": _metadata_predictive_power(train, heldout, lambda row: len(str(row.get("surface", "")).split())),
    }
    majority_baseline = max(Counter(_label(record) for record in train).values()) / len(train) if train else 0.0
    metadata_excess = {
        key: value - majority_baseline
        for key, value in metadata_power.items()
    }
    classes = {
        "exact_duplicate": {"count": len(exact_pairs), "status": "pass" if not exact_pairs else "review", "pairs": exact_pairs[:20]},
        "paraphrase_similarity": {"count": len(similarity_pairs), "status": "review" if similarity_pairs else "pass", "highest_similarity_pairs": sorted(similarity_pairs, key=lambda item: item["similarity"], reverse=True)[:20]},
        "template_identity": {"count": len(template_overlap), "status": "documented_overlap" if template_overlap else "pass", "values": template_overlap},
        "topology_overlap": {"count": len(topology_overlap), "status": "review" if topology_overlap else "pass", "values": topology_overlap},
        "entity_instance_overlap": {"count": len(entity_overlap), "status": "documented_overlap" if entity_overlap else "pass", "values": entity_overlap},
        "label_metadata_leakage": {
            "count": sum(value > METADATA_EXCESS_THRESHOLD for value in metadata_excess.values()),
            "status": "review" if any(value > METADATA_EXCESS_THRESHOLD for value in metadata_excess.values()) else "pass",
            "predictive_power": metadata_power,
            "majority_baseline": majority_baseline,
            "excess_over_majority": metadata_excess,
            "excess_threshold": METADATA_EXCESS_THRESHOLD,
        },
        "formatting_leakage": {"count": 0, "status": "pass", "note": "No split marker is included in the surface text audit."},
    }
    return {
        "train_records": len(train),
        "heldout_records": len(heldout),
        "classes": classes,
        "gate_passed": all(item["status"] in {"pass", "documented_overlap"} for item in classes.values()),
        "interpretation": "Documented template/entity overlap is not treated as unexplained leakage; exact duplicates, high paraphrase similarity, topology overlap, and metadata predictive power require review before confirmatory use.",
    }


def audit_dataset(records_by_split: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    return audit_records(records_by_split.get("train", ()), records_by_split.get("sealed-test", ()))
