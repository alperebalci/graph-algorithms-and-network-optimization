from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

from .disjoint_set import DisjointSet

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def has_cycle_undirected_dfs(graph: Graph[Node]) -> bool:
    seen: set[Node] = set()

    def visit(u: Node, parent: Node | None) -> bool:
        seen.add(u)
        for v in graph.get(u, ()):
            if v == parent:
                continue
            if v in seen or visit(v, u):
                return True
        return False

    for node in graph:
        if node not in seen and visit(node, None):
            return True
    return False


def has_cycle_undirected_dsu(vertices: Iterable[Node], edges: Iterable[tuple[Node, Node]]) -> bool:
    dsu = DisjointSet(vertices)
    for u, v in edges:
        if not dsu.union(u, v):
            return True
    return False


def has_cycle_directed(graph: Graph[Node]) -> bool:
    color: dict[Node, int] = {}

    def visit(u: Node) -> bool:
        color[u] = 1
        for v in graph.get(u, ()):
            state = color.get(v, 0)
            if state == 1:
                return True
            if state == 0 and visit(v):
                return True
        color[u] = 2
        return False

    nodes = set(graph)
    for neigh in graph.values():
        nodes.update(neigh)
    return any(color.get(node, 0) == 0 and visit(node) for node in nodes)


def topological_sort_kahn(graph: Graph[Node]) -> list[Node]:
    nodes = set(graph)
    for neigh in graph.values():
        nodes.update(neigh)
    indeg = {u: 0 for u in nodes}
    for u in nodes:
        for v in graph.get(u, ()):
            indeg[v] += 1
    queue: deque[Node] = deque(u for u in nodes if indeg[u] == 0)
    order: list[Node] = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, ()):
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    if len(order) != len(nodes):
        raise ValueError("graph contains a directed cycle")
    return order


def topological_sort_dfs(graph: Graph[Node]) -> list[Node]:
    color: dict[Node, int] = {}
    order: list[Node] = []

    def visit(u: Node) -> None:
        state = color.get(u, 0)
        if state == 1:
            raise ValueError("graph contains a directed cycle")
        if state == 2:
            return
        color[u] = 1
        for v in graph.get(u, ()):
            visit(v)
        color[u] = 2
        order.append(u)

    nodes = set(graph)
    for neigh in graph.values():
        nodes.update(neigh)
    for node in nodes:
        if color.get(node, 0) == 0:
            visit(node)
    order.reverse()
    return order
