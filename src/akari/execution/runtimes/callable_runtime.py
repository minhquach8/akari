"""Runtime for simple Python callables."""

from __future__ import annotations

from typing import Any

from akari.registry.specs import BaseSpec

from .base import ModelRuntime


class CallableRuntime(ModelRuntime):
    """Execute a spec whose binding is a Python callable."""
    
    def run(self, spec: BaseSpec, task_input: Any) -> Any:
        if not callable(spec.binding):
            raise TypeError(f"Spec {spec.id} has a non-callable binding.")
        try:
            return spec.binding(**task_input) if isinstance(task_input, dict) else spec.binding(task_input)
        except Exception as e:
            raise RuntimeError(f"CallableRuntime failed: {e}") from e
