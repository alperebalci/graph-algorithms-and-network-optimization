from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable


@dataclass
class _Node:
    key: Hashable
    value: float = 0.0
    total: float = 0.0
    left: "_Node | None" = None
    right: "_Node | None" = None
    parent: "_Node | None" = None
    reversed: bool = False

    def __post_init__(self) -> None:
        self.total = float(self.value)


class LinkCutTree:
    """Splay-based link-cut tree for a dynamic forest.

    Supports link, cut, connectivity, vertex-value updates, and path sums in
    amortized O(log V) time per operation.
    """

    def __init__(self) -> None:
        self.nodes: dict[Hashable, _Node] = {}

    def add(self, key: Hashable, value: float = 0.0) -> None:
        if key in self.nodes:
            raise ValueError(f"duplicate node: {key!r}")
        self.nodes[key] = _Node(key=key, value=float(value))

    def _node(self, key: Hashable) -> _Node:
        if key not in self.nodes:
            raise KeyError(key)
        return self.nodes[key]

    @staticmethod
    def _is_aux_root(x: _Node) -> bool:
        p = x.parent
        return p is None or (p.left is not x and p.right is not x)

    @staticmethod
    def _sum(x: _Node | None) -> float:
        return 0.0 if x is None else x.total

    def _update(self, x: _Node) -> None:
        x.total = x.value + self._sum(x.left) + self._sum(x.right)

    def _push(self, x: _Node) -> None:
        if not x.reversed:
            return
        x.left, x.right = x.right, x.left
        if x.left is not None:
            x.left.reversed = not x.left.reversed
        if x.right is not None:
            x.right.reversed = not x.right.reversed
        x.reversed = False

    def _push_path(self, x: _Node) -> None:
        stack = [x]
        y = x
        while not self._is_aux_root(y):
            assert y.parent is not None
            y = y.parent
            stack.append(y)
        while stack:
            self._push(stack.pop())

    def _rotate(self, x: _Node) -> None:
        p = x.parent
        assert p is not None
        g = p.parent

        if p.left is x:
            p.left = x.right
            if x.right is not None:
                x.right.parent = p
            x.right = p
        else:
            p.right = x.left
            if x.left is not None:
                x.left.parent = p
            x.left = p

        p.parent = x
        x.parent = g
        if g is not None:
            if g.left is p:
                g.left = x
            elif g.right is p:
                g.right = x

        self._update(p)
        self._update(x)

    def _splay(self, x: _Node) -> None:
        self._push_path(x)
        while not self._is_aux_root(x):
            p = x.parent
            assert p is not None
            if not self._is_aux_root(p):
                g = p.parent
                assert g is not None
                if (g.left is p) == (p.left is x):
                    self._rotate(p)
                else:
                    self._rotate(x)
            self._rotate(x)

    def _access(self, x: _Node) -> None:
        last: _Node | None = None
        y: _Node | None = x
        while y is not None:
            self._splay(y)
            y.right = last
            self._update(y)
            last = y
            y = y.parent
        self._splay(x)

    def _make_root(self, x: _Node) -> None:
        self._access(x)
        x.reversed = not x.reversed
        self._push(x)

    def _find_root(self, x: _Node) -> _Node:
        self._access(x)
        while True:
            self._push(x)
            if x.left is None:
                break
            x = x.left
        self._splay(x)
        return x

    def connected(self, a: Hashable, b: Hashable) -> bool:
        x, y = self._node(a), self._node(b)
        return self._find_root(x) is self._find_root(y)

    def link(self, child: Hashable, parent: Hashable) -> None:
        x, y = self._node(child), self._node(parent)
        self._make_root(x)
        if self._find_root(y) is x:
            raise ValueError("link would create a cycle")
        x.parent = y

    def cut(self, a: Hashable, b: Hashable) -> None:
        x, y = self._node(a), self._node(b)
        self._make_root(x)
        self._access(y)
        if y.left is not x or x.right is not None:
            raise ValueError("specified nodes are not joined by a direct tree edge")
        y.left.parent = None
        y.left = None
        self._update(y)

    def set_value(self, key: Hashable, value: float) -> None:
        x = self._node(key)
        self._access(x)
        x.value = float(value)
        self._update(x)

    def path_sum(self, a: Hashable, b: Hashable) -> float:
        x, y = self._node(a), self._node(b)
        self._make_root(x)
        if self._find_root(y) is not x:
            raise ValueError("nodes are in different trees")
        self._make_root(x)
        self._access(y)
        return y.total
