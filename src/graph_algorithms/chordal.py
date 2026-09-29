from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _normalize(graph: Graph[Node]) -> dict[Node, set[Node]]:
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    adjacency = {u: set(graph.get(u, ())) - {u} for u in nodes}
    for u in nodes:
        for v in tuple(adjacency[u]):
            adjacency.setdefault(v, set()).add(u)
    return adjacency


def maximum_cardinality_search(graph: Graph[Node]) -> list[Node]:
    """Maximum Cardinality Search ordering for an undirected graph."""
    adjacency = _normalize(graph)
    weight = {u: 0 for u in adjacency}
    unnumbered = set(adjacency)
    selected: list[Node] = []

    while unnumbered:
        v = max(unnumbered, key=lambda u: weight[u])
        unnumbered.remove(v)
        selected.append(v)
        for u in adjacency[v] & unnumbered:
            weight[u] += 1
    return selected


def chordal_perfect_elimination_order(
    graph: Graph[Node],
) -> list[Node] | None:
    """Return a perfect elimination ordering iff the graph is chordal."""
    adjacency = _normalize(graph)
    peo = list(reversed(maximum_cardinality_search(adjacency)))
    position = {u: i for i, u in enumerate(peo)}

    for v in peo:
        later = [u for u in adjacency[v] if position[u] > position[v]]
        if len(later) <= 1:
            continue
        parent = min(later, key=lambda u: position[u])
        for u in later:
            if u != parent and parent not in adjacency[u]:
                return None
    return peo


def is_chordal(graph: Graph[Node]) -> bool:
    return chordal_perfect_elimination_order(graph) is not None
