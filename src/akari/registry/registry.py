from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

from akari.registry.specs import SPEC_ID_SEPARATOR, BaseSpec, SpecKindLiteral


@dataclass
class IdentityRegistry:
    """
    In-memory registry for AKARI specs.

    This stores BaseSpec (and subclasses) keyed by their canonical id. It does not perform any execution; it is purely about identiy storage and lookup.
    """

    _items: Dict[str, BaseSpec] = field(default_factory=dict)

    def register(self, spec: BaseSpec) -> None:
        """
        Register a spec in the registry.

        If an item with the same id already exists, it will be overwritten. In later versions, we may want stricter behaviour (e.g., raising).
        """

        self._items[spec.id] = spec

    def _resolve_by_id_or_name(
        self,
        id_or_name: str,
        *,
        include_disabled: bool = False,
    ) -> Optional[BaseSpec]:
        """Internal helper to resolve a spec by id or by unique name."""
        # First, try direct id lookup
        spec = self._items.get(id_or_name)
        if spec is not None:
            if spec.enabled or include_disabled:
                return spec
            return None

        # If the string looks like an id (contains the separator), we stop here.
        # This avoids surprising behaviour where "model:..." is treated as a name.
        if SPEC_ID_SEPARATOR in id_or_name:
            return None

        # Otherwise, treat it as a human-entered name and normalise it to a slug.
        normalised = BaseSpec.normalise_name(id_or_name)

        # If not found by id, try by name (must be unique)
        candidates = [
            item
            for item in self._items.values()
            if item.name == normalised and (item.enabled or include_disabled)
        ]
        if not candidates:
            return None
        if len(candidates) > 1:
            # Ambiguous name; in this simple implementation we just return None.
            # Later we might raise a dedicated error or require id usage.
            return None
        return candidates[0]

    def get(
        self,
        id_or_name: str,
        *,
        include_disabled: bool = False,
    ) -> Optional[BaseSpec]:
        """
        Retrieve a spec by id or by unique name.

        Returns None if not found, disabled (and include_disabled is False), or if the name is ambiguous.
        """

        return self._resolve_by_id_or_name(
            id_or_name, include_disabled=include_disabled
        )

    def disable(self, id_or_name: str) -> bool:
        """
        Disable a spec by id or by unique name.

        Returns True if a spec was found and disabled, False otherwise.
        """

        spec = self._resolve_by_id_or_name(id_or_name, include_disabled=True)
        if spec is None:
            return False
        spec.enabled = False
        return True

    def list(
        self,
        *,
        kind: Optional[SpecKindLiteral] = None,
        tags: Optional[Sequence[str]] = None,
        include_disabled: bool = False,
    ) -> List[BaseSpec]:
        """
        List all spec, optionally filtered by kind and tags.

        - kind: filter by spec.kind if provided.
        - tags: if provided, only specs that contain all given tags are returned.
        - include_disabled: include specs with enabled=False if True.
        """

        items = list(self._items.values())

        if not include_disabled:
            items = [spec for spec in items if spec.enabled]

        if kind is not None:
            items = [spec for spec in items if spec.kind == kind]

        if tags:
            tag_set = set(tags)
            items = [spec for spec in items if tag_set.issubset(spec.tags)]

        return items
