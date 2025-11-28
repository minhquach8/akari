"""
In-memory identity registry for AKARI.

The IdentityRegistry stores BaseSpec instances (models, agents, tools, resources, workspaces) and provides simple lookup and filtering utilities.

This registry is intentionally minimal at v0.2.2:
- in-memory only,
- single-process,
- no persistence.

It focuses on:
- fast lookup by id or name,
- simple filtering by kind and tags,
- support for enabling/disabling entries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set

from akari.registry.specs import BaseSpec, SpecKind


@dataclass
class IdentityRegistry:
    _by_id: Dict[str, BaseSpec] = field(default_factory=dict, repr=False)

    # ---- Core operations ------------------------------------------------

    def register(self, spec: BaseSpec) -> None:
        """
        Register a spec in the registry.

        Raises:
            ValueEroor: if the id already present in the registry.
        """
        if spec.id in self._by_id:
            raise ValueError(f"Spec with id '{spec.id}' is already registered.")
        self._by_id[spec.id] = spec

    def get(
        self,
        id_or_name: str,
        *,
        include_disabled: bool = False,
    ) -> Optional[BaseSpec]:
        """
        Retrieve a spec by id or name.

        Lookup order:
        1) Direct id match.
        2) First spec whose name matches id_or_name exactly.

        Args:
            id_or_name:
                The spec id or name to search for.
            include_disabled:
                If False, disabled specs are ignored.

        Returns:
            The matching spec, or None if not found.
        """
        # 1) Try id lookup first
        spec = self._by_id.get(id_or_name)
        if spec is not None:
            if spec.enabled or include_disabled:
                return spec
            return None

        # 2) Fallback to name lookup.
        for candidate in self._by_id.values():
            if candidate.name == id_or_name:
                if candidate.enabled or include_disabled:
                    return candidate

        return None

    def disable(self, id_or_name: str) -> bool:
        """
        Disable a spec by id or name.

        Returns:
            True if a spec was found and disabled, False otherwise.
        """
        spec = self.get(id_or_name, include_disabled=True)
        if spec is None:
            return False
        spec.disable()
        return True

    # ---- Query operations -----------------------------------------------

    def list(
        self,
        *,
        kind: Optional[SpecKind] = None,
        tags: Optional[Set[str]] = None,
        workspace: Optional[str] = None,
        include_disabled: bool = False,
    ) -> List[BaseSpec]:
        """
        List specs matching the given filters.

        Args:
            kind:
                if provided, only specs with this SpecKind are returned.
            tags:
                If provided, only specs that contain all of these tags are returned.
            workspace:
                Reserved for future workspace scoping.
            include_disabled:
                If False, disabled specs are excluded.
        """
        tags = tags or set()
        result: List[BaseSpec] = []

        for spec in self._by_id.values():
            if not include_disabled and not spec.enabled:
                continue
            if kind is not None and spec.kind is not kind:
                continue
            if tags and not tags.issubset(spec.tags):
                continue

            result.append(spec)

        return result

    # ---- Introspection --------------------------------------------------

    def all_ids(self) -> Sequence[str]:
        """Return all registered ids (for diagnostics or testing)."""
        return list(self._by_id.keys())

    def __len__(self) -> int:
        return len(self._by_id)

    def __iter__(self) -> Iterable[BaseSpec]:
        return iter(self._by_id.values())
