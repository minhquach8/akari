"""Models for tool definitions and invocation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolDefinition:
    """High-level description of a tool.

    This is a lightweight description that can be used by userland
    or higher-level agent frameworks. In v0.8.0 it is minimal and
    acts mainly as a reserved structure for future expansion.
    """

    id: str
    name: str
    description: Optional[str] = None
    spec_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolInvocationResult:
    """Result of invoking a tool through the ToolManager."""

    success: bool
    output: Any = None
    error: Optional[str] = None
