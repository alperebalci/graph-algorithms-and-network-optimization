import pytest

from graph_algorithms.analytics import (
    brandes_betweenness_centrality,
    core_numbers,
    hits,
    pagerank,
)
from graph_algorithms.dynamic_graphs import (
    RollbackDisjointSet,
    offline_dynamic_connectivity,
)
from graph_algorithms.link_cut_tree import LinkCutTree
from graph_algorithms.references import (
    louvain_communities_reference,
    network_simplex_reference,
    vf2pp_isomorphism_reference,
    weighted_blossom_matching_reference,
)


def test_rollback_dsu_and_offline_dynamic_connectivity():
    dsu = RollbackDisjointSet([1, 2, 3])
    snap = dsu.snapshot()
    dsu.union(1, 2)
    assert dsu.connected(1, 2)
    dsu.rollback(snap)
    assert not dsu.connected(1, 2)

    operations = [
        ("add", "a", "b"),
        ("query", "a", "c"),
        ("add", "b", "c"),
        ("query", "a", "c"),
        ("remove", "a", "b"),
        ("query", "a", "c"),
    ]
    assert offline_dynamic_connectivity(operations) == [False, True, False]


def test_link_cut_tree_dynamic_forest_and_path_sum():
    tree = LinkCutTree()
    for node, value in [(1, 1), (2, 2), (3, 3), (4, 4)]:
        tree.add(node, value)

    tree.link(1, 2)
    tree.link(2, 3)
    assert tree.connected(1, 3)
    assert not tree.connected(1, 4)
    assert tree.path_sum(1, 3) == pytest.approx(6.0)

    tree.set_value(2, 5)
    assert tree.path_sum(1, 3) == pytest.approx(9.0)

    tree.cut(2, 3)
    assert not tree.connected(1, 3)
    tree.link(3, 4)
    assert tree.path_sum(3, 4) == pytest.approx(7.0)


def test_native_graph_analytics():
    directed = {
        "a": ["b"],
        "b": ["c"],
        "c": ["a"],
        "d": ["c"],
    }
    rank = pagerank(directed)
    assert sum(rank.values()) == pytest.approx(1.0)
    assert rank["c"] > rank["d"]

    hubs, authorities = hits(directed)
    assert set(hubs) == set(authorities) == set(directed)

    path = {
        0: [1],
        1: [0, 2],
        2: [1, 3],
        3: [2],
    }
    centrality = brandes_betweenness_centrality(path)
    assert centrality[1] == pytest.approx(2 / 3)
    assert centrality[2] == pytest.approx(2 / 3)
    assert centrality[0] == centrality[3] == 0

    cores = core_numbers(path)
    assert cores == {0: 1, 1: 1, 2: 1, 3: 1}


def test_networkx_reference_adapters():
    pytest.importorskip("networkx")

    weighted = {
        "a": [("b", 5), ("c", 1)],
        "b": [("a", 5), ("c", 4)],
        "c": [("a", 1), ("b", 4)],
    }
    matching = weighted_blossom_matching_reference(
        weighted, max_cardinality=True
    )
    assert len(matching) == 1

    g1 = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    g2 = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
    mapping = vf2pp_isomorphism_reference(g1, g2)
    assert mapping is not None
    assert set(mapping) == set(g1)
    assert set(mapping.values()) == set(g2)

    capacity = {"s": {"t": 3}, "t": {}}
    cost = {"s": {"t": 2}, "t": {}}
    total_cost, flow = network_simplex_reference(
        capacity,
        cost,
        {"s": -2, "t": 2},
    )
    assert total_cost == pytest.approx(4.0)
    assert flow["s"]["t"] == pytest.approx(2.0)

    communities = louvain_communities_reference(
        {
            0: [(1, 5), (2, 5)],
            1: [(0, 5), (2, 5)],
            2: [(0, 5), (1, 5), (3, 0.1)],
            3: [(2, 0.1), (4, 5), (5, 5)],
            4: [(3, 5), (5, 5)],
            5: [(3, 5), (4, 5)],
        },
        seed=1,
    )
    assert sorted(len(c) for c in communities) == [3, 3]
