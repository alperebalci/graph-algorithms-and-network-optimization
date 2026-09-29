from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import TypeVar

from .matching import hopcroft_karp

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]
WeightedGraph = Mapping[Node, Mapping[Node, float]]


def vertex_cover_2approx(graph: Graph[Node]) -> set[Node]:
    """Standard maximal-matching 2-approximation for minimum vertex cover."""
    nodes = list(graph)
    seen_nodes = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen_nodes:
                seen_nodes.add(v)
                nodes.append(v)

    covered: set[Node] = set()
    processed: set[frozenset[Node]] = set()
    for u in nodes:
        for v in graph.get(u, ()):
            if u == v:
                covered.add(u)
                continue
            key = frozenset((u, v))
            if key in processed:
                continue
            processed.add(key)
            if u not in covered and v not in covered:
                covered.add(u)
                covered.add(v)
    return covered


def konig_minimum_vertex_cover(
    graph: Mapping[Node, Iterable[Node]],
    left: Iterable[Node],
) -> set[Node]:
    """Exact bipartite minimum vertex cover via Konig plus Hopcroft-Karp."""
    left_nodes = list(dict.fromkeys(left))
    left_set = set(left_nodes)
    adjacency = {u: list(graph.get(u, ())) for u in left_nodes}
    for u in left_nodes:
        for v in adjacency[u]:
            if v in left_set:
                raise ValueError("left and right bipartition sets must be disjoint")

    matching = hopcroft_karp(adjacency, left_nodes)
    reverse = {v: u for u, v in matching.items()}

    z_left: set[Node] = {u for u in left_nodes if u not in matching}
    z_right: set[Node] = set()
    queue: deque[tuple[bool, Node]] = deque((True, u) for u in z_left)

    while queue:
        on_left, u = queue.popleft()
        if on_left:
            for v in adjacency.get(u, ()):
                if matching.get(u) == v:
                    continue
                if v not in z_right:
                    z_right.add(v)
                    queue.append((False, v))
        else:
            mate = reverse.get(u)
            if mate is not None and mate not in z_left:
                z_left.add(mate)
                queue.append((True, mate))

    return (left_set - z_left) | z_right


@dataclass(frozen=True)
class MaxCutResult:
    value: float
    left: frozenset[Hashable]
    right: frozenset[Hashable]


def max_cut_local_search(
    graph: WeightedGraph[Node],
    *,
    max_passes: int = 10000,
) -> MaxCutResult:
    """Deterministic 1-flip local search with the standard 1/2 Max-Cut guarantee."""
    if max_passes < 1:
        raise ValueError("max_passes must be positive")

    nodes = list(graph)
    seen = set(nodes)
    edges: dict[frozenset[Node], tuple[Node, Node, float]] = {}

    for u, neighbors in graph.items():
        for v, raw_weight in neighbors.items():
            weight = float(raw_weight)
            if weight < 0:
                raise ValueError("Max-Cut guarantee requires non-negative weights")
            if u == v:
                continue
            if v not in seen:
                seen.add(v)
                nodes.append(v)
            key = frozenset((u, v))
            if key in edges:
                _, _, old = edges[key]
                if abs(old - weight) > 1e-9:
                    raise ValueError(
                        "symmetric entries of an undirected edge must agree"
                    )
            else:
                edges[key] = (u, v, weight)

    adjacency: dict[Node, list[tuple[Node, float]]] = {u: [] for u in nodes}
    for u, v, weight in edges.values():
        adjacency[u].append((v, weight))
        adjacency[v].append((u, weight))

    side = {u: 0 for u in nodes}

    for _ in range(max_passes):
        changed = False
        for u in nodes:
            same = 0.0
            across = 0.0
            for v, weight in adjacency[u]:
                if side[v] == side[u]:
                    same += weight
                else:
                    across += weight
            if same - across > 1e-12:
                side[u] = 1 - side[u]
                changed = True
        if not changed:
            break

    left = frozenset(u for u in nodes if side[u] == 0)
    right = frozenset(u for u in nodes if side[u] == 1)
    value = sum(
        weight
        for u, v, weight in edges.values()
        if side[u] != side[v]
    )
    return MaxCutResult(value=value, left=left, right=right)
