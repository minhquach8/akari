"""Agent runtime for handling messages from the IPC bus."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .bus import InMemoryMessageBus
from .message import AgentMessage, MessageKind, MessageRole

HandlerType = Callable[[AgentMessage], Optional[AgentMessage]]


class AgentRuntime:
    """Simple runtime loop for a single agent.

    The runtime pulls messages from the bus, passes each to a handler,
    and, if the handler returns a reply, sends it back via the bus.

    The handler is responsible for deciding what to do with the payload
    (e.g. constructing Tasks, calling the Kernel, etc.).
    """

    def __init__(
        self,
        agent_id: str,
        bus: InMemoryMessageBus,
        handler: HandlerType,
    ) -> None:
        self.agent_id = agent_id
        self._bus = bus
        self._handler = handler

    # ---- Messaging helpers ---------------------------------------------

    def send(
        self,
        to: str,
        kind: MessageKind,
        role: MessageRole,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> AgentMessage:
        """Send a message to another agent."""
        msg = AgentMessage.new(
            sender=self.agent_id,
            recipient=to,
            kind=kind,
            role=role,
            payload=payload,
            correlation_id=correlation_id,
        )
        self._bus.send(msg)
        return msg

    def receive(
        self,
        max_messages: int | None = None,
    ) -> List[AgentMessage]:
        """Receive messages for this agent from the bus."""
        return self._bus.receive(self.agent_id, max_messages=max_messages)

    # ---- Run loop ------------------------------------------------------

    def run_once(self) -> None:
        """Process all currently queued messages once.

        For each message:
        - Call handler(message) → reply or None.
        - If reply is not None, ensure correlation_id is set and send.
        """
        for msg in self.receive():
            reply = self._handler(msg)
            if reply is None:
                continue

            # Preserve or set correlation id.
            if reply.correlation_id is None:
                reply.correlation_id = msg.correlation_id or msg.id

            # If handler did not set recipient, default to original sender.
            if not reply.recipient:
                reply.recipient = msg.sender

            self._bus.send(reply)

    def run_loop(self, max_iterations: int = 100) -> None:
        """Run multiple iterations of run_once (simple loop).

        This is mainly for examples; in real deployments, a more
        sophisticated scheduling mechanism may be required.
        """
        for _ in range(max_iterations):
            messages = self.receive(max_messages=None)
            if not messages:
                break
            for msg in messages:
                reply = self._handler(msg)
                if reply is None:
                    continue
                if reply.correlation_id is None:
                    reply.correlation_id = msg.correlation_id or msg.id
                if not reply.recipient:
                    reply.recipient = msg.sender
                self._bus.send(reply)
