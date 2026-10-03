"""Monotone submodular maximum coverage under a cardinality budget."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Hashable, Iterable, Mapping, Sequence

Element = Hashable


@dataclass(frozen=True)
class CoverageResult:
    selected: tuple[int, ...]
    value: float
    covered: frozenset[Element]


def _weight(element: Element, weights: Mapping[Element, float] | None) -> float:
    if weights is None:
        return 1.0
    value = float(weights.get(element, 0.0))
    if value < 0:
        raise ValueError("coverage weights must be nonnegative")
    return value


def coverage_value(
    selected: Iterable[int],
    sets: Sequence[set[Element] | frozenset[Element]],
    weights: Mapping[Element, float] | None = None,
) -> float:
    covered: set[Element] = set()
    for i in selected:
        covered.update(sets[i])
    return float(sum(_weight(e, weights) for e in covered))


def marginal_gain(
    selected: Iterable[int],
    candidate: int,
    sets: Sequence[set[Element] | frozenset[Element]],
    weights: Mapping[Element, float] | None = None,
) -> float:
    chosen = tuple(selected)
    if candidate in chosen:
        return 0.0
    return coverage_value((*chosen, candidate), sets, weights) - coverage_value(
        chosen, sets, weights
    )


def greedy_maximum_coverage(
    sets: Sequence[set[Element] | frozenset[Element]],
    budget: int,
    weights: Mapping[Element, float] | None = None,
) -> CoverageResult:
    """Greedy (1-1/e)-approximation for monotone maximum coverage."""
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    if budget > len(sets):
        budget = len(sets)

    selected: list[int] = []
    covered: set[Element] = set()
    for _ in range(budget):
        best_index = None
        best_gain = -1.0
        for i in range(len(sets)):
            if i in selected:
                continue
            gain = sum(_weight(e, weights) for e in sets[i] if e not in covered)
            if gain > best_gain + 1e-12 or (
                abs(gain - best_gain) <= 1e-12
                and best_index is not None
                and i < best_index
            ):
                best_gain = float(gain)
                best_index = i
        if best_index is None or best_gain <= 0.0:
            break
        selected.append(best_index)
        covered.update(sets[best_index])

    return CoverageResult(
        selected=tuple(selected),
        value=float(sum(_weight(e, weights) for e in covered)),
        covered=frozenset(covered),
    )


def exact_maximum_coverage(
    sets: Sequence[set[Element] | frozenset[Element]],
    budget: int,
    weights: Mapping[Element, float] | None = None,
) -> CoverageResult:
    """Exact enumeration oracle for small instances."""
    if budget < 0:
        raise ValueError("budget must be nonnegative")
    budget = min(budget, len(sets))
    best = CoverageResult((), 0.0, frozenset())
    for r in range(budget + 1):
        for selected in combinations(range(len(sets)), r):
            covered: set[Element] = set()
            for i in selected:
                covered.update(sets[i])
            value = float(sum(_weight(e, weights) for e in covered))
            if value > best.value + 1e-12:
                best = CoverageResult(selected, value, frozenset(covered))
    return best
