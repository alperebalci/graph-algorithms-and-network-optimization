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


## Costed flow networks

Minimum-cost flow uses two nested mappings with the same directed edge set:

```python
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
```

A cost is required for every capacity edge. Negative edge costs are allowed, but a reachable negative-cost residual cycle is rejected because ordinary successive-shortest-path augmentation would otherwise need an additional cycle-canceling phase.

## Circulation with lower bounds and demands

`feasible_circulation(lower, upper, demands)` uses the convention

```text
inflow(v) - outflow(v) = demand(v)
```

so a positive demand consumes flow and a negative demand supplies flow. The implementation subtracts lower bounds and reduces feasibility to one super-source/super-sink max-flow problem.

## Gomory-Hu input

`gomory_hu_tree` expects a non-negative undirected capacity graph represented as a nested mapping. Each undirected edge may be listed once or symmetrically in both directions. If both directions are listed, their capacities must agree.
