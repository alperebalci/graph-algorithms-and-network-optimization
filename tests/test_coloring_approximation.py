import pytest

from graph_algorithms.approximation import (
    christofides_tsp,
    greedy_set_cover,
    metric_tsp_2approx,
)
from graph_algorithms.coloring import (
    brooks_bound,
    exact_chromatic_number,
    is_valid_coloring,
    k_color_backtracking,
    welsh_powell_coloring,
)


def test_coloring_cycle_and_complete_graph():
    c5 = {
        i: [(i - 1) % 5, (i + 1) % 5]
        for i in range(5)
    }
    coloring = welsh_powell_coloring(c5)
    assert is_valid_coloring(c5, coloring)
    assert k_color_backtracking(c5, 2) is None
    chi, exact = exact_chromatic_number(c5)
    assert chi == 3 and is_valid_coloring(c5, exact)
    assert brooks_bound(c5) == 3

    k4 = {
        i: [j for j in range(4) if j != i]
        for i in range(4)
    }
    assert exact_chromatic_number(k4)[0] == 4
    assert brooks_bound(k4) == 4


def _square_metric():
    pts = {
        0: (0, 0),
        1: (1, 0),
        2: (1, 1),
        3: (0, 1),
    }
    return {
        i: {
            j: (
                abs(pts[i][0] - pts[j][0])
                + abs(pts[i][1] - pts[j][1])
            )
            for j in pts
        }
        for i in pts
    }


def test_tsp_approximations_return_hamiltonian_cycles():
    dist = _square_metric()
    for solver in (metric_tsp_2approx, christofides_tsp):
        cost, tour = solver(dist, start=0)
        assert tour[0] == tour[-1] == 0
        assert set(tour[:-1]) == set(dist)
        assert len(tour) == len(dist) + 1
        assert cost == pytest.approx(4.0)


def test_greedy_set_cover_and_uncovered_report():
    universe = {1, 2, 3, 4, 5}
    subsets = {
        "A": {1, 2, 3},
        "B": {2, 4},
        "C": {3, 4, 5},
    }
    chosen, uncovered = greedy_set_cover(universe, subsets)
    assert uncovered == set()
    covered = set().union(
        *(subsets[name] for name in chosen)
    )
    assert universe <= covered
