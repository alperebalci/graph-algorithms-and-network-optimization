import pytest

from graph_algorithms.covering import (
    konig_minimum_vertex_cover,
    max_cut_local_search,
    vertex_cover_2approx,
)
from graph_algorithms.postman import undirected_chinese_postman
from graph_algorithms.steiner import steiner_tree_2approx


def test_vertex_cover_2approx_is_valid():
    graph = {
        0: [1, 2],
        1: [0, 2],
        2: [0, 1, 3],
        3: [2],
    }
    cover = vertex_cover_2approx(graph)
    for u, neighbors in graph.items():
        for v in neighbors:
            assert u in cover or v in cover


def test_konig_min_vertex_cover_matches_max_matching_size():
    graph = {
        "u1": ["v1", "v2"],
        "u2": ["v1"],
        "u3": ["v2", "v3"],
    }
    cover = konig_minimum_vertex_cover(graph, graph.keys())
    assert len(cover) == 3
    for u, neighbors in graph.items():
        for v in neighbors:
            assert u in cover or v in cover


def test_max_cut_local_search_half_approx_property():
    graph = {
        0: {1: 2.0, 2: 1.0},
        1: {0: 2.0, 2: 3.0},
        2: {0: 1.0, 1: 3.0},
    }
    result = max_cut_local_search(graph)
    assert result.value >= 3.0
    assert result.left.isdisjoint(result.right)
    assert result.left | result.right == {0, 1, 2}


def test_steiner_metric_closure_2approx():
    graph = {
        "a": [("x", 1), ("b", 5)],
        "x": [("a", 1), ("b", 1), ("c", 1)],
        "b": [("x", 1), ("a", 5), ("c", 5)],
        "c": [("x", 1), ("b", 5)],
    }
    result = steiner_tree_2approx(graph, ["a", "b", "c"])
    assert result.value == pytest.approx(3.0)
    assert {"a", "b", "c"} <= result.vertices
    assert "x" in result.vertices


def test_undirected_chinese_postman_duplicates_shortest_odd_pairing():
    graph = {
        0: [(1, 1), (2, 1), (3, 2)],
        1: [(0, 1), (2, 1)],
        2: [(0, 1), (1, 1), (3, 1)],
        3: [(0, 2), (2, 1)],
    }
    result = undirected_chinese_postman(graph, start=0)
    assert result.value == pytest.approx(7.0)
    assert result.circuit[0] == result.circuit[-1] == 0
    assert len(result.duplicated_paths) == 1
