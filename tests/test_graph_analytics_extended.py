import pytest

from graph_algorithms.analytics import (
    label_propagation_communities,
    personalized_pagerank,
    triangle_count,
)


def test_personalized_pagerank_biases_teleport_target():
    graph = {
        0: [1],
        1: [0, 2],
        2: [1],
    }
    rank = personalized_pagerank(graph, {0: 1.0})
    assert sum(rank.values()) == pytest.approx(1.0)
    assert rank[0] > rank[2]


def test_triangle_count_global_and_local():
    graph = {
        0: [1, 2],
        1: [0, 2, 3],
        2: [0, 1, 3],
        3: [1, 2],
    }
    total, local = triangle_count(graph)
    assert total == 2
    assert local == {0: 1, 1: 2, 2: 2, 3: 1}


def test_label_propagation_finds_disconnected_groups():
    graph = {
        0: [1],
        1: [0],
        2: [3],
        3: [2],
    }
    communities = {
        frozenset(c)
        for c in label_propagation_communities(graph)
    }
    assert communities == {
        frozenset({0, 1}),
        frozenset({2, 3}),
    }
