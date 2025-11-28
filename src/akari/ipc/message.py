"""Message primitives for AKARI IPC subsystem."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class MessageKind(str, Enum):
    """High-level categorisation of messages."""

    TASK = "task"
    CONTROL = "control"
    CHAT = "chat"
    EVENT = "event"


class MessageRole(str, Enum):
    """Role of the sender/recipient in the conversation."""

    PLANNER = "planner"
    WORKER = "worker"
    SYSTEM = "system"
    USER = "user"
    OTHER = "other"


@dataclass
class AgentMessage:
    """
    Message exchanged between agents via the message bus.

    Fields:
        id:
            Unique identifier for this message.
        correlation_id:
            Identifier used to correlate request/response pairs.
        sender:
            Agent id of the sender.
        recipient:
            Agent id of the intended recipient.
        kind:
            High-level message kind (task/control/chat/...).
        role:
            Role of the sender.
        payload:
            Arbitrary payload data (must be JSON-serialisable for persistence).
        created_at:
            Timestamp when the message was created.
    """

    id: str
    sender: str
    recipient: str
    kind: MessageKind
    role: MessageRole
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)

    @classmethod
    def new(
        cls,
        sender: str,
        recipient: str,
        kind: MessageKind,
        role: MessageRole,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> "AgentMessage":
        return cls(
            id=str(uuid.uuid4()),
            sender=sender,
            recipient=recipient,
            kind=kind,
            role=role,
            payload=payload,
            correlation_id=correlation_id,
            created_at=datetime.now(timezone.utc),
        )
