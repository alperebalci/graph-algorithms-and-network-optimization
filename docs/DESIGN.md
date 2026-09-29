# Design and graph representations

The package intentionally avoids a single heavyweight graph object. Algorithms accept ordinary Python mappings so the mathematical structure stays visible and test fixtures stay small.

## Unweighted adjacency

```python
{
    "a": ["b", "c"],
    "b": ["a"],
    "c": ["a"],
}
```

For undirected algorithms, both directions should be present unless the function explicitly takes an edge list.

## Weighted adjacency

```python
{
    "a": [("b", 1.5), ("c", 3.0)],
    "b": [("c", 0.5)],
    "c": [],
}
```

Dijkstra, A*, Prim, and bidirectional Dijkstra use this representation.

## Edge lists

Bellman-Ford, Floyd-Warshall, Johnson, and Kruskal use `(u, v, weight)` triples where that representation makes the algorithm simpler and less ambiguous.

## Capacity networks

```python
{
    "s": {"a": 10, "b": 5},
    "a": {"t": 7},
    "b": {"t": 5},
    "t": {},
}
```

The max-flow implementations operate on directed capacities and construct residual networks internally.

## Metric TSP matrices

The TSP approximation implementations use a complete symmetric nested mapping. With `validate_metric=True` (the default), they verify non-negativity, symmetry, zero diagonal, completeness, and the triangle inequality.

## Planar embeddings

`faces_from_rotation_system` accepts a rotation system: for each vertex, the cyclic order of its neighbors in a planar embedding. This is a combinatorial embedding and is independent of geometric coordinates.

## Scope discipline

Some names commonly placed in a generic “graph algorithms” list need qualification:

- Hungarian is an assignment / bipartite matching algorithm, not intrinsically a max-flow algorithm.
- Gale-Shapley solves stable matching, not maximum-cardinality matching.
- Brooks' theorem is a structural theorem, not a coloring algorithm; the package exposes `brooks_bound` rather than pretending otherwise.
- Set Cover is a general combinatorial optimization problem; its greedy approximation is included because it is often taught alongside graph approximation algorithms.
- R-trees are spatial indexes, not shortest-path algorithms.
- Boyer-Myrvold is sufficiently intricate that v0.1 exposes an explicit NetworkX reference adapter rather than a misleading partial reimplementation.
