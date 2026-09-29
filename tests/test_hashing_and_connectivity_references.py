import pytest

from graph_algorithms.hashing import (
    weisfeiler_lehman_graph_hash,
    weisfeiler_lehman_refinement,
)
from graph_algorithms.references import (
    capacity_scaling_min_cost_reference,
    three_vertex_connected_components_reference,
)


def test_wl_hash_is_isomorphism_invariant_on_relabeling():
    triangle_a = {
        0: [1, 2],
        1: [0, 2],
        2: [0, 1],
    }
    triangle_b = {
        "x": ["y", "z"],
        "y": ["x", "z"],
        "z": ["x", "y"],
    }
    path3 = {
        0: [1],
        1: [0, 2],
        2: [1],
    }
    assert (
        weisfeiler_lehman_graph_hash(triangle_a)
        == weisfeiler_lehman_graph_hash(triangle_b)
    )
    assert (
        weisfeiler_lehman_graph_hash(triangle_a)
        != weisfeiler_lehman_graph_hash(path3)
    )
    colors = weisfeiler_lehman_refinement(path3)
    assert colors[0] == colors[2]
    assert colors[0] != colors[1]


def test_capacity_scaling_reference():
    pytest.importorskip("networkx")
    capacity = {
        "s": {"a": 3, "t": 1},
        "a": {"t": 3},
        "t": {},
    }
    cost = {
        "s": {"a": 1, "t": 5},
        "a": {"t": 1},
        "t": {},
    }
    total_cost, flow = capacity_scaling_min_cost_reference(
        capacity,
        cost,
        {"s": -3, "t": 3},
    )
    assert total_cost == pytest.approx(6.0)
    assert flow["s"]["a"] == pytest.approx(3.0)


def test_three_vertex_connected_components_reference():
    nx = pytest.importorskip("networkx")
    graph = {
        u: [v for v in range(4) if v != u]
        for u in range(4)
    }
    components = three_vertex_connected_components_reference(graph)
    assert {frozenset(c) for c in components} == {frozenset(range(4))}
