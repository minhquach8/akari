"""
Specification models for AKARI identities.

This module defines the core *Spec* dataclasses that describe models,
agents, tools, resources and workspaces in a declarative way.

The goal is to separate:
- *what* something is (its identity, configuration, runtime), from
- *how* it is executed (handled later by runtime implementations).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Set


class SpecKind(str, Enum):
    """Canonical kinds of registry entries."""

    MODEL = "model"
    AGENT = "agent"
    TOOL = "tool"
    RESOURCE = "resource"
    WORKSPACE = "workspace"


@dataclass
class BaseSpec:
    """
    Base specification for any registered identity in AKARI.

    Fields:
        id:
            Globally unique identifier within the AKARI registry.
            Convention is up to the user, but "kind:name" is a common pattern.
        name:
            Human-readable name for display and logging.
        kind:
            High-level type of the spec (model, agent, tool, ...).
        runtime:
            Declarative runtime identifier, e.g. "callable", "sklearn",
            "pytorch", "hf", "external-api". The Kernel will later use this
            string to select the appropriate runtime implementation.
        metadata:
            Arbitrary metadata about this identity (owner, description,
            tags for UX, etc.).
        config:
            Configuration parameters for the runtime (hyperparameters, URIs,
            options, etc.).
        tags:
            Set of string tags to support simple filtering and grouping.
        enabled:
            Whether this identity is currently active and should be returned
            by "enabled-only" queries.
        binding:
            Concrete object backing this spec (callable, model instance,
            client, descriptor, etc.). May be None for lazy loading.
        version:
            Optional version string, reserved for future replay / lineage.
    """

    id: str
    name: str
    kind: SpecKind
    runtime: str

    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    enabled: bool = True
    binding: Optional[Any] = None
    version: Optional[str] = None

    def add_tag(self, tag: str) -> None:
        """Attach a tag to this spec."""
        self.tags.add(tag)

    def disable(self) -> None:
        """Disable this spec so that it is not used in normal operation."""
        self.enabled = False

    def enable(self) -> None:
        """Enable this spec."""
        self.enabled = True


@dataclass
class ModelSpec(BaseSpec):
    """Specification for a model (sklearn, PyTorch, HF, etc.)."""

    kind: SpecKind = field(default=SpecKind.MODEL, init=False)


@dataclass
class AgentSpec(BaseSpec):
    """Specification for an agent (planner, worker, UI-facing agent, etc.)."""

    kind: SpecKind = field(default=SpecKind.AGENT, init=False)


@dataclass
class ToolSpec(BaseSpec):
    """
    Specification for a tool (callable, HTTP tool, system capability, etc.).
    """

    kind: SpecKind = field(default=SpecKind.TOOL, init=False)


@dataclass
class ResourceSpec(BaseSpec):
    """Specification for an external resource (file, database, bucket, etc.)."""

    kind: SpecKind = field(default=SpecKind.RESOURCE, init=False)


@dataclass
class WorkspaceSpec(BaseSpec):
    """
    Specification for a workspace (userland context, project, or session).

    This may later hold workspace-specific configuration such as default
    policies, memory channels, and experiment preferences.
    """

    kind: SpecKind = field(default=SpecKind.WORKSPACE, init=False)
