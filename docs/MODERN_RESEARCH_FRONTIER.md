# Modern graph-algorithm research frontier

This repository separates **native/reference implementations** from **research-frontier results** whose faithful implementation would require substantial dynamic data structures, sparsification machinery, or group-theoretic infrastructure.

The goal of this document is to keep the 2016–2026 landscape visible without pretending that a short educational implementation is equivalent to the research algorithm.

## Practical modern methods represented in code

### Customizable routing

The repository contains a native, exact educational Contraction Hierarchy plus dense CH-derived hub labels. The next routing target is **Customizable Contraction Hierarchies (CCH)**.

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
