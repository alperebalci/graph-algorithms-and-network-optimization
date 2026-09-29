from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def lengauer_tarjan_dominators(
    graph: Graph[Node], start: Node
) -> dict[Node, Node]:
    """Immediate dominators of vertices reachable from start.

    Implements the Lengauer-Tarjan semidominator algorithm. The returned map
    sets start as its own immediate dominator.
    """
    vertex: list[Node | None] = [None]
    parent: dict[Node, Node | None] = {start: None}
    dfs_number: dict[Node, int] = {}

    def dfs(u: Node) -> None:
        dfs_number[u] = len(vertex)
        vertex.append(u)
        for v in graph.get(u, ()):
            if v not in dfs_number:
                parent[v] = u
                dfs(v)

    dfs(start)
    n = len(vertex) - 1
    if n == 0:
        return {}

    pred: dict[Node, list[Node]] = defaultdict(list)
    for u in list(dfs_number):
        for v in graph.get(u, ()):
            if v in dfs_number:
                pred[v].append(u)

    semi = {u: dfs_number[u] for u in dfs_number}
    ancestor: dict[Node, Node | None] = {u: None for u in dfs_number}
    label = {u: u for u in dfs_number}
    bucket: dict[Node, list[Node]] = defaultdict(list)
    idom: dict[Node, Node] = {}

    def compress(v: Node) -> None:
        a = ancestor[v]
        if a is None:
            return
        aa = ancestor[a]
        if aa is not None:
            compress(a)
            if semi[label[a]] < semi[label[v]]:
                label[v] = label[a]
            ancestor[v] = ancestor[a]

    def eval_node(v: Node) -> Node:
        if ancestor[v] is None:
            return label[v]
        compress(v)
        return label[v]

    def link(v: Node, w: Node) -> None:
        ancestor[w] = v

    for i in range(n, 1, -1):
        w = vertex[i]
        assert w is not None
        for v in pred[w]:
            u = eval_node(v)
            semi[w] = min(semi[w], semi[u])

        semi_vertex = vertex[semi[w]]
        assert semi_vertex is not None
        bucket[semi_vertex].append(w)

        p = parent[w]
        assert p is not None
        link(p, w)

        pending = bucket[p]
        for v in pending:
            u = eval_node(v)
            idom[v] = u if semi[u] < semi[v] else p
        bucket[p] = []

    for i in range(2, n + 1):
        w = vertex[i]
        assert w is not None
        semi_vertex = vertex[semi[w]]
        assert semi_vertex is not None
        if idom[w] != semi_vertex:
            idom[w] = idom[idom[w]]

    idom[start] = start
    return idom
