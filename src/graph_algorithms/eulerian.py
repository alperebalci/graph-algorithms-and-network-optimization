from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Hashable, Iterable
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)


def hierholzer_eulerian_path(
    edges: Iterable[tuple[Node, Node]],
    *,
    directed: bool = False,
) -> list[Node]:
    """Return an Eulerian path/circuit using every supplied edge exactly once.

    Parallel edges are supported because edges are tracked by unique IDs.
    Raises ValueError when the non-isolated edge set is not Eulerian.
    Complexity is O(V+E).
    """
    edge_list = list(edges)
    if not edge_list:
        return []

    adjacency: dict[Node, list[tuple[Node, int]]] = defaultdict(list)
    indegree: dict[Node, int] = defaultdict(int)
    outdegree: dict[Node, int] = defaultdict(int)
    degree: dict[Node, int] = defaultdict(int)

    for eid, (u, v) in enumerate(edge_list):
        adjacency[u].append((v, eid))
        outdegree[u] += 1
        indegree[v] += 1
        degree[u] += 1
        degree[v] += 1
        if not directed:
            adjacency[v].append((u, eid))

    nodes = set(degree) | set(indegree) | set(outdegree)

    if directed:
        starts = [
            u for u in nodes
            if outdegree[u] - indegree[u] == 1
        ]
        ends = [
            u for u in nodes
            if indegree[u] - outdegree[u] == 1
        ]
        balanced = [
            u for u in nodes
            if indegree[u] == outdegree[u]
        ]
        if not (
            (len(starts) == len(ends) == 1 and len(balanced) == len(nodes) - 2)
            or (len(starts) == len(ends) == 0 and len(balanced) == len(nodes))
        ):
            raise ValueError("directed edge set is not Eulerian")
        start = starts[0] if starts else edge_list[0][0]
    else:
        odd = [u for u in nodes if degree[u] % 2 == 1]
        if len(odd) not in (0, 2):
            raise ValueError("undirected edge set is not Eulerian")
        start = odd[0] if odd else edge_list[0][0]

    # Connectivity on the underlying undirected edge set.
    undirected: dict[Node, set[Node]] = defaultdict(set)
    for u, v in edge_list:
        undirected[u].add(v)
        undirected[v].add(u)
    seen = {start}
    queue: deque[Node] = deque([start])
    while queue:
        u = queue.popleft()
        for v in undirected[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    active_nodes = {u for u in nodes if degree[u] > 0}
    if not active_nodes <= seen:
        raise ValueError("edge set is disconnected")

    used: set[int] = set()
    cursor = {u: 0 for u in nodes}
    stack = [start]
    circuit: list[Node] = []

    while stack:
        u = stack[-1]
        entries = adjacency[u]
        while cursor[u] < len(entries) and entries[cursor[u]][1] in used:
            cursor[u] += 1
        if cursor[u] == len(entries):
            circuit.append(stack.pop())
            continue
        v, eid = entries[cursor[u]]
        cursor[u] += 1
        if eid in used:
            continue
        used.add(eid)
        stack.append(v)

    if len(used) != len(edge_list):
        raise ValueError("edge set is not Eulerian")
    circuit.reverse()
    return circuit
