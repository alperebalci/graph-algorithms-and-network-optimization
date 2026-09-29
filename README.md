# Graph Algorithms and Network Optimization

A tested Python reference repository for **classical graph algorithms**, **network optimization**, and selected **combinatorial approximation algorithms**. The emphasis is not just on collecting names: each implementation makes its graph model, preconditions, complexity, and correctness assumptions explicit.

The repository is designed as the classical-algorithm counterpart to learning-based graph / combinatorial optimization work: exact, polynomial-time, heuristic, approximation, and structural graph methods live here; GNN-based guidance belongs elsewhere.

## What is implemented

### Traversal and search

- BFS and DFS
- Iterative-deepening DFS
- Bidirectional BFS

### Shortest paths

- Dijkstra
- Bellman-Ford with reachable negative-cycle detection
- Floyd-Warshall
- Johnson's all-pairs algorithm
- A*
- Bidirectional Dijkstra
- 0-1 BFS, Dial's algorithm, and DAG shortest paths
- Yen k-shortest loopless paths
- Suurballe two edge-disjoint shortest paths

### Spanning trees, cycles, DAGs, and connectivity

- Prim, Kruskal, and Boruvka MST
- Union-Find / Disjoint Set Union
- Directed and undirected cycle detection
- Kahn and DFS topological sorting
- Connected components
- Kosaraju SCC and Tarjan SCC
- Bridges, articulation points, biconnected components, and block-cut forests
- Transitive closure and DAG transitive reduction
- Lengauer-Tarjan immediate dominators
- Hierholzer Euler paths/circuits

### Network flow and matching

- Ford-Fulkerson
- Edmonds-Karp
- Dinic
- Push-Relabel / Preflow-Push
- Stoer-Wagner deterministic global min-cut
- Karger-Stein randomized global min-cut
- Minimum s-t cut
- Minimum-cost flow for a prescribed flow value
- Minimum-cost maximum flow
- Feasible circulation with lower/upper bounds and node demands
- Gomory-Hu tree for all-pairs minimum cuts in undirected capacitated graphs
- Kuhn bipartite matching
- Hopcroft-Karp
- Hungarian assignment
- Edmonds blossom for unweighted maximum-cardinality matching in general graphs
- Gale-Shapley stable matching

### Dynamic graphs and analytics

- Rollback DSU and offline dynamic connectivity
- Link-Cut Tree with link/cut/connectivity/path-sum operations
- PageRank and HITS
- Brandes betweenness centrality
- k-core decomposition
- NetworkX reference adapters for weighted Blossom, Network Simplex, VF2++, and Louvain
- Optional igraph/leidenalg reference adapter for Leiden community detection

### Coloring

- Greedy coloring
- Welsh-Powell
- Exact `k`-colorability by DSATUR-style backtracking
- Exact chromatic number for small graphs
- Brooks-theorem bound helper

### Approximation

- Metric TSP double-tree 2-approximation
- Christofides 1.5-approximation
- Greedy Set Cover

### Planar and tree algorithms

- Face identification from a rotation system
- Boyer-Myrvold planarity test and planar embedding through an explicit optional NetworkX reference adapter
- Euler tour / subtree intervals
- Binary-lifting LCA
- Tarjan offline LCA
- Heavy-light decomposition
- Centroid decomposition

See [`docs/ALGORITHM_CATALOG.md`](docs/ALGORITHM_CATALOG.md) for status, complexity, caveats, and roadmap items.

## Taxonomy corrections

Several items are often placed under misleading headings in generic graph-algorithm lists. This repository keeps the distinctions explicit:

- **Hungarian** and **Hopcroft-Karp** are matching/assignment algorithms, not max-flow algorithms by definition.
- **Gale-Shapley** solves stable matching; it is not a maximum-cardinality matching algorithm.
- **Brooks' theorem** is a theorem, not a coloring procedure. The code therefore exposes `brooks_bound` rather than a fictional “Brooks algorithm.”
- **Set Cover** is a general combinatorial optimization problem. It is included in approximation methods, with that scope stated directly.
- **R-trees** are spatial indexes rather than graph shortest-path algorithms, so they are not presented as such.
- **Contraction Hierarchies**, **Hub Labeling**, and **SPQR / 3-connected decomposition** are tracked as roadmap items instead of being represented by incomplete stubs.

## Installation

Core implementations have no runtime dependencies:

```bash
python -m pip install -e .
```

For the optional Boyer-Myrvold / planar-embedding reference adapter:

```bash
python -m pip install -e '.[reference]'
```

For development and tests:

```bash
python -m pip install -e '.[dev]'
pytest
```

## Quick example

```python
from graph_algorithms import dijkstra, dinic, hopcroft_karp

weighted_graph = {
    "s": [("a", 2), ("b", 5)],
    "a": [("b", 1), ("t", 5)],
    "b": [("t", 1)],
    "t": [],
}

dist, _ = dijkstra(weighted_graph, "s")
assert dist["t"] == 4

capacity = {
    "s": {"a": 8, "b": 5},
    "a": {"t": 6},
    "b": {"t": 5},
    "t": {},
}
assert dinic(capacity, "s", "t").value == 11

bipartite = {
    "u1": ["v1", "v2"],
    "u2": ["v1"],
    "u3": ["v2", "v3"],
}
assert len(hopcroft_karp(bipartite, bipartite)) == 3
```

More examples are in [`examples/`](examples/).

## Repository layout

```text
src/graph_algorithms/
  traversal.py
  shortest_paths.py
  advanced_shortest_paths.py
  shortest_paths_extra.py
  dag_algorithms.py
  dominators.py
  eulerian.py
  mincuts.py
  structural.py
  dynamic_graphs.py
  link_cut_tree.py
  analytics.py
  references.py
  spanning_trees.py
  cycles_and_dag.py
  connectivity.py
  flow.py
  network_optimization.py
  matching.py
  coloring.py
  approximation.py
  planarity.py
  tree_algorithms.py
  disjoint_set.py

tests/
examples/
docs/
  ALGORITHM_CATALOG.md
  DESIGN.md
.github/workflows/ci.yml
```

## Correctness and test policy

The initial test suite covers traversal, shortest paths, negative-cycle detection, MST agreement, SCC agreement, low-link algorithms, three max-flow implementations on the same benchmark network, minimum cut, min-cost flow, lower-bound circulation, Gomory-Hu trees, bipartite/general matching, coloring, TSP approximations, LCA/tree decompositions, and planarity integration.

A new algorithm should not enter the catalog as “Native” until it has at least one meaningful correctness test and its preconditions are documented. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Current limitations

- The original max-flow API is aimed at standard directed capacity networks; the newer network-optimization residual engine separately supports antiparallel arcs for min-cut, circulation, min-cost flow, and Gomory-Hu reductions.
- The min-cost routines use successive shortest augmenting paths with Bellman-Ford. They support negative edge costs but reject a reachable negative-cost residual cycle instead of silently returning a non-optimal result.
- Christofides uses exact subset-DP minimum-weight perfect matching to remain self-contained. This preserves the approximation guarantee but makes that step exponential in the number of odd-degree MST vertices, so it is an educational/small-instance implementation rather than a large-scale TSP engine.
- The planarity test/embedding is explicitly delegated to NetworkX; face walking from an already-known embedding is native.
- Contraction Hierarchies, Customizable Contraction Hierarchies, Hub Labeling, SPQR decomposition, native weighted Blossom, cost-scaling min-cost flow, and native Network Simplex remain advanced roadmap items; reference adapters are used where explicitly documented.

## License

MIT
