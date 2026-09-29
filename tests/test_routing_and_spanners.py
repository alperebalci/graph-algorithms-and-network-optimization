import math

import pytest

from graph_algorithms.routing import (
    alt_shortest_path,
    build_contraction_hierarchy,
    build_dense_hub_labels,
    build_landmark_index,
)
from graph_algorithms.shortest_paths import dijkstra
from graph_algorithms.spanners import greedy_spanner


def _undirected_graph():
    return {
        0: [(1, 2), (2, 5)],
        1: [(0, 2), (2, 1), (3, 4)],
        2: [(0, 5), (1, 1), (3, 1)],
        3: [(1, 4), (2, 1), (4, 2)],
        4: [(3, 2)],
    }


def test_alt_matches_dijkstra():
    graph = _undirected_graph()
    index = build_landmark_index(graph, [0, 4])
    result = alt_shortest_path(graph, 0, 4, index)
    assert result is not None
    dist, path = result
    baseline, _ = dijkstra(graph, 0)
    assert dist == pytest.approx(baseline[4])
    assert path[0] == 0 and path[-1] == 4


def test_contraction_hierarchy_all_pairs_and_dense_hub_labels():
    graph = _undirected_graph()
    ch = build_contraction_hierarchy(graph, order=[0, 4, 1, 3, 2])
    labels = build_dense_hub_labels(ch)

    for source in graph:
        baseline, _ = dijkstra(graph, source)
        for target in graph:
            query = ch.query(source, target)
            assert query is not None
            distance, path = query
            assert distance == pytest.approx(baseline[target])
            assert path[0] == source
            assert path[-1] == target
            assert labels.distance(source, target) == pytest.approx(
                baseline[target]
            )


def test_greedy_spanner_respects_stretch_on_complete_metric():
    vertices = [0, 1, 2, 3]
    points = {0: 0.0, 1: 1.0, 2: 2.0, 3: 3.0}
    edges = [
        (u, v, abs(points[u] - points[v]))
        for u in vertices
        for v in vertices
        if u < v
    ]
    spanner = greedy_spanner(vertices, edges, stretch=2.0)
    adjacency = {u: [] for u in vertices}
    original = {}
    for u, v, w in edges:
        original[(u, v)] = w
        original[(v, u)] = w
    for u, v, w in spanner:
        adjacency[u].append((v, w))
        adjacency[v].append((u, w))

    for u in vertices:
        dist, _ = dijkstra(adjacency, u)
        for v in vertices:
            if u == v:
                continue
            assert dist[v] <= 2.0 * original[(u, v)] + 1e-12
