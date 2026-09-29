from __future__ import annotations

from collections import deque
from collections.abc import Hashable, Iterable, Mapping, Sequence
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)


def kuhn_maximum_bipartite_matching(
    graph: Mapping[Node, Iterable[Node]], left: Iterable[Node]
) -> dict[Node, Node]:
    """Maximum bipartite matching via DFS augmenting paths. O(VE)."""
    left_nodes = list(left)
    right_match: dict[Node, Node] = {}

    def augment(u: Node, seen: set[Node]) -> bool:
        for v in graph.get(u, ()):
            if v in seen:
                continue
            seen.add(v)
            if v not in right_match or augment(right_match[v], seen):
                right_match[v] = u
                return True
        return False

    for u in left_nodes:
        augment(u, set())
    return {u: v for v, u in right_match.items()}


def hopcroft_karp(
    graph: Mapping[Node, Iterable[Node]], left: Iterable[Node]
) -> dict[Node, Node]:
    """Maximum bipartite matching in O(E sqrt(V)). Returns left->right matches."""
    left_nodes = list(left)
    pair_u: dict[Node, Node | None] = {u: None for u in left_nodes}
    pair_v: dict[Node, Node | None] = {}
    dist: dict[Node, int] = {}

    for u in left_nodes:
        for v in graph.get(u, ()):
            pair_v.setdefault(v, None)

    def bfs() -> bool:
        q: deque[Node] = deque()
        found = False
        for u in left_nodes:
            if pair_u[u] is None:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = -1
        while q:
            u = q.popleft()
            for v in graph.get(u, ()):
                mate = pair_v.get(v)
                if mate is None:
                    found = True
                elif dist.get(mate, -1) < 0:
                    dist[mate] = dist[u] + 1
                    q.append(mate)
        return found

    def dfs(u: Node) -> bool:
        for v in graph.get(u, ()):
            mate = pair_v.get(v)
            if mate is None or (dist.get(mate) == dist[u] + 1 and dfs(mate)):
                pair_u[u] = v
                pair_v[v] = u
                return True
        dist[u] = -1
        return False

    while bfs():
        for u in left_nodes:
            if pair_u[u] is None:
                dfs(u)
    return {u: v for u, v in pair_u.items() if v is not None}


def hungarian(cost: Sequence[Sequence[float]]) -> tuple[float, list[int]]:
    """Minimum-cost assignment for a rectangular matrix with rows <= columns. O(n^2 m)."""
    n = len(cost)
    if n == 0:
        return 0.0, []
    m = len(cost[0])
    if any(len(row) != m for row in cost):
        raise ValueError("cost matrix must be rectangular")
    if n > m:
        raise ValueError("hungarian expects number of rows <= number of columns")

    u = [0.0] * (n + 1)
    v = [0.0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0] = i
        minv = [float("inf")] * (m + 1)
        used = [False] * (m + 1)
        j0 = 0
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, m + 1):
                if used[j]:
                    continue
                cur = float(cost[i0 - 1][j - 1]) - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = [-1] * n
    for j in range(1, m + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1
    total = sum(float(cost[i][assignment[i]]) for i in range(n))
    return total, assignment


def gale_shapley(
    proposer_preferences: Mapping[Node, Sequence[Node]],
    receiver_preferences: Mapping[Node, Sequence[Node]],
) -> dict[Node, Node]:
    """Stable matching with proposers as the proposing side. O(n^2)."""
    rank = {
        receiver: {proposer: i for i, proposer in enumerate(prefs)}
        for receiver, prefs in receiver_preferences.items()
    }
    free: deque[Node] = deque(proposer_preferences)
    next_choice = {p: 0 for p in proposer_preferences}
    receiver_match: dict[Node, Node] = {}

    while free:
        p = free.popleft()
        prefs = proposer_preferences[p]
        if next_choice[p] >= len(prefs):
            continue
        r = prefs[next_choice[p]]
        next_choice[p] += 1
        if r not in rank or p not in rank[r]:
            raise ValueError("preference lists must be mutually consistent")
        incumbent = receiver_match.get(r)
        if incumbent is None:
            receiver_match[r] = p
        elif rank[r][p] < rank[r][incumbent]:
            receiver_match[r] = p
            free.append(incumbent)
        else:
            free.append(p)
    return {p: r for r, p in receiver_match.items()}


def blossom_maximum_cardinality_matching(
    graph: Mapping[Node, Iterable[Node]],
) -> set[tuple[Node, Node]]:
    """Edmonds' blossom algorithm for maximum cardinality matching in a general graph.

    This is the unweighted O(V^3) variant. Self-loops are ignored.
    """
    nodes: list[Node] = list(graph)
    seen = set(nodes)
    for nbrs in graph.values():
        for v in nbrs:
            if v not in seen:
                seen.add(v)
                nodes.append(v)
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}
    adj: list[list[int]] = [[] for _ in range(n)]
    for u in nodes:
        ui = idx[u]
        for v in graph.get(u, ()):
            vi = idx[v]
            if ui != vi and vi not in adj[ui]:
                adj[ui].append(vi)
            if ui != vi and ui not in adj[vi]:
                adj[vi].append(ui)

    match = [-1] * n
    parent = [-1] * n
    base = list(range(n))
    used = [False] * n
    in_blossom = [False] * n

    def lca(a: int, b: int) -> int:
        used_path = [False] * n
        while True:
            a = base[a]
            used_path[a] = True
            if match[a] == -1:
                break
            a = parent[match[a]]
        while True:
            b = base[b]
            if used_path[b]:
                return b
            b = parent[match[b]]

    def mark_path(v: int, b: int, child: int) -> None:
        while base[v] != b:
            in_blossom[base[v]] = True
            in_blossom[base[match[v]]] = True
            parent[v] = child
            child = match[v]
            v = parent[match[v]]

    def find_augmenting_path(root: int) -> int:
        nonlocal base, parent, used, in_blossom
        used = [False] * n
        parent = [-1] * n
        base = list(range(n))
        q: deque[int] = deque([root])
        used[root] = True

        while q:
            v = q.popleft()
            for u in adj[v]:
                if base[v] == base[u] or match[v] == u:
                    continue
                if u == root or (match[u] != -1 and parent[match[u]] != -1):
                    curbase = lca(v, u)
                    in_blossom = [False] * n
                    mark_path(v, curbase, u)
                    mark_path(u, curbase, v)
                    for i in range(n):
                        if in_blossom[base[i]]:
                            base[i] = curbase
                            if not used[i]:
                                used[i] = True
                                q.append(i)
                elif parent[u] == -1:
                    parent[u] = v
                    if match[u] == -1:
                        return u
                    u = match[u]
                    used[u] = True
                    q.append(u)
        return -1

    for i in range(n):
        if match[i] != -1:
            continue
        v = find_augmenting_path(i)
        while v != -1:
            pv = parent[v]
            ppv = match[pv] if pv != -1 else -1
            if pv != -1:
                match[v] = pv
                match[pv] = v
            v = ppv

    result: set[tuple[Node, Node]] = set()
    for i, j in enumerate(match):
        if j != -1 and i < j:
            result.add((nodes[i], nodes[j]))
    return result
