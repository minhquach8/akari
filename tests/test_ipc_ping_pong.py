"""Tests for IPC ping-pong behaviour with AgentRuntime."""

from akari.ipc.agent_runtime import AgentRuntime
from akari.ipc.bus import InMemoryMessageBus
from akari.ipc.message import AgentMessage, MessageKind, MessageRole


def test_ipc_ping_pong_correlation_id() -> None:
    bus = InMemoryMessageBus()

    # Handler for agent B: echo payload with kind=CHAT.
    def handler_b(msg: AgentMessage) -> AgentMessage | None:
        return AgentMessage.new(
            sender="agent:b",
            recipient=msg.sender,
            kind=MessageKind.CHAT,
            role=MessageRole.WORKER,
            payload={"text": f"pong: {msg.payload.get('text', '')}"},
            correlation_id=msg.correlation_id or msg.id,
        )

    # Handler for agent A: store last received message.
    last_received: dict[str, AgentMessage | None] = {"msg": None}

    def handler_a(msg: AgentMessage) -> None:
        last_received["msg"] = msg
        return None

    agent_a = AgentRuntime("agent:a", bus, handler_a)
    agent_b = AgentRuntime("agent:b", bus, handler_b)

    # A sends ping to B.
    ping = agent_a.send(
        to="agent:b",
        kind=MessageKind.CHAT,
        role=MessageRole.PLANNER,
        payload={"text": "ping"},
    )

    # B processes message and sends reply.
    agent_b.run_once()

    # A processes reply.
    agent_a.run_once()

    reply = last_received["msg"]
    assert reply is not None
    # correlation_id must match original ping id (or its correlation id).
    assert reply.correlation_id == ping.id
    assert reply.sender == "agent:b"
    assert reply.recipient == "agent:a"
