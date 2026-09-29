import itertools

import pytest

from graph_algorithms.dag_algorithms import (
    transitive_closure,
    transitive_reduction_dag,
)
from graph_algorithms.dominators import lengauer_tarjan_dominators
from graph_algorithms.eulerian import hierholzer_eulerian_path
from graph_algorithms.flow import dinic, push_relabel
from graph_algorithms.mincuts import (
    karger_stein_min_cut,
    stoer_wagner_min_cut,
)
from graph_algorithms.shortest_paths_extra import (
    dag_shortest_paths,
    dial_shortest_paths,
    suurballe_two_edge_disjoint_paths,
    yen_k_shortest_paths,
    zero_one_bfs,
)
from graph_algorithms.spanning_trees import boruvka, kruskal
from graph_algorithms.structural import BlockNode, block_cut_forest


def test_push_relabel_matches_dinic():
    capacity = {
        "s": {"a": 10, "b": 5},
        "a": {"b": 15, "t": 10},
        "b": {"t": 10},
        "t": {},
    }
    assert push_relabel(capacity, "s", "t").value == pytest.approx(
        dinic(capacity, "s", "t").value
    )


def test_stoer_wagner_and_karger_stein_global_min_cut():
    graph = {
        0: {1: 3, 2: 1},
        1: {0: 3, 2: 2},
        2: {0: 1, 1: 2},
    }
    exact = stoer_wagner_min_cut(graph)
    randomized = karger_stein_min_cut(graph, seed=7, trials=4)
    assert exact.value == pytest.approx(3.0)
    assert randomized.value == pytest.approx(exact.value)
    assert exact.left.isdisjoint(exact.right)
    assert exact.left | exact.right == set(graph)


def test_boruvka_matches_kruskal():
    vertices = list("abcd")
    edges = [
        ("a", "b", 1),
        ("a", "c", 4),
        ("b", "c", 2),
        ("b", "d", 5),
        ("c", "d", 1),
    ]
    assert boruvka(vertices, edges)[0] == kruskal(vertices, edges)[0] == 4


def test_hierholzer_undirected_and_directed():
    undirected = [(0, 1), (1, 2), (2, 0)]
    path = hierholzer_eulerian_path(undirected)
    assert path[0] == path[-1]
    assert len(path) == len(undirected) + 1

    directed = [("s", "a"), ("a", "b"), ("b", "a"), ("a", "t")]
    path = hierholzer_eulerian_path(directed, directed=True)
    assert path[0] == "s"
    assert path[-1] == "t"
    assert len(path) == len(directed) + 1


def test_specialized_shortest_paths():
    g01 = {
        "s": [("a", 0), ("b", 1)],
        "a": [("b", 0), ("t", 1)],
        "b": [("t", 0)],
        "t": [],
    }
    dist01, _ = zero_one_bfs(g01, "s")
    assert dist01["t"] == 0

    gint = {
        "s": [("a", 2), ("b", 5)],
        "a": [("b", 1), ("t", 5)],
        "b": [("t", 1)],
        "t": [],
    }
    dist_dial, _ = dial_shortest_paths(gint, "s")
    assert dist_dial["t"] == 4

    dag = {
        "s": [("a", 2), ("b", 4)],
        "a": [("b", -3), ("t", 5)],
        "b": [("t", 2)],
        "t": [],
    }
    dist_dag, _ = dag_shortest_paths(dag, "s")
    assert dist_dag["t"] == 1


def test_yen_k_shortest_loopless_paths():
    graph = {
        "s": [("a", 1), ("b", 1)],
        "a": [("t", 1), ("b", 1)],
        "b": [("t", 1), ("a", 1)],
        "t": [],
    }
    paths = yen_k_shortest_paths(graph, "s", "t", 4)
    assert len(paths) == 4
    assert [cost for cost, _ in paths] == [2.0, 2.0, 3.0, 3.0]
    assert len({tuple(path) for _, path in paths}) == 4
    assert all(len(path) == len(set(path)) for _, path in paths)


def test_suurballe_two_edge_disjoint_paths():
    graph = {
        "s": [("a", 1), ("b", 1)],
        "a": [("c", 1), ("t", 4)],
        "b": [("c", 1), ("t", 4)],
        "c": [("t", 1)],
        "t": [],
    }
    result = suurballe_two_edge_disjoint_paths(graph, "s", "t")
    assert result is not None
    (_, p1), (_, p2) = result
    e1 = set(zip(p1, p1[1:]))
    e2 = set(zip(p2, p2[1:]))
    assert e1.isdisjoint(e2)
    assert p1[0] == p2[0] == "s"
    assert p1[-1] == p2[-1] == "t"


def test_transitive_closure_and_reduction():
    dag = {
        0: [1, 2, 3],
        1: [2, 3],
        2: [3],
        3: [],
    }
    closure = transitive_closure(dag)
    assert closure[0] == {1, 2, 3}
    reduced = transitive_reduction_dag(dag)
    assert reduced == {0: [1], 1: [2], 2: [3], 3: []}
    assert transitive_closure(reduced) == closure


def test_lengauer_tarjan_dominators():
    graph = {
        "s": ["a", "b"],
        "a": ["c"],
        "b": ["c"],
        "c": ["d"],
        "d": [],
    }
    idom = lengauer_tarjan_dominators(graph, "s")
    assert idom["s"] == "s"
    assert idom["a"] == "s"
    assert idom["b"] == "s"
    assert idom["c"] == "s"
    assert idom["d"] == "c"


def test_block_cut_forest():
    graph = {
        0: [1, 2],
        1: [0, 2, 3],
        2: [0, 1],
        3: [1, 4],
        4: [3],
        5: [],
    }
    forest = block_cut_forest(graph)
    assert forest.articulation_vertices == frozenset({1, 3})
    assert frozenset({5}) in forest.blocks
    for articulation in forest.articulation_vertices:
        assert articulation in forest.adjacency
        assert all(
            isinstance(node, BlockNode)
            for node in forest.adjacency[articulation]
        )
