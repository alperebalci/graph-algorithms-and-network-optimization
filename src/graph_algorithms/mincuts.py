from __future__ import annotations

import math
import random
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
WeightedUndirectedGraph = Mapping[Node, Mapping[Node, float]]
EPS = 1e-12


@dataclass(frozen=True)
class GlobalMinCutResult:
    value: float
    left: frozenset[Hashable]
    right: frozenset[Hashable]


def _normalize(
    graph: WeightedUndirectedGraph[Node],
) -> tuple[list[Hashable], dict[Hashable, dict[Hashable, float]]]:
    nodes: list[Hashable] = []
    seen: set[Hashable] = set()

    def remember(u: Hashable) -> None:
        if u not in seen:
            seen.add(u)
            nodes.append(u)

    edge_values: dict[frozenset[Hashable], tuple[Hashable, Hashable, float]] = {}
    for u, neighbors in graph.items():
        remember(u)
        for v, raw_weight in neighbors.items():
            remember(v)
            weight = float(raw_weight)
            if weight < -EPS:
                raise ValueError("min-cut capacities must be non-negative")
            if u == v:
                continue
            key = frozenset((u, v))
            if key in edge_values:
                _, _, old = edge_values[key]
                if abs(old - weight) > 1e-9:
                    raise ValueError(
                        "symmetric entries of an undirected edge must agree"
                    )
            else:
                edge_values[key] = (u, v, max(0.0, weight))

    adjacency = {u: {} for u in nodes}
    for u, v, weight in edge_values.values():
        adjacency[u][v] = adjacency[u].get(v, 0.0) + weight
        adjacency[v][u] = adjacency[v].get(u, 0.0) + weight
    return nodes, adjacency


def stoer_wagner_min_cut(
    graph: WeightedUndirectedGraph[Node],
) -> GlobalMinCutResult:
    """Deterministic global minimum cut in an undirected weighted graph.

    This direct maximum-adjacency-search implementation runs in O(V^3).
    """
    nodes, adjacency = _normalize(graph)
    if len(nodes) < 2:
        raise ValueError("global min-cut requires at least two vertices")

    active = list(nodes)
    groups: dict[Hashable, set[Hashable]] = {u: {u} for u in nodes}
    best_value = math.inf
    best_left: set[Hashable] | None = None

    while len(active) > 1:
        used: set[Hashable] = set()
        weights = {u: 0.0 for u in active}
        previous: Hashable | None = None

        for i in range(len(active)):
            candidates = [u for u in active if u not in used]
            selected = max(candidates, key=lambda u: weights[u])
            used.add(selected)

            if i == len(active) - 1:
                cut_value = weights[selected]
                if cut_value < best_value:
                    best_value = cut_value
                    best_left = set(groups[selected])

                assert previous is not None
                for v in list(active):
                    if v in (previous, selected):
                        continue
                    merged_weight = (
                        adjacency[previous].get(v, 0.0)
                        + adjacency[selected].get(v, 0.0)
                    )
                    if merged_weight > EPS:
                        adjacency[previous][v] = merged_weight
                        adjacency[v][previous] = merged_weight
                    else:
                        adjacency[previous].pop(v, None)
                        adjacency[v].pop(previous, None)
                    adjacency[v].pop(selected, None)

                groups[previous].update(groups[selected])
                adjacency[previous].pop(selected, None)
                adjacency.pop(selected, None)
                groups.pop(selected, None)
                active.remove(selected)
                break

            previous = selected
            for v, weight in adjacency[selected].items():
                if v in weights and v not in used:
                    weights[v] += weight

    assert best_left is not None
    all_nodes = set(nodes)
    return GlobalMinCutResult(
        value=best_value,
        left=frozenset(best_left),
        right=frozenset(all_nodes - best_left),
    )


def _exact_cut_on_state(
    groups: dict[int, set[Hashable]],
    edges: list[tuple[int, int, float]],
) -> GlobalMinCutResult:
    ids = list(groups)
    if len(ids) < 2:
        raise ValueError("cut state requires at least two supernodes")
    first = ids[0]
    best = math.inf
    best_side: set[int] | None = None
    remaining = ids[1:]

    for mask in range(1 << len(remaining)):
        side = {first}
        for i, node in enumerate(remaining):
            if mask & (1 << i):
                side.add(node)
        if len(side) == len(ids):
            continue
        value = sum(
            weight
            for u, v, weight in edges
            if (u in side) != (v in side)
        )
        if value < best:
            best = value
            best_side = side

    assert best_side is not None
    left = set().union(*(groups[u] for u in best_side))
    right = set().union(*(groups[u] for u in ids if u not in best_side))
    return GlobalMinCutResult(best, frozenset(left), frozenset(right))


def _contract_to(
    groups: dict[int, set[Hashable]],
    edges: list[tuple[int, int, float]],
    target: int,
    rng: random.Random,
) -> tuple[dict[int, set[Hashable]], list[tuple[int, int, float]]]:
    groups = {u: set(values) for u, values in groups.items()}
    edges = list(edges)

    while len(groups) > target:
        positive = [(u, v, w) for u, v, w in edges if w > EPS and u != v]
        if not positive:
            break
        total = sum(w for _, _, w in positive)
        pick = rng.random() * total
        acc = 0.0
        a = b = -1
        for u, v, w in positive:
            acc += w
            if acc >= pick:
                a, b = u, v
                break

        groups[a].update(groups.pop(b))
        new_edges: list[tuple[int, int, float]] = []
        for u, v, w in edges:
            if u == b:
                u = a
            if v == b:
                v = a
            if u != v:
                new_edges.append((u, v, w))
        edges = new_edges

    return groups, edges


def karger_stein_min_cut(
    graph: WeightedUndirectedGraph[Node],
    *,
    seed: int | None = None,
    trials: int = 8,
) -> GlobalMinCutResult:
    """Randomized Karger-Stein global minimum cut.

    Weighted capacities are interpreted as parallel-edge mass during random
    contractions. Small recursive states are solved exactly, making the
    implementation reproducible and robust for educational benchmarks.
    """
    if trials < 1:
        raise ValueError("trials must be at least 1")
    nodes, adjacency = _normalize(graph)
    if len(nodes) < 2:
        raise ValueError("global min-cut requires at least two vertices")

    index = {node: i for i, node in enumerate(nodes)}
    groups0 = {i: {node} for node, i in index.items()}
    edges0: list[tuple[int, int, float]] = []
    for i, u in enumerate(nodes):
        for v, weight in adjacency[u].items():
            if i < index[v]:
                edges0.append((i, index[v], weight))

    rng = random.Random(seed)

    def recurse(
        groups: dict[int, set[Hashable]],
        edges: list[tuple[int, int, float]],
    ) -> GlobalMinCutResult:
        n = len(groups)
        if n <= 6:
            return _exact_cut_on_state(groups, edges)
        target = math.ceil(n / math.sqrt(2.0)) + 1
        g1, e1 = _contract_to(groups, edges, target, rng)
        g2, e2 = _contract_to(groups, edges, target, rng)
        r1 = recurse(g1, e1)
        r2 = recurse(g2, e2)
        return r1 if r1.value <= r2.value else r2

    best: GlobalMinCutResult | None = None
    for _ in range(trials):
        result = recurse(groups0, edges0)
        if best is None or result.value < best.value:
            best = result
    assert best is not None
    return best
