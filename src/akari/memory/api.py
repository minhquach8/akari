"""High-level memory API exposed via the Kernel."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from akari.observability.logging import LogEvent, LogStore
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
        logger: LogStore | None = None,
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
        subject_id = subject or 'unknown'
        return self._policy_engine.evaluate(
            subject=subject_id,
            action=action,
            resource=resource,
            context=ctx,
        )
        
    def _log_event(
        self,
        event_type: str,
        subject: Optional[str],
        channel: str,
        payload: Dict[str, Any],
    ) -> None:
        if self._logger is None:
            return
        event = LogEvent.new(
            event_type=event_type,
            payload=payload,
            subject=subject,
            workspace=None,
            spec_id=None,
            task_id=None,
        )
        self._logger.append(event)


    # ---- Symbolic memory ------------------------------------------------

    def write_symbolic(
        self,
        channel: str,
        record_id: str,
        content: Any,
        subject: Optional[str],
        metadata: Optional[Dict[str, Any]] = None,
        classification: str = 'internal',
        version: Optional[str] = None,
    ) -> Optional[MemoryRecord]:
        """Write a symbolic record with optional policy enforcement."""
        chan = MemoryChannelId(channel)
        resource = f'memory:{channel}'

        decision = self._authorise(
            subject=subject,
            action='memory.write',
            resource=resource,
            context={
                'channel': channel,
                'classification': classification,
            },
        )
        if decision is not None and not decision.allowed:
            # For v0.5.0 we simply return None on deny; later versions
            # may raise a specific PolicyDeniedError.
            return None

        rec = self._symbolic.write(
            channel=chan,
            record_id=record_id,
            content=content,
            metadata=metadata,
            classification=classification,
            version=version,
        )
        self._log_event(
            event_type="memory.write",
            subject=subject,
            channel=channel,
            payload={
                "channel": channel,
                "record_id": rec.id,
                "classification": classification,
            },
        )
        return rec


    def query_symbolic(
        self,
        channel: str,
        subject: Optional[str],
        metadata_filters: Optional[Dict[str, Any]] = None,
        text_contains: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """Query symbolic records with optional policy enforcement."""
        resource = f'memory:{channel}'
        decision = self._authorise(
            subject=subject,
            action='memory.read',
            resource=resource,
            context={'channel': channel},
        )
        if decision is not None and not decision.allowed:
            return []

        chan = MemoryChannelId(channel)
        results = self._symbolic.query(
            channel=chan,
            metadata_filters=metadata_filters,
            text_contains=text_contains,
        )
        self._log_event(
            event_type="memory.read",
            subject=subject,
            channel=channel,
            payload={
                "channel": channel,
                "result_count": len(results),
            },
        )
        return results


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
        resource = f'memory:{channel}'
        decision = self._authorise(
            subject=subject,
            action='memory.write',
            resource=resource,
            context={'channel': channel},
        )
        if decision is not None and not decision.allowed:
            return None

        chan = MemoryChannelId(channel)
        rec = self._vector.index(
            channel=chan,
            record_id=record_id,
            text=text,
            metadata=metadata,
        )
        self._log_event(
            event_type="memory.write",
            subject=subject,
            channel=channel,
            payload={
                "channel": channel,
                "record_id": rec.id,
                "kind": "vector",
            },
        )
        return rec

    def search_vector(
        self,
        channel: str,
        query_text: str,
        subject: Optional[str],
        top_k: int = 5,
    ):
        """Search the vector store, enforcing read policy."""
        resource = f'memory:{channel}'
        decision = self._authorise(
            subject=subject,
            action='memory.read',
            resource=resource,
            context={'channel': channel},
        )
        if decision is not None and not decision.allowed:
            return []

        chan = MemoryChannelId(channel)
        results = self._vector.search(
            channel=chan,
            query_text=query_text,
            top_k=top_k,
        )
        self._log_event(
            event_type="memory.read",
            subject=subject,
            channel=channel,
            payload={
                "channel": channel,
                "result_count": len(results),
                "kind": "vector",
            },
        )
        return results
