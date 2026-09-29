# Implementation roadmap

The repository uses three statuses: native, explicit reference adapter, and roadmap. Roadmap items are ordered by dependency structure and implementation value.

## Phase A — classical completeness

Completed:

- Push-Relabel max flow
- Stoer-Wagner global min-cut
- Karger-Stein randomized min-cut
- Boruvka MST
- Hierholzer Euler path/circuit
- 0-1 BFS
- Dial shortest paths
- DAG shortest paths
- Yen k-shortest loopless paths
- Suurballe two edge-disjoint paths
- transitive closure/reduction
- Lengauer-Tarjan dominators
- block-cut forest
- Chu-Liu/Edmonds minimum arborescence
- Karp minimum mean cycle
- Maximum Cardinality Search / chordality recognition
- Bron-Kerbosch maximal clique enumeration
- Minimum Vertex Cover 2-approximation and exact bipartite Konig cover
- weighted Max-Cut 1/2 local-search approximation
- Steiner Tree metric-closure 2-approximation
- exact small-instance undirected Chinese Postman

## Phase B — dynamic and advanced structural layer

Completed:

- rollback DSU
- offline dynamic connectivity
- Link-Cut Tree
- weighted Blossom reference adapter
- Network Simplex reference adapter
- capacity-scaling min-cost-flow reference adapter
- exact 3-node-components reference adapter
- VF2++ reference adapter
- Weisfeiler-Lehman refinement/hash

Still open:

- native weighted Blossom
- SPQR / triconnected-component decomposition
- cost-scaling min-cost flow
- native Network Simplex
- Euler-tour trees

## Phase C — routing and sparse graph infrastructure

Completed:

- ALT / landmark A*
- educational exact Contraction Hierarchy
- exact unpruned CH-derived hub labels
- greedy weighted spanner

Completed additionally:

- Customizable Contraction Hierarchies (educational topology/customization split)
- effective-resistance spectral sparsification baseline

Next:

- pruned/optimized Hub Labeling
- Arc Flags
- multi-level Dijkstra
- Baswana-Sen randomized spanner
- Benczur-Karger cut sparsification
- low-stretch spanning trees
- expander-decomposition interfaces

## Phase D — graph analytics and modern practical algorithms

Completed:

- PageRank
- HITS
- Brandes betweenness centrality
- k-core decomposition
- Louvain reference adapter
- Leiden reference adapter

Completed additionally:

- label propagation
- triangle counting
- personalized PageRank

Still optional:

- spectral clustering (would introduce a numerical dependency)

## Phase E — research frontier

Document first, implement only with the required supporting machinery:

- deterministic almost-linear global min-cut
- directed global min-cut via partial sparsification
- faster approximate/exact Gomory-Hu tree constructions
- randomized and deterministic near-linear negative-weight SSSP
- almost-linear exact max-flow/min-cost-flow
- incremental SCC / shortest path / flow
- decremental min-cost flow / SCC
- advanced dynamic sparsifiers and expander hierarchies
- Babai-style quasipolynomial graph isomorphism


The dated research index is maintained in [LAST_DECADE_2016_2026.md](LAST_DECADE_2016_2026.md); new theory results are added there before any claim of native implementation is made.


## 2026 frontier intake

Research results tracked as of 2026-09-30, without pretending they are compact textbook routines:

- real-valued negative-weight SSSP in `m^(1+o(1))`;
- dense negative-weight SSSP in `n^(2+o(1))`;
- faster weak expander decompositions and approximate max flow;
- semi-streaming `(Delta-1)` coloring beyond Brooks;
- almost-optimal directed global min-cut approximation;
- accepted FOCS 2026 advances in dense combinatorial min-cost flow, 2-approximate APSP, next-to-shortest paths, dynamic connectivity/MST/2-edge connectivity, and parallel reachability.

Before native implementations are attempted, the missing infrastructure is prioritized as: stronger sparsification primitives, low-stretch trees, expander-decomposition interfaces, Euler-tour-tree-style dynamic forests, and richer dynamic shortest-path/flow scaffolding.
