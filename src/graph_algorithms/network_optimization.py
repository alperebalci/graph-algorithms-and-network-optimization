from __future__ import annotations

import math
from collections import deque
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import TypeVar

from .exceptions import InfeasibleFlowError, NegativeCycleError

Node = TypeVar("Node", bound=Hashable)
CapacityGraph = Mapping[Node, Mapping[Node, float]]
CostGraph = Mapping[Node, Mapping[Node, float]]
EPS = 1e-12


@dataclass(frozen=True)
class MinCutResult:
    """Result of an s-t minimum cut."""

    value: float
    source_side: frozenset[Hashable]
    sink_side: frozenset[Hashable]
    cut_edges: tuple[tuple[Hashable, Hashable, float], ...]


@dataclass(frozen=True)
class MinCostFlowResult:
    """Flow value, total cost, and directed edge flows."""

    flow_value: float
    cost: float
    flow: dict[Hashable, dict[Hashable, float]]


@dataclass(frozen=True)
class CirculationResult:
    """Feasibility flag and a circulation satisfying bounds/demands when feasible."""

    feasible: bool
    flow: dict[Hashable, dict[Hashable, float]]


@dataclass(frozen=True)
class GomoryHuTree:
    """Weighted tree encoding all-pairs minimum-cut values of an undirected graph."""

    nodes: tuple[Hashable, ...]
    edges: tuple[tuple[Hashable, Hashable, float], ...]

    def minimum_cut_value(self, source: Hashable, target: Hashable) -> float:
        """Return the pairwise minimum-cut value as the minimum tree edge on the path."""
        if source == target:
            raise ValueError("source and target must be distinct")
        if source not in self.nodes or target not in self.nodes:
            raise KeyError("source and target must be tree nodes")
        adjacency: dict[Hashable, list[tuple[Hashable, float]]] = {
            node: [] for node in self.nodes
        }
        for u, v, weight in self.edges:
            adjacency[u].append((v, weight))
            adjacency[v].append((u, weight))

        stack: list[tuple[Hashable, Hashable | None, float]] = [
            (source, None, math.inf)
        ]
        while stack:
            u, parent, bottleneck = stack.pop()
            if u == target:
                return bottleneck
            for v, weight in adjacency[u]:
                if v != parent:
                    stack.append((v, u, min(bottleneck, weight)))
        raise ValueError("Gomory-Hu tree is disconnected")


@dataclass
class _ResidualEdge:
    to: Hashable
    rev: int
    capacity: float
    cost: float
    initial_capacity: float


class _ResidualNetwork:
    def __init__(self) -> None:
        self.adj: dict[Hashable, list[_ResidualEdge]] = {}

    def add_node(self, node: Hashable) -> None:
        self.adj.setdefault(node, [])

    def add_edge(
        self,
        u: Hashable,
        v: Hashable,
        capacity: float,
        cost: float = 0.0,
    ) -> tuple[Hashable, int]:
        cap = float(capacity)
        edge_cost = float(cost)
        if cap < -EPS:
            raise ValueError(f"negative capacity on edge {u!r}->{v!r}")
        cap = max(0.0, cap)
        self.add_node(u)
        self.add_node(v)

        forward_index = len(self.adj[u])
        if u == v:
            reverse_index = forward_index + 1
        else:
            reverse_index = len(self.adj[v])

        forward = _ResidualEdge(
            to=v,
            rev=reverse_index,
            capacity=cap,
            cost=edge_cost,
            initial_capacity=cap,
        )
        reverse = _ResidualEdge(
            to=u,
            rev=forward_index,
            capacity=0.0,
            cost=-edge_cost,
            initial_capacity=0.0,
        )
        self.adj[u].append(forward)
        self.adj[v].append(reverse)
        return u, forward_index


def _build_capacity_network(
    capacity: CapacityGraph[Node],
) -> tuple[_ResidualNetwork, dict[tuple[Hashable, Hashable], tuple[Hashable, int]], tuple[Hashable, ...]]:
    network = _ResidualNetwork()
    nodes: list[Hashable] = []
    seen: set[Hashable] = set()

    def add_node(node: Hashable) -> None:
        if node not in seen:
            seen.add(node)
            nodes.append(node)
            network.add_node(node)

    for u, neighbors in capacity.items():
        add_node(u)
        for v in neighbors:
            add_node(v)

    refs: dict[tuple[Hashable, Hashable], tuple[Hashable, int]] = {}
    for u, neighbors in capacity.items():
        for v, cap in neighbors.items():
            refs[(u, v)] = network.add_edge(u, v, float(cap))
    return network, refs, tuple(nodes)


def _dinic_on_network(
    network: _ResidualNetwork,
    source: Hashable,
    sink: Hashable,
) -> float:
    if source == sink:
        return 0.0
    total = 0.0

    while True:
        level: dict[Hashable, int] = {source: 0}
        queue: deque[Hashable] = deque([source])
        while queue:
            u = queue.popleft()
            for edge in network.adj[u]:
                if edge.capacity > EPS and edge.to not in level:
                    level[edge.to] = level[u] + 1
                    queue.append(edge.to)
        if sink not in level:
            return total

        ptr = {node: 0 for node in network.adj}

        def send(u: Hashable, pushed: float) -> float:
            if u == sink:
                return pushed
            while ptr[u] < len(network.adj[u]):
                idx = ptr[u]
                edge = network.adj[u][idx]
                if (
                    edge.capacity > EPS
                    and level.get(edge.to, -1) == level[u] + 1
                ):
                    amount = send(edge.to, min(pushed, edge.capacity))
                    if amount > EPS:
                        edge.capacity -= amount
                        reverse = network.adj[edge.to][edge.rev]
                        reverse.capacity += amount
                        return amount
                ptr[u] += 1
            return 0.0

        while True:
            pushed = send(source, math.inf)
            if pushed <= EPS:
                break
            total += pushed


def _flows_from_refs(
    network: _ResidualNetwork,
    refs: Mapping[tuple[Hashable, Hashable], tuple[Hashable, int]],
    nodes: tuple[Hashable, ...],
) -> dict[Hashable, dict[Hashable, float]]:
    flow: dict[Hashable, dict[Hashable, float]] = {node: {} for node in nodes}
    for (u, v), (ref_u, idx) in refs.items():
        edge = network.adj[ref_u][idx]
        value = edge.initial_capacity - edge.capacity
        if abs(value) <= EPS:
            value = 0.0
        flow.setdefault(u, {})[v] = value
        flow.setdefault(v, {})
    return flow


def minimum_st_cut(
    capacity: CapacityGraph[Node],
    source: Node,
    sink: Node,
) -> MinCutResult:
    """Minimum s-t cut in a directed capacitated graph.

    Uses Dinic to compute a maximum flow, then residual reachability to recover
    the source side. The general Dinic bound is O(V^2 E).
    """
    if source == sink:
        raise ValueError("source and sink must be distinct")
    network, _, nodes = _build_capacity_network(capacity)
    if source not in network.adj or sink not in network.adj:
        raise KeyError("source and sink must be graph nodes")

    _dinic_on_network(network, source, sink)

    reachable: set[Hashable] = {source}
    queue: deque[Hashable] = deque([source])
    while queue:
        u = queue.popleft()
        for edge in network.adj[u]:
            if edge.capacity > EPS and edge.to not in reachable:
                reachable.add(edge.to)
                queue.append(edge.to)

    source_side = frozenset(reachable)
    sink_side = frozenset(node for node in nodes if node not in reachable)
    cut_edges: list[tuple[Hashable, Hashable, float]] = []
    value = 0.0
    for u, neighbors in capacity.items():
        if u not in source_side:
            continue
        for v, cap_raw in neighbors.items():
            cap = float(cap_raw)
            if v in sink_side and cap > EPS:
                cut_edges.append((u, v, cap))
                value += cap

    return MinCutResult(
        value=value,
        source_side=source_side,
        sink_side=sink_side,
        cut_edges=tuple(cut_edges),
    )


min_cut = minimum_st_cut


def _build_cost_network(
    capacity: CapacityGraph[Node],
    cost: CostGraph[Node],
) -> tuple[_ResidualNetwork, dict[tuple[Hashable, Hashable], tuple[Hashable, int]], tuple[Hashable, ...]]:
    network = _ResidualNetwork()
    nodes: list[Hashable] = []
    seen: set[Hashable] = set()

    def add_node(node: Hashable) -> None:
        if node not in seen:
            seen.add(node)
            nodes.append(node)
            network.add_node(node)

    for u, neighbors in capacity.items():
        add_node(u)
        for v in neighbors:
            add_node(v)

    refs: dict[tuple[Hashable, Hashable], tuple[Hashable, int]] = {}
    for u, neighbors in capacity.items():
        for v, cap_raw in neighbors.items():
            if u not in cost or v not in cost[u]:
                raise ValueError(f"missing cost for capacity edge {u!r}->{v!r}")
            refs[(u, v)] = network.add_edge(
                u, v, float(cap_raw), float(cost[u][v])
            )
    return network, refs, tuple(nodes)


def _bellman_ford_residual_path(
    network: _ResidualNetwork,
    source: Hashable,
    sink: Hashable,
) -> dict[Hashable, tuple[Hashable, int]] | None:
    nodes = list(network.adj)
    dist = {node: math.inf for node in nodes}
    predecessor: dict[Hashable, tuple[Hashable, int]] = {}
    dist[source] = 0.0

    for _ in range(max(0, len(nodes) - 1)):
        changed = False
        for u in nodes:
            if math.isinf(dist[u]):
                continue
            for idx, edge in enumerate(network.adj[u]):
                if edge.capacity <= EPS:
                    continue
                candidate = dist[u] + edge.cost
                if candidate < dist[edge.to] - EPS:
                    dist[edge.to] = candidate
                    predecessor[edge.to] = (u, idx)
                    changed = True
        if not changed:
            break

    for u in nodes:
        if math.isinf(dist[u]):
            continue
        for edge in network.adj[u]:
            if (
                edge.capacity > EPS
                and dist[u] + edge.cost < dist[edge.to] - EPS
            ):
                raise NegativeCycleError(
                    "reachable negative-cost residual cycle detected"
                )

    if math.isinf(dist[sink]):
        return None
    return predecessor


def _augment_costed_path(
    network: _ResidualNetwork,
    predecessor: Mapping[Hashable, tuple[Hashable, int]],
    source: Hashable,
    sink: Hashable,
    limit: float,
) -> tuple[float, float]:
    bottleneck = float(limit)
    path_cost = 0.0
    v = sink
    while v != source:
        if v not in predecessor:
            return 0.0, 0.0
        u, idx = predecessor[v]
        edge = network.adj[u][idx]
        bottleneck = min(bottleneck, edge.capacity)
        path_cost += edge.cost
        v = u

    if bottleneck <= EPS:
        return 0.0, 0.0

    v = sink
    while v != source:
        u, idx = predecessor[v]
        edge = network.adj[u][idx]
        edge.capacity -= bottleneck
        network.adj[edge.to][edge.rev].capacity += bottleneck
        v = u

    return bottleneck, path_cost


def _min_cost_flow_impl(
    capacity: CapacityGraph[Node],
    cost: CostGraph[Node],
    source: Node,
    sink: Node,
    required_flow: float | None,
) -> MinCostFlowResult:
    if source == sink:
        raise ValueError("source and sink must be distinct")
    if required_flow is not None and required_flow < -EPS:
        raise ValueError("required_flow must be non-negative")

    network, refs, nodes = _build_cost_network(capacity, cost)
    if source not in network.adj or sink not in network.adj:
        raise KeyError("source and sink must be graph nodes")

    target = None if required_flow is None else max(0.0, float(required_flow))
    flow_value = 0.0
    total_cost = 0.0

    while target is None or flow_value < target - EPS:
        predecessor = _bellman_ford_residual_path(network, source, sink)
        if predecessor is None:
            break
        remaining = math.inf if target is None else target - flow_value
        amount, unit_cost = _augment_costed_path(
            network, predecessor, source, sink, remaining
        )
        if amount <= EPS:
            break
        flow_value += amount
        total_cost += amount * unit_cost

    if target is not None and flow_value < target - EPS:
        raise InfeasibleFlowError(
            f"requested flow {target} exceeds feasible s-t capacity {flow_value}"
        )
    if target is not None and abs(flow_value - target) <= EPS:
        flow_value = target

    return MinCostFlowResult(
        flow_value=flow_value,
        cost=total_cost,
        flow=_flows_from_refs(network, refs, nodes),
    )


def min_cost_flow(
    capacity: CapacityGraph[Node],
    cost: CostGraph[Node],
    source: Node,
    sink: Node,
    amount: float,
) -> MinCostFlowResult:
    """Minimum-cost s-t flow of exactly the requested amount.

    Uses successive shortest augmenting paths with Bellman-Ford on the residual
    graph. Negative edge costs are supported; reachable negative-cost residual
    cycles are rejected explicitly.
    """
    return _min_cost_flow_impl(capacity, cost, source, sink, float(amount))


def min_cost_max_flow(
    capacity: CapacityGraph[Node],
    cost: CostGraph[Node],
    source: Node,
    sink: Node,
) -> MinCostFlowResult:
    """Maximum s-t flow with minimum cost under successive shortest paths."""
    return _min_cost_flow_impl(capacity, cost, source, sink, None)


def feasible_circulation(
    lower: CapacityGraph[Node],
    upper: CapacityGraph[Node],
    demands: Mapping[Node, float] | None = None,
) -> CirculationResult:
    """Find a feasible circulation with lower/upper bounds and node demands.

    Convention: inflow(v) - outflow(v) = demand(v). Positive values are
    consumption/demand; negative values are supply. Feasibility is reduced to
    a single super-source/super-sink maximum-flow problem.
    """
    demand_map: Mapping[Node, float] = demands or {}
    nodes: list[Hashable] = []
    seen: set[Hashable] = set()

    def remember(node: Hashable) -> None:
        if node not in seen:
            seen.add(node)
            nodes.append(node)

    for graph in (upper, lower):
        for u, neighbors in graph.items():
            remember(u)
            for v in neighbors:
                remember(v)
    for node in demand_map:
        remember(node)

    if abs(sum(float(demand_map.get(node, 0.0)) for node in nodes)) > 1e-9:
        return CirculationResult(False, {})

    for u, neighbors in lower.items():
        for v, lo_raw in neighbors.items():
            if u not in upper or v not in upper[u]:
                if abs(float(lo_raw)) > EPS:
                    raise ValueError(
                        f"lower-bound edge {u!r}->{v!r} is missing from upper bounds"
                    )

    network = _ResidualNetwork()
    for node in nodes:
        network.add_node(node)

    lower_balance = {node: 0.0 for node in nodes}
    refs: dict[tuple[Hashable, Hashable], tuple[Hashable, int]] = {}
    lower_value: dict[tuple[Hashable, Hashable], float] = {}

    for u, neighbors in upper.items():
        for v, up_raw in neighbors.items():
            up = float(up_raw)
            lo = float(lower.get(u, {}).get(v, 0.0))
            if lo < -EPS or up < -EPS or lo > up + EPS:
                raise ValueError(
                    f"invalid bounds on edge {u!r}->{v!r}: lower={lo}, upper={up}"
                )
            lo = max(0.0, lo)
            refs[(u, v)] = network.add_edge(u, v, max(0.0, up - lo))
            lower_value[(u, v)] = lo
            lower_balance[u] -= lo
            lower_balance[v] += lo

    super_source = object()
    super_sink = object()
    network.add_node(super_source)
    network.add_node(super_sink)

    total_required = 0.0
    for node in nodes:
        residual_requirement = (
            float(demand_map.get(node, 0.0)) - lower_balance[node]
        )
        if residual_requirement > EPS:
            network.add_edge(node, super_sink, residual_requirement)
            total_required += residual_requirement
        elif residual_requirement < -EPS:
            network.add_edge(super_source, node, -residual_requirement)

    routed = _dinic_on_network(network, super_source, super_sink)
    if abs(routed - total_required) > 1e-9:
        return CirculationResult(False, {})

    residual_flow = _flows_from_refs(network, refs, tuple(nodes))
    flow: dict[Hashable, dict[Hashable, float]] = {
        node: {} for node in nodes
    }
    for (u, v), lo in lower_value.items():
        flow[u][v] = lo + residual_flow[u][v]
    return CirculationResult(True, flow)


def _normalize_undirected_capacity(
    graph: CapacityGraph[Node],
) -> tuple[tuple[Hashable, ...], dict[Hashable, dict[Hashable, float]]]:
    nodes: list[Hashable] = []
    seen: set[Hashable] = set()

    def remember(node: Hashable) -> None:
        if node not in seen:
            seen.add(node)
            nodes.append(node)

    undirected_edges: dict[
        frozenset[Hashable], tuple[Hashable, Hashable, float]
    ] = {}
    for u, neighbors in graph.items():
        remember(u)
        for v, weight_raw in neighbors.items():
            remember(v)
            weight = float(weight_raw)
            if weight < -EPS:
                raise ValueError("Gomory-Hu requires non-negative capacities")
            if u == v:
                continue
            key = frozenset((u, v))
            if key in undirected_edges:
                _, _, existing = undirected_edges[key]
                if abs(existing - weight) > 1e-9:
                    raise ValueError(
                        "symmetric entries for an undirected edge must have equal capacity"
                    )
            else:
                undirected_edges[key] = (u, v, max(0.0, weight))

    directed: dict[Hashable, dict[Hashable, float]] = {
        node: {} for node in nodes
    }
    for u, v, weight in undirected_edges.values():
        directed[u][v] = directed[u].get(v, 0.0) + weight
        directed[v][u] = directed[v].get(u, 0.0) + weight
    return tuple(nodes), directed


def gomory_hu_tree(graph: CapacityGraph[Node]) -> GomoryHuTree:
    """Construct a Gomory-Hu tree for an undirected non-negative capacity graph.

    The implementation uses the classical parent-update algorithm and exactly
    V-1 s-t minimum-cut computations.
    """
    nodes, directed = _normalize_undirected_capacity(graph)
    n = len(nodes)
    if n <= 1:
        return GomoryHuTree(nodes=nodes, edges=())

    parent = [0] * n
    cut_value = [0.0] * n

    for s in range(1, n):
        t = parent[s]
        result = minimum_st_cut(directed, nodes[s], nodes[t])
        source_side = result.source_side

        for i in range(s + 1, n):
            if parent[i] == t and nodes[i] in source_side:
                parent[i] = s

        if t != 0 and nodes[parent[t]] in source_side:
            parent[s] = parent[t]
            parent[t] = s
            cut_value[s] = cut_value[t]
            cut_value[t] = result.value
        else:
            cut_value[s] = result.value

    edges = tuple(
        (nodes[i], nodes[parent[i]], cut_value[i])
        for i in range(1, n)
    )
    return GomoryHuTree(nodes=nodes, edges=edges)
