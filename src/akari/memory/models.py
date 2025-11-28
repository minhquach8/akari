"""Core models for the AKARI memory subsystem."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, NewType, Optional

MemoryChannelId = NewType('MemoryChannelId', str)


@dataclass
class MemoryRecord:
    """
    Symbolic memory record stored in channels.

    Fields:
        id:
            Unique identifier of the record.
        channel:
            Logical channel identifier (e.g. "notes", "logs", "session:123").
        content:
            Arbitrary content payload (usually text or small dict).
        metadata:
            Key-value metadata for filtering and organisation.
        created_at:
            Timestamp when the record was created.
        classification:
            Data classification, e.g. "internal", "sensitive".
        version:
            Optional version tag for lineage/reproducibility.
    """

    id: str
    channel: MemoryChannelId
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    classification: str = 'internal'
    version: Optional[str] = None
