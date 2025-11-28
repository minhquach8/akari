"""Symbolic (structured) memory store."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import MemoryChannelId, MemoryRecord


class SymbolicMemoryStore:
    """In-memory store of symbolic MemoryRecord objects.

    Records are grouped by channel. This is a simple implementation
    intended for v0.5.0 and tests; a persistent backend can be added later.
    """

    def __init__(self) -> None:
        self._records_by_channel: Dict[MemoryChannelId, List[MemoryRecord]] = {}

    # ---- Write ----------------------------------------------------------

    def write(
        self,
        channel: MemoryChannelId,
        record_id: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        classification: str = 'internal',
        version: Optional[str] = None,
    ) -> MemoryRecord:
        """Store a new record in the given channel."""
        record = MemoryRecord(
            id=record_id,
            channel=channel,
            content=content,
            metadata=metadata or {},
            classification=classification,
            version=version,
        )
        self._records_by_channel.setdefault(channel, []).append(record)
        return record

    # ---- Query ----------------------------------------------------------

    def query(
        self,
        channel: MemoryChannelId,
        metadata_filters: Optional[Dict[str, Any]] = None,
        text_contains: Optional[str] = None,
    ) -> List[MemoryRecord]:
        """Query records by channel, metadata filters and optional text match.

        metadata_filters:
            All specified key/value pairs must match record.metadata.
        text_contains:
            If given, record.content is converted to str and must contain
            this substring (case-insensitive).
        """
        records = self._records_by_channel.get(channel, [])
        results: List[MemoryRecord] = []

        for rec in records:
            if metadata_filters and not self._metadata_matches(
                rec.metadata, metadata_filters
            ):
                continue

            if text_contains is not None:
                haystack = str(rec.content).lower()
                if text_contains.lower() not in haystack:
                    continue

            results.append(rec)

        return results

    @staticmethod
    def _metadata_matches(
        metadata: Dict[str, Any],
        filters: Dict[str, Any],
    ) -> bool:
        for key, expected in filters.items():
            if metadata.get(key) != expected:
                return False
        return True
