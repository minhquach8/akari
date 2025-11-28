"""Registry mapping runtime strings to runtime implementations."""

from __future__ import annotations

from typing import Dict

from .runtimes.base import ModelRuntime


class RuntimeRegistry:
    """
    Map runtime string → runtime implementation.

    Example:
        r = RuntimeRegistry()
        r.register("callable", CallableRuntime())
        r.register("sklearn", SklearnRuntime())
        runtime = r.get("sklearn")
    """

    def __init__(self) -> None:
        self._table: Dict[str, ModelRuntime] = {}

    def register(self, name: str, runtime: ModelRuntime) -> None:
        if name in self._table:
            raise ValueError(f"Runtime '{name}' already registered")
        self._table[name] = runtime

    def get(self, name: str) -> ModelRuntime:
        if name not in self._table:
            raise KeyError(f"No runtime registered under name '{name}'")
        return self._table[name]

    def list_runtimes(self):
        return list(self._table.keys())
