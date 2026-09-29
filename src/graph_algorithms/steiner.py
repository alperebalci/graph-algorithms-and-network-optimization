from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import TypeVar

from .shortest_paths import dijkstra, reconstruct_path
from .spanning_trees import kruskal

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


@dataclass(frozen=True)
class SteinerTreeResult:
    value: float
    edges: tuple[tuple[Hashable, Hashable, float], ...]
    vertices: frozenset[Hashable]


def steiner_tree_2approx(
    graph: WeightedGraph[Node],
    terminals: Iterable[Node],
) -> SteinerTreeResult:
    """Metric-closure MST 2-approximation for undirected Steiner Tree."""
    terminal_list = list(dict.fromkeys(terminals))
    terminal_set = set(terminal_list)
    if not terminal_list:
        return SteinerTreeResult(0.0, (), frozenset())
    if len(terminal_list) == 1:
        return SteinerTreeResult(0.0, (), frozenset(terminal_list))

    nodes = list(graph)
    seen = set(nodes)
    weights: dict[frozenset[Node], tuple[Node, Node, float]] = {}

    for u, neighbors in graph.items():
        for v, raw_weight in neighbors:
            weight = float(raw_weight)
            if weight < 0:
                raise ValueError("Steiner 2-approximation requires non-negative weights")
            if v not in seen:
                seen.add(v)
                nodes.append(v)
            if u == v:
                continue
            key = frozenset((u, v))
            if key in weights:
                _, _, old = weights[key]
                if abs(old - weight) > 1e-9:
                    raise ValueError(
                        "symmetric entries of an undirected edge must agree"
                    )
            else:
                weights[key] = (u, v, weight)

    if not terminal_set <= seen:
        raise KeyError(f"terminals missing from graph: {terminal_set - seen}")

    distances: dict[Node, dict[Node, float]] = {}
    predecessors: dict[Node, dict[Node, Node | None]] = {}
    for terminal in terminal_list:
        dist, prev = dijkstra(graph, terminal)
        distances[terminal] = dist
        predecessors[terminal] = prev
        if any(other not in dist for other in terminal_list):
            raise ValueError("all terminals must belong to one connected component")

    closure_edges: list[tuple[Node, Node, float]] = []
    for i, u in enumerate(terminal_list):
        for v in terminal_list[i + 1 :]:
            closure_edges.append((u, v, distances[u][v]))

    _, closure_mst = kruskal(terminal_list, closure_edges)
    expanded_edges: dict[
        frozenset[Node], tuple[Node, Node, float]
    ] = {}
    expanded_vertices: set[Node] = set()

    for u, v, _ in closure_mst:
        path = reconstruct_path(predecessors[u], u, v)
        if path is None:
            raise AssertionError("terminal shortest path disappeared")
        expanded_vertices.update(path)
        for a, b in zip(path, path[1:]):
            key = frozenset((a, b))
            if key not in weights:
                raise AssertionError("shortest path uses an unknown undirected edge")
            expanded_edges[key] = weights[key]

    _, tree_edges = kruskal(expanded_vertices, list(expanded_edges.values()))
    adjacency: dict[Node, set[Node]] = {u: set() for u in expanded_vertices}
    edge_weight: dict[frozenset[Node], float] = {}
    for u, v, weight in tree_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
        edge_weight[frozenset((u, v))] = weight

    queue = [
        u for u in expanded_vertices
        if u not in terminal_set and len(adjacency[u]) <= 1
    ]
    while queue:
        u = queue.pop()
        if u in terminal_set or len(adjacency[u]) > 1 or not adjacency[u]:
            continue
        v = next(iter(adjacency[u]))
        adjacency[u].remove(v)
        adjacency[v].remove(u)
        edge_weight.pop(frozenset((u, v)), None)
        if v not in terminal_set and len(adjacency[v]) <= 1:
            queue.append(v)

    final_edges: list[tuple[Hashable, Hashable, float]] = []
    final_vertices: set[Hashable] = set(terminal_set)
    for key, weight in edge_weight.items():
        u, v = tuple(key)
        final_edges.append((u, v, weight))
        final_vertices.update((u, v))

    return SteinerTreeResult(
        value=sum(weight for _, _, weight in final_edges),
        edges=tuple(final_edges),
        vertices=frozenset(final_vertices),
    )
