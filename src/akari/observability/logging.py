"""Logging primitives for AKARI observability."""

from __future__ import annotations

import json
import os
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class LogEvent:
    """
    Single observability event.

    Fields:
        id:
            Unique identifier of the event.
        timestamp:
            UTC time when the event occurred.
        event_type:
            Short type string, e.g. "task.started", "memory.write".
        payload:
            Arbitrary additional data, must be JSON-serialisable for
            persistent backends.
        subject:
            Optional subject id (user/agent).
        workspace:
            Optional workspace identifier.
        spec_id:
            Optional spec identifier.
        task_id:
            Optional task identifier.
    """

    id: str
    timestamp: datetime
    event_type: str
    payload: Dict[str, Any]
    subject: Optional[str] = None
    workspace: Optional[str] = None
    spec_id: Optional[str] = None
    task_id: Optional[str] = None

    @classmethod
    def new(
        cls,
        event_type: str,
        payload: Dict[str, Any],
        subject: Optional[str] = None,
        workspace: Optional[str] = None,
        spec_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> "LogEvent":
        return cls(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            payload=payload,
            subject=subject,
            workspace=workspace,
            spec_id=spec_id,
            task_id=task_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEvent":
        data = dict(data)
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
        

class LogStore(ABC):
    """Interface for event stores."""

    @abstractmethod
    def append(self, event: LogEvent) -> None:
        """Append a log event."""
        raise NotImplementedError

    @abstractmethod
    def list_events(self, event_type: Optional[str] = None) -> List[LogEvent]:
        """Return all events, optionally filtered by type."""
        raise NotImplementedError


class InMemoryLogStore(LogStore):
    """Simple in-memory log store, useful for tests and small runs."""

    def __init__(self) -> None:
        self._events: List[LogEvent] = []

    def append(self, event: LogEvent) -> None:
        self._events.append(event)

    def list_events(self, event_type: Optional[str] = None) -> List[LogEvent]:
        if event_type is None:
            return list(self._events)
        return [e for e in self._events if e.event_type == event_type]


class JsonLinesLogStore(LogStore):
    """Persistent log store writing JSONL to a file."""

    def __init__(self, path: str) -> None:
        self._path = path
        # Ensure directory exists.
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def append(self, event: LogEvent) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            json.dump(event.to_dict(), f)
            f.write("\n")

    def list_events(self, event_type: Optional[str] = None) -> List[LogEvent]:
        if not os.path.exists(self._path):
            return []
        events: List[LogEvent] = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                event = LogEvent.from_dict(data)
                if event_type is None or event.event_type == event_type:
                    events.append(event)
        return events
