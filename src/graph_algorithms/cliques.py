from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _normalize(graph: Graph[Node]) -> dict[Node, set[Node]]:
    nodes = set(graph)
    for neighbors in graph.values():
        nodes.update(neighbors)
    adjacency = {u: set(graph.get(u, ())) - {u} for u in nodes}
    for u in list(nodes):
        for v in tuple(adjacency[u]):
            adjacency.setdefault(v, set()).add(u)
    return adjacency


def bron_kerbosch_maximal_cliques(
    graph: Graph[Node],
) -> list[frozenset[Node]]:
    """Enumerate maximal cliques using Bron-Kerbosch with pivoting."""
    adjacency = _normalize(graph)
    result: list[frozenset[Node]] = []

    def search(r: set[Node], p: set[Node], x: set[Node]) -> None:
        if not p and not x:
            result.append(frozenset(r))
            return
        union = p | x
        pivot = (
            max(union, key=lambda u: len(p & adjacency[u]))
            if union
            else None
        )
        candidates = p - (adjacency[pivot] if pivot is not None else set())
        for v in list(candidates):
            search(r | {v}, p & adjacency[v], x & adjacency[v])
            p.remove(v)
            x.add(v)

    search(set(), set(adjacency), set())
    return result


def maximum_clique(graph: Graph[Node]) -> frozenset[Node]:
    """Return one maximum clique by maximal-clique enumeration."""
    cliques = bron_kerbosch_maximal_cliques(graph)
    return max(cliques, key=len, default=frozenset())
