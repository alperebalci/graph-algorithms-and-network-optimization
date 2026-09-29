from __future__ import annotations

import heapq
import math
from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


def bidirectional_dijkstra(
    graph: WeightedGraph[Node],
    reverse_graph: WeightedGraph[Node],
    source: Node,
    target: Node,
) -> tuple[float, list[Node]] | None:
    """Bidirectional Dijkstra for directed non-negative graphs.

    reverse_graph must contain every original edge reversed with the same weight.
    For undirected graphs it can be the same mapping as graph.
    """
    if source == target:
        return 0.0, [source]

    dist_f = {source: 0.0}
    dist_b = {target: 0.0}
    prev_f: dict[Node, Node | None] = {source: None}
    prev_b: dict[Node, Node | None] = {target: None}
    qf: list[tuple[float, int, Node]] = [(0.0, 0, source)]
    qb: list[tuple[float, int, Node]] = [(0.0, 0, target)]
    sf: set[Node] = set()
    sb: set[Node] = set()
    serial = 1
    best = math.inf
    meet: Node | None = None

    def relax(
        queue: list[tuple[float, int, Node]],
        own_dist: dict[Node, float],
        own_prev: dict[Node, Node | None],
        own_seen: set[Node],
        other_dist: dict[Node, float],
        adj: WeightedGraph[Node],
    ) -> tuple[float, Node | None]:
        nonlocal serial
        while queue:
            d, _, u = heapq.heappop(queue)
            if u in own_seen or d != own_dist.get(u):
                continue
            own_seen.add(u)
            candidate = d + other_dist.get(u, math.inf)
            local_best, local_meet = (
                candidate,
                u if candidate < math.inf else None,
            )
            for v, w in adj.get(u, ()):
                if w < 0:
                    raise ValueError(
                        "bidirectional Dijkstra requires non-negative weights"
                    )
                nd = d + w
                if nd < own_dist.get(v, math.inf):
                    own_dist[v] = nd
                    own_prev[v] = u
                    heapq.heappush(queue, (nd, serial, v))
                    serial += 1
                c = nd + other_dist.get(v, math.inf)
                if c < local_best:
                    local_best, local_meet = c, v
            return local_best, local_meet
        return math.inf, None

    while qf and qb:
        if qf[0][0] + qb[0][0] >= best:
            break
        if qf[0][0] <= qb[0][0]:
            candidate, node = relax(
                qf, dist_f, prev_f, sf, dist_b, graph
            )
        else:
            candidate, node = relax(
                qb, dist_b, prev_b, sb, dist_f, reverse_graph
            )
        if candidate < best:
            best, meet = candidate, node

    if meet is None:
        return None

    left: list[Node] = []
    cur: Node | None = meet
    while cur is not None:
        left.append(cur)
        cur = prev_f.get(cur)
    left.reverse()

    right: list[Node] = []
    cur = prev_b.get(meet)
    while cur is not None:
        right.append(cur)
        cur = prev_b.get(cur)
    return best, left + right
