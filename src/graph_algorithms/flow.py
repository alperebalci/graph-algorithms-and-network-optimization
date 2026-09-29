from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
CapacityGraph = Mapping[Node, Mapping[Node, float]]


@dataclass(frozen=True)
class FlowResult:
    value: float
    flow: dict[Node, dict[Node, float]]


def _residual(capacity: CapacityGraph[Node]) -> tuple[dict[Node, dict[Node, float]], set[Node]]:
    nodes: set[Node] = set(capacity)
    for u, nbrs in capacity.items():
        nodes.update(nbrs)
        for v, c in nbrs.items():
            if c < 0:
                raise ValueError(f"negative capacity on edge {u!r}->{v!r}")
    residual = {u: {v: 0.0 for v in nodes} for u in nodes}
    for u, nbrs in capacity.items():
        for v, c in nbrs.items():
            residual[u][v] += float(c)
    return residual, nodes


def _extract_flow(
    capacity: CapacityGraph[Node], residual: Mapping[Node, Mapping[Node, float]]
) -> dict[Node, dict[Node, float]]:
    flow: dict[Node, dict[Node, float]] = {}
    for u, nbrs in capacity.items():
        flow[u] = {}
        for v, c in nbrs.items():
            # For antiparallel original edges, residual arcs are coupled. This package
            # reports a valid net flow; tests and docs use standard simple networks.
            flow[u][v] = max(0.0, float(c) - residual[u][v])
    return flow


def ford_fulkerson(capacity: CapacityGraph[Node], source: Node, sink: Node) -> FlowResult:
    """Ford-Fulkerson using DFS augmenting paths. Terminates for integer capacities."""
    residual, nodes = _residual(capacity)
    if source not in nodes or sink not in nodes:
        raise KeyError("source and sink must be graph nodes")
    if source == sink:
        return FlowResult(0.0, _extract_flow(capacity, residual))
    value = 0.0

    def find_path() -> tuple[dict[Node, Node], float] | None:
        parent: dict[Node, Node] = {}
        seen = {source}
        stack = [(source, float("inf"))]
        while stack:
            u, bottleneck = stack.pop()
            if u == sink:
                return parent, bottleneck
            for v, c in residual[u].items():
                if c > 1e-15 and v not in seen:
                    seen.add(v)
                    parent[v] = u
                    stack.append((v, min(bottleneck, c)))
        return None

    while True:
        found = find_path()
        if found is None:
            break
        parent, aug = found
        value += aug
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= aug
            residual[v][u] += aug
            v = u
    return FlowResult(value, _extract_flow(capacity, residual))


def edmonds_karp(capacity: CapacityGraph[Node], source: Node, sink: Node) -> FlowResult:
    """Maximum flow using BFS augmenting paths. O(V E^2)."""
    residual, nodes = _residual(capacity)
    if source not in nodes or sink not in nodes:
        raise KeyError("source and sink must be graph nodes")
    if source == sink:
        return FlowResult(0.0, _extract_flow(capacity, residual))
    value = 0.0

    while True:
        parent: dict[Node, Node] = {}
        aug = {source: float("inf")}
        q: deque[Node] = deque([source])
        while q and sink not in aug:
            u = q.popleft()
            for v, c in residual[u].items():
                if c > 1e-15 and v not in aug:
                    parent[v] = u
                    aug[v] = min(aug[u], c)
                    q.append(v)
        if sink not in aug:
            break
        delta = aug[sink]
        value += delta
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= delta
            residual[v][u] += delta
            v = u
    return FlowResult(value, _extract_flow(capacity, residual))


def dinic(capacity: CapacityGraph[Node], source: Node, sink: Node) -> FlowResult:
    """Dinic maximum flow with level graphs and blocking-flow DFS. O(V^2 E) general bound."""
    residual, nodes = _residual(capacity)
    if source not in nodes or sink not in nodes:
        raise KeyError("source and sink must be graph nodes")
    if source == sink:
        return FlowResult(0.0, _extract_flow(capacity, residual))
    node_list = list(nodes)
    value = 0.0

    while True:
        level = {u: -1 for u in nodes}
        level[source] = 0
        q: deque[Node] = deque([source])
        while q:
            u = q.popleft()
            for v, c in residual[u].items():
                if c > 1e-15 and level[v] < 0:
                    level[v] = level[u] + 1
                    q.append(v)
        if level[sink] < 0:
            break

        neighbors = {
            u: [v for v in node_list if residual[u][v] > 1e-15] for u in nodes
        }
        ptr = {u: 0 for u in nodes}

        def send(u: Node, pushed: float) -> float:
            if u == sink or pushed <= 1e-15:
                return pushed
            while ptr[u] < len(neighbors[u]):
                v = neighbors[u][ptr[u]]
                if level[v] == level[u] + 1 and residual[u][v] > 1e-15:
                    amount = send(v, min(pushed, residual[u][v]))
                    if amount > 1e-15:
                        residual[u][v] -= amount
                        residual[v][u] += amount
                        return amount
                ptr[u] += 1
            return 0.0

        while True:
            pushed = send(source, float("inf"))
            if pushed <= 1e-15:
                break
            value += pushed

    return FlowResult(value, _extract_flow(capacity, residual))



def push_relabel(
    capacity: CapacityGraph[Node], source: Node, sink: Node
) -> FlowResult:
    """Goldberg-Tarjan preflow-push maximum flow.

    Uses FIFO active vertices with admissible pushes and relabel operations.
    This compact reference implementation has an O(V^2 E) worst-case bound.
    """
    residual, nodes = _residual(capacity)
    if source not in nodes or sink not in nodes:
        raise KeyError("source and sink must be graph nodes")
    if source == sink:
        return FlowResult(0.0, _extract_flow(capacity, residual))

    height = {u: 0 for u in nodes}
    excess = {u: 0.0 for u in nodes}
    height[source] = len(nodes)
    active: deque[Node] = deque()
    in_queue: set[Node] = set()

    def enqueue(u: Node) -> None:
        if (
            u != source
            and u != sink
            and excess[u] > 1e-15
            and u not in in_queue
        ):
            active.append(u)
            in_queue.add(u)

    for v, cap in list(residual[source].items()):
        if cap <= 1e-15:
            continue
        residual[source][v] -= cap
        residual[v][source] += cap
        excess[source] -= cap
        excess[v] += cap
        enqueue(v)

    node_list = list(nodes)
    while active:
        u = active.popleft()
        in_queue.discard(u)

        while excess[u] > 1e-15:
            pushed = False
            for v in node_list:
                if (
                    residual[u][v] > 1e-15
                    and height[u] == height[v] + 1
                ):
                    delta = min(excess[u], residual[u][v])
                    residual[u][v] -= delta
                    residual[v][u] += delta
                    excess[u] -= delta
                    excess[v] += delta
                    enqueue(v)
                    pushed = True
                    if excess[u] <= 1e-15:
                        break

            if excess[u] <= 1e-15:
                break

            if not pushed:
                admissible_heights = [
                    height[v]
                    for v in node_list
                    if residual[u][v] > 1e-15
                ]
                if not admissible_heights:
                    break
                height[u] = min(admissible_heights) + 1

        enqueue(u)

    return FlowResult(excess[sink], _extract_flow(capacity, residual))
