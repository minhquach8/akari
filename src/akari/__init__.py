"""
AKARI – AI control-plane kernel and orchestration layer.

This top-level package exposes the central Kernel object and defines the public facade for the AKARI project. Internal subsystems (registry, execution, policy, memory, observability, IPC, tools) are organised under the src/akari namespace according to the architecture design.
"""

from akari.core.kernel import Kernel

__all__ = ["Kernel"]