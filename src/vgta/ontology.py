"""Minimal Turtle fixture loader used by the reproducibility tests.

This parser deliberately supports only the small, line-oriented subset used
by the repository examples.  It is not intended to replace an RDF/OWL
implementation for research or production workloads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str


@dataclass(frozen=True)
class Ontology:
    prefixes: dict[str, str]
    triples: tuple[Triple, ...]

    @classmethod
    def from_turtle(cls, path: str | Path) -> "Ontology":
        return parse_turtle(Path(path).read_text(encoding="utf-8"))

    def contains(self, subject: str, predicate: str, object: str) -> bool:
        return Triple(subject, predicate, object) in self.triples

    def objects_for(self, subject: str, predicate: str) -> tuple[str, ...]:
        return tuple(
            triple.object
            for triple in self.triples
            if triple.subject == subject and triple.predicate == predicate
        )

    def subjects_for(self, predicate: str, object: str) -> tuple[str, ...]:
        return tuple(
            triple.subject
            for triple in self.triples
            if triple.predicate == predicate and triple.object == object
        )


_PREFIX_RE = re.compile(r"@prefix\s+([\w-]+):\s*<([^>]+)>\s*\.")
_TRIPLE_RE = re.compile(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s*\.$")


def _expand(term: str, prefixes: dict[str, str]) -> str:
    if term.startswith("<") and term.endswith(">"):
        return term[1:-1]
    if ":" in term:
        prefix, local = term.split(":", 1)
        if prefix in prefixes:
            return prefixes[prefix] + local
    return term


def parse_turtle(text: str) -> Ontology:
    prefixes: dict[str, str] = {}
    statements: list[str] = []
    buffer = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        prefix_match = _PREFIX_RE.fullmatch(line)
        if prefix_match:
            prefixes[prefix_match.group(1)] = prefix_match.group(2)
            continue
        line = line.split("#", 1)[0].strip()
        if line:
            buffer += (" " if buffer else "") + line
            while "." in buffer:
                statement, buffer = buffer.split(".", 1)
                statements.append(statement.strip() + ".")

    triples: list[Triple] = []
    for statement in statements:
        match = _TRIPLE_RE.fullmatch(statement)
        if not match:
            raise ValueError(f"Unsupported Turtle statement: {statement}")
        triples.append(
            Triple(
                _expand(match.group(1), prefixes),
                _expand(match.group(2), prefixes),
                _expand(match.group(3), prefixes),
            )
        )
    return Ontology(prefixes=prefixes, triples=tuple(triples))


def triples_as_rows(ontology: Ontology) -> Iterable[tuple[str, str, str]]:
    """Return triples in stable order for simple fixtures and reports."""

    return ((item.subject, item.predicate, item.object) for item in ontology.triples)
