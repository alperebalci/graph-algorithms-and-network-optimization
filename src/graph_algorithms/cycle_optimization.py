from __future__ import annotations

import math
from collections.abc import Hashable, Iterable, Sequence
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Edge = tuple[Node, Node, float]


def minimum_cycle_mean(
    vertices: Iterable[Node],
    edges: Sequence[Edge[Node]],
) -> float | None:
    """Karp minimum mean-weight directed cycle algorithm. O(VE)."""
    nodes = list(dict.fromkeys(vertices))
    incoming: dict[Node, list[tuple[Node, float]]] = {
        v: [] for v in nodes
    }
    for u, v, w in edges:
        if u not in incoming:
            incoming[u] = []
            nodes.append(u)
        if v not in incoming:
            incoming[v] = []
            nodes.append(v)
        incoming[v].append((u, float(w)))

    n = len(nodes)
    if n == 0:
        return None
    index = {v: i for i, v in enumerate(nodes)}
    dp = [[math.inf] * n for _ in range(n + 1)]
    for i in range(n):
        dp[0][i] = 0.0

    for k in range(1, n + 1):
        for v in nodes:
            vi = index[v]
            for u, weight in incoming.get(v, ()):
                candidate = dp[k - 1][index[u]] + weight
                if candidate < dp[k][vi]:
                    dp[k][vi] = candidate

    answer = math.inf
    for v in nodes:
        vi = index[v]
        if math.isinf(dp[n][vi]):
            continue
        worst = -math.inf
        for k in range(n):
            if math.isinf(dp[k][vi]):
                continue
            worst = max(
                worst,
                (dp[n][vi] - dp[k][vi]) / (n - k),
            )
        if worst > -math.inf:
            answer = min(answer, worst)

    return None if math.isinf(answer) else answer
