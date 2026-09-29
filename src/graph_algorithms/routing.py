from __future__ import annotations

import heapq
import math
from collections.abc import Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TypeVar

from .shortest_paths import astar, dijkstra

Node = TypeVar("Node", bound=Hashable)
WeightedGraph = Mapping[Node, Iterable[tuple[Node, float]]]


@dataclass(frozen=True)
class LandmarkIndex:
    landmarks: tuple[Hashable, ...]
    distances: dict[Hashable, dict[Hashable, float]]


def build_landmark_index(
    graph: WeightedGraph[Node], landmarks: Sequence[Node]
) -> LandmarkIndex:
    """Precompute ALT landmark distances for an undirected non-negative graph."""
    if not landmarks:
        raise ValueError("at least one landmark is required")
    distances: dict[Hashable, dict[Hashable, float]] = {}
    for landmark in landmarks:
        dist, _ = dijkstra(graph, landmark)
        distances[landmark] = dict(dist)
    return LandmarkIndex(tuple(landmarks), distances)


def alt_shortest_path(
    graph: WeightedGraph[Node],
    source: Node,
    target: Node,
    index: LandmarkIndex,
) -> tuple[float, list[Node]] | None:
    """A* + landmarks + triangle inequality (ALT) for undirected graphs."""

    def heuristic(u: Node, goal: Node) -> float:
        bound = 0.0
        for landmark in index.landmarks:
            dist = index.distances[landmark]
            if u in dist and goal in dist:
                bound = max(bound, abs(dist[goal] - dist[u]))
        return bound

    return astar(graph, source, target, heuristic)


@dataclass(frozen=True)
class _CHEdge:
    u: Hashable
    v: Hashable
    weight: float
    left: int | None = None
    right: int | None = None


@dataclass
class ContractionHierarchy:
    """Naive but exact Contraction Hierarchy for non-negative directed graphs.

    Preprocessing uses an explicit contraction order and bounded Dijkstra
    witness searches. It favors inspectability over road-network-scale speed.
    """

    rank: dict[Hashable, int]
    edges: tuple[_CHEdge, ...]
    upward: dict[Hashable, tuple[tuple[Hashable, float, int], ...]]
    backward_upward: dict[
        Hashable, tuple[tuple[Hashable, float, int], ...]
    ]

    def _expand_edge(self, edge_id: int) -> list[tuple[Hashable, Hashable]]:
        edge = self.edges[edge_id]
        if edge.left is None or edge.right is None:
            return [(edge.u, edge.v)]
        return self._expand_edge(edge.left) + self._expand_edge(edge.right)

    def query(
        self, source: Hashable, target: Hashable
    ) -> tuple[float, list[Hashable]] | None:
        """Exact shortest-path query using upward searches from both ends."""
        if source not in self.rank or target not in self.rank:
            raise KeyError("source and target must be hierarchy nodes")
        if source == target:
            return 0.0, [source]

        def run(
            start: Hashable,
            adjacency: Mapping[
                Hashable, Iterable[tuple[Hashable, float, int]]
            ],
        ) -> tuple[
            dict[Hashable, float],
            dict[Hashable, tuple[Hashable, int]],
        ]:
            dist = {start: 0.0}
            prev: dict[Hashable, tuple[Hashable, int]] = {}
            heap: list[tuple[float, int, Hashable]] = [(0.0, 0, start)]
            serial = 1
            while heap:
                d, _, u = heapq.heappop(heap)
                if d != dist.get(u):
                    continue
                for v, weight, edge_id in adjacency.get(u, ()):
                    nd = d + weight
                    if nd < dist.get(v, math.inf):
                        dist[v] = nd
                        prev[v] = (u, edge_id)
                        heapq.heappush(heap, (nd, serial, v))
                        serial += 1
            return dist, prev

        forward_dist, forward_prev = run(source, self.upward)
        backward_dist, backward_prev = run(target, self.backward_upward)
        common = set(forward_dist) & set(backward_dist)
        if not common:
            return None
        meet = min(
            common,
            key=lambda u: forward_dist[u] + backward_dist[u],
        )
        best = forward_dist[meet] + backward_dist[meet]

        forward_edge_ids: list[int] = []
        cur = meet
        while cur != source:
            parent, edge_id = forward_prev[cur]
            forward_edge_ids.append(edge_id)
            cur = parent
        forward_edge_ids.reverse()

        backward_edge_ids: list[int] = []
        cur = meet
        while cur != target:
            nxt, edge_id = backward_prev[cur]
            backward_edge_ids.append(edge_id)
            cur = nxt

        original_edges: list[tuple[Hashable, Hashable]] = []
        for edge_id in forward_edge_ids + backward_edge_ids:
            original_edges.extend(self._expand_edge(edge_id))

        if not original_edges:
            return best, [source]
        path: list[Hashable] = [original_edges[0][0]]
        for u, v in original_edges:
            if path[-1] != u:
                raise AssertionError("shortcut expansion produced a broken path")
            path.append(v)
        return best, path


def build_contraction_hierarchy(
    graph: WeightedGraph[Node],
    order: Sequence[Node] | None = None,
) -> ContractionHierarchy:
    """Build a Contraction Hierarchy with exact witness searches.

    The default order is a static degree heuristic. For serious road-network
    work, nested-dissection/customized orderings are preferable.
    """
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v, weight in neighbors:
            if weight < 0:
                raise ValueError(
                    "Contraction Hierarchies require non-negative weights"
                )
            if v not in seen:
                seen.add(v)
                nodes.append(v)

    if order is None:
        in_degree = {u: 0 for u in nodes}
        out_degree = {u: 0 for u in nodes}
        for u in nodes:
            for v, _ in graph.get(u, ()):
                out_degree[u] += 1
                in_degree[v] += 1
        contraction_order = sorted(
            nodes,
            key=lambda u: (in_degree[u] + out_degree[u]),
        )
    else:
        contraction_order = list(order)
        if len(contraction_order) != len(nodes) or set(contraction_order) != set(nodes):
            raise ValueError("order must contain every graph node exactly once")

    records: list[_CHEdge] = []
    best_out: dict[Hashable, dict[Hashable, int]] = {
        u: {} for u in nodes
    }
    best_in: dict[Hashable, dict[Hashable, int]] = {
        u: {} for u in nodes
    }

    def add_edge(
        u: Hashable,
        v: Hashable,
        weight: float,
        left: int | None = None,
        right: int | None = None,
    ) -> int:
        existing = best_out[u].get(v)
        if existing is not None and records[existing].weight <= weight + 1e-12:
            return existing
        edge_id = len(records)
        records.append(_CHEdge(u, v, float(weight), left, right))
        best_out[u][v] = edge_id
        best_in[v][u] = edge_id
        return edge_id

    for u in nodes:
        for v, weight in graph.get(u, ()):
            if u != v:
                add_edge(u, v, float(weight))

    active = set(nodes)
    rank: dict[Hashable, int] = {}

    def witness_distance(
        source: Hashable,
        target: Hashable,
        excluded: Hashable,
        limit: float,
    ) -> float:
        if source == target:
            return 0.0
        dist = {source: 0.0}
        heap: list[tuple[float, int, Hashable]] = [(0.0, 0, source)]
        serial = 1
        while heap:
            d, _, u = heapq.heappop(heap)
            if d != dist.get(u):
                continue
            if d > limit + 1e-12:
                return math.inf
            if u == target:
                return d
            for v, edge_id in best_out[u].items():
                if v == excluded or v not in active:
                    continue
                weight = records[edge_id].weight
                nd = d + weight
                if nd < dist.get(v, math.inf) and nd <= limit + 1e-12:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, serial, v))
                    serial += 1
        return math.inf

    for current_rank, x in enumerate(contraction_order):
        incoming = [
            (u, edge_id)
            for u, edge_id in best_in[x].items()
            if u in active and u != x
        ]
        outgoing = [
            (v, edge_id)
            for v, edge_id in best_out[x].items()
            if v in active and v != x
        ]

        for u, left_id in incoming:
            for v, right_id in outgoing:
                if u == v:
                    continue
                candidate = (
                    records[left_id].weight + records[right_id].weight
                )
                existing = best_out[u].get(v)
                if (
                    existing is not None
                    and records[existing].weight <= candidate + 1e-12
                ):
                    continue
                witness = witness_distance(u, v, x, candidate)
                if witness > candidate + 1e-12:
                    add_edge(
                        u,
                        v,
                        candidate,
                        left=left_id,
                        right=right_id,
                    )

        rank[x] = current_rank
        active.remove(x)

    upward: dict[
        Hashable, list[tuple[Hashable, float, int]]
    ] = {u: [] for u in nodes}
    backward_upward: dict[
        Hashable, list[tuple[Hashable, float, int]]
    ] = {u: [] for u in nodes}

    for edge_id, edge in enumerate(records):
        if rank[edge.u] < rank[edge.v]:
            upward[edge.u].append((edge.v, edge.weight, edge_id))
        elif rank[edge.u] > rank[edge.v]:
            # Reverse traversal of a downward original/shortcut edge.
            backward_upward[edge.v].append(
                (edge.u, edge.weight, edge_id)
            )

    return ContractionHierarchy(
        rank=rank,
        edges=tuple(records),
        upward={u: tuple(vs) for u, vs in upward.items()},
        backward_upward={
            u: tuple(vs) for u, vs in backward_upward.items()
        },
    )


@dataclass(frozen=True)
class DenseHubLabels:
    """Unpruned exact 2-hop labels derived from a Contraction Hierarchy."""

    forward: dict[Hashable, dict[Hashable, float]]
    backward: dict[Hashable, dict[Hashable, float]]

    def distance(self, source: Hashable, target: Hashable) -> float:
        if source not in self.forward or target not in self.backward:
            raise KeyError("source and target must be label vertices")
        common = set(self.forward[source]) & set(self.backward[target])
        if not common:
            return math.inf
        return min(
            self.forward[source][hub] + self.backward[target][hub]
            for hub in common
        )


def build_dense_hub_labels(ch: ContractionHierarchy) -> DenseHubLabels:
    """Build exact but unpruned hub labels from all upward CH searches."""

    def all_distances(
        start: Hashable,
        adjacency: Mapping[
            Hashable, Iterable[tuple[Hashable, float, int]]
        ],
    ) -> dict[Hashable, float]:
        dist = {start: 0.0}
        heap: list[tuple[float, int, Hashable]] = [(0.0, 0, start)]
        serial = 1
        while heap:
            d, _, u = heapq.heappop(heap)
            if d != dist.get(u):
                continue
            for v, weight, _ in adjacency.get(u, ()):
                nd = d + weight
                if nd < dist.get(v, math.inf):
                    dist[v] = nd
                    heapq.heappush(heap, (nd, serial, v))
                    serial += 1
        return dist

    nodes = list(ch.rank)
    forward = {
        u: all_distances(u, ch.upward)
        for u in nodes
    }
    backward = {
        u: all_distances(u, ch.backward_upward)
        for u in nodes
    }
    return DenseHubLabels(forward=forward, backward=backward)



@dataclass(frozen=True)
class CCHTopology:
    """Metric-independent chordal completion for Customizable CH."""

    order: tuple[Hashable, ...]
    rank: dict[Hashable, int]
    higher_neighbors: dict[Hashable, tuple[Hashable, ...]]
    edges: tuple[tuple[Hashable, Hashable], ...]


@dataclass
class CustomizableContractionHierarchy:
    """Basic Customizable Contraction Hierarchy for undirected graphs.

    The topology is built once from an elimination order. customize() can then
    be called repeatedly for new non-negative edge weights without rebuilding
    the chordal completion.
    """

    topology: CCHTopology
    weights: dict[tuple[Hashable, Hashable], float]
    witness: dict[tuple[Hashable, Hashable], Hashable | None]

    def _key(
        self, a: Hashable, b: Hashable
    ) -> tuple[Hashable, Hashable]:
        rank = self.topology.rank
        if rank[a] < rank[b]:
            return a, b
        return b, a

    def _expand(
        self, a: Hashable, b: Hashable
    ) -> list[Hashable]:
        key = self._key(a, b)
        middle = self.witness.get(key)
        if middle is None:
            return [a, b]
        left = self._expand(a, middle)
        right = self._expand(middle, b)
        return left[:-1] + right

    def query(
        self, source: Hashable, target: Hashable
    ) -> tuple[float, list[Hashable]] | None:
        """Exact shortest path by two upward Dijkstra searches."""
        rank = self.topology.rank
        if source not in rank or target not in rank:
            raise KeyError("source and target must be hierarchy nodes")
        if source == target:
            return 0.0, [source]

        upward = {
            u: [
                (v, self.weights[self._key(u, v)])
                for v in self.topology.higher_neighbors[u]
                if not math.isinf(self.weights[self._key(u, v)])
            ]
            for u in self.topology.order
        }

        def run(start: Hashable):
            dist = {start: 0.0}
            prev: dict[Hashable, Hashable] = {}
            heap: list[tuple[float, int, Hashable]] = [(0.0, 0, start)]
            serial = 1
            while heap:
                d, _, u = heapq.heappop(heap)
                if d != dist.get(u):
                    continue
                for v, weight in upward[u]:
                    nd = d + weight
                    if nd < dist.get(v, math.inf):
                        dist[v] = nd
                        prev[v] = u
                        heapq.heappush(heap, (nd, serial, v))
                        serial += 1
            return dist, prev

        ds, ps = run(source)
        dt, pt = run(target)
        common = set(ds) & set(dt)
        if not common:
            return None
        meet = min(common, key=lambda u: ds[u] + dt[u])
        best = ds[meet] + dt[meet]

        left_pairs: list[tuple[Hashable, Hashable]] = []
        cur = meet
        while cur != source:
            parent = ps[cur]
            left_pairs.append((parent, cur))
            cur = parent
        left_pairs.reverse()

        right_pairs: list[tuple[Hashable, Hashable]] = []
        cur = meet
        while cur != target:
            parent = pt[cur]
            # pt maps a higher-ranked node to its predecessor on target -> meet.
            # Walking those predecessors from meet therefore already yields
            # the correct meet -> target orientation.
            right_pairs.append((cur, parent))
            cur = parent

        path: list[Hashable] = [source]
        for a, b in left_pairs + right_pairs:
            expanded = self._expand(a, b)
            if path[-1] != expanded[0]:
                raise AssertionError("CCH shortcut expansion produced a broken path")
            path.extend(expanded[1:])
        return best, path


def build_cch_topology(
    graph: WeightedGraph[Node],
    order: Sequence[Node],
) -> CCHTopology:
    """Build metric-independent CCH topology by elimination/fill.

    This educational implementation uses the supplied elimination order and
    explicit clique fill among higher-ranked neighbors.
    """
    nodes = list(graph)
    seen = set(nodes)
    for neighbors in graph.values():
        for v, _ in neighbors:
            if v not in seen:
                seen.add(v)
                nodes.append(v)

    order_tuple = tuple(order)
    if len(order_tuple) != len(nodes) or set(order_tuple) != set(nodes):
        raise ValueError("order must contain every graph node exactly once")
    rank = {u: i for i, u in enumerate(order_tuple)}

    neighbors: dict[Hashable, set[Hashable]] = {u: set() for u in nodes}
    for u in nodes:
        for v, weight in graph.get(u, ()):
            if weight < 0:
                raise ValueError("CCH requires non-negative edge weights")
            if u == v:
                continue
            neighbors[u].add(v)
            neighbors[v].add(u)

    edges: set[tuple[Hashable, Hashable]] = set()

    def key(a: Hashable, b: Hashable):
        return (a, b) if rank[a] < rank[b] else (b, a)

    for u in nodes:
        for v in neighbors[u]:
            edges.add(key(u, v))

    for x in order_tuple:
        higher = [v for v in neighbors[x] if rank[v] > rank[x]]
        for i, u in enumerate(higher):
            for v in higher[i + 1 :]:
                if v not in neighbors[u]:
                    neighbors[u].add(v)
                    neighbors[v].add(u)
                edges.add(key(u, v))

    higher_neighbors = {
        u: tuple(
            sorted(
                (v for v in neighbors[u] if rank[v] > rank[u]),
                key=lambda v: rank[v],
            )
        )
        for u in order_tuple
    }
    return CCHTopology(
        order=order_tuple,
        rank=rank,
        higher_neighbors=higher_neighbors,
        edges=tuple(
            sorted(edges, key=lambda e: (rank[e[0]], rank[e[1]]))
        ),
    )


def customize_contraction_hierarchy(
    topology: CCHTopology,
    graph: WeightedGraph[Node],
) -> CustomizableContractionHierarchy:
    """Customize a prebuilt CCH topology for a particular edge-weight metric."""
    rank = topology.rank

    def key(a: Hashable, b: Hashable):
        return (a, b) if rank[a] < rank[b] else (b, a)

    weights = {edge: math.inf for edge in topology.edges}
    witness: dict[
        tuple[Hashable, Hashable], Hashable | None
    ] = {edge: None for edge in topology.edges}

    for u in topology.order:
        for v, raw_weight in graph.get(u, ()):
            weight = float(raw_weight)
            if weight < 0:
                raise ValueError("CCH requires non-negative edge weights")
            if u == v:
                continue
            if v not in rank:
                raise ValueError("metric graph contains a node outside the topology")
            edge = key(u, v)
            if edge not in weights:
                raise ValueError(
                    "metric graph contains an edge absent from CCH topology"
                )
            weights[edge] = min(weights[edge], weight)

    for x in topology.order:
        higher = topology.higher_neighbors[x]
        for i, u in enumerate(higher):
            xu = key(x, u)
            if math.isinf(weights[xu]):
                continue
            for v in higher[i + 1 :]:
                xv = key(x, v)
                if math.isinf(weights[xv]):
                    continue
                uv = key(u, v)
                candidate = weights[xu] + weights[xv]
                if candidate < weights[uv] - 1e-12:
                    weights[uv] = candidate
                    witness[uv] = x

    return CustomizableContractionHierarchy(
        topology=topology,
        weights=weights,
        witness=witness,
    )


def build_customizable_contraction_hierarchy(
    graph: WeightedGraph[Node],
    order: Sequence[Node],
) -> CustomizableContractionHierarchy:
    """Convenience wrapper for CCH topology construction + customization."""
    topology = build_cch_topology(graph, order)
    return customize_contraction_hierarchy(topology, graph)
