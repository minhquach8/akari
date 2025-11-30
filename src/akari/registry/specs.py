from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional, Set

SpecKindLiteral = Literal['model', 'tool', 'resource', 'agent', 'workspace']
SPEC_ID_SEPARATOR = ':'


@dataclass
class BaseSpec:
    """
    Base specification for any registered identity in AKARI.

    The `id` field should follow the canonical pattern 'kind:slug', where `kind` is one of: 'model', 'tool', 'resource', 'agent', 'workspace' The slug is a lower-case, underscore-separated identifier derived from a human-readable name.

    This describes the common identity and configuration fields used by all higher-level spec types (models, tools, resources, agents, workspaces).
    """

    id: str = field(init=False)
    name: str
    display_name: Optional[str] = None
    kind: SpecKindLiteral
    runtime: str

    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    enabled: bool = True
    binding: Optional[Any] = None
    version: Optional[str] = None

    @classmethod
    def normalise_name(cls, raw_name: str) -> str:
        """
        Normalise a human-readable name into a canonical slug.

        Steps:
        - strip leading and trailing whitespace,
        - collapse internal whitespace to single underscores,
        - convert to lower case.

        Example:
            "  Iris   Classifier " -> "iris_classifier"
        """
        normalised_name = raw_name.strip()
        slug = '_'.join(normalised_name.split()).lower()
        return slug

    @classmethod
    def build_spec_id(cls, kind: SpecKindLiteral, name: str) -> str:
        """
        Build a canonical spec identifier of the form 'kind:slug'.

        The slug is derived from the given name by normalising it:

        Example:
            kind="model", name="Iris Classifier" -> "model:iris_classifier"
        """
        slug = cls.normalise_name(name)
        return f'{kind}{SPEC_ID_SEPARATOR}{slug}'


@dataclass
class ModelSpec(BaseSpec):
    """Specification for a model identiy."""

    kind: SpecKindLiteral = field(default='model', init=False)


@dataclass
class ModelSpec(BaseSpec):
    """Specification for a model identiy."""

    kind: SpecKindLiteral = field(default='model', init=False)

    def __post_init__(self) -> None:
        # If no display_name provided, keep the original name for human-facing usage.
        if self.display_name is None:
            self.display_name = self.name.strip()

        # Canonicalise the name into a slug for internal use.
        slug = self.normalise_name(self.name)
        self.name = slug

        # Build the canonical id from kind and slug.
        self.id = self.build_spec_id('model', self.name)


@dataclass
class ToolSpec(BaseSpec):
    """Specification for a tool identity."""

    kind: SpecKindLiteral = field(default='tool', init=False)

    def __post_init__(self) -> None:
        if self.display_name is None:
            self.display_name = self.name.strip()

        slug = self.normalise_name(self.name)
        self.name = slug

        self.id = self.build_spec_id('tool', self.name)


@dataclass
class ResourceSpec(BaseSpec):
    """Specification for a resource identity."""

    kind: SpecKindLiteral = field(default='resource', init=False)

    def __post_init__(self) -> None:
        if self.display_name is None:
            self.display_name = self.name.strip()

        slug = self.normalise_name(self.name)
        self.name = slug

        self.id = self.build_spec_id('resource', self.name)


@dataclass
class AgentSpec(BaseSpec):
    """Specification for an agent identity."""

    kind: SpecKindLiteral = field(default='agent', init=False)

    def __post_init__(self) -> None:
        if self.display_name is None:
            self.display_name = self.name.strip()

        slug = self.normalise_name(self.name)
        self.name = slug

        self.id = self.build_spec_id('agent', self.name)


@dataclass
class WorkspaceSpec(BaseSpec):
    """Specification for a workspace identity."""

    kind: SpecKindLiteral = field(default='workspace', init=False)

    def __post_init__(self) -> None:
        if self.display_name is None:
            self.display_name = self.name.strip()

        slug = self.normalise_name(self.name)
        self.name = slug

        self.id = self.build_spec_id('workspace', self.name)
