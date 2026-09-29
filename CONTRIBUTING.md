# Contributing

This repository treats graph algorithms as executable mathematical objects: every implementation should state its preconditions, asymptotic complexity, graph representation, and correctness assumptions.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

## Contribution contract

A new algorithm should normally include:

1. a focused implementation under `src/graph_algorithms/`;
2. a docstring that states the graph model and complexity;
3. tests containing at least one non-trivial instance and one relevant edge case;
4. an entry in `docs/ALGORITHM_CATALOG.md`;
5. no silent delegation to a third-party library.

Third-party reference adapters are allowed when the underlying implementation is deliberately out of scope, but the adapter must be explicit in both the function docstring and the algorithm catalog. NetworkX is currently used this way only for Boyer-Myrvold planarity testing / embedding.

## Correctness before micro-optimization

Prefer a small, inspectable implementation with strong invariants over an opaque micro-optimized version. When an algorithm has subtle preconditions—metricity for Christofides, non-negative weights for Dijkstra, bipartiteness for Hopcroft-Karp—tests and documentation should make those assumptions visible.
