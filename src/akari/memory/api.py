"""High-level memory API exposed via the Kernel."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyDecision

from .models import MemoryChannelId, MemoryRecord
from .symbolic_store import SymbolicMemoryStore
from .vector_store import VectorMemoryStore, VectorRecord


class MemorySubsystem:
    """Facade over symbolic + vector memory with optional policy checks."""

    def __init__(
        self,
        symbolic_store: SymbolicMemoryStore,
        vector_store: VectorMemoryStore,
        policy_engine: Optional[PolicyEngine] = None,
        logger: Any | None = None,
    ) -> None:
        self._symbolic = symbolic_store
        self._vector = vector_store
        self._policy_engine = policy_engine
        self._logger = logger

    # ---- Policy helpers -------------------------------------------------

    def _authorise(
        self,
        subject: Optional[str],
        action: str,
        resource: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision | None:
        if self._policy_engine is None:
            return None
        ctx = context or {}
        subject_id = subject or "unknown"
        return self._policy_engine.evaluate(
            subject=subject_id,
            action=action,
            resource=resource,
            context=ctx,
        )

    # ---- Symbolic memory ------------------------------------------------

    def write_symbolic(
        self,
        channel: str,
        record_id: str,
        content: Any,
        subject: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        classification: str = "internal",
        version: Optional[str] = None,
    ) -> Optional[MemoryRecord]:
        """Write a symbolic record with optional policy enforcement."""
        chan = MemoryChannelId(channel)
        resource = f"memory:{channel}"

        decision = self._authorise(
            subject=subject,
            action="memory.write",
            resource=resource,
            context={
                "channel": channel,
                "classification": classification,
            },
        )
        if decision is not None and not decision.allowed:
            # For v0.5.0 we simply return None on deny; later versions
            # may raise a specific PolicyDeniedError.
            return None

        return self._symbolic.write(
            channel=chan,
            record_id=record_id,
            content=content,
            metadata=metadata,
            classification=classification,
            version=version,
        )

    def query_symbolic(
        self,
        channel: str,
        subject: Optional[str],
        metadata_filters: Optional[Dict[str, Any]] = None,
        text_contains: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """Query symbolic records with optional policy enforcement."""
        resource = f"memory:{channel}"
        decision = self._authorise(
            subject=subject,
            action="memory.read",
            resource=resource,
            context={"channel": channel},
        )
        if decision is not None and not decision.allowed:
            return []

        chan = MemoryChannelId(channel)
        return self._symbolic.query(
            channel=chan,
            metadata_filters=metadata_filters,
            text_contains=text_contains,
        )

    # ---- Vector memory --------------------------------------------------

    def index_vector(
        self,
        channel: str,
        record_id: str,
        text: str,
        subject: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[VectorRecord]:
        """Index a text record in the vector store."""
        resource = f"memory:{channel}"
        decision = self._authorise(
            subject=subject,
            action="memory.write",
            resource=resource,
            context={"channel": channel},
        )
        if decision is not None and not decision.allowed:
            return None

        chan = MemoryChannelId(channel)
        return self._vector.index(
            channel=chan,
            record_id=record_id,
            text=text,
            metadata=metadata,
        )

    def search_vector(
        self,
        channel: str,
        query_text: str,
        subject: Optional[str],
        top_k: int = 5,
    ):
        """Search the vector store, enforcing read policy."""
        resource = f"memory:{channel}"
        decision = self._authorise(
            subject=subject,
            action="memory.read",
            resource=resource,
            context={"channel": channel},
        )
        if decision is not None and not decision.allowed:
            return []

        chan = MemoryChannelId(channel)
        return self._vector.search(
            channel=chan,
            query_text=query_text,
            top_k=top_k,
        )
