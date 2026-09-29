from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)


class RollbackDisjointSet:
    """Union-Find with snapshots and rollback, without path compression."""

    def __init__(self, items: Iterable[Node] = ()) -> None:
        self.parent: dict[Node, Node] = {}
        self.size: dict[Node, int] = {}
        self.history: list[tuple[Node | None, Node | None, int]] = []
        for item in items:
            self.add(item)

    def add(self, item: Node) -> None:
        if item not in self.parent:
            self.parent[item] = item
            self.size[item] = 1

    def find(self, item: Node) -> Node:
        if item not in self.parent:
            self.add(item)
        while self.parent[item] != item:
            item = self.parent[item]
        return item

    def union(self, a: Node, b: Node) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            self.history.append((None, None, 0))
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.history.append((rb, ra, self.size[ra]))
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True

    def snapshot(self) -> int:
        return len(self.history)

    def rollback(self, snapshot: int) -> None:
        if snapshot < 0 or snapshot > len(self.history):
            raise ValueError("invalid rollback snapshot")
        while len(self.history) > snapshot:
            child, root, old_size = self.history.pop()
            if child is None or root is None:
                continue
            self.parent[child] = child
            self.size[root] = old_size

    def connected(self, a: Node, b: Node) -> bool:
        return self.find(a) == self.find(b)


Operation = tuple[str, Node, Node]


def offline_dynamic_connectivity(
    operations: Sequence[Operation[Node]],
) -> list[bool]:
    """Answer add/remove/query connectivity operations offline.

    Operations are ("add", u, v), ("remove", u, v), and ("query", u, v).
    A segment tree stores the time intervals over which each undirected edge is
    active; rollback DSU makes each DFS branch reversible. Complexity is
    O((Q + I) log Q log V) in this compact implementation.
    """
    total = len(operations)
    if total == 0:
        return []

    def edge_key(u: Node, v: Node) -> frozenset[Node]:
        if u == v:
            return frozenset((u,))
        return frozenset((u, v))

    endpoints: dict[frozenset[Node], tuple[Node, Node]] = {}
    active: dict[frozenset[Node], int] = {}
    intervals: list[tuple[int, int, tuple[Node, Node]]] = []
    vertices: set[Node] = set()

    for t, (kind, u, v) in enumerate(operations):
        vertices.update((u, v))
        key = edge_key(u, v)
        endpoints.setdefault(key, (u, v))
        if kind == "add":
            if key in active:
                raise ValueError("edge added twice without removal")
            active[key] = t
        elif kind == "remove":
            if key not in active:
                raise ValueError("removing an inactive edge")
            intervals.append((active.pop(key), t, endpoints[key]))
        elif kind != "query":
            raise ValueError(f"unknown operation kind: {kind!r}")

    for key, start in active.items():
        intervals.append((start, total, endpoints[key]))

    tree: list[list[tuple[Node, Node]]] = [[] for _ in range(4 * total)]

    def add_interval(
        idx: int,
        left: int,
        right: int,
        ql: int,
        qr: int,
        edge: tuple[Node, Node],
    ) -> None:
        if ql >= right or qr <= left:
            return
        if ql <= left and right <= qr:
            tree[idx].append(edge)
            return
        mid = (left + right) // 2
        add_interval(idx * 2, left, mid, ql, qr, edge)
        add_interval(idx * 2 + 1, mid, right, ql, qr, edge)

    for start, end, edge in intervals:
        if start < end:
            add_interval(1, 0, total, start, end, edge)

    dsu = RollbackDisjointSet(vertices)
    answers: list[bool] = []

    def solve(idx: int, left: int, right: int) -> None:
        snap = dsu.snapshot()
        for u, v in tree[idx]:
            dsu.union(u, v)

        if right - left == 1:
            kind, u, v = operations[left]
            if kind == "query":
                answers.append(dsu.connected(u, v))
        else:
            mid = (left + right) // 2
            solve(idx * 2, left, mid)
            solve(idx * 2 + 1, mid, right)

        dsu.rollback(snap)

    solve(1, 0, total)
    return answers
