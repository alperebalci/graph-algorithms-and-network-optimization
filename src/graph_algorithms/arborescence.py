from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import TypeVar

Node = TypeVar("Node", bound=Hashable)
Edge = tuple[Node, Node, float]


@dataclass
class _Arc:
    u: Hashable
    v: Hashable
    weight: float
    origin: "_Arc | None" = None


def minimum_spanning_arborescence(
    vertices: Iterable[Node],
    edges: Sequence[Edge[Node]],
    root: Node,
) -> tuple[float, list[Edge[Node]]]:
    """Chu-Liu/Edmonds minimum spanning arborescence rooted at root.

    Parallel edges are supported. Every non-root vertex must admit a directed
    path from the root in the feasible branching structure.
    """
    nodes = list(dict.fromkeys(vertices))
    if root not in nodes:
        nodes.append(root)
    arcs = [_Arc(u, v, float(w)) for u, v, w in edges if u != v]

    def solve(
        current_nodes: list[Hashable],
        current_arcs: list[_Arc],
        current_root: Hashable,
    ) -> list[_Arc]:
        incoming: dict[Hashable, _Arc] = {}
        for arc in current_arcs:
            if arc.v == current_root:
                continue
            best = incoming.get(arc.v)
            if best is None or arc.weight < best.weight:
                incoming[arc.v] = arc

        for v in current_nodes:
            if v != current_root and v not in incoming:
                raise ValueError(
                    f"no spanning arborescence exists: {v!r} has no incoming arc"
                )

        parent = {
            v: incoming[v].u
            for v in current_nodes
            if v != current_root
        }

        cycle: list[Hashable] | None = None
        globally_seen: set[Hashable] = set()

        for start in current_nodes:
            if start == current_root or start in globally_seen:
                continue
            local_index: dict[Hashable, int] = {}
            walk: list[Hashable] = []
            u = start
            while (
                u != current_root
                and u not in globally_seen
                and u not in local_index
            ):
                local_index[u] = len(walk)
                walk.append(u)
                u = parent[u]
            if u in local_index:
                cycle = walk[local_index[u] :]
                break
            globally_seen.update(walk)

        if cycle is None:
            return [incoming[v] for v in current_nodes if v != current_root]

        cycle_set = set(cycle)
        supernode = object()
        contracted_nodes = [
            v for v in current_nodes if v not in cycle_set
        ] + [supernode]
        contracted_arcs: list[_Arc] = []

        for arc in current_arcs:
            u_in = arc.u in cycle_set
            v_in = arc.v in cycle_set
            if u_in and v_in:
                continue
            if not u_in and v_in:
                adjusted = arc.weight - incoming[arc.v].weight
                contracted_arcs.append(
                    _Arc(arc.u, supernode, adjusted, origin=arc)
                )
            elif u_in and not v_in:
                contracted_arcs.append(
                    _Arc(supernode, arc.v, arc.weight, origin=arc)
                )
            else:
                contracted_arcs.append(
                    _Arc(arc.u, arc.v, arc.weight, origin=arc)
                )

        selected_contracted = solve(
            contracted_nodes,
            contracted_arcs,
            current_root,
        )

        selected_current: list[_Arc] = []
        entry_vertex: Hashable | None = None

        for contracted_arc in selected_contracted:
            current_arc = contracted_arc.origin
            assert current_arc is not None
            selected_current.append(current_arc)
            if contracted_arc.v is supernode:
                entry_vertex = current_arc.v

        if entry_vertex is None:
            raise AssertionError("contracted directed cycle received no entering arc")

        for v in cycle:
            if v != entry_vertex:
                selected_current.append(incoming[v])

        return selected_current

    selected = solve(nodes, arcs, root)
    result = [(arc.u, arc.v, arc.weight) for arc in selected]
    total = sum(weight for _, _, weight in result)
    return total, result
