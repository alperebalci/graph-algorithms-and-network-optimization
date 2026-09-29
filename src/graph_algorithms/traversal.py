from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def _neighbors(graph: Graph[Node], node: Node) -> Iterable[Node]:
    return graph.get(node, ())


def bfs_order(graph: Graph[Node], start: Node) -> list[Node]:
    """Return nodes in breadth-first visitation order. O(V+E)."""
    seen = {start}
    queue: deque[Node] = deque([start])
    order: list[Node] = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in _neighbors(graph, node):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order


def dfs_order(graph: Graph[Node], start: Node) -> list[Node]:
    """Return nodes in iterative depth-first visitation order. O(V+E)."""
    seen: set[Node] = set()
    stack: list[Node] = [start]
    order: list[Node] = []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        neighbors = list(_neighbors(graph, node))
        stack.extend(reversed(neighbors))
    return order


def iterative_deepening_path(
    graph: Graph[Node], start: Node, goal: Node, max_depth: int
) -> list[Node] | None:
    """Find a path with iterative-deepening DFS up to max_depth edges."""
    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")

    def dls(node: Node, depth: int, path: list[Node], on_path: set[Node]) -> list[Node] | None:
        if node == goal:
            return path.copy()
        if depth == 0:
            return None
        for nxt in _neighbors(graph, node):
            if nxt in on_path:
                continue
            on_path.add(nxt)
            path.append(nxt)
            found = dls(nxt, depth - 1, path, on_path)
            if found is not None:
                return found
            path.pop()
            on_path.remove(nxt)
        return None

    for limit in range(max_depth + 1):
        found = dls(start, limit, [start], {start})
        if found is not None:
            return found
    return None


def bidirectional_bfs_path(graph: Graph[Node], start: Node, goal: Node) -> list[Node] | None:
    """Shortest path in an unweighted undirected graph using two BFS frontiers."""
    if start == goal:
        return [start]

    front_a = {start}
    front_b = {goal}
    parent_a: dict[Node, Node | None] = {start: None}
    parent_b: dict[Node, Node | None] = {goal: None}

    def expand(
        frontier: set[Node],
        own_parent: dict[Node, Node | None],
        other_parent: dict[Node, Node | None],
    ) -> tuple[set[Node], Node | None]:
        nxt_front: set[Node] = set()
        for node in frontier:
            for nxt in _neighbors(graph, node):
                if nxt in own_parent:
                    continue
                own_parent[nxt] = node
                if nxt in other_parent:
                    return nxt_front, nxt
                nxt_front.add(nxt)
        return nxt_front, None

    meeting: Node | None = None
    while front_a and front_b:
        if len(front_a) <= len(front_b):
            front_a, meeting = expand(front_a, parent_a, parent_b)
        else:
            front_b, meeting = expand(front_b, parent_b, parent_a)
        if meeting is not None:
            break

    if meeting is None:
        return None

    left: list[Node] = []
    cur: Node | None = meeting
    while cur is not None:
        left.append(cur)
        cur = parent_a[cur]
    left.reverse()

    right: list[Node] = []
    cur = parent_b[meeting]
    while cur is not None:
        right.append(cur)
        cur = parent_b[cur]
    return left + right
