"""Base interface for all AKARI runtimes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from akari.registry.specs import BaseSpec


class ModelRuntime(ABC):
    """
    Abstract base class for AKARI runtimes.

    All runtimes must implement `run(spec, task_input)`.

    Runtimes do not know about Task or TaskResult.
    They only execute a spec.binding with an input payload.
    """
    
    @abstractmethod
    def run(self, spec: BaseSpec, task_input: Any) -> Any:
        """
        Execute the runtime for the given spec.

        Args:
            spec:
                The registered identity being executed.
            task_input:
                Arbitrary input payload.

        Returns:
            Output value from the underlying model/tool.
        """
        raise NotImplementedError