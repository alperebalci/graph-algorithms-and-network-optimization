# Major graph-algorithm developments, 2016–2026

**Coverage date: 2026-09-30.**

This is a curated index of major developments that materially changed a classical graph-algorithm frontier or introduced a broadly useful practical method. It is not intended to list every graph-theory paper published during the decade.

Status convention:

- **Native** — implemented and tested in this repository.
- **Reference** — exposed through an explicitly named mature external implementation.
- **Research frontier** — documented, but not presented as a small local implementation when the actual result depends on substantial modern machinery.
- **Accepted / upcoming** — accepted to a 2026 conference whose event date is still after this coverage date.

## 2016

### Graph Isomorphism in quasipolynomial time

Babai placed general Graph Isomorphism in quasipolynomial time using group-theoretic and combinatorial machinery.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/1512.03547

### Customizable Contraction Hierarchies

CCH separated road-network topology preprocessing from fast metric customization, making repeated routing under changing edge weights substantially more practical.

- Repository status: **Native educational implementation**
- Reference: https://doi.org/10.1145/2886843

## 2018

### VF2++

VF2++ improved practical graph-isomorphism search through a new matching order and stronger cutting rules.

- Repository status: **Reference**
- Reference: https://doi.org/10.1016/j.dam.2018.02.018

## 2019

### Leiden community detection

Leiden addressed connectivity pathologies of Louvain communities and introduced a refinement phase with stronger connectivity properties.

- Repository status: **Reference**
- Reference: https://doi.org/10.1038/s41598-019-41695-z

## 2021

### Deterministic weighted global min-cut in almost-linear time

A deterministic `m^(1+o(1)))-time algorithm was obtained for weighted undirected global minimum cut.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2106.05513

### Faster directed global minimum cut

Partial sparsification reduced the cost of directed global min-cut and improved the long-standing `~O(nm)` regime.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2111.08959

### Approximate Gomory-Hu trees with far fewer max-flow calls

A randomized `(1+epsilon)` approximate Gomory-Hu construction reduced the number of max-flow computations from the classical `n-1` scale to polylogarithmically many calls.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2111.02022

### Exact Gomory-Hu tree progress

Near-quadratic-time progress substantially tightened the complexity frontier for exact Gomory-Hu trees.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2112.01042

## 2022

### Randomized near-linear negative-weight SSSP

Directed single-source shortest paths with integral negative edge weights received a randomized near-linear-time algorithm.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2203.03456

### Exact maximum flow and minimum-cost flow in almost-linear time

Exact directed max-flow and min-cost-flow reached `m^(1+o(1))` time for polynomially bounded integral data using minimum-ratio-cycle and dynamic-graph machinery.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2203.00671

## 2023

### Deterministic almost-linear exact flow

The almost-linear exact max-flow/min-cost-flow framework was derandomized for polynomially bounded integral data.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2309.16629

### Almost-linear total-time incremental graph algorithms

Major progress was obtained for incremental cycle detection, SCC maintenance, shortest paths, max flow, and min-cost flow.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2311.18295

## 2024

### Decremental min-cost-flow and SCC-related algorithms

Almost-linear total-time decremental techniques were developed for min-cost-flow-related problems, approximate s-t distance, and strongly connected components.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2407.10830

### Parallel negative-weight SSSP

Negative-weight SSSP obtained a parallel algorithm with near-linear work and sublinear span.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2410.20959

## 2025

### Deterministic near-linear negative-weight SSSP

Deterministic padded decompositions on directed graphs enabled the first near-linear deterministic negative-weight SSSP algorithm for integral weights.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2511.07859

### Shortcutting for negative-weight shortest paths

A new shortcutting procedure reduced the number of negative edges encountered on shortest paths and improved dense-graph negative-weight SSSP.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2511.12714

### Dynamic connectivity worst-case progress

Expected polylogarithmic worst-case update bounds were obtained for dynamic connectivity using interleaved vertex/edge sparsification ideas.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2510.08297

### Almost-optimal approximation for directed global min-cut

Randomized `(1+epsilon)` approximation for directed global edge/vertex min-cut reached `m^(1+o(1))/epsilon` time under polynomially bounded weights.

- Repository status: **Research frontier / STOC 2026**
- Reference: https://arxiv.org/abs/2512.09080

## 2026 — published / publicly available by 2026-09-30

### Bellman-Ford in almost-linear time for real-valued negative weights

A July 2026 result solves directed SSSP with **real-valued, possibly negative** edge weights in `m^(1+o(1))` time. This materially strengthens the prior integral-weight negative-SSSP frontier.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2607.19346

### Deterministic exact fully-dynamic minimum cut

A SODA 2026 result gives deterministic subpolynomial update time for exact fully-dynamic minimum cut when the minimum-cut size is in a superpolylogarithmic regime; combined with sparsification it also yields a randomized fully-dynamic weighted (1+epsilon)-approximation.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2512.13105

### Incremental shortest paths in almost-linear total time

A deterministic modified interior-point method maintains (1+epsilon)-approximate SSSP distances under directed edge insertions in total time `m^(1+o(1)) log W` for the stated epsilon regime.

- Repository status: **Research frontier / STOC 2026**
- Reference: https://arxiv.org/abs/2506.19207

### Dense Bellman-Ford in almost-quadratic time

For dense directed graphs with real-valued possibly negative weights, SSSP was improved to `n^(2+o(1))`.

- Repository status: **Research frontier / FOCS 2026 accepted**
- Reference: https://arxiv.org/abs/2602.16153

### Faster weak expander decomposition and approximate max flow

ICALP 2026 introduced a warm-start weak-expander-decomposition framework and an undirected `(1-epsilon)` approximate max-flow algorithm within a few logarithmic factors of the expander-decomposition barrier.

- Repository status: **Research frontier**
- Reference: https://doi.org/10.4230/LIPIcs.ICALP.2026.91

### Beyond Brooks in semi-streaming

A one-pass semi-streaming algorithm was given for `(Delta-1)`-coloring sufficiently high-degree graphs with no `Delta`-clique, together with matching-style space lower-bound results for using still fewer colors.

- Repository status: **Research frontier**
- Reference: https://doi.org/10.4230/LIPIcs.ICALP.2026.92

## 2026 — accepted / upcoming as of 2026-09-30

FOCS 2026 is scheduled for 2026-11-08 through 2026-11-11, so the entries below are marked as accepted rather than already presented at the conference.

### Combinatorial minimum-cost flow in almost-linear time on dense graphs

An accepted FOCS 2026 paper gives a combinatorial almost-linear-time min-cost-flow result for dense graphs.

- Repository status: **Research frontier / accepted**
- Accepted-papers index: https://focs.computer.org/2026/accepted-papers/

### Optimal 2-approximate APSP — almost

A randomized near-`n^2` 2-approximation result for all-pairs shortest paths was accepted to FOCS 2026.

- Repository status: **Research frontier / accepted**
- Reference: https://arxiv.org/abs/2607.18714

### Polynomial-time next-to-shortest path in positively weighted digraphs

The positive-weight directed next-to-shortest-path problem received a polynomial-time algorithm.

- Repository status: **Research frontier / accepted**
- Reference: https://arxiv.org/abs/2511.04345

### Shortcutting for negative-weight SSSP

The shortcutting line for real-valued negative-weight SSSP was presented at STOC 2026 and is a direct predecessor of the July 2026 almost-linear Bellman-Ford result.

- Repository status: **Research frontier**
- Reference: https://arxiv.org/abs/2511.12714

### Polylogarithmic worst-case dynamic connectivity / MST / 2-edge connectivity

FOCS 2026 accepted a result giving polylogarithmic worst-case update bounds for dynamic connectivity, minimum spanning tree, and 2-edge connectivity.

- Repository status: **Research frontier / accepted**
- Accepted-papers index: https://focs.computer.org/2026/accepted-papers/

### Parallel reachability faster than transitive closure

FOCS 2026 accepted a near-constant-depth parallel reachability result that improves on the transitive-closure baseline.

- Repository status: **Research frontier / accepted**
- Accepted-papers index: https://focs.computer.org/2026/accepted-papers/

## Repository policy for frontier results

A complexity breakthrough is not automatically added as a function. Many 2021–2026 results rely on combinations of:

- dynamic graph data structures;
- low-diameter / padded / expander decompositions;
- sparsifiers and spanners;
- low-stretch trees;
- congestion approximators;
- interior-point methods;
- minimum-ratio cycles;
- sophisticated randomized or derandomized recursion.

The repository therefore implements reusable and inspectable prerequisites first, while recording frontier results here with their actual status.
