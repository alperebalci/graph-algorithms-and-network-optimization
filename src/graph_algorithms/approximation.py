from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Iterable, Mapping, Sequence
from functools import lru_cache
from typing import TypeVar

from .exceptions import InvalidGraphError
from .spanning_trees import prim

Node = TypeVar("Node", bound=Hashable)
DistanceMatrix = Mapping[Node, Mapping[Node, float]]


def _validate_complete_metric(distance: DistanceMatrix[Node]) -> list[Node]:
    nodes = list(distance)
    for u in nodes:
        if u not in distance[u] or abs(float(distance[u][u])) > 1e-12:
            raise InvalidGraphError("metric matrix must contain zero diagonal entries")
        for v in nodes:
            if v not in distance[u]:
                raise InvalidGraphError("distance matrix must be complete")
            if float(distance[u][v]) < 0:
                raise InvalidGraphError("metric distances must be non-negative")
            if abs(float(distance[u][v]) - float(distance[v][u])) > 1e-9:
                raise InvalidGraphError("metric TSP requires symmetric distances")
    for u in nodes:
        for v in nodes:
            for w in nodes:
                if (
                    float(distance[u][w])
                    > float(distance[u][v]) + float(distance[v][w]) + 1e-9
                ):
                    raise InvalidGraphError("triangle inequality violated")
    return nodes


def tour_cost(distance: DistanceMatrix[Node], tour: Sequence[Node]) -> float:
    if len(tour) < 2:
        return 0.0
    return sum(
        float(distance[tour[i]][tour[i + 1]]) for i in range(len(tour) - 1)
    )


def metric_tsp_2approx(
    distance: DistanceMatrix[Node],
    start: Node | None = None,
    *,
    validate_metric: bool = True,
) -> tuple[float, list[Node]]:
    """Double-tree 2-approximation for metric TSP via MST preorder traversal."""
    nodes = _validate_complete_metric(distance) if validate_metric else list(distance)
    if not nodes:
        return 0.0, []
    if start is None:
        start = nodes[0]
    graph = {
        u: [(v, float(distance[u][v])) for v in nodes if v != u] for u in nodes
    }
    _, mst_edges = prim(graph, start)
    tree: dict[Node, list[Node]] = {u: [] for u in nodes}
    for u, v, _ in mst_edges:
        tree[u].append(v)
        tree[v].append(u)

    preorder: list[Node] = []
    stack: list[tuple[Node, Node | None]] = [(start, None)]
    while stack:
        u, parent = stack.pop()
        preorder.append(u)
        for v in reversed(tree[u]):
            if v != parent:
                stack.append((v, u))
    tour = preorder + [start]
    return tour_cost(distance, tour), tour


def _minimum_weight_perfect_matching_dp(
    vertices: Sequence[Node], distance: DistanceMatrix[Node]
) -> list[tuple[Node, Node]]:
    """Exact MWPM via subset DP; exponential, used to keep Christofides self-contained."""
    if len(vertices) % 2:
        raise ValueError("perfect matching requires an even number of vertices")
    verts = tuple(vertices)
    n = len(verts)

    @lru_cache(maxsize=None)
    def solve(mask: int) -> tuple[float, tuple[tuple[int, int], ...]]:
        if mask == 0:
            return 0.0, ()
        i = (mask & -mask).bit_length() - 1
        best_cost = float("inf")
        best_pairs: tuple[tuple[int, int], ...] = ()
        remaining = mask & ~(1 << i)
        jmask = remaining
        while jmask:
            j = (jmask & -jmask).bit_length() - 1
            rest = remaining & ~(1 << j)
            sub_cost, sub_pairs = solve(rest)
            cost = float(distance[verts[i]][verts[j]]) + sub_cost
            if cost < best_cost:
                best_cost = cost
                best_pairs = ((i, j),) + sub_pairs
            jmask &= jmask - 1
        return best_cost, best_pairs

    _, pairs = solve((1 << n) - 1)
    return [(verts[i], verts[j]) for i, j in pairs]


def christofides_tsp(
    distance: DistanceMatrix[Node],
    start: Node | None = None,
    *,
    validate_metric: bool = True,
) -> tuple[float, list[Node]]:
    """Christofides' 1.5-approximation for metric TSP.

    The minimum-weight perfect matching step is implemented with exact subset DP to
    avoid a heavyweight dependency. The approximation guarantee is preserved, but
    this implementation is exponential in the number of odd-degree MST vertices and
    is therefore intended for educational/small benchmark instances.
    """
    nodes = _validate_complete_metric(distance) if validate_metric else list(distance)
    if not nodes:
        return 0.0, []
    if len(nodes) == 1:
        return 0.0, [nodes[0], nodes[0]]
    if start is None:
        start = nodes[0]

    graph = {
        u: [(v, float(distance[u][v])) for v in nodes if v != u] for u in nodes
    }
    _, mst_edges = prim(graph, start)
    degree = Counter()
    for u, v, _ in mst_edges:
        degree[u] += 1
        degree[v] += 1
    odd = [u for u in nodes if degree[u] % 2 == 1]
    matching = _minimum_weight_perfect_matching_dp(odd, distance)

    multiedges: list[tuple[Node, Node]] = [
        (u, v) for u, v, _ in mst_edges
    ] + matching
    adj: dict[Node, list[tuple[Node, int]]] = {u: [] for u in nodes}
    for eid, (u, v) in enumerate(multiedges):
        adj[u].append((v, eid))
        adj[v].append((u, eid))

    used: set[int] = set()
    stack: list[Node] = [start]
    circuit: list[Node] = []
    positions = {u: 0 for u in nodes}
    while stack:
        u = stack[-1]
        while positions[u] < len(adj[u]) and adj[u][positions[u]][1] in used:
            positions[u] += 1
        if positions[u] == len(adj[u]):
            circuit.append(stack.pop())
        else:
            v, eid = adj[u][positions[u]]
            positions[u] += 1
            if eid in used:
                continue
            used.add(eid)
            stack.append(v)
    circuit.reverse()

    seen: set[Node] = set()
    tour: list[Node] = []
    for u in circuit:
        if u not in seen:
            seen.add(u)
            tour.append(u)
    tour.append(tour[0])
    return tour_cost(distance, tour), tour


def greedy_set_cover(
    universe: Iterable[Node], subsets: Mapping[Node, Iterable[Node]]
) -> tuple[list[Node], set[Node]]:
    """Greedy H_n-approximation for Set Cover. Set Cover is not graph-specific."""
    uncovered = set(universe)
    normalized = {name: set(values) for name, values in subsets.items()}
    chosen: list[Node] = []
    while uncovered:
        best = None
        best_gain: set[Node] = set()
        for name, values in normalized.items():
            gain = values & uncovered
            if len(gain) > len(best_gain):
                best = name
                best_gain = gain
        if best is None or not best_gain:
            break
        chosen.append(best)
        uncovered -= best_gain
    return chosen, uncovered
