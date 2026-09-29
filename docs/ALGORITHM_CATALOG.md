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
| Shortest path | 0-1 BFS | Native | `O(V+E)`, weights in {0,1} |
| Shortest path | Dial | Native | `O(E + VC)` for bounded non-negative integer weights |
| Shortest path | DAG shortest path | Native | `O(V+E)`, negative weights allowed in DAGs |
| k-shortest path | Yen | Native | loopless k-shortest paths |
| Disjoint paths | Suurballe | Native | two edge-disjoint shortest directed paths |
| Advanced routing | ALT / Landmark A* | Native | landmark lower bounds + A* |
| Advanced routing | Contraction Hierarchies | Native | exact, naive witness-search educational implementation |
| Advanced routing | Dense CH Hub Labeling | Native | exact unpruned 2-hop labels derived from CH |
| Advanced routing | Customizable Contraction Hierarchies | Native | metric-independent fill topology + repeatable basic customization |
| Advanced routing | Optimized Hub Labeling | Roadmap | pruning/order engineering for compact labels |
| Sparse graphs | Greedy weighted spanner | Native | t-spanner by shortest-path edge filtering |
| Sparse graphs | Effective-resistance spectral sparsifier | Native optional | dense Laplacian pseudoinverse + leverage-score sampling |
| MST | Prim | Native | `O(E log V)` |
| MST | Kruskal | Native | `O(E log E)` + DSU |
| MST | Boruvka | Native | `O(E log V)` |
| Directed branching | Chu-Liu/Edmonds arborescence | Native | cycle contraction; directed MST analogue |
| Cycle optimization | Karp minimum mean cycle | Native | `O(VE)` |
| Eulerian | Hierholzer | Native | `O(V+E)`, directed/undirected, parallel-edge support |
| Connectivity | Connected components | Native | `O(V+E)` |
| Connectivity | Kosaraju SCC | Native | `O(V+E)` |
| Connectivity | Tarjan SCC | Native | `O(V+E)` |
| Connectivity | Bridges | Native | Tarjan low-link, `O(V+E)` |
| Connectivity | Articulation points | Native | Tarjan low-link, `O(V+E)` |
| Connectivity | Biconnected components | Native | Tarjan edge stack |
| Connectivity | Block-cut forest | Native | derived from biconnected blocks + articulation vertices |
| Connectivity | 3-connected / SPQR decomposition | Roadmap | substantially more involved than biconnected components |
| Matching | Native weighted Blossom | Roadmap | reference adapter exists; native primal-dual blossom remains |
| Min-cost flow | Cost scaling | Roadmap | epsilon-scaling / push-relabel family |
| Min-cost flow | Native Network Simplex | Roadmap | reference adapter exists |
| DAG / cycles | Directed cycle detection | Native | DFS colors |
| DAG / cycles | Undirected cycle detection | Native | DFS and DSU variants |
| DAG / cycles | Kahn topological sort | Native | `O(V+E)` |
| DAG / cycles | DFS topological sort | Native | `O(V+E)` |
| DAG / reachability | Transitive closure | Native | repeated DFS |
| DAG / reachability | Transitive reduction | Native | unique reduction for DAGs |
| Directed structure | Lengauer-Tarjan dominators | Native | immediate dominators from a start vertex |
| Chordal graphs | Maximum Cardinality Search | Native | MCS ordering + chordality recognition |
| Cliques | Bron-Kerbosch with pivoting | Native | maximal clique enumeration |
| Cliques | Maximum clique | Native exact | maximum over maximal cliques; exponential worst case |
| Max flow | Ford-Fulkerson | Native | DFS augmenting paths; integer-capacity termination guarantee |
| Max flow | Edmonds-Karp | Native | `O(VE^2)` |
| Max flow | Dinic | Native | `O(V^2E)` general bound |
| Max flow | Push-Relabel | Native | FIFO preflow-push, `O(V^2E)` worst-case |
| Global min-cut | Stoer-Wagner | Native | deterministic weighted undirected min-cut, `O(V^3)` |
| Global min-cut | Karger-Stein | Native | randomized contraction; exact base cases |
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
| Matching | Weighted Blossom | Reference adapter | NetworkX max-weight matching |
| Min-cost flow | Network Simplex | Reference adapter | NetworkX network simplex |
| Isomorphism | VF2++ | Reference adapter | NetworkX VF2++ |
| Community detection | Louvain | Reference adapter | NetworkX Louvain |
| Community detection | Leiden | Reference adapter | optional igraph + leidenalg |
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
| Dynamic graphs | Rollback DSU | Native | snapshot/rollback union-find |
| Dynamic graphs | Offline dynamic connectivity | Native | segment tree over time + rollback DSU |
| Dynamic trees | Link-Cut Tree | Native | amortized `O(log V)` link/cut/path-sum |
| Graph analytics | PageRank | Native | power iteration |
| Graph analytics | Personalized PageRank | Native | teleport-vector power iteration |
| Graph analytics | HITS | Native | power iteration |
| Graph analytics | Brandes betweenness | Native | `O(VE)` unweighted |
| Graph analytics | k-core decomposition | Native | `O(V+E)` |
| Graph analytics | Triangle counting | Native | degree-oriented intersection scheme |
| Community detection | Label propagation | Native | deterministic tie-breaking heuristic |
| Spatial indexing | R-tree | Out of scope | spatial index, not itself a graph shortest-path algorithm |

## Why some advanced entries remain roadmap items

The repository favors complete, testable implementations over name coverage. Contraction Hierarchies, Hub Labeling, and SPQR decomposition require non-trivial preprocessing invariants and deserve their own focused benchmark/test suites. They are explicitly tracked rather than represented by placeholders that merely raise `NotImplementedError`.


## Research-frontier results tracked separately

The catalog above lists executable algorithms. Complexity breakthroughs that require substantial modern machinery are indexed in [LAST_DECADE_2016_2026.md](LAST_DECADE_2016_2026.md) and [MODERN_RESEARCH_FRONTIER.md](MODERN_RESEARCH_FRONTIER.md), including 2021 directed/global min-cut advances, 2022–2025 negative-weight SSSP breakthroughs, deterministic almost-linear exact flow, and modern incremental/decremental graph algorithms.
