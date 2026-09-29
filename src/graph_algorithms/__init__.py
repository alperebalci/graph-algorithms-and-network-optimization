"""Classical graph algorithms and network optimization primitives."""

from .advanced_shortest_paths import bidirectional_dijkstra
from .approximation import (
    christofides_tsp,
    greedy_set_cover,
    metric_tsp_2approx,
    tour_cost,
)
from .coloring import (
    brooks_bound,
    exact_chromatic_number,
    greedy_coloring,
    is_valid_coloring,
    k_color_backtracking,
    welsh_powell_coloring,
)
from .connectivity import (
    articulation_points,
    biconnected_components,
    bridges,
    connected_components,
    kosaraju_scc,
    tarjan_scc,
)
from .cycles_and_dag import (
    has_cycle_directed,
    has_cycle_undirected_dfs,
    has_cycle_undirected_dsu,
    topological_sort_dfs,
    topological_sort_kahn,
)
from .disjoint_set import DisjointSet
from .flow import FlowResult, dinic, edmonds_karp, ford_fulkerson
from .matching import (
    blossom_maximum_cardinality_matching,
    gale_shapley,
    hopcroft_karp,
    hungarian,
    kuhn_maximum_bipartite_matching,
)
from .shortest_paths import (
    astar,
    bellman_ford,
    dijkstra,
    floyd_warshall,
    johnson,
    reconstruct_path,
)
from .spanning_trees import kruskal, prim
from .traversal import (
    bfs_order,
    bidirectional_bfs_path,
    dfs_order,
    iterative_deepening_path,
)
from .tree_algorithms import (
    BinaryLiftingLCA,
    CentroidDecomposition,
    HeavyLightDecomposition,
    euler_tour,
    tarjan_offline_lca,
)

__all__ = [
    "BinaryLiftingLCA",
    "CentroidDecomposition",
    "DisjointSet",
    "FlowResult",
    "HeavyLightDecomposition",
    "articulation_points",
    "astar",
    "bellman_ford",
    "bfs_order",
    "biconnected_components",
    "bidirectional_bfs_path",
    "bidirectional_dijkstra",
    "blossom_maximum_cardinality_matching",
    "brooks_bound",
    "bridges",
    "christofides_tsp",
    "connected_components",
    "dfs_order",
    "dijkstra",
    "dinic",
    "edmonds_karp",
    "euler_tour",
    "exact_chromatic_number",
    "floyd_warshall",
    "ford_fulkerson",
    "gale_shapley",
    "greedy_coloring",
    "greedy_set_cover",
    "has_cycle_directed",
    "has_cycle_undirected_dfs",
    "has_cycle_undirected_dsu",
    "hopcroft_karp",
    "hungarian",
    "is_valid_coloring",
    "iterative_deepening_path",
    "johnson",
    "k_color_backtracking",
    "kosaraju_scc",
    "kruskal",
    "kuhn_maximum_bipartite_matching",
    "metric_tsp_2approx",
    "prim",
    "reconstruct_path",
    "tarjan_offline_lca",
    "tarjan_scc",
    "topological_sort_dfs",
    "topological_sort_kahn",
    "tour_cost",
    "welsh_powell_coloring",
]

__version__ = "0.1.0"
