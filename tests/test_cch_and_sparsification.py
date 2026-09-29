import pytest

from graph_algorithms.routing import (
    build_cch_topology,
    build_customizable_contraction_hierarchy,
    customize_contraction_hierarchy,
)
from graph_algorithms.shortest_paths import dijkstra
from graph_algorithms.sparsification import effective_resistance_sparsifier


def _graph(weight_03=10.0):
    return {
        0: [(1, 2.0), (2, 5.0), (3, weight_03)],
        1: [(0, 2.0), (2, 1.0), (3, 4.0)],
        2: [(0, 5.0), (1, 1.0), (3, 1.0)],
        3: [(0, weight_03), (1, 4.0), (2, 1.0), (4, 2.0)],
        4: [(3, 2.0)],
    }


def test_cch_matches_dijkstra_all_pairs():
    graph = _graph()
    order = [0, 4, 1, 3, 2]
    cch = build_customizable_contraction_hierarchy(graph, order)

    for source in graph:
        baseline, _ = dijkstra(graph, source)
        for target in graph:
            result = cch.query(source, target)
            assert result is not None
            distance, path = result
            assert distance == pytest.approx(baseline[target])
            assert path[0] == source
            assert path[-1] == target


def test_cch_recustomizes_without_rebuilding_topology():
    base = _graph(weight_03=10.0)
    changed = _graph(weight_03=0.5)
    order = [0, 4, 1, 3, 2]
    topology = build_cch_topology(base, order)

    first = customize_contraction_hierarchy(topology, base)
    second = customize_contraction_hierarchy(topology, changed)

    assert first.query(0, 4)[0] == pytest.approx(6.0)
    assert second.query(0, 4)[0] == pytest.approx(2.5)
    assert first.topology.edges == second.topology.edges


def test_effective_resistance_sparsifier_full_sampling_at_high_rate():
    pytest.importorskip("numpy")
    graph = {
        0: {1: 1.0, 2: 1.0},
        1: {0: 1.0, 2: 1.0},
        2: {0: 1.0, 1: 1.0},
    }
    result = effective_resistance_sparsifier(
        graph,
        epsilon=0.5,
        oversampling=100.0,
        seed=1,
    )
    assert result.graph == graph
    assert all(p == 1.0 for p in result.probabilities.values())
    # Effective resistance of an edge in K3 with unit conductances is 2/3.
    assert all(
        resistance == pytest.approx(2.0 / 3.0)
        for resistance in result.effective_resistances.values()
    )
