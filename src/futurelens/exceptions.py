class FutureLensError(Exception):
    """Base error for FutureLens."""


class ConventionError(FutureLensError):
    """Raised when a calculation convention is missing or invalid."""


class DependencyError(FutureLensError):
    """Raised when a required dependency is not available."""


class InvariantViolation(FutureLensError):
    """Raised when a classical mathematical invariant is violated."""
