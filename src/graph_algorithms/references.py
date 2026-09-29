from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import Any, TypeVar

Node = TypeVar("Node", bound=Hashable)


def weighted_blossom_matching_reference(
    graph: Mapping[Node, Iterable[tuple[Node, float]]],
    *,
    max_cardinality: bool = False,
) -> set[tuple[Node, Node]]:
    """Maximum-weight general matching via NetworkX's blossom implementation."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g = nx.Graph()
    for u, neighbors in graph.items():
        g.add_node(u)
        for v, weight in neighbors:
            g.add_edge(u, v, weight=float(weight))
    return set(
        nx.max_weight_matching(
            g,
            maxcardinality=max_cardinality,
            weight="weight",
        )
    )


def vf2pp_isomorphism_reference(
    graph1: Mapping[Node, Iterable[Node]],
    graph2: Mapping[Node, Iterable[Node]],
    *,
    labels1: Mapping[Node, Any] | None = None,
    labels2: Mapping[Node, Any] | None = None,
) -> dict[Node, Node] | None:
    """VF2++ graph-isomorphism mapping through NetworkX 3.2+."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g1 = nx.Graph()
    g2 = nx.Graph()
    for u, neighbors in graph1.items():
        g1.add_node(u)
        for v in neighbors:
            g1.add_edge(u, v)
    for u, neighbors in graph2.items():
        g2.add_node(u)
        for v in neighbors:
            g2.add_edge(u, v)

    node_label = None
    if labels1 is not None or labels2 is not None:
        node_label = "_label"
        for u in g1:
            g1.nodes[u][node_label] = None if labels1 is None else labels1.get(u)
        for u in g2:
            g2.nodes[u][node_label] = None if labels2 is None else labels2.get(u)

    return nx.vf2pp_isomorphism(g1, g2, node_label=node_label)


def network_simplex_reference(
    capacity: Mapping[Node, Mapping[Node, float]],
    cost: Mapping[Node, Mapping[Node, float]],
    demands: Mapping[Node, float],
) -> tuple[float, dict[Node, dict[Node, float]]]:
    """Minimum-cost flow with node demands through NetworkX network simplex."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g = nx.DiGraph()
    nodes = set(capacity) | set(demands)
    for neighbors in capacity.values():
        nodes.update(neighbors)
    for u in nodes:
        g.add_node(u, demand=float(demands.get(u, 0.0)))
    for u, neighbors in capacity.items():
        for v, cap in neighbors.items():
            if u not in cost or v not in cost[u]:
                raise ValueError(f"missing cost for edge {u!r}->{v!r}")
            g.add_edge(
                u,
                v,
                capacity=float(cap),
                weight=float(cost[u][v]),
            )

    total_cost, flow = nx.network_simplex(g)
    return float(total_cost), {
        u: {v: float(value) for v, value in neighbors.items()}
        for u, neighbors in flow.items()
    }


def louvain_communities_reference(
    graph: Mapping[Node, Iterable[tuple[Node, float]]],
    *,
    resolution: float = 1.0,
    seed: int | None = None,
) -> list[set[Node]]:
    """Louvain modularity communities through NetworkX."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g = nx.Graph()
    for u, neighbors in graph.items():
        g.add_node(u)
        for v, weight in neighbors:
            g.add_edge(u, v, weight=float(weight))
    return [
        set(c)
        for c in nx.community.louvain_communities(
            g,
            weight="weight",
            resolution=resolution,
            seed=seed,
        )
    ]


def leiden_communities_reference(
    graph: Mapping[Node, Iterable[tuple[Node, float]]],
    *,
    resolution: float = 1.0,
    seed: int | None = None,
) -> list[set[Node]]:
    """Leiden communities through optional igraph + leidenalg dependencies."""
    try:
        import igraph as ig
        import leidenalg
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[community]"
        ) from exc

    nodes: list[Node] = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v, _ in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    index = {u: i for i, u in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    weights: list[float] = []
    added: set[frozenset[Node]] = set()

    for u, neighbors in graph.items():
        for v, weight in neighbors:
            key = frozenset((u, v))
            if key in added or u == v:
                continue
            added.add(key)
            edges.append((index[u], index[v]))
            weights.append(float(weight))

    ig_graph = ig.Graph(n=len(nodes), edges=edges, directed=False)
    partition = leidenalg.find_partition(
        ig_graph,
        leidenalg.RBConfigurationVertexPartition,
        weights=weights,
        resolution_parameter=resolution,
        seed=seed,
    )
    return [{nodes[i] for i in community} for community in partition]



def capacity_scaling_min_cost_reference(
    capacity: Mapping[Node, Mapping[Node, float]],
    cost: Mapping[Node, Mapping[Node, float]],
    demands: Mapping[Node, float],
) -> tuple[float, dict[Node, dict[Node, float]]]:
    """Capacity-scaling successive-shortest-path min-cost flow via NetworkX."""
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g = nx.DiGraph()
    nodes = set(capacity) | set(demands)
    for neighbors in capacity.values():
        nodes.update(neighbors)
    for u in nodes:
        g.add_node(u, demand=demands.get(u, 0))
    for u, neighbors in capacity.items():
        for v, cap in neighbors.items():
            if u not in cost or v not in cost[u]:
                raise ValueError(f"missing cost for edge {u!r}->{v!r}")
            g.add_edge(
                u,
                v,
                capacity=cap,
                weight=cost[u][v],
            )

    total_cost, flow = nx.capacity_scaling(g)
    return float(total_cost), {
        u: {v: float(value) for v, value in neighbors.items()}
        for u, neighbors in flow.items()
    }


def three_vertex_connected_components_reference(
    graph: Mapping[Node, Iterable[Node]],
) -> list[set[Node]]:
    """Exact 3-node-connected components via NetworkX k_components.

    This is a k-component decomposition, not an SPQR tree. SPQR additionally
    records the triconnected decomposition structure and virtual edges.
    """
    try:
        import networkx as nx
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "install graph-algorithms-network-optimization[reference]"
        ) from exc

    g = nx.Graph()
    for u, neighbors in graph.items():
        g.add_node(u)
        for v in neighbors:
            g.add_edge(u, v)

    components = nx.k_components(g)
    return [set(component) for component in components.get(3, [])]
