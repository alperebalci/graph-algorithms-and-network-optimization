from __future__ import annotations

import math
import random
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Mapping[Node, float]]


@dataclass(frozen=True)
class SpectralSparsifierResult:
    graph: dict[Hashable, dict[Hashable, float]]
    probabilities: dict[frozenset[Hashable], float]
    effective_resistances: dict[frozenset[Hashable], float]


def effective_resistance_sparsifier(
    graph: WeightedGraph[Node],
    *,
    epsilon: float = 0.5,
    oversampling: float = 8.0,
    seed: int | None = None,
) -> SpectralSparsifierResult:
    """Spielman-Srivastava-style effective-resistance edge sampling.

    Edge weights are interpreted as conductances. The implementation computes
    exact effective resistances using a dense Laplacian pseudoinverse, so it is
    intended for small/medium educational benchmarks rather than massive
    sparse graphs. Sampled edges are reweighted by 1/p.

    A sufficiently large oversampling constant gives the standard high-
    probability spectral approximation; this routine exposes the constant
    explicitly rather than hiding a problem-size-dependent engineering choice.
    """
    if not 0.0 < epsilon < 1.0:
        raise ValueError("epsilon must be in (0, 1)")
    if oversampling <= 0:
        raise ValueError("oversampling must be positive")
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[numerical]"
        ) from exc

    nodes: list[Hashable] = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    n = len(nodes)
    if n == 0:
        return SpectralSparsifierResult({}, {}, {})

    index = {u: i for i, u in enumerate(nodes)}
    edges: dict[
        frozenset[Hashable], tuple[Hashable, Hashable, float]
    ] = {}
    for u, neighbors in graph.items():
        for v, raw_weight in neighbors.items():
            weight = float(raw_weight)
            if weight < 0:
                raise ValueError("spectral sparsification requires non-negative weights")
            if u == v or weight == 0:
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

    laplacian = np.zeros((n, n), dtype=float)
    for u, v, weight in edges.values():
        i, j = index[u], index[v]
        laplacian[i, i] += weight
        laplacian[j, j] += weight
        laplacian[i, j] -= weight
        laplacian[j, i] -= weight

    pinv = np.linalg.pinv(laplacian, hermitian=True)
    resistances: dict[frozenset[Hashable], float] = {}
    probabilities: dict[frozenset[Hashable], float] = {}
    log_factor = math.log(max(2, n))

    for key, (u, v, weight) in edges.items():
        i, j = index[u], index[v]
        resistance = (
            pinv[i, i] + pinv[j, j] - 2.0 * pinv[i, j]
        )
        resistance = max(0.0, float(resistance))
        leverage = weight * resistance
        probability = min(
            1.0,
            oversampling * leverage * log_factor / (epsilon * epsilon),
        )
        resistances[key] = resistance
        probabilities[key] = probability

    rng = random.Random(seed)
    sparse = {u: {} for u in nodes}
    for key, (u, v, weight) in edges.items():
        p = probabilities[key]
        if p > 0 and rng.random() <= p:
            sampled_weight = weight / p
            sparse[u][v] = sampled_weight
            sparse[v][u] = sampled_weight

    return SpectralSparsifierResult(
        graph=sparse,
        probabilities=probabilities,
        effective_resistances=resistances,
    )
