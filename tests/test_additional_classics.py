import pytest

from graph_algorithms.arborescence import minimum_spanning_arborescence
from graph_algorithms.chordal import chordal_perfect_elimination_order, is_chordal
from graph_algorithms.cliques import bron_kerbosch_maximal_cliques, maximum_clique
from graph_algorithms.cycle_optimization import minimum_cycle_mean


def test_chu_liu_edmonds_contracts_cycle():
    vertices = ["r", "a", "b", "c"]
    edges = [
        ("r", "a", 5),
        ("r", "b", 5),
        ("a", "b", 1),
        ("b", "a", 1),
        ("a", "c", 2),
        ("b", "c", 4),
        ("r", "c", 10),
    ]
    cost, tree = minimum_spanning_arborescence(vertices, edges, "r")
    assert cost == pytest.approx(8.0)
    assert len(tree) == len(vertices) - 1
    assert sum(1 for _, v, _ in tree if v == "a") == 1
    assert sum(1 for _, v, _ in tree if v == "b") == 1
    assert sum(1 for _, v, _ in tree if v == "c") == 1


def test_karp_minimum_cycle_mean():
    vertices = [0, 1, 2, 3]
    edges = [
        (0, 1, 2),
        (1, 0, 0),
        (1, 2, 5),
        (2, 3, -2),
        (3, 2, 0),
    ]
    assert minimum_cycle_mean(vertices, edges) == pytest.approx(-1.0)
    assert minimum_cycle_mean([0, 1, 2], [(0, 1, 1), (1, 2, 1)]) is None


def test_bron_kerbosch_and_maximum_clique():
    graph = {
        0: [1, 2],
        1: [0, 2, 3],
        2: [0, 1, 3],
        3: [1, 2],
    }
    maximal = set(bron_kerbosch_maximal_cliques(graph))
    assert frozenset({0, 1, 2}) in maximal
    assert frozenset({1, 2, 3}) in maximal
    assert len(maximum_clique(graph)) == 3


def test_chordality_and_peo():
    chordal = {
        0: [1, 2],
        1: [0, 2, 3],
        2: [0, 1, 3],
        3: [1, 2],
    }
    peo = chordal_perfect_elimination_order(chordal)
    assert peo is not None
    assert set(peo) == set(chordal)
    assert is_chordal(chordal)

    c4 = {
        0: [1, 3],
        1: [0, 2],
        2: [1, 3],
        3: [0, 2],
    }
    assert not is_chordal(c4)
    assert chordal_perfect_elimination_order(c4) is None
