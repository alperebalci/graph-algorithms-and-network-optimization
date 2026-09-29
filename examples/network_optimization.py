from graph_algorithms import (
    feasible_circulation,
    gomory_hu_tree,
    min_cost_flow,
    minimum_st_cut,
)

capacity = {
    "s": {"a": 2, "b": 1},
    "a": {"b": 1, "t": 1},
    "b": {"t": 2},
    "t": {},
}
cost = {
    "s": {"a": 1, "b": 5},
    "a": {"b": 0, "t": 3},
    "b": {"t": 1},
    "t": {},
}

cut = minimum_st_cut(capacity, "s", "t")
print("min cut:", cut.value, cut.source_side, cut.sink_side)

flow = min_cost_flow(capacity, cost, "s", "t", 2)
print("min-cost flow:", flow.flow_value, "cost:", flow.cost)

lower = {"a": {"b": 2}, "b": {"c": 1}, "c": {"a": 0}}
upper = {"a": {"b": 5}, "b": {"c": 4}, "c": {"a": 3}}
print("circulation:", feasible_circulation(lower, upper))

undirected = {
    0: {1: 3, 2: 1},
    1: {0: 3, 2: 2},
    2: {0: 1, 1: 2},
}
print("Gomory-Hu:", gomory_hu_tree(undirected).edges)
