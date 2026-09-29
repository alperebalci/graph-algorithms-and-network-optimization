from __future__ import annotations

from collections import defaultdict
from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import Generic, TypeVar

from .disjoint_set import DisjointSet

Node = TypeVar("Node", bound=Hashable)
Tree = Mapping[Node, Iterable[Node]]


def euler_tour(
    tree: Tree[Node], root: Node
) -> tuple[list[Node], dict[Node, int], dict[Node, int]]:
    """DFS Euler-entry order plus inclusive subtree intervals [tin, tout]. O(V)."""
    order: list[Node] = []
    tin: dict[Node, int] = {}
    tout: dict[Node, int] = {}

    def dfs(u: Node, parent: Node | None) -> None:
        tin[u] = len(order)
        order.append(u)
        for v in tree.get(u, ()):
            if v != parent:
                dfs(v, u)
        tout[u] = len(order) - 1

    dfs(root, None)
    return order, tin, tout


class BinaryLiftingLCA(Generic[Node]):
    """Lowest common ancestor with O(V log V) preprocessing and O(log V) queries."""

    def __init__(self, tree: Tree[Node], root: Node) -> None:
        self.nodes: list[Node] = []
        self.depth: dict[Node, int] = {}
        self.parent: dict[Node, Node] = {}

        def dfs(u: Node, p: Node, d: int) -> None:
            self.nodes.append(u)
            self.depth[u] = d
            self.parent[u] = p
            for v in tree.get(u, ()):
                if v != p:
                    dfs(v, u, d + 1)

        dfs(root, root, 0)
        self.log = max(1, len(self.nodes).bit_length())
        self.up: list[dict[Node, Node]] = [
            dict() for _ in range(self.log)
        ]
        for u in self.nodes:
            self.up[0][u] = self.parent[u]
        for j in range(1, self.log):
            for u in self.nodes:
                self.up[j][u] = self.up[j - 1][self.up[j - 1][u]]

    def lift(self, u: Node, steps: int) -> Node:
        if u not in self.depth:
            raise KeyError(u)
        bit = 0
        while steps:
            if steps & 1:
                u = self.up[bit][u]
            steps >>= 1
            bit += 1
        return u

    def lca(self, a: Node, b: Node) -> Node:
        if a not in self.depth or b not in self.depth:
            raise KeyError("query node not present in rooted tree")
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        a = self.lift(a, self.depth[a] - self.depth[b])
        if a == b:
            return a
        for j in range(self.log - 1, -1, -1):
            if self.up[j][a] != self.up[j][b]:
                a = self.up[j][a]
                b = self.up[j][b]
        return self.up[0][a]


def tarjan_offline_lca(
    tree: Tree[Node], root: Node, queries: Sequence[tuple[Node, Node]]
) -> list[Node]:
    """Tarjan offline LCA for a batch of queries. O((V+Q) alpha(V))."""
    query_map: dict[Node, list[tuple[Node, int]]] = defaultdict(list)
    for i, (u, v) in enumerate(queries):
        query_map[u].append((v, i))
        query_map[v].append((u, i))

    dsu: DisjointSet[Node] = DisjointSet()
    ancestor: dict[Node, Node] = {}
    visited: set[Node] = set()
    answers: list[Node | None] = [None] * len(queries)

    def dfs(u: Node, parent: Node | None) -> None:
        dsu.add(u)
        ancestor[dsu.find(u)] = u
        for v in tree.get(u, ()):
            if v == parent:
                continue
            dfs(v, u)
            dsu.union(u, v)
            ancestor[dsu.find(u)] = u
        visited.add(u)
        for other, idx in query_map.get(u, ()):
            if other in visited:
                answers[idx] = ancestor[dsu.find(other)]

    dfs(root, None)
    if any(answer is None for answer in answers):
        raise ValueError("all query nodes must belong to the rooted tree")
    return [answer for answer in answers if answer is not None]


class HeavyLightDecomposition(Generic[Node]):
    """Heavy-light decomposition of a rooted tree.

    path_segments(u, v) returns O(log V) inclusive index intervals in the base
    array. Attach a segment tree/Fenwick tree externally for path queries/updates.
    """

    def __init__(self, tree: Tree[Node], root: Node) -> None:
        self.tree = tree
        self.root = root
        self.parent: dict[Node, Node] = {root: root}
        self.depth: dict[Node, int] = {root: 0}
        self.size: dict[Node, int] = {}
        self.heavy: dict[Node, Node | None] = {}
        self.head: dict[Node, Node] = {}
        self.pos: dict[Node, int] = {}
        self.order: list[Node] = []

        def dfs(u: Node, p: Node) -> int:
            size = 1
            best_size = 0
            heavy_child: Node | None = None
            for v in tree.get(u, ()):
                if v == p:
                    continue
                self.parent[v] = u
                self.depth[v] = self.depth[u] + 1
                child_size = dfs(v, u)
                size += child_size
                if child_size > best_size:
                    best_size = child_size
                    heavy_child = v
            self.size[u] = size
            self.heavy[u] = heavy_child
            return size

        def decompose(u: Node, h: Node) -> None:
            self.head[u] = h
            self.pos[u] = len(self.order)
            self.order.append(u)
            heavy_child = self.heavy[u]
            if heavy_child is not None:
                decompose(heavy_child, h)
            for v in tree.get(u, ()):
                if v == self.parent[u] or v == heavy_child:
                    continue
                decompose(v, v)

        dfs(root, root)
        decompose(root, root)

    def path_segments(self, u: Node, v: Node) -> list[tuple[int, int]]:
        segments: list[tuple[int, int]] = []
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            hu = self.head[u]
            segments.append((self.pos[hu], self.pos[u]))
            u = self.parent[hu]
        lo, hi = sorted((self.pos[u], self.pos[v]))
        segments.append((lo, hi))
        return segments


class CentroidDecomposition(Generic[Node]):
    """Centroid decomposition of an undirected tree in O(V log V)."""

    def __init__(self, tree: Tree[Node]) -> None:
        self.adj: dict[Node, set[Node]] = {
            u: set(vs) for u, vs in tree.items()
        }
        for u, vs in list(self.adj.items()):
            for v in vs:
                self.adj.setdefault(v, set()).add(u)
        self.removed: set[Node] = set()
        self.size: dict[Node, int] = {}
        self.parent: dict[Node, Node | None] = {}
        if self.adj:
            start = next(iter(self.adj))
            self._build(start, None)

    def _compute_size(self, u: Node, p: Node | None) -> int:
        total = 1
        for v in self.adj[u]:
            if v != p and v not in self.removed:
                total += self._compute_size(v, u)
        self.size[u] = total
        return total

    def _find_centroid(
        self, u: Node, p: Node | None, total: int
    ) -> Node:
        for v in self.adj[u]:
            if (
                v != p
                and v not in self.removed
                and self.size[v] > total // 2
            ):
                return self._find_centroid(v, u, total)
        return u

    def _build(self, entry: Node, parent: Node | None) -> Node:
        total = self._compute_size(entry, None)
        centroid = self._find_centroid(entry, None, total)
        self.parent[centroid] = parent
        self.removed.add(centroid)
        for v in list(self.adj[centroid]):
            if v not in self.removed:
                self._build(v, centroid)
        return centroid
