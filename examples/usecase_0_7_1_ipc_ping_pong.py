"""Use Case 0.7.1 – IPC ping-pong between two agents."""

from __future__ import annotations

from akari.ipc.agent_runtime import AgentRuntime
from akari.ipc.bus import InMemoryMessageBus
from akari.ipc.message import AgentMessage, MessageKind, MessageRole


def main() -> None:
    bus = InMemoryMessageBus()

    def handler_b(msg: AgentMessage):
        print(f"[agent:b] received from {msg.sender}: {msg.payload}")
        return AgentMessage.new(
            sender="agent:b",
            recipient=msg.sender,
            kind=MessageKind.CHAT,
            role=MessageRole.WORKER,
            payload={"text": f"pong to {msg.payload.get('text', '')}"},
            correlation_id=msg.correlation_id or msg.id,
        )

    def handler_a(msg: AgentMessage):
        print(f"[agent:a] received from {msg.sender}: {msg.payload}")
        # No reply.
        return None

    agent_a = AgentRuntime("agent:a", bus, handler_a)
    agent_b = AgentRuntime("agent:b", bus, handler_b)

    print("=== Use Case 0.7.1 – IPC ping-pong ===\n")

    # A sends one ping.
    ping = agent_a.send(
        to="agent:b",
        kind=MessageKind.CHAT,
        role=MessageRole.PLANNER,
        payload={"text": "ping"},
    )
    print(f"[agent:a] sent ping id={ping.id}")

    # B handles ping and responds.
    agent_b.run_once()
    # A handles pong.
    agent_a.run_once()

    print("\nPing-pong completed.")


if __name__ == "__main__":
    main()
