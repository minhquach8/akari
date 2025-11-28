"""Base error types for AKARI."""

from __future__ import annotations


class AkariError(Exception):
    """Base class for all AKARI-specific errors."""


class TaskExecutionError(AkariError):
    """Error raised when task execution fails."""


class PolicyDeniedError(AkariError):
    """Error raised when a policy denies an operation."""
