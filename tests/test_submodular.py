import math

from graph_algorithms import (
    coverage_value,
    exact_maximum_coverage,
    greedy_maximum_coverage,
    marginal_gain,
)


def test_diminishing_returns_for_coverage_function():
    sets = [
        {1, 2, 3},
        {3, 4},
        {4, 5, 6},
        {1, 6},
    ]
    small = (0,)
    large = (0, 1)
    candidate = 2
    assert marginal_gain(small, candidate, sets) >= marginal_gain(
        large, candidate, sets
    )


def test_greedy_maximum_coverage_meets_classical_guarantee_on_fixture():
    sets = [
        {1, 2, 3, 4},
        {3, 4, 5, 6},
        {5, 6, 7, 8},
        {1, 8, 9},
        {9, 10},
    ]
    greedy = greedy_maximum_coverage(sets, budget=2)
    optimum = exact_maximum_coverage(sets, budget=2)
    assert greedy.value >= (1.0 - 1.0 / math.e) * optimum.value - 1e-12
    assert greedy.value <= optimum.value + 1e-12


def test_weighted_coverage_and_exact_oracle():
    sets = [{"a", "b"}, {"b", "c"}, {"d"}]
    weights = {"a": 5.0, "b": 1.0, "c": 4.0, "d": 3.0}
    exact = exact_maximum_coverage(sets, budget=1, weights=weights)
    assert exact.selected == (0,)
    assert coverage_value(exact.selected, sets, weights) == 6.0
