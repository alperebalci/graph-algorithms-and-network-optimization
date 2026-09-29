from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

from .cycles_and_dag import topological_sort_kahn

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _all_nodes(graph: Graph[Node]) -> list[Node]:
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    return nodes


def transitive_closure(graph: Graph[Node]) -> dict[Node, set[Node]]:
    """Reachability sets for every vertex. O(V(V+E)) by repeated DFS."""
    nodes = _all_nodes(graph)
    closure: dict[Node, set[Node]] = {}
    for source in nodes:
        reached: set[Node] = set()
        stack = list(graph.get(source, ()))
        while stack:
            u = stack.pop()
            if u in reached:
                continue
            reached.add(u)
            stack.extend(graph.get(u, ()))
        closure[source] = reached
    return closure


def transitive_reduction_dag(graph: Graph[Node]) -> dict[Node, list[Node]]:
    """Unique transitive reduction of a DAG.

    An edge u->v is removed exactly when another directed u-v path exists.
    """
    nodes = _all_nodes(graph)
    normalized = {u: list(dict.fromkeys(graph.get(u, ()))) for u in nodes}
    order = topological_sort_kahn(normalized)
    position = {u: i for i, u in enumerate(order)}

    descendants: dict[Node, set[Node]] = {u: set() for u in nodes}
    reduced: dict[Node, list[Node]] = {u: [] for u in nodes}

    for u in reversed(order):
        covered: set[Node] = set()
        neighbors = sorted(normalized[u], key=lambda v: position[v])
        for v in neighbors:
            if v in covered:
                continue
            reduced[u].append(v)
            covered.add(v)
            covered.update(descendants[v])
        descendants[u] = covered
    return reduced
