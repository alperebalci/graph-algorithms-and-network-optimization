import pytest

from graph_algorithms.planarity import (
    faces_from_rotation_system,
    is_planar_boyer_myrvold,
    planar_embedding,
)
from graph_algorithms.tree_algorithms import (
    BinaryLiftingLCA,
    CentroidDecomposition,
    HeavyLightDecomposition,
    euler_tour,
    tarjan_offline_lca,
)


def _tree():
    return {
        0: [1, 2],
        1: [0, 3, 4],
        2: [0, 5, 6],
        3: [1],
        4: [1],
        5: [2],
        6: [2],
    }


def test_tree_algorithms():
    tree = _tree()
    order, tin, tout = euler_tour(tree, 0)
    assert order[0] == 0
    assert tin[1] <= tin[3] <= tout[1]

    lca = BinaryLiftingLCA(tree, 0)
    assert lca.lca(3, 4) == 1
    assert lca.lca(3, 6) == 0
    assert tarjan_offline_lca(
        tree,
        0,
        [(3, 4), (3, 6), (5, 6)],
    ) == [1, 0, 2]

    hld = HeavyLightDecomposition(tree, 0)
    segments = hld.path_segments(3, 6)
    assert 1 <= len(segments) <= 4
    covered_positions = sum(
        hi - lo + 1 for lo, hi in segments
    )
    assert covered_positions >= 5

    cd = CentroidDecomposition(tree)
    roots = [
        u for u, p in cd.parent.items()
        if p is None
    ]
    assert roots == [0]
    assert set(cd.parent) == set(tree)


def test_rotation_system_faces_triangle():
    rotation = {
        0: [1, 2],
        1: [2, 0],
        2: [0, 1],
    }
    faces = faces_from_rotation_system(rotation)
    assert len(faces) == 2
    assert sorted(len(face) for face in faces) == [3, 3]


def test_networkx_boyer_myrvold_reference_adapter():
    pytest.importorskip("networkx")
    k4 = {
        i: [j for j in range(4) if j != i]
        for i in range(4)
    }
    assert is_planar_boyer_myrvold(k4)
    rotation = planar_embedding(k4)
    assert set(rotation) == set(k4)

    k5 = {
        i: [j for j in range(5) if j != i]
        for i in range(5)
    }
    assert not is_planar_boyer_myrvold(k5)
