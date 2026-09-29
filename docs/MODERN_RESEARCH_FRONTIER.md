# Modern graph-algorithm research frontier

This repository separates **native/reference implementations** from **research-frontier results** whose faithful implementation would require substantial dynamic data structures, sparsification machinery, or group-theoretic infrastructure.

The goal of this document is to keep the 2016–2026 landscape visible without pretending that a short educational implementation is equivalent to the research algorithm.

## Practical modern methods represented in code

### Customizable routing

The repository contains native educational implementations of exact Contraction Hierarchies, dense CH-derived hub labels, and a metric-independent **Customizable Contraction Hierarchy (CCH)** topology/customization split.

Dibbelt, Strasser, and Wagner's *Customizable Contraction Hierarchies* appeared in ACM Journal of Experimental Algorithmics in 2016. CCH separates topology preprocessing from a lightweight metric-customization phase and uses nested-dissection orders, which is useful when road-network edge weights change frequently.

- DOI: https://doi.org/10.1145/2886843

### VF2++

VF2++ was published in 2018 as an improved subgraph-isomorphism algorithm with a revised node-matching order and stronger cutting rules. This repository exposes the NetworkX VF2++ implementation as an explicit reference adapter rather than relabeling an ordinary VF2 implementation as VF2++.

- DOI: https://doi.org/10.1016/j.dam.2018.02.018

### Leiden

Leiden was introduced in 2019 to address connectivity pathologies that can occur in Louvain communities. The repository exposes an optional igraph/leidenalg reference adapter.

- Paper: https://doi.org/10.1038/s41598-019-41695-z

## Complexity breakthroughs documented, not reimplemented

### Deterministic global min-cut in almost-linear time (2021)

Jason Li gave a deterministic algorithm for weighted undirected global min-cut running in `m^(1+o(1))` time. The implementation in this repository remains Stoer-Wagner plus Karger-Stein because they are inspectable classical algorithms; the 2021 result depends on substantially deeper sparsification/expander-decomposition machinery.

- arXiv: https://arxiv.org/abs/2106.05513

### Exact max-flow and min-cost flow in almost-linear time (2022)

Chen, Kyng, Liu, Peng, Probst Gutenberg, and Sachdeva gave exact maximum-flow and minimum-cost-flow algorithms for directed graphs in `m^(1+o(1))` time under polynomially bounded integral data. The framework uses approximate minimum-ratio cycles and dynamic graph data structures.

- arXiv: https://arxiv.org/abs/2203.00671

### Incremental graph algorithms (2023)

Chen, Kyng, Liu, Meierhans, and Probst Gutenberg gave almost-linear total-time algorithms for several incremental problems, including cycle detection, SCC maintenance, s-t shortest path, maximum flow, and minimum-cost flow.

- arXiv: https://arxiv.org/abs/2311.18295

### Decremental min-cost flow and related problems (2024)

van den Brand, Chen, Kyng, Liu, Meierhans, Probst Gutenberg, and Sachdeva developed almost-linear total-time decremental algorithms for min-cost-flow-related problems, including approximating s-t distance and maintaining SCCs.

- arXiv: https://arxiv.org/abs/2407.10830

### Graph isomorphism in quasipolynomial time

Babai's STOC 2016 result placed general graph isomorphism in quasipolynomial time using group-theoretic and combinatorial machinery. The repository treats this as a theory landmark; VF2++ is the practical isomorphism reference currently exposed.

- arXiv: https://arxiv.org/abs/1512.03547

## Infrastructure to add before research-frontier implementations

Several modern breakthroughs depend on reusable primitives. The preferred implementation order is:

1. greedy and randomized graph spanners;
2. cut/spectral sparsification baselines;
3. expander-decomposition interfaces;
4. richer fully dynamic forest structures;
5. dynamic shortest-path / flow scaffolding;
6. only then research-grade incremental/decremental algorithms.

This avoids presenting a complexity theorem as if it were a small standalone routine.


### Negative-weight SSSP in near-linear time (2022)

Bernstein, Nanongkai, and Wulff-Nilsen gave a randomized near-linear-time algorithm for directed single-source shortest paths with integral negative edge weights, resolving a long-standing barrier for general negative-weight SSSP.

- arXiv: https://arxiv.org/abs/2203.03456

### Directed global min-cut via partial sparsification (2021)

Cen, Li, Nanongkai, Panigrahi, Quanrud, and Saranurak improved the long-standing directed global min-cut bound by reducing the problem to substantially fewer max-flow calls using partial sparsification.

- arXiv: https://arxiv.org/abs/2111.08959

### Approximate Gomory-Hu trees faster than n-1 max flows (2021)

Li and Panigrahi gave a randomized (1+epsilon)-approximate Gomory-Hu tree algorithm using only polylogarithmically many max-flow computations, breaking the classical n-1-max-flow barrier for approximation.

- arXiv: https://arxiv.org/abs/2111.02022

### Deterministic almost-linear exact flow (2023)

van den Brand, Chen, Kyng, Liu, Peng, Probst Gutenberg, Sachdeva, and Sidford derandomized the almost-linear-time exact maximum-flow/minimum-cost-flow framework for polynomially bounded integral data.

- arXiv: https://arxiv.org/abs/2309.16629

### Parallel negative-weight SSSP (2024)

Fischer, Haeupler, Latypov, Roeyskoe, and Sulser gave a parallel negative-weight SSSP algorithm with near-linear work and sublinear span.

- arXiv: https://arxiv.org/abs/2410.20959

### Deterministic nearly-linear negative-weight SSSP (2025)

Haeupler, Jiang, and Saranurak gave the first deterministic nearly-linear-time algorithm for directed SSSP with negative integral edge weights, introducing directed path covers as a new structural primitive.

- arXiv: https://arxiv.org/abs/2511.08551

### Dynamic connectivity worst-case progress (2025)

Meierhans and Probst Gutenberg obtained expected polylogarithmic worst-case update time for dynamic connectivity, using a hierarchy that interleaves vertex and edge sparsification.

- arXiv: https://arxiv.org/abs/2510.08297

See [LAST_DECADE_2016_2026.md](LAST_DECADE_2016_2026.md) for a year-by-year index.


## 2026 update — through 2026-09-30

The 2026 frontier moved substantially in shortest paths, flow, dynamic graphs, streaming coloring, and sparsification-based methods.

### Real-weight Bellman-Ford reaches almost-linear time

Hair, George Z. Li, Jason Li, and Junkai Zhang give an `m^(1+o(1)))-time algorithm for directed SSSP with real-valued, possibly negative edge weights.

- arXiv: https://arxiv.org/abs/2607.19346

This is stronger in weight generality than the earlier integral-weight negative-SSSP results and is kept as a research-frontier entry rather than a misleading lightweight reimplementation.

### Dense negative-weight SSSP

Li, Li, and Zhang obtain `n^(2+o(1))) time for dense directed graphs with real-valued possibly negative edge weights.

- arXiv: https://arxiv.org/abs/2602.16153
- FOCS 2026: accepted; conference scheduled for November 2026.

### Expander decomposition and approximate max flow

Fleischmann, George Z. Li, and Jason Li improve weak expander decompositions and use them to obtain a faster non-recursive approximate max-flow framework.

- DOI: https://doi.org/10.4230/LIPIcs.ICALP.2026.91

### Streaming coloring beyond Brooks

Flin and Halldórsson give a one-pass semi-streaming algorithm for `(Delta-1)` coloring in the sufficiently-high-degree/no-`Delta`-clique regime.

- DOI: https://doi.org/10.4230/LIPIcs.ICALP.2026.92

### Directed global min-cut approximation

Mosenzon gives almost-optimal randomized `(1+epsilon)` approximation algorithms for directed global edge/vertex min-cut in `m^(1+o(1))/epsilon` time under polynomially bounded weights.

- arXiv: https://arxiv.org/abs/2512.09080
- STOC 2026 result.

### FOCS 2026 accepted graph-algorithm results

As of this coverage date, FOCS 2026 is still upcoming (November 8–11, 2026), but its accepted-paper list already includes several results relevant to this repository:

- combinatorial minimum-cost flow in almost-linear time on dense graphs;
- almost-optimal 2-approximate APSP;
- polynomial-time next-to-shortest path in positively weighted digraphs;
- dynamic connectivity, MST, and 2-edge connectivity with polylogarithmic worst-case update time;
- parallel reachability faster than transitive closure.

Accepted-paper index: https://focs.computer.org/2026/accepted-papers/

The dated summary is maintained in [LAST_DECADE_2016_2026.md](LAST_DECADE_2016_2026.md).
