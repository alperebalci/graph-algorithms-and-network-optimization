from __future__ import annotations

import heapq
import math
from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

from .cycles_and_dag import topological_sort_kahn

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


def _all_nodes(graph: WeightedGraph[Node]) -> list[Node]:
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v, _ in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    return nodes


def zero_one_bfs(
    graph: WeightedGraph[Node], source: Node
) -> tuple[dict[Node, float], dict[Node, Node | None]]:
    """Shortest paths for edge weights in {0,1}. O(V+E)."""
    nodes = _all_nodes(graph)
    if source not in nodes:
        nodes.append(source)
    dist = {u: math.inf for u in nodes}
    prev: dict[Node, Node | None] = {source: None}
    dist[source] = 0.0
    queue: deque[Node] = deque([source])

    while queue:
        u = queue.popleft()
        for v, raw_w in graph.get(u, ()):
            if raw_w not in (0, 1, 0.0, 1.0):
                raise ValueError("0-1 BFS requires every edge weight to be 0 or 1")
            w = float(raw_w)
            nd = dist[u] + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                if w == 0:
                    queue.appendleft(v)
                else:
                    queue.append(v)
    return dist, prev


def dial_shortest_paths(
    graph: WeightedGraph[Node],
    source: Node,
    *,
    max_edge_weight: int | None = None,
) -> tuple[dict[Node, float], dict[Node, Node | None]]:
    """Dial's bucket-based SSSP for non-negative integer edge weights.

    Complexity is O(E + V*C) with maximum edge weight C.
    """
    nodes = _all_nodes(graph)
    if source not in nodes:
        nodes.append(source)

    observed_max = 0
    normalized: dict[Node, list[tuple[Node, int]]] = {u: [] for u in nodes}
    for u in nodes:
        for v, raw_w in graph.get(u, ()):
            if int(raw_w) != raw_w or raw_w < 0:
                raise ValueError(
                    "Dial's algorithm requires non-negative integer weights"
                )
            w = int(raw_w)
            observed_max = max(observed_max, w)
            normalized[u].append((v, w))

    c = observed_max if max_edge_weight is None else max_edge_weight
    if c < observed_max or c < 0:
        raise ValueError("max_edge_weight must cover all observed weights")

    max_distance = c * max(0, len(nodes) - 1)
    buckets: list[deque[Node]] = [
        deque() for _ in range(max_distance + 1)
    ]
    dist = {u: math.inf for u in nodes}
    prev: dict[Node, Node | None] = {source: None}
    dist[source] = 0.0
    buckets[0].append(source)

    current = 0
    while current <= max_distance:
        while current <= max_distance and not buckets[current]:
            current += 1
        if current > max_distance:
            break
        u = buckets[current].popleft()
        if dist[u] != current:
            continue
        for v, w in normalized[u]:
            nd = current + w
            if nd < dist[v]:
                dist[v] = float(nd)
                prev[v] = u
                buckets[nd].append(v)
    return dist, prev


def dag_shortest_paths(
    graph: WeightedGraph[Node], source: Node
) -> tuple[dict[Node, float], dict[Node, Node | None]]:
    """Single-source shortest paths in a DAG in O(V+E), including negative weights."""
    nodes = _all_nodes(graph)
    unweighted = {
        u: [v for v, _ in graph.get(u, ())]
        for u in nodes
    }
    order = topological_sort_kahn(unweighted)
    dist = {u: math.inf for u in nodes}
    prev: dict[Node, Node | None] = {source: None}
    if source not in dist:
        dist[source] = 0.0
        order.insert(0, source)
    else:
        dist[source] = 0.0

    for u in order:
        if math.isinf(dist.get(u, math.inf)):
            continue
        for v, w in graph.get(u, ()):
            nd = dist[u] + float(w)
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
    return dist, prev


def _dijkstra_path(
    graph: WeightedGraph[Node],
    source: Node,
    target: Node,
    *,
    banned_nodes: set[Node] | None = None,
    banned_edges: set[tuple[Node, Node]] | None = None,
) -> tuple[float, list[Node]] | None:
    banned_nodes = banned_nodes or set()
    banned_edges = banned_edges or set()
    if source in banned_nodes or target in banned_nodes:
        return None

    dist = {source: 0.0}
    prev: dict[Node, Node | None] = {source: None}
    heap: list[tuple[float, int, Node]] = [(0.0, 0, source)]
    serial = 1

    while heap:
        d, _, u = heapq.heappop(heap)
        if d != dist.get(u):
            continue
        if u == target:
            path: list[Node] = []
            cur: Node | None = target
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            return d, path
        for v, w in graph.get(u, ()):
            if w < 0:
                raise ValueError("non-negative weights are required")
            if v in banned_nodes or (u, v) in banned_edges:
                continue
            nd = d + float(w)
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, serial, v))
                serial += 1
    return None


def _path_cost(graph: WeightedGraph[Node], path: list[Node]) -> float:
    total = 0.0
    for u, v in zip(path, path[1:]):
        candidates = [float(w) for nxt, w in graph.get(u, ()) if nxt == v]
        if not candidates:
            raise ValueError("path uses a missing graph edge")
        total += min(candidates)
    return total


def yen_k_shortest_paths(
    graph: WeightedGraph[Node],
    source: Node,
    target: Node,
    k: int,
) -> list[tuple[float, list[Node]]]:
    """Yen's algorithm for k shortest loopless paths with non-negative weights."""
    if k < 1:
        return []
    first = _dijkstra_path(graph, source, target)
    if first is None:
        return []

    accepted: list[tuple[float, list[Node]]] = [first]
    candidates: list[tuple[float, int, list[Node]]] = []
    seen_candidates: set[tuple[Node, ...]] = set()
    serial = 0

    for _ in range(1, k):
        _, previous_path = accepted[-1]
        for spur_index in range(len(previous_path) - 1):
            spur_node = previous_path[spur_index]
            root_path = previous_path[: spur_index + 1]
            banned_edges: set[tuple[Node, Node]] = set()

            for _, path in accepted:
                if (
                    len(path) > spur_index
                    and path[: spur_index + 1] == root_path
                ):
                    banned_edges.add(
                        (path[spur_index], path[spur_index + 1])
                    )

            banned_nodes = set(root_path[:-1])
            spur = _dijkstra_path(
                graph,
                spur_node,
                target,
                banned_nodes=banned_nodes,
                banned_edges=banned_edges,
            )
            if spur is None:
                continue
            _, spur_path = spur
            total_path = root_path[:-1] + spur_path
            key = tuple(total_path)
            if key in seen_candidates:
                continue
            if any(tuple(path) == key for _, path in accepted):
                continue
            seen_candidates.add(key)
            total_cost = _path_cost(graph, total_path)
            heapq.heappush(candidates, (total_cost, serial, total_path))
            serial += 1

        if not candidates:
            break
        cost, _, path = heapq.heappop(candidates)
        accepted.append((cost, path))

    return accepted


def suurballe_two_edge_disjoint_paths(
    graph: WeightedGraph[Node],
    source: Node,
    target: Node,
) -> tuple[tuple[float, list[Node]], tuple[float, list[Node]]] | None:
    """Suurballe's algorithm for two edge-disjoint shortest directed paths.

    Requires a simple directed graph with non-negative weights. Parallel edges
    are not supported by this compact reference implementation.
    """
    nodes = _all_nodes(graph)
    weights: dict[tuple[Node, Node], float] = {}
    for u in nodes:
        for v, w in graph.get(u, ()):
            if w < 0:
                raise ValueError("Suurballe requires non-negative weights")
            if (u, v) in weights:
                raise ValueError("parallel edges are not supported")
            weights[(u, v)] = float(w)

    first = _dijkstra_path(graph, source, target)
    if first is None:
        return None
    _, p1 = first

    # Distances from source are needed for non-negative reweighting.
    dist: dict[Node, float] = {source: 0.0}
    heap: list[tuple[float, int, Node]] = [(0.0, 0, source)]
    serial = 1
    while heap:
        d, _, u = heapq.heappop(heap)
        if d != dist.get(u):
            continue
        for v, w in graph.get(u, ()):
            nd = d + float(w)
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                heapq.heappush(heap, (nd, serial, v))
                serial += 1

    path_edges = set(zip(p1, p1[1:]))
    transformed: dict[
        Node, list[tuple[Node, float, tuple[str, Node, Node]]]
    ] = {u: [] for u in nodes}

    for (u, v), w in weights.items():
        if u not in dist or v not in dist:
            continue
        if (u, v) in path_edges:
            transformed[v].append((u, 0.0, ("reverse", u, v)))
        else:
            rw = w + dist[u] - dist[v]
            transformed[u].append((v, max(0.0, rw), ("original", u, v)))

    tdist = {source: 0.0}
    prev: dict[Node, tuple[Node, tuple[str, Node, Node]]] = {}
    q: list[tuple[float, int, Node]] = [(0.0, 0, source)]
    serial = 1
    while q:
        d, _, u = heapq.heappop(q)
        if d != tdist.get(u):
            continue
        if u == target:
            break
        for v, w, tag in transformed.get(u, ()):
            nd = d + w
            if nd < tdist.get(v, math.inf):
                tdist[v] = nd
                prev[v] = (u, tag)
                heapq.heappush(q, (nd, serial, v))
                serial += 1

    if target not in tdist:
        return None

    second_tags: list[tuple[str, Node, Node]] = []
    cur = target
    while cur != source:
        if cur not in prev:
            return None
        parent, tag = prev[cur]
        second_tags.append(tag)
        cur = parent
    second_tags.reverse()

    remaining: list[tuple[Node, Node]] = list(path_edges)
    for kind, u, v in second_tags:
        if kind == "reverse":
            try:
                remaining.remove((u, v))
            except ValueError:
                return None
        else:
            remaining.append((u, v))

    adjacency: dict[Node, list[Node]] = {}
    for u, v in remaining:
        adjacency.setdefault(u, []).append(v)

    def extract_path() -> list[Node] | None:
        stack: list[tuple[Node, list[Node], set[tuple[Node, Node]]]] = [
            (source, [source], set())
        ]
        while stack:
            u, path, used_edges = stack.pop()
            if u == target:
                for a, b in zip(path, path[1:]):
                    adjacency[a].remove(b)
                return path
            for v in list(adjacency.get(u, ())):
                edge = (u, v)
                if edge in used_edges or v in path:
                    continue
                stack.append((v, path + [v], used_edges | {edge}))
        return None

    a = extract_path()
    b = extract_path()
    if a is None or b is None:
        return None
    result_a = (_path_cost(graph, a), a)
    result_b = (_path_cost(graph, b), b)
    return result_a, result_b
