from __future__ import annotations

import math
from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _nodes(graph: Graph[Node]) -> list[Node]:
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    return nodes


def pagerank(
    graph: Graph[Node],
    *,
    damping: float = 0.85,
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
) -> dict[Node, float]:
    """Power-iteration PageRank for a directed graph."""
    if not 0.0 < damping < 1.0:
        raise ValueError("damping must be strictly between 0 and 1")
    nodes = _nodes(graph)
    n = len(nodes)
    if n == 0:
        return {}

    outgoing = {u: list(graph.get(u, ())) for u in nodes}
    rank = {u: 1.0 / n for u in nodes}
    base = (1.0 - damping) / n

    for _ in range(max_iterations):
        dangling = sum(rank[u] for u in nodes if not outgoing[u])
        new_rank = {u: base + damping * dangling / n for u in nodes}
        for u in nodes:
            if not outgoing[u]:
                continue
            share = damping * rank[u] / len(outgoing[u])
            for v in outgoing[u]:
                new_rank[v] += share
        error = sum(abs(new_rank[u] - rank[u]) for u in nodes)
        rank = new_rank
        if error <= tolerance:
            break

    total = sum(rank.values())
    return {u: value / total for u, value in rank.items()}


def hits(
    graph: Graph[Node],
    *,
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
) -> tuple[dict[Node, float], dict[Node, float]]:
    """HITS hub and authority scores by power iteration."""
    nodes = _nodes(graph)
    if not nodes:
        return {}, {}
    incoming: dict[Node, list[Node]] = {u: [] for u in nodes}
    outgoing = {u: list(graph.get(u, ())) for u in nodes}
    for u in nodes:
        for v in outgoing[u]:
            incoming[v].append(u)

    hubs = {u: 1.0 for u in nodes}
    authorities = {u: 1.0 for u in nodes}

    for _ in range(max_iterations):
        new_auth = {
            u: sum(hubs[v] for v in incoming[u]) for u in nodes
        }
        norm = math.sqrt(sum(x * x for x in new_auth.values())) or 1.0
        new_auth = {u: x / norm for u, x in new_auth.items()}

        new_hubs = {
            u: sum(new_auth[v] for v in outgoing[u]) for u in nodes
        }
        norm = math.sqrt(sum(x * x for x in new_hubs.values())) or 1.0
        new_hubs = {u: x / norm for u, x in new_hubs.items()}

        error = sum(
            abs(new_hubs[u] - hubs[u])
            + abs(new_auth[u] - authorities[u])
            for u in nodes
        )
        hubs, authorities = new_hubs, new_auth
        if error <= tolerance:
            break
    return hubs, authorities


def brandes_betweenness_centrality(
    graph: Graph[Node], *, normalized: bool = True, directed: bool = False
) -> dict[Node, float]:
    """Brandes betweenness centrality for unweighted graphs. O(VE)."""
    nodes = _nodes(graph)
    centrality = {v: 0.0 for v in nodes}

    for source in nodes:
        stack: list[Node] = []
        predecessors: dict[Node, list[Node]] = {v: [] for v in nodes}
        sigma = {v: 0.0 for v in nodes}
        sigma[source] = 1.0
        distance = {v: -1 for v in nodes}
        distance[source] = 0
        queue: deque[Node] = deque([source])

        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph.get(v, ()):
                if distance[w] < 0:
                    queue.append(w)
                    distance[w] = distance[v] + 1
                if distance[w] == distance[v] + 1:
                    sigma[w] += sigma[v]
                    predecessors[w].append(v)

        dependency = {v: 0.0 for v in nodes}
        while stack:
            w = stack.pop()
            if sigma[w] > 0:
                coeff = (1.0 + dependency[w]) / sigma[w]
                for v in predecessors[w]:
                    dependency[v] += sigma[v] * coeff
            if w != source:
                centrality[w] += dependency[w]

    if not directed:
        centrality = {v: x / 2.0 for v, x in centrality.items()}

    if normalized and len(nodes) > 2:
        scale = 1.0 / ((len(nodes) - 1) * (len(nodes) - 2))
        if not directed:
            scale *= 2.0
        centrality = {v: x * scale for v, x in centrality.items()}
    return centrality


def core_numbers(graph: Graph[Node]) -> dict[Node, int]:
    """k-core decomposition of a simple undirected graph in O(V+E)."""
    nodes = _nodes(graph)
    neighbors = {u: set(graph.get(u, ())) - {u} for u in nodes}
    degree = {u: len(neighbors[u]) for u in nodes}
    if not nodes:
        return {}

    max_degree = max(degree.values(), default=0)
    bins = [0] * (max_degree + 1)
    for d in degree.values():
        bins[d] += 1

    start = 0
    for d in range(max_degree + 1):
        count = bins[d]
        bins[d] = start
        start += count

    position: dict[Node, int] = {}
    vertices: list[Node] = [nodes[0]] * len(nodes)
    next_pos = bins.copy()
    for v in nodes:
        d = degree[v]
        position[v] = next_pos[d]
        vertices[position[v]] = v
        next_pos[d] += 1

    for d in range(max_degree, 0, -1):
        bins[d] = bins[d - 1]
    bins[0] = 0

    for v in vertices:
        for u in list(neighbors[v]):
            if degree[u] > degree[v]:
                du = degree[u]
                pu = position[u]
                pw = bins[du]
                w = vertices[pw]
                if u != w:
                    vertices[pu], vertices[pw] = vertices[pw], vertices[pu]
                    position[u], position[w] = pw, pu
                bins[du] += 1
                degree[u] -= 1
    return degree



def personalized_pagerank(
    graph: Graph[Node],
    personalization: Mapping[Node, float],
    *,
    damping: float = 0.85,
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
) -> dict[Node, float]:
    """Personalized PageRank with an arbitrary non-negative teleport vector."""
    if not 0.0 < damping < 1.0:
        raise ValueError("damping must be strictly between 0 and 1")
    nodes = _nodes(graph)
    if not nodes:
        return {}

    teleport = {u: float(personalization.get(u, 0.0)) for u in nodes}
    if any(value < 0 for value in teleport.values()):
        raise ValueError("personalization weights must be non-negative")
    total_teleport = sum(teleport.values())
    if total_teleport <= 0:
        raise ValueError("personalization must have positive total mass")
    teleport = {
        u: value / total_teleport for u, value in teleport.items()
    }

    outgoing = {u: list(graph.get(u, ())) for u in nodes}
    rank = dict(teleport)

    for _ in range(max_iterations):
        dangling_mass = sum(
            rank[u] for u in nodes if not outgoing[u]
        )
        new_rank = {
            u: (1.0 - damping) * teleport[u]
            + damping * dangling_mass * teleport[u]
            for u in nodes
        }
        for u in nodes:
            if not outgoing[u]:
                continue
            share = damping * rank[u] / len(outgoing[u])
            for v in outgoing[u]:
                new_rank[v] += share

        error = sum(abs(new_rank[u] - rank[u]) for u in nodes)
        rank = new_rank
        if error <= tolerance:
            break

    total = sum(rank.values())
    return {u: value / total for u, value in rank.items()}


def triangle_count(graph: Graph[Node]) -> tuple[int, dict[Node, int]]:
    """Count triangles in a simple undirected graph.

    Returns the global triangle count and the number of incident triangles per
    vertex. The orientation-by-degree scheme avoids triple enumeration of the
    same triangle.
    """
    nodes = _nodes(graph)
    neighbors = {u: set(graph.get(u, ())) - {u} for u in nodes}
    for u in nodes:
        for v in tuple(neighbors[u]):
            neighbors.setdefault(v, set()).add(u)

    order = sorted(nodes, key=lambda u: (len(neighbors[u]), repr(u)))
    rank = {u: i for i, u in enumerate(order)}
    forward = {
        u: {v for v in neighbors[u] if rank[u] < rank[v]}
        for u in nodes
    }
    local = {u: 0 for u in nodes}
    total = 0
    for u in nodes:
        for v in forward[u]:
            common = forward[u] & forward[v]
            for w in common:
                total += 1
                local[u] += 1
                local[v] += 1
                local[w] += 1
    return total, local


def label_propagation_communities(
    graph: Graph[Node],
    *,
    max_iterations: int = 100,
) -> list[set[Node]]:
    """Deterministic label-propagation community heuristic.

    Ties are resolved by the original node order so repeated runs are stable.
    """
    nodes = _nodes(graph)
    if not nodes:
        return []
    neighbors = {u: list(graph.get(u, ())) for u in nodes}
    labels = {u: i for i, u in enumerate(nodes)}

    for _ in range(max_iterations):
        changed = False
        for u in nodes:
            counts: dict[int, int] = {}
            for v in neighbors[u]:
                label = labels[v]
                counts[label] = counts.get(label, 0) + 1
            if not counts:
                continue
            best_count = max(counts.values())
            best_label = min(
                label for label, count in counts.items()
                if count == best_count
            )
            if labels[u] != best_label:
                labels[u] = best_label
                changed = True
        if not changed:
            break

    communities: dict[int, set[Node]] = {}
    for u in nodes:
        communities.setdefault(labels[u], set()).add(u)
    return list(communities.values())
