"""In-memory message bus for AKARI agents."""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List

from .message import AgentMessage


class InMemoryMessageBus:
    """Simple in-memory message bus with a mailbox per agent id.

    This design keeps v0.7.0 synchronous and easy to test. No threading
    or async behaviour is introduced at this stage.
    """

    def __init__(self) -> None:
        self._mailboxes: Dict[str, Deque[AgentMessage]] = {}

    def send(self, message: AgentMessage) -> None:
        """Send a message to the recipient's mailbox."""
        mailbox = self._mailboxes.setdefault(message.recipient, deque())
        mailbox.append(message)

    def receive(
        self,
        agent_id: str,
        max_messages: int | None = None,
    ) -> List[AgentMessage]:
        """Receive up to max_messages messages for agent_id.

        If max_messages is None, all messages currently in the mailbox
        are returned. This method is non-blocking.
        """
        mailbox = self._mailboxes.get(agent_id)
        if not mailbox:
            return []

        messages: List[AgentMessage] = []
        remaining = max_messages if max_messages is not None else len(mailbox)
        while mailbox and remaining > 0:
            messages.append(mailbox.popleft())
            remaining -= 1
        return messages
