# Algorithm catalog

Status meanings:

- **Native** — implemented in this repository without calling a graph-algorithm library.
- **Reference adapter** — deliberately delegated to an optional external implementation and clearly marked.
- **Roadmap** — in scope, but not yet implemented because a correct implementation deserves dedicated tests and documentation.

| Area | Algorithm / method | Status | Main complexity / note |
|---|---|---:|---|
| Traversal | BFS | Native | `O(V+E)` |
| Traversal | DFS | Native | `O(V+E)` |
| Traversal | Iterative deepening DFS | Native | depth-limited repeated DFS |
| Traversal | Bidirectional BFS | Native | shortest path in unweighted undirected graphs |
| Shortest path | Dijkstra | Native | `O((V+E) log V)`, non-negative weights |
| Shortest path | Bellman-Ford | Native | `O(VE)`, negative-edge support |
| Shortest path | Floyd-Warshall | Native | `O(V^3)`, all pairs |
| Shortest path | Johnson | Native | sparse all-pairs, negative edges allowed without negative cycles |
| Shortest path | A* | Native | optimal under an admissible heuristic |
| Shortest path | Bidirectional Dijkstra | Native | non-negative weighted graphs |
| Advanced routing | Contraction Hierarchies | Roadmap | preprocessing + very fast queries |
| Advanced routing | Hub Labeling | Roadmap | label construction and query trade-offs |
| MST | Prim | Native | `O(E log V)` |
| MST | Kruskal | Native | `O(E log E)` + DSU |
| Connectivity | Connected components | Native | `O(V+E)` |
| Connectivity | Kosaraju SCC | Native | `O(V+E)` |
| Connectivity | Tarjan SCC | Native | `O(V+E)` |
| Connectivity | Bridges | Native | Tarjan low-link, `O(V+E)` |
| Connectivity | Articulation points | Native | Tarjan low-link, `O(V+E)` |
| Connectivity | Biconnected components | Native | Tarjan edge stack |
| Connectivity | 3-connected / SPQR decomposition | Roadmap | substantially more involved than biconnected components |
| DAG / cycles | Directed cycle detection | Native | DFS colors |
| DAG / cycles | Undirected cycle detection | Native | DFS and DSU variants |
| DAG / cycles | Kahn topological sort | Native | `O(V+E)` |
| DAG / cycles | DFS topological sort | Native | `O(V+E)` |
| Max flow | Ford-Fulkerson | Native | DFS augmenting paths; integer-capacity termination guarantee |
| Max flow | Edmonds-Karp | Native | `O(VE^2)` |
| Max flow | Dinic | Native | `O(V^2E)` general bound |
| Network optimization | Minimum s-t cut | Native | max-flow/min-cut using Dinic residual reachability |
| Network optimization | Minimum-cost flow | Native | prescribed flow value; Bellman-Ford shortest augmenting paths |
| Network optimization | Minimum-cost maximum flow | Native | successive shortest augmenting paths until no s-t path remains |
| Network optimization | Feasible circulation | Native | lower/upper bounds + node demands via super-source/super-sink reduction |
| Network optimization | Gomory-Hu tree | Native | all-pairs undirected min-cut representation using `V-1` s-t min-cut calls |
| Matching | Kuhn | Native | bipartite matching via DFS augmentations |
| Matching | Hopcroft-Karp | Native | `O(E sqrt(V))` |
| Matching | Hungarian | Native | rectangular min-cost assignment, rows <= columns |
| Matching | Edmonds blossom | Native | unweighted maximum-cardinality general matching, `O(V^3)` |
| Matching | Gale-Shapley | Native | stable matching, `O(n^2)` |
| Coloring | Greedy coloring | Native | order-dependent heuristic |
| Coloring | Welsh-Powell | Native | degree-ordered greedy heuristic |
| Coloring | Exact k-colorability | Native | DSATUR-style backtracking; exponential worst case |
| Coloring | Exact chromatic number | Native | repeated exact k-colorability; small graphs |
| Coloring | Brooks theorem bound | Native helper | theorem-derived upper bound, not a coloring algorithm |
| Approximation | Metric TSP double-tree | Native | 2-approximation under triangle inequality |
| Approximation | Christofides | Native | 1.5-approximation; MWPM step uses exact subset DP in this educational implementation |
| Approximation | Greedy Set Cover | Native | `H_n` approximation; not graph-specific |
| Planarity | Boyer-Myrvold test | Reference adapter | optional NetworkX dependency |
| Planarity | Planar embedding | Reference adapter | optional NetworkX dependency |
| Planarity | Face identification | Native | rotation-system face walk |
| Tree algorithms | Euler tour / subtree intervals | Native | `O(V)` |
| Tree algorithms | Binary-lifting LCA | Native | preprocess `O(V log V)`, query `O(log V)` |
| Tree algorithms | Tarjan offline LCA | Native | near-linear batch LCA |
| Tree algorithms | Heavy-light decomposition | Native | path decomposition into `O(log V)` segments |
| Tree algorithms | Centroid decomposition | Native | `O(V log V)` |
| Spatial indexing | R-tree | Out of scope | spatial index, not itself a graph shortest-path algorithm |

## Why some advanced entries remain roadmap items

The repository favors complete, testable implementations over name coverage. Contraction Hierarchies, Hub Labeling, and SPQR decomposition require non-trivial preprocessing invariants and deserve their own focused benchmark/test suites. They are explicitly tracked rather than represented by placeholders that merely raise `NotImplementedError`.
