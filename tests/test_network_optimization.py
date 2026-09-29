import itertools

import pytest

from graph_algorithms.exceptions import InfeasibleFlowError
from graph_algorithms.network_optimization import (
    feasible_circulation,
    gomory_hu_tree,
    min_cost_flow,
    min_cost_max_flow,
    minimum_st_cut,
)


def test_minimum_st_cut_matches_classic_max_flow_value():
    capacity = {
        "s": {"v1": 16, "v2": 13},
        "v1": {"v2": 10, "v3": 12},
        "v2": {"v1": 4, "v4": 14},
        "v3": {"v2": 9, "t": 20},
        "v4": {"v3": 7, "t": 4},
        "t": {},
    }
    result = minimum_st_cut(capacity, "s", "t")
    assert result.value == pytest.approx(23.0)
    assert "s" in result.source_side
    assert "t" in result.sink_side
    assert result.source_side.isdisjoint(result.sink_side)
    assert sum(cap for _, _, cap in result.cut_edges) == pytest.approx(
        result.value
    )


def _costed_network():
    capacity = {
        "s": {"a": 2, "b": 1},
        "a": {"b": 1, "t": 1},
        "b": {"t": 2},
        "t": {},
    }
    cost = {
        "s": {"a": 1, "b": 5},
        "a": {"b": 0, "t": 3},
        "b": {"t": 1},
        "t": {},
    }
    return capacity, cost


def test_min_cost_flow_and_min_cost_max_flow():
    capacity, cost = _costed_network()
    fixed = min_cost_flow(capacity, cost, "s", "t", 2)
    assert fixed.flow_value == pytest.approx(2.0)
    assert fixed.cost == pytest.approx(6.0)

    maximum = min_cost_max_flow(capacity, cost, "s", "t")
    assert maximum.flow_value == pytest.approx(3.0)
    assert maximum.cost == pytest.approx(12.0)


def test_min_cost_flow_rejects_infeasible_requested_amount():
    capacity, cost = _costed_network()
    with pytest.raises(InfeasibleFlowError):
        min_cost_flow(capacity, cost, "s", "t", 4)


def test_feasible_circulation_with_lower_bounds():
    lower = {
        "a": {"b": 2},
        "b": {"c": 1},
        "c": {"a": 0},
    }
    upper = {
        "a": {"b": 5},
        "b": {"c": 4},
        "c": {"a": 3},
    }
    result = feasible_circulation(lower, upper)
    assert result.feasible

    for u, neighbors in upper.items():
        for v, up in neighbors.items():
            value = result.flow[u][v]
            assert lower.get(u, {}).get(v, 0) <= value <= up

    for node in upper:
        inflow = sum(
            result.flow[u].get(node, 0.0)
            for u in result.flow
        )
        outflow = sum(result.flow[node].values())
        assert inflow - outflow == pytest.approx(0.0)


def test_circulation_supports_supply_and_demand():
    lower = {"s": {"m": 0}, "m": {"t": 0}, "t": {}}
    upper = {"s": {"m": 3}, "m": {"t": 3}, "t": {}}
    result = feasible_circulation(
        lower,
        upper,
        {"s": -2, "t": 2},
    )
    assert result.feasible
    assert result.flow["s"]["m"] == pytest.approx(2.0)
    assert result.flow["m"]["t"] == pytest.approx(2.0)


def test_infeasible_circulation_returns_false():
    lower = {"s": {"t": 0}, "t": {}}
    upper = {"s": {"t": 1}, "t": {}}
    result = feasible_circulation(
        lower,
        upper,
        {"s": -2, "t": 2},
    )
    assert not result.feasible
    assert result.flow == {}


def test_gomory_hu_tree_reproduces_all_pair_min_cuts():
    graph = {
        0: {1: 3, 2: 1},
        1: {0: 3, 2: 2},
        2: {0: 1, 1: 2},
    }
    tree = gomory_hu_tree(graph)
    assert len(tree.edges) == len(graph) - 1

    directed = {
        u: dict(neighbors)
        for u, neighbors in graph.items()
    }
    for u, v in itertools.combinations(graph, 2):
        direct_cut = minimum_st_cut(directed, u, v).value
        assert tree.minimum_cut_value(u, v) == pytest.approx(direct_cut)
