from __future__ import annotations

import heapq
import math
from collections.abc import Hashable, Iterable, Sequence
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Edge = tuple[Node, Node, float]


def greedy_spanner(
    vertices: Iterable[Node],
    edges: Sequence[Edge[Node]],
    stretch: float,
) -> list[Edge[Node]]:
    """Greedy weighted t-spanner for an undirected graph.

    Edges are considered in nondecreasing weight order and added only when the
    current spanner distance exceeds t times the edge weight.
    """
    if stretch < 1.0:
        raise ValueError("stretch must be at least 1")
    nodes = list(dict.fromkeys(vertices))
    adjacency: dict[Node, list[tuple[Node, float]]] = {
        u: [] for u in nodes
    }
    result: list[Edge[Node]] = []

    def distance(source: Node, target: Node, limit: float) -> float:
        if source == target:
            return 0.0
        dist = {source: 0.0}
        heap: list[tuple[float, int, Node]] = [(0.0, 0, source)]
        serial = 1
        while heap:
            d, _, u = heapq.heappop(heap)
            if d != dist.get(u):
                continue
            if d > limit:
                return math.inf
            if u == target:
                return d
            for v, weight in adjacency.get(u, ()):
                nd = d + weight
                if nd < dist.get(v, math.inf) and nd <= limit:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, serial, v))
                    serial += 1
        return math.inf

    for u, v, raw_weight in sorted(edges, key=lambda edge: edge[2]):
        weight = float(raw_weight)
        if weight < 0:
            raise ValueError("greedy spanner requires non-negative weights")
        threshold = stretch * weight
        if distance(u, v, threshold) > threshold + 1e-12:
            adjacency.setdefault(u, []).append((v, weight))
            adjacency.setdefault(v, []).append((u, weight))
            result.append((u, v, weight))
    return result
