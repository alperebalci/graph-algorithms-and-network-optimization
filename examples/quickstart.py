from graph_algorithms import dijkstra, dinic, hopcroft_karp

weighted_graph = {
    "s": [("a", 2), ("b", 5)],
    "a": [("b", 1), ("t", 5)],
    "b": [("t", 1)],
    "t": [],
}

dist, _ = dijkstra(weighted_graph, "s")
print("shortest s->t:", dist["t"])

capacity = {
    "s": {"a": 8, "b": 5},
    "a": {"t": 6},
    "b": {"t": 5},
    "t": {},
}
print("max flow:", dinic(capacity, "s", "t").value)

bipartite = {"u1": ["v1", "v2"], "u2": ["v1"], "u3": ["v2", "v3"]}
print("matching:", hopcroft_karp(bipartite, bipartite))
