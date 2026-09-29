from __future__ import annotations

import heapq
from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import TypeVar

from .disjoint_set import DisjointSet
from .exceptions import DisconnectedGraphError

Node = TypeVar("Node", bound=Hashable)
Edge = tuple[Node, Node, float]
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


def kruskal(vertices: Iterable[Node], edges: Sequence[Edge[Node]]) -> tuple[float, list[Edge[Node]]]:
    """Minimum spanning tree of a connected undirected weighted graph. O(E log E)."""
    nodes = list(dict.fromkeys(vertices))
    dsu = DisjointSet(nodes)
    tree: list[Edge[Node]] = []
    total = 0.0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if dsu.union(u, v):
            tree.append((u, v, w))
            total += w
            if len(tree) == max(0, len(nodes) - 1):
                break
    if len(tree) != max(0, len(nodes) - 1):
        raise DisconnectedGraphError("graph is disconnected")
    return total, tree


def prim(graph: WeightedGraph[Node], start: Node | None = None) -> tuple[float, list[Edge[Node]]]:
    """Minimum spanning tree of a connected undirected weighted graph. O(E log V)."""
    nodes = list(graph)
    if not nodes:
        return 0.0, []
    if start is None:
        start = nodes[0]
    if start not in graph:
        raise KeyError(start)

    seen = {start}
    heap: list[tuple[float, int, Node, Node]] = []
    serial = 0
    for v, w in graph.get(start, ()):
        heapq.heappush(heap, (w, serial, start, v))
        serial += 1

    tree: list[Edge[Node]] = []
    total = 0.0
    while heap and len(seen) < len(nodes):
        w, _, u, v = heapq.heappop(heap)
        if v in seen:
            continue
        seen.add(v)
        tree.append((u, v, w))
        total += w
        for nxt, nw in graph.get(v, ()):
            if nxt not in seen:
                heapq.heappush(heap, (nw, serial, v, nxt))
                serial += 1

    if len(seen) != len(nodes):
        raise DisconnectedGraphError("graph is disconnected")
    return total, tree



def boruvka(
    vertices: Iterable[Node], edges: Sequence[Edge[Node]]
) -> tuple[float, list[Edge[Node]]]:
    """Boruvka minimum spanning tree for a connected undirected graph.

    Each phase adds the cheapest outgoing edge of every current component.
    There are O(log V) phases, each scanning all edges: O(E log V).
    """
    nodes = list(dict.fromkeys(vertices))
    if not nodes:
        return 0.0, []

    dsu = DisjointSet(nodes)
    components = len(nodes)
    tree: list[Edge[Node]] = []
    total = 0.0

    while components > 1:
        cheapest: dict[Node, Edge[Node]] = {}
        for u, v, w in edges:
            ru, rv = dsu.find(u), dsu.find(v)
            if ru == rv:
                continue
            if ru not in cheapest or w < cheapest[ru][2]:
                cheapest[ru] = (u, v, w)
            if rv not in cheapest or w < cheapest[rv][2]:
                cheapest[rv] = (u, v, w)

        merged = 0
        for edge in list(cheapest.values()):
            u, v, w = edge
            if dsu.union(u, v):
                tree.append(edge)
                total += w
                components -= 1
                merged += 1

        if merged == 0:
            raise DisconnectedGraphError("graph is disconnected")

    return total, tree
