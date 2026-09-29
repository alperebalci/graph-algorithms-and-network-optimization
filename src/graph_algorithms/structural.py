from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass
from typing import TypeVar

from .connectivity import articulation_points, biconnected_components

Node = TypeVar("Node", bound=Hashable)
Graph = Mapping[Node, Iterable[Node]]


@dataclass(frozen=True)
class BlockNode:
    index: int


@dataclass(frozen=True)
class BlockCutForest:
    blocks: tuple[frozenset[Hashable], ...]
    articulation_vertices: frozenset[Hashable]
    adjacency: dict[Hashable | BlockNode, frozenset[Hashable | BlockNode]]


def block_cut_forest(graph: Graph[Node]) -> BlockCutForest:
    """Build the block-cut forest of an undirected graph.

    Block nodes represent vertex-biconnected components; articulation vertices
    connect exactly the blocks containing them. Isolated vertices become
    singleton blocks.
    """
    all_nodes: set[Hashable] = set(graph)
    for neighbors in graph.values():
        all_nodes.update(neighbors)

    edge_blocks = biconnected_components(graph)
    blocks: list[frozenset[Hashable]] = []
    covered: set[Hashable] = set()
    for edges in edge_blocks:
        vertices: set[Hashable] = set()
        for u, v in edges:
            vertices.add(u)
            vertices.add(v)
        if vertices:
            block = frozenset(vertices)
            blocks.append(block)
            covered.update(vertices)

    for u in all_nodes - covered:
        blocks.append(frozenset({u}))

    cuts = frozenset(articulation_points(graph))
    adjacency: dict[Hashable | BlockNode, set[Hashable | BlockNode]] = {}

    for i, block in enumerate(blocks):
        block_node = BlockNode(i)
        adjacency.setdefault(block_node, set())
        for u in block:
            if u in cuts:
                adjacency.setdefault(u, set()).add(block_node)
                adjacency[block_node].add(u)

    frozen_adjacency = {
        node: frozenset(neighbors)
        for node, neighbors in adjacency.items()
    }
    return BlockCutForest(
        blocks=tuple(blocks),
        articulation_vertices=cuts,
        adjacency=frozen_adjacency,
    )
