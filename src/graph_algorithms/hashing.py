from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Hashable, Iterable, Mapping
from typing import Any, TypeVar

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


def weisfeiler_lehman_refinement(
    graph: Graph[Node],
    *,
    iterations: int = 3,
    node_labels: Mapping[Node, Any] | None = None,
) -> dict[Node, str]:
    """1-dimensional Weisfeiler-Lehman color refinement.

    The returned colors are deterministic hashes of the refinement classes.
    Equal colors are useful as isomorphism invariants but do not constitute a
    complete isomorphism test.
    """
    if iterations < 0:
        raise ValueError("iterations must be non-negative")

    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)

    adjacency = {u: list(graph.get(u, ())) for u in nodes}
    if node_labels is None:
        labels = {u: f"d:{len(adjacency[u])}" for u in nodes}
    else:
        labels = {u: f"l:{node_labels.get(u)!r}" for u in nodes}

    def digest(text: str) -> str:
        return hashlib.blake2b(
            text.encode("utf-8"), digest_size=16
        ).hexdigest()

    for _ in range(iterations):
        signatures = {}
        for u in nodes:
            neighbor_labels = sorted(labels[v] for v in adjacency[u])
            signatures[u] = labels[u] + "|" + "|".join(neighbor_labels)

        # Canonicalize equal signatures before hashing so equality classes are
        # independent of Python object identity and vertex names.
        unique = {
            signature: digest(signature)
            for signature in set(signatures.values())
        }
        labels = {u: unique[signatures[u]] for u in nodes}
    return labels


def weisfeiler_lehman_graph_hash(
    graph: Graph[Node],
    *,
    iterations: int = 3,
    node_labels: Mapping[Node, Any] | None = None,
) -> str:
    """Graph-level 1-WL hash built from refinement histograms."""
    if iterations < 0:
        raise ValueError("iterations must be non-negative")

    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    adjacency = {u: list(graph.get(u, ())) for u in nodes}

    if node_labels is None:
        labels = {u: f"d:{len(adjacency[u])}" for u in nodes}
    else:
        labels = {u: f"l:{node_labels.get(u)!r}" for u in nodes}

    history: list[str] = []

    def h(text: str) -> str:
        return hashlib.blake2b(
            text.encode("utf-8"), digest_size=16
        ).hexdigest()

    for _ in range(iterations + 1):
        counts = Counter(labels.values())
        history.append(
            ";".join(
                f"{label}:{count}"
                for label, count in sorted(counts.items())
            )
        )
        signatures = {
            u: labels[u]
            + "|"
            + "|".join(sorted(labels[v] for v in adjacency[u]))
            for u in nodes
        }
        labels = {u: h(signatures[u]) for u in nodes}

    return h("||".join(history))
