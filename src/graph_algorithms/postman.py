from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from functools import lru_cache
from typing import TypeVar

from .eulerian import hierholzer_eulerian_path
from .shortest_paths import dijkstra, reconstruct_path

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


@dataclass(frozen=True)
class ChinesePostmanResult:
    value: float
    circuit: tuple[Hashable, ...]
    duplicated_paths: tuple[tuple[Hashable, ...], ...]


def undirected_chinese_postman(
    graph: WeightedGraph[Node],
    *,
    start: Node | None = None,
) -> ChinesePostmanResult:
    """Exact small-instance undirected Chinese Postman / route inspection."""
    nodes = list(graph)
    seen = set(nodes)
    edges: dict[frozenset[Node], tuple[Node, Node, float]] = {}

    for u, neighbors in graph.items():
        for v, raw_weight in neighbors:
            weight = float(raw_weight)
            if weight < 0:
                raise ValueError("Chinese Postman requires non-negative weights")
            if v not in seen:
                seen.add(v)
                nodes.append(v)
            if u == v:
                continue
            key = frozenset((u, v))
            if key in edges:
                _, _, old = edges[key]
                if abs(old - weight) > 1e-9:
                    raise ValueError(
                        "symmetric entries of an undirected edge must agree"
                    )
            else:
                edges[key] = (u, v, weight)

    if not edges:
        if start is None:
            return ChinesePostmanResult(0.0, (), ())
        if start not in seen:
            raise KeyError(start)
        return ChinesePostmanResult(0.0, (start,), ())

    degree = {u: 0 for u in nodes}
    unweighted: list[tuple[Node, Node]] = []
    original_cost = 0.0
    for u, v, weight in edges.values():
        degree[u] += 1
        degree[v] += 1
        unweighted.append((u, v))
        original_cost += weight

    active = {u for u in nodes if degree[u] > 0}
    seed = next(iter(active))
    dist0, _ = dijkstra(graph, seed)
    if not active <= set(dist0):
        raise ValueError("graph edges must form one connected component")

    odd = [u for u in nodes if degree[u] % 2 == 1]
    odd_dist: dict[Node, dict[Node, float]] = {}
    odd_prev: dict[Node, dict[Node, Node | None]] = {}
    for u in odd:
        dist, prev = dijkstra(graph, u)
        odd_dist[u] = dist
        odd_prev[u] = prev

    odd_tuple = tuple(odd)
    n = len(odd_tuple)

    @lru_cache(maxsize=None)
    def matching(mask: int) -> tuple[
        float,
        tuple[tuple[int, int], ...],
    ]:
        if mask == 0:
            return 0.0, ()
        i = (mask & -mask).bit_length() - 1
        remaining = mask & ~(1 << i)
        best = float("inf")
        best_pairs: tuple[tuple[int, int], ...] = ()
        candidates = remaining
        while candidates:
            j = (candidates & -candidates).bit_length() - 1
            rest = remaining & ~(1 << j)
            subcost, pairs = matching(rest)
            candidate = odd_dist[odd_tuple[i]][odd_tuple[j]] + subcost
            if candidate < best:
                best = candidate
                best_pairs = ((i, j),) + pairs
            candidates &= candidates - 1
        return best, best_pairs

    matching_cost, pairs = matching((1 << n) - 1)
    duplicated_paths: list[tuple[Hashable, ...]] = []
    multiedges = list(unweighted)

    for i, j in pairs:
        u, v = odd_tuple[i], odd_tuple[j]
        path = reconstruct_path(odd_prev[u], u, v)
        if path is None:
            raise AssertionError("odd-vertex shortest path disappeared")
        duplicated_paths.append(tuple(path))
        multiedges.extend(zip(path, path[1:]))

    circuit = hierholzer_eulerian_path(multiedges, directed=False)
    if start is not None:
        if start not in circuit:
            raise KeyError(start)
        base = circuit[:-1]
        index = base.index(start)
        base = base[index:] + base[:index]
        circuit = base + [start]

    return ChinesePostmanResult(
        value=original_cost + matching_cost,
        circuit=tuple(circuit),
        duplicated_paths=tuple(duplicated_paths),
    )
