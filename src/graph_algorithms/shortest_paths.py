from __future__ import annotations

import heapq
import math
from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from typing import TypeVar

from .exceptions import NegativeCycleError

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]
Edge = tuple[Node, Node, float]


def reconstruct_path(prev: Mapping[Node, Node | None], source: Node, target: Node) -> list[Node] | None:
    if target not in prev:
        return None
    path: list[Node] = []
    cur: Node | None = target
    while cur is not None:
        path.append(cur)
        if cur == source:
            return list(reversed(path))
        cur = prev.get(cur)
    return None


def dijkstra(graph: WeightedGraph[Node], source: Node) -> tuple[dict[Node, float], dict[Node, Node | None]]:
    """Single-source shortest paths for non-negative edge weights. O((V+E) log V)."""
    dist: dict[Node, float] = {source: 0.0}
    prev: dict[Node, Node | None] = {source: None}
    heap: list[tuple[float, int, Node]] = [(0.0, 0, source)]
    serial = 1
    while heap:
        d, _, u = heapq.heappop(heap)
        if d != dist.get(u):
            continue
        for v, w in graph.get(u, ()):
            if w < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, serial, v))
                serial += 1
    return dist, prev


def bellman_ford(
    vertices: Iterable[Node], edges: Sequence[Edge[Node]], source: Node
) -> tuple[dict[Node, float], dict[Node, Node | None]]:
    """Single-source shortest paths with negative edges; raises on reachable negative cycles."""
    nodes = list(dict.fromkeys(vertices))
    if source not in nodes:
        nodes.append(source)
    dist = {v: math.inf for v in nodes}
    prev: dict[Node, Node | None] = {source: None}
    dist[source] = 0.0

    for _ in range(max(0, len(nodes) - 1)):
        changed = False
        for u, v, w in edges:
            if dist.get(u, math.inf) == math.inf:
                continue
            nd = dist[u] + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                changed = True
        if not changed:
            break

    for u, v, w in edges:
        if dist.get(u, math.inf) != math.inf and dist[u] + w < dist.get(v, math.inf):
            raise NegativeCycleError("reachable negative-weight cycle detected")
    return dist, prev


def floyd_warshall(
    vertices: Iterable[Node], edges: Sequence[Edge[Node]]
) -> dict[Node, dict[Node, float]]:
    """All-pairs shortest-path distances. O(V^3), supports negative edges but not negative cycles."""
    nodes = list(dict.fromkeys(vertices))
    dist = {u: {v: math.inf for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 0.0
    for u, v, w in edges:
        if u not in dist:
            dist[u] = {x: math.inf for x in nodes}
        dist[u][v] = min(dist[u].get(v, math.inf), w)
    for k in nodes:
        for i in nodes:
            dik = dist[i][k]
            if dik == math.inf:
                continue
            for j in nodes:
                nd = dik + dist[k][j]
                if nd < dist[i][j]:
                    dist[i][j] = nd
    if any(dist[v][v] < 0 for v in nodes):
        raise NegativeCycleError("negative-weight cycle detected")
    return dist


def johnson(vertices: Iterable[Node], edges: Sequence[Edge[Node]]) -> dict[Node, dict[Node, float]]:
    """All-pairs shortest paths for sparse directed graphs, allowing negative edges."""
    nodes = list(dict.fromkeys(vertices))
    marker = object()
    augmented_vertices: list[Node | object] = [*nodes, marker]
    augmented_edges: list[tuple[Node | object, Node | object, float]] = [
        *edges, *((marker, v, 0.0) for v in nodes)
    ]
    h, _ = bellman_ford(augmented_vertices, augmented_edges, marker)

    reweighted: dict[Node, list[tuple[Node, float]]] = {u: [] for u in nodes}
    for u, v, w in edges:
        rw = w + h[u] - h[v]
        if rw < -1e-12:
            raise AssertionError("Johnson reweighting produced a negative edge")
        reweighted.setdefault(u, []).append((v, max(0.0, rw)))

    result: dict[Node, dict[Node, float]] = {}
    for src in nodes:
        d, _ = dijkstra(reweighted, src)
        result[src] = {
            dst: (math.inf if dst not in d else d[dst] - h[src] + h[dst]) for dst in nodes
        }
    return result


def astar(
    graph: WeightedGraph[Node],
    start: Node,
    goal: Node,
    heuristic: Callable[[Node, Node], float],
) -> tuple[float, list[Node]] | None:
    """A* shortest path. Optimal when heuristic is admissible and edge weights are non-negative."""
    g_score: dict[Node, float] = {start: 0.0}
    prev: dict[Node, Node | None] = {start: None}
    heap: list[tuple[float, int, Node]] = [(heuristic(start, goal), 0, start)]
    serial = 1
    closed: set[Node] = set()

    while heap:
        _, _, u = heapq.heappop(heap)
        if u in closed:
            continue
        if u == goal:
            path = reconstruct_path(prev, start, goal)
            assert path is not None
            return g_score[goal], path
        closed.add(u)
        for v, w in graph.get(u, ()):
            if w < 0:
                raise ValueError("A* requires non-negative edge weights")
            tentative = g_score[u] + w
            if tentative < g_score.get(v, math.inf):
                g_score[v] = tentative
                prev[v] = u
                heapq.heappush(heap, (tentative + heuristic(v, goal), serial, v))
                serial += 1
                closed.discard(v)
    return None
