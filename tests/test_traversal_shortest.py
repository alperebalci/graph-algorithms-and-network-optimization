import math

import pytest

from graph_algorithms.advanced_shortest_paths import bidirectional_dijkstra
from graph_algorithms.exceptions import NegativeCycleError
from graph_algorithms.shortest_paths import (
    astar,
    bellman_ford,
    dijkstra,
    floyd_warshall,
    johnson,
    reconstruct_path,
)
from graph_algorithms.traversal import (
    bfs_order,
    bidirectional_bfs_path,
    dfs_order,
    iterative_deepening_path,
)


def test_traversals_and_bidirectional_bfs():
    g = {
        0: [1, 2],
        1: [0, 3],
        2: [0, 3],
        3: [1, 2, 4],
        4: [3],
    }
    assert bfs_order(g, 0) == [0, 1, 2, 3, 4]
    assert dfs_order(g, 0)[0] == 0
    assert set(dfs_order(g, 0)) == set(g)
    assert iterative_deepening_path(g, 0, 4, 3) in (
        [0, 1, 3, 4],
        [0, 2, 3, 4],
    )
    assert iterative_deepening_path(g, 0, 4, 2) is None
    path = bidirectional_bfs_path(g, 0, 4)
    assert (
        path is not None
        and len(path) == 4
        and path[0] == 0
        and path[-1] == 4
    )


def test_dijkstra_and_astar():
    g = {
        "s": [("a", 1), ("b", 4)],
        "a": [("b", 2), ("t", 6)],
        "b": [("t", 1)],
        "t": [],
    }
    dist, prev = dijkstra(g, "s")
    assert dist["t"] == 4
    assert reconstruct_path(prev, "s", "t") == ["s", "a", "b", "t"]
    result = astar(g, "s", "t", lambda _u, _v: 0)
    assert result == (4.0, ["s", "a", "b", "t"])


def test_bellman_ford_floyd_warshall_johnson_agree():
    vertices = ["a", "b", "c", "d"]
    edges = [
        ("a", "b", 1),
        ("a", "c", 4),
        ("b", "c", -2),
        ("c", "d", 2),
        ("b", "d", 5),
    ]
    bf, _ = bellman_ford(vertices, edges, "a")
    fw = floyd_warshall(vertices, edges)
    jj = johnson(vertices, edges)
    assert bf["d"] == 1
    for u in vertices:
        for v in vertices:
            a, b = fw[u][v], jj[u][v]
            if math.isinf(a):
                assert math.isinf(b)
            else:
                assert a == pytest.approx(b)


def test_negative_cycle_detection():
    vertices = [0, 1, 2]
    edges = [(0, 1, 1), (1, 2, -3), (2, 1, 1)]
    with pytest.raises(NegativeCycleError):
        bellman_ford(vertices, edges, 0)
    with pytest.raises(NegativeCycleError):
        floyd_warshall(vertices, edges)


def test_bidirectional_dijkstra_directed():
    g = {
        "s": [("a", 2), ("b", 8)],
        "a": [("b", 2), ("t", 7)],
        "b": [("t", 1)],
        "t": [],
    }
    rg = {
        "s": [],
        "a": [("s", 2)],
        "b": [("s", 8), ("a", 2)],
        "t": [("a", 7), ("b", 1)],
    }
    result = bidirectional_dijkstra(g, rg, "s", "t")
    assert result == (5.0, ["s", "a", "b", "t"])
