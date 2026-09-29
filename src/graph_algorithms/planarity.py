from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from typing import Any, TypeVar

Node = TypeVar("Node", bound=Hashable)


def faces_from_rotation_system(
    rotation: Mapping[Node, Iterable[Node]]
) -> list[list[Node]]:
    """Enumerate faces from a planar rotation system / combinatorial embedding.

    rotation[u] gives the cyclic order of neighbors around u. Each directed edge
    (dart) belongs to exactly one face. The returned face walks include each
    boundary vertex once per encountered dart; the start vertex is not repeated.
    """
    rot = {u: list(nbrs) for u, nbrs in rotation.items()}
    position = {u: {v: i for i, v in enumerate(nbrs)} for u, nbrs in rot.items()}
    darts = {(u, v) for u, nbrs in rot.items() for v in nbrs}
    for u, v in list(darts):
        if v not in rot or u not in position[v]:
            raise ValueError(
                "rotation system must contain both directions of every edge"
            )

    visited: set[tuple[Node, Node]] = set()
    faces: list[list[Node]] = []
    for start in darts:
        if start in visited:
            continue
        face: list[Node] = []
        dart = start
        while dart not in visited:
            visited.add(dart)
            u, v = dart
            face.append(u)
            nbrs = rot[v]
            idx = position[v][u]
            w = nbrs[(idx - 1) % len(nbrs)]
            dart = (v, w)
        faces.append(face)
    return faces


def is_planar_boyer_myrvold(graph: Mapping[Node, Iterable[Node]]) -> bool:
    """Planarity test through NetworkX's Boyer-Myrvold implementation.

    This is deliberately an optional reference adapter rather than a
    reimplementation of the sophisticated linear-time planarity machinery.
    """
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc
    g = nx.Graph()
    for u, nbrs in graph.items():
        for v in nbrs:
            g.add_edge(u, v)
    planar, _ = nx.check_planarity(g, counterexample=False)
    return bool(planar)


def planar_embedding(
    graph: Mapping[Node, Iterable[Node]]
) -> dict[Node, list[Node]]:
    """Return a planar rotation system using NetworkX; raises if non-planar."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc
    g = nx.Graph()
    for u, nbrs in graph.items():
        for v in nbrs:
            g.add_edge(u, v)
    planar, embedding = nx.check_planarity(g, counterexample=False)
    if not planar:
        raise ValueError("graph is not planar")
    result: dict[Any, list[Any]] = {}
    for u in embedding:
        result[u] = list(embedding.neighbors_cw_order(u))
    return result
