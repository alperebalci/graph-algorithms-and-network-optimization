import pytest

from graph_algorithms.connectivity import (
    articulation_points,
    biconnected_components,
    bridges,
    connected_components,
    kosaraju_scc,
    tarjan_scc,
)
from graph_algorithms.cycles_and_dag import (
    has_cycle_directed,
    has_cycle_undirected_dfs,
    has_cycle_undirected_dsu,
    topological_sort_dfs,
    topological_sort_kahn,
)
from graph_algorithms.spanning_trees import kruskal, prim


def test_mst_prim_and_kruskal():
    g = {
        "a": [("b", 1), ("c", 4)],
        "b": [("a", 1), ("c", 2), ("d", 5)],
        "c": [("a", 4), ("b", 2), ("d", 1)],
        "d": [("b", 5), ("c", 1)],
    }
    edges = [
        ("a", "b", 1),
        ("a", "c", 4),
        ("b", "c", 2),
        ("b", "d", 5),
        ("c", "d", 1),
    ]
    assert prim(g)[0] == 4
    assert kruskal(g.keys(), edges)[0] == 4


def test_cycles_and_topological_sort():
    undirected = {0: [1], 1: [0, 2], 2: [1]}
    assert not has_cycle_undirected_dfs(undirected)
    assert not has_cycle_undirected_dsu(
        [0, 1, 2], [(0, 1), (1, 2)]
    )
    assert has_cycle_undirected_dsu(
        [0, 1, 2], [(0, 1), (1, 2), (2, 0)]
    )

    dag = {0: [1, 2], 1: [3], 2: [3], 3: []}
    assert not has_cycle_directed(dag)
    for sorter in (topological_sort_kahn, topological_sort_dfs):
        order = sorter(dag)
        pos = {u: i for i, u in enumerate(order)}
        assert all(
            pos[u] < pos[v]
            for u, vs in dag.items()
            for v in vs
        )

    cyclic = {0: [1], 1: [2], 2: [0]}
    assert has_cycle_directed(cyclic)
    with pytest.raises(ValueError):
        topological_sort_kahn(cyclic)


def test_components_scc_bridges_articulation_and_biconnected():
    ug = {
        0: [1, 2],
        1: [0, 2, 3],
        2: [0, 1],
        3: [1, 4, 5],
        4: [3, 5],
        5: [3, 4, 6],
        6: [5],
        7: [],
    }
    comps = [frozenset(c) for c in connected_components(ug)]
    assert frozenset({7}) in comps
    assert frozenset(range(7)) in comps
    assert {frozenset(e) for e in bridges(ug)} == {
        frozenset((1, 3)),
        frozenset((5, 6)),
    }
    assert articulation_points(ug) == {1, 3, 5}
    blocks = biconnected_components(ug)
    assert len(blocks) >= 4

    dg = {0: [1], 1: [2, 3], 2: [0], 3: [4], 4: [3]}
    expected = {
        frozenset({0, 1, 2}),
        frozenset({3, 4}),
    }
    assert {frozenset(c) for c in kosaraju_scc(dg)} == expected
    assert {frozenset(c) for c in tarjan_scc(dg)} == expected
