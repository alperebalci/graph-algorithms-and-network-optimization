from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _nodes(graph: Graph[Node]) -> list[Node]:
    nodes = list(graph)
    seen = set(nodes)
    for nbrs in graph.values():
        for v in nbrs:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    return nodes


def greedy_coloring(graph: Graph[Node], order: Sequence[Node] | None = None) -> dict[Node, int]:
    """Greedy vertex coloring. Result quality depends on vertex order."""
    nodes = list(order) if order is not None else _nodes(graph)
    color: dict[Node, int] = {}
    for u in nodes:
        forbidden = {color[v] for v in graph.get(u, ()) if v in color}
        c = 0
        while c in forbidden:
            c += 1
        color[u] = c
    return color


def welsh_powell_coloring(graph: Graph[Node]) -> dict[Node, int]:
    """Greedy coloring with non-increasing degree ordering (Welsh-Powell heuristic)."""
    nodes = _nodes(graph)
    degree = {u: len(set(graph.get(u, ()))) for u in nodes}
    order = sorted(nodes, key=lambda u: degree[u], reverse=True)
    return greedy_coloring(graph, order)


def is_valid_coloring(graph: Graph[Node], coloring: Mapping[Node, int]) -> bool:
    for u in _nodes(graph):
        if u not in coloring:
            return False
        for v in graph.get(u, ()):
            if u != v and coloring.get(v) == coloring[u]:
                return False
    return True


def k_color_backtracking(graph: Graph[Node], k: int) -> dict[Node, int] | None:
    """Exact k-colorability search using a DSATUR-style branching order."""
    if k < 0:
        raise ValueError("k must be non-negative")
    nodes = _nodes(graph)
    if not nodes:
        return {}
    if k == 0:
        return None
    neighbors = {u: set(graph.get(u, ())) - {u} for u in nodes}
    color: dict[Node, int] = {}

    def choose_vertex() -> Node:
        uncolored = [u for u in nodes if u not in color]
        return max(
            uncolored,
            key=lambda u: (
                len({color[v] for v in neighbors[u] if v in color}),
                len(neighbors[u]),
            ),
        )

    def search() -> bool:
        if len(color) == len(nodes):
            return True
        u = choose_vertex()
        forbidden = {color[v] for v in neighbors[u] if v in color}
        for c in range(k):
            if c in forbidden:
                continue
            color[u] = c
            if search():
                return True
            del color[u]
        return False

    return color.copy() if search() else None


def exact_chromatic_number(graph: Graph[Node]) -> tuple[int, dict[Node, int]]:
    """Exact chromatic number by repeated k-colorability; intended for small graphs."""
    nodes = _nodes(graph)
    if not nodes:
        return 0, {}
    upper_coloring = welsh_powell_coloring(graph)
    upper = 1 + max(upper_coloring.values())
    for k in range(1, upper + 1):
        coloring = k_color_backtracking(graph, k)
        if coloring is not None:
            return k, coloring
    raise AssertionError("unreachable")


def brooks_bound(graph: Graph[Node]) -> int:
    """Return the chromatic upper bound implied by Brooks' theorem for a connected simple graph.

    Brooks' theorem is a theorem, not a coloring algorithm: chi(G) <= Delta except for
    complete graphs and odd cycles, where chi(G)=Delta+1.
    """
    nodes = _nodes(graph)
    if not nodes:
        return 0
    neighbors = {u: set(graph.get(u, ())) - {u} for u in nodes}
    delta = max(len(neighbors[u]) for u in nodes)
    n = len(nodes)
    complete = all(len(neighbors[u]) == n - 1 for u in nodes)
    odd_cycle = n >= 3 and n % 2 == 1 and all(len(neighbors[u]) == 2 for u in nodes)
    return delta + 1 if complete or odd_cycle else max(1, delta)
