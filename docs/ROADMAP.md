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

## Phase B — dynamic and advanced structural layer

Completed:

- rollback DSU
- offline dynamic connectivity
- Link-Cut Tree
- weighted Blossom reference adapter
- Network Simplex reference adapter
- VF2++ reference adapter

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

Next:

- Customizable Contraction Hierarchies
- pruned/optimized Hub Labeling
- Arc Flags
- multi-level Dijkstra
- Baswana-Sen randomized spanner
- Benczur-Karger cut sparsification
- spectral sparsification
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

Possible native additions:

- label propagation
- triangle counting
- personalized PageRank
- spectral clustering (would introduce a numerical dependency)

## Phase E — research frontier

Document first, implement only with the required supporting machinery:

- deterministic almost-linear global min-cut
- almost-linear exact max-flow/min-cost-flow
- incremental SCC / shortest path / flow
- decremental min-cost flow / SCC
- advanced dynamic sparsifiers and expander hierarchies
- Babai-style quasipolynomial graph isomorphism
