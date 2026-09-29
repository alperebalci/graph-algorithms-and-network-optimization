from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]
Edge = tuple[Node, Node]


def _all_nodes(graph: Graph[Node]) -> set[Node]:
    nodes = set(graph)
    for neigh in graph.values():
        nodes.update(neigh)
    return nodes


def connected_components(graph: Graph[Node]) -> list[set[Node]]:
    """Connected components of an undirected graph. O(V+E)."""
    seen: set[Node] = set()
    components: list[set[Node]] = []
    for start in _all_nodes(graph):
        if start in seen:
            continue
        comp: set[Node] = set()
        stack = [start]
        seen.add(start)
        while stack:
            u = stack.pop()
            comp.add(u)
            for v in graph.get(u, ()):
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        components.append(comp)
    return components


def kosaraju_scc(graph: Graph[Node]) -> list[set[Node]]:
    """Strongly connected components of a directed graph. O(V+E)."""
    nodes = _all_nodes(graph)
    seen: set[Node] = set()
    finish: list[Node] = []

    def dfs1(u: Node) -> None:
        seen.add(u)
        for v in graph.get(u, ()):
            if v not in seen:
                dfs1(v)
        finish.append(u)

    for u in nodes:
        if u not in seen:
            dfs1(u)

    rev: dict[Node, list[Node]] = {u: [] for u in nodes}
    for u in nodes:
        for v in graph.get(u, ()):
            rev[v].append(u)

    seen.clear()
    result: list[set[Node]] = []

    def dfs2(u: Node, comp: set[Node]) -> None:
        seen.add(u)
        comp.add(u)
        for v in rev[u]:
            if v not in seen:
                dfs2(v, comp)

    for u in reversed(finish):
        if u not in seen:
            comp: set[Node] = set()
            dfs2(u, comp)
            result.append(comp)
    return result


def tarjan_scc(graph: Graph[Node]) -> list[set[Node]]:
    """Tarjan strongly connected components via low-link values. O(V+E)."""
    nodes = _all_nodes(graph)
    index = 0
    indices: dict[Node, int] = {}
    low: dict[Node, int] = {}
    stack: list[Node] = []
    on_stack: set[Node] = set()
    result: list[set[Node]] = []

    def strongconnect(v: Node) -> None:
        nonlocal index
        indices[v] = index
        low[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.get(v, ()):
            if w not in indices:
                strongconnect(w)
                low[v] = min(low[v], low[w])
            elif w in on_stack:
                low[v] = min(low[v], indices[w])

        if low[v] == indices[v]:
            comp: set[Node] = set()
            while True:
                w = stack.pop()
                on_stack.remove(w)
                comp.add(w)
                if w == v:
                    break
            result.append(comp)

    for v in nodes:
        if v not in indices:
            strongconnect(v)
    return result


def bridges(graph: Graph[Node]) -> list[Edge[Node]]:
    """Tarjan bridge detection in an undirected simple graph. O(V+E)."""
    timer = 0
    tin: dict[Node, int] = {}
    low: dict[Node, int] = {}
    result: list[Edge[Node]] = []

    def dfs(u: Node, parent: Node | None) -> None:
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        skipped_parent = False
        for v in graph.get(u, ()):
            if v == parent and not skipped_parent:
                skipped_parent = True
                continue
            if v in tin:
                low[u] = min(low[u], tin[v])
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    result.append((u, v))

    for u in _all_nodes(graph):
        if u not in tin:
            dfs(u, None)
    return result


def articulation_points(graph: Graph[Node]) -> set[Node]:
    """Tarjan articulation-point detection in an undirected graph. O(V+E)."""
    timer = 0
    tin: dict[Node, int] = {}
    low: dict[Node, int] = {}
    result: set[Node] = set()

    def dfs(u: Node, parent: Node | None) -> None:
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        children = 0
        for v in graph.get(u, ()):
            if v == parent:
                continue
            if v in tin:
                low[u] = min(low[u], tin[v])
            else:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent is not None and low[v] >= tin[u]:
                    result.add(u)
                children += 1
        if parent is None and children > 1:
            result.add(u)

    for u in _all_nodes(graph):
        if u not in tin:
            dfs(u, None)
    return result


def biconnected_components(graph: Graph[Node]) -> list[list[Edge[Node]]]:
    """Vertex-biconnected edge blocks of an undirected graph via Tarjan's edge stack."""
    timer = 0
    tin: dict[Node, int] = {}
    low: dict[Node, int] = {}
    edge_stack: list[Edge[Node]] = []
    result: list[list[Edge[Node]]] = []

    def pop_until(stop: Edge[Node]) -> None:
        comp: list[Edge[Node]] = []
        while edge_stack:
            e = edge_stack.pop()
            comp.append(e)
            if e == stop:
                break
        if comp:
            result.append(comp)

    def dfs(u: Node, parent: Node | None) -> None:
        nonlocal timer
        tin[u] = low[u] = timer
        timer += 1
        for v in graph.get(u, ()):
            if v == parent:
                continue
            if v not in tin:
                edge_stack.append((u, v))
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] >= tin[u]:
                    pop_until((u, v))
            elif tin[v] < tin[u]:
                edge_stack.append((u, v))
                low[u] = min(low[u], tin[v])

    for u in _all_nodes(graph):
        if u not in tin:
            dfs(u, None)
            if edge_stack:
                comp = edge_stack[:]
                edge_stack.clear()
                result.append(comp)
    return result
