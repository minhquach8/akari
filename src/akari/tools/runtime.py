"""Runtime implementations for tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from akari.registry.specs import ToolSpec


class ToolRuntime(ABC):
    """Abstract base class for tool runtimes."""

    @abstractmethod
    def invoke(self, spec: ToolSpec, arguments: Dict[str, Any]) -> Any:
        """Invoke the tool described by spec with the given arguments."""
        raise NotImplementedError


class CallableToolRuntime(ToolRuntime):
    """Runtime for tools backed by plain Python callables."""

    def invoke(self, spec: ToolSpec, arguments: Dict[str, Any]) -> Any:
        binding = spec.binding
        if not callable(binding):
            raise TypeError(
                f"Tool '{spec.id}' has runtime 'callable' but binding "
                f"is not callable."
            )
        # Simple convention: arguments is a dict that we unpack as kwargs.
        return binding(**arguments)


class HttpToolRuntime(ToolRuntime):
    """Mock HTTP runtime.

    In v0.8.0 this does NOT perform real network requests. It returns
    a structured description of what would be called, so we can test
    policy behaviour around HTTP tools safely.
    """

    def invoke(self, spec: ToolSpec, arguments: Dict[str, Any]) -> Any:
        metadata = spec.metadata or {}
        base_url = metadata.get("url", "https://example.local")
        method = metadata.get("method", "GET")
        domain = metadata.get("domain", "example.local")

        return {
            "status": "ok",
            "url": base_url,
            "method": method,
            "domain": domain,
            "payload": arguments,
        }
