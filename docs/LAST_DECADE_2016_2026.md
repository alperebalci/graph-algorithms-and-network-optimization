# Major graph-algorithm developments, 2016–2026

This is a **curated research timeline**, not a claim that every graph-theory paper of the decade belongs in one implementation repository. Entries are included when they materially changed a classical graph-algorithm frontier or produced a method with broad practical impact.

The repository distinguishes:

- **Native** — implemented and tested here.
- **Reference** — delegated explicitly to a mature external implementation.
- **Research frontier** — documented because a faithful implementation needs substantial machinery beyond a compact reference routine.

| Year | Development | Repository status | Primary reference |
|---:|---|---|---|
| 2016 | Babai quasipolynomial Graph Isomorphism | Research frontier | https://arxiv.org/abs/1512.03547 |
| 2016 | Customizable Contraction Hierarchies | Native educational CCH | https://doi.org/10.1145/2886843 |
| 2017 | Major progress on fully dynamic connectivity with worst-case guarantees | Research frontier | dynamic-graph lineage tracked in frontier notes |
| 2018 | VF2++ subgraph/graph isomorphism | Reference | https://doi.org/10.1016/j.dam.2018.02.018 |
| 2019 | Leiden community detection | Reference | https://doi.org/10.1038/s41598-019-41695-z |
| 2021 | Deterministic weighted undirected global min-cut in almost-linear time | Research frontier | https://arxiv.org/abs/2106.05513 |
| 2021 | Directed global min-cut via partial sparsification, beating the old `~O(nm)` barrier | Research frontier | https://arxiv.org/abs/2111.08959 |
| 2021 | Approximate Gomory-Hu tree with polylogarithmically many max-flow calls | Research frontier | https://arxiv.org/abs/2111.02022 |
| 2021 | Exact Gomory-Hu tree reaches near-quadratic-time frontier | Research frontier | https://arxiv.org/abs/2112.01042 |
| 2022 | Negative-weight directed SSSP in randomized near-linear time | Research frontier | https://arxiv.org/abs/2203.03456 |
| 2022 | Exact max-flow and min-cost flow in `m^(1+o(1))` time | Research frontier | https://arxiv.org/abs/2203.00671 |
| 2023 | Deterministic exact max-flow/min-cost flow in `m^(1+o(1))` time | Research frontier | https://arxiv.org/abs/2309.16629 |
| 2023 | Almost-linear total-time incremental cycle/SCC/shortest-path/flow algorithms | Research frontier | https://arxiv.org/abs/2311.18295 |
| 2024 | Almost-linear total-time decremental min-cost-flow/SCC-related algorithms | Research frontier | https://arxiv.org/abs/2407.10830 |
| 2024 | Parallel negative-weight SSSP with near-linear work | Research frontier | https://arxiv.org/abs/2410.20959 |
| 2025 | Dynamic connectivity with expected polylogarithmic worst-case update time | Research frontier | https://arxiv.org/abs/2510.08297 |
| 2025 | First deterministic nearly-linear negative-weight directed SSSP | Research frontier | https://arxiv.org/abs/2511.08551 |

## What is intentionally not flattened into "one more Python function"

Recent near-linear flow, dynamic-graph, and negative-weight shortest-path results rely on combinations of dynamic spanners, sparsifiers, low-stretch trees, minimum-ratio cycles, interior-point methods, low-diameter decompositions, path covers, and/or sophisticated derandomization. A faithful implementation is a research software project, not a short textbook routine.

For this reason the repository implements the reusable layers first:

- Link-Cut Tree and rollback DSU;
- static exact min-cut/max-flow families;
- classical Gomory-Hu;
- greedy spanners;
- effective-resistance spectral sparsification;
- CH/CCH routing infrastructure.

The research-frontier entries remain documented until their prerequisite machinery is sufficiently complete.
