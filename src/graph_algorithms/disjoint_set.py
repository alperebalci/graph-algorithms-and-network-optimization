from __future__ import annotations

from collections.abc import Iterable
from typing import Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class DisjointSet(Generic[T]):
    """Union-Find / DSU with path compression and union by rank."""

    def __init__(self, items: Iterable[T] = ()) -> None:
        self.parent: dict[T, T] = {}
        self.rank: dict[T, int] = {}
        for item in items:
            self.add(item)

    def add(self, item: T) -> None:
        if item not in self.parent:
            self.parent[item] = item
            self.rank[item] = 0

    def find(self, item: T) -> T:
        if item not in self.parent:
            self.add(item)
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            parent = self.parent[item]
            self.parent[item] = root
            item = parent
        return root

    def union(self, a: T, b: T) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
