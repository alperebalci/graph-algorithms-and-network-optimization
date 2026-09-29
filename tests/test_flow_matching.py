from graph_algorithms.flow import (
    dinic,
    edmonds_karp,
    ford_fulkerson,
)
from graph_algorithms.matching import (
    blossom_maximum_cardinality_matching,
    gale_shapley,
    hopcroft_karp,
    hungarian,
    kuhn_maximum_bipartite_matching,
)


def test_max_flow_algorithms_agree_on_classic_network():
    capacity = {
        "s": {"v1": 16, "v2": 13},
        "v1": {"v2": 10, "v3": 12},
        "v2": {"v1": 4, "v4": 14},
        "v3": {"v2": 9, "t": 20},
        "v4": {"v3": 7, "t": 4},
        "t": {},
    }
    for solver in (ford_fulkerson, edmonds_karp, dinic):
        assert solver(capacity, "s", "t").value == 23


def test_bipartite_matching_algorithms():
    graph = {
        "u1": ["v1", "v2"],
        "u2": ["v1"],
        "u3": ["v2", "v3"],
    }
    left = list(graph)
    assert len(kuhn_maximum_bipartite_matching(graph, left)) == 3
    assert len(hopcroft_karp(graph, left)) == 3


def test_hungarian_assignment():
    cost = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    total, assignment = hungarian(cost)
    assert total == 5
    assert len(set(assignment)) == 3


def test_gale_shapley_is_stable_for_example():
    proposers = {
        "A": ["X", "Y", "Z"],
        "B": ["Y", "X", "Z"],
        "C": ["Y", "Z", "X"],
    }
    receivers = {
        "X": ["B", "A", "C"],
        "Y": ["A", "B", "C"],
        "Z": ["A", "C", "B"],
    }
    matching = gale_shapley(proposers, receivers)
    assert set(matching) == set(proposers)
    assert len(set(matching.values())) == 3

    inv = {r: p for p, r in matching.items()}
    rank_p = {
        p: {r: i for i, r in enumerate(pref)}
        for p, pref in proposers.items()
    }
    rank_r = {
        r: {p: i for i, p in enumerate(pref)}
        for r, pref in receivers.items()
    }
    for p in proposers:
        for r in receivers:
            if rank_p[p][r] < rank_p[p][matching[p]]:
                assert not (
                    rank_r[r][p] < rank_r[r][inv[r]]
                )


def test_blossom_handles_odd_cycle():
    c5 = {
        0: [1, 4],
        1: [0, 2],
        2: [1, 3],
        3: [2, 4],
        4: [3, 0],
    }
    matching = blossom_maximum_cardinality_matching(c5)
    assert len(matching) == 2
    touched = [u for edge in matching for u in edge]
    assert len(touched) == len(set(touched))


def test_blossom_on_triangle_with_tail():
    g = {
        0: [1, 2],
        1: [0, 2],
        2: [0, 1, 3],
        3: [2],
    }
    matching = blossom_maximum_cardinality_matching(g)
    assert len(matching) == 2
