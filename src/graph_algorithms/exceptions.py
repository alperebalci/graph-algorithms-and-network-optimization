class GraphAlgorithmError(Exception):
    """Base exception for graph_algorithms."""


class NegativeCycleError(GraphAlgorithmError):
    """Raised when a reachable negative-weight cycle is detected."""


class DisconnectedGraphError(GraphAlgorithmError):
    """Raised when an algorithm requires a connected graph."""


class InvalidGraphError(GraphAlgorithmError):
    """Raised when graph input violates an algorithm's preconditions."""
