from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set

SpecKindLiteral = Literal['model', 'tool', 'resource', 'agent', 'workspace']


@dataclass
class BaseSpec:
    """
    Base specification for any registered identity in AKARI.

    This describes the common identity and configuration fields used by all higher-level spec types (models, tools, resources, agents, workspaces).
    """

    id: str
    name: str
    kind: SpecKindLiteral
    runtime: str

    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    enabled: bool = True
    binding: Optional[Any] = None
    version: Optional[str] = None


@dataclass
class ModelSpec(BaseSpec):
    """Specification for a model identiy."""

    kind: SpecKindLiteral = field(default='model', init=False)


@dataclass
class ToolSpec(BaseSpec):
    """Specification for a tool identity."""

    kind: SpecKindLiteral = field(default='tool', init=False)


@dataclass
class ResourceSpec(BaseSpec):
    """Specification for a resource identity."""

    kind: SpecKindLiteral = field(default='resource', init=False)


@dataclass
class AgentSpec(BaseSpec):
    """Specification for an agent identity."""

    kind: SpecKindLiteral = field(default='agent', init=False)


@dataclass
class WorkspaceSpec(BaseSpec):
    """Specification for a workspace identity."""

    kind: SpecKindLiteral = field(default='workspace', init=False)
