"""Use Case 0.4.3 – Policy: deny memory write to sensitive channel.

This is a conceptual demo using a small in-file FakeMemory that checks
PolicyEngine before writing. The real memory subsystem will arrive in
v0.5.x, but the policy model (action/resource) is the same.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from akari.policy.engine import PolicyEngine
from akari.policy.models import PolicyEffect, PolicyRule, PolicySet


@dataclass
class FakeMemory:
    """A minimal in-memory store that consults PolicyEngine."""

    engine: PolicyEngine
    records: Dict[str, List[Any]]

    def write(self, channel: str, content: Any, subject: str) -> bool:
        resource = f"memory:{channel}"
        decision = self.engine.evaluate(
            subject=subject,
            action="memory.write",
            resource=resource,
            context={"channel": channel},
        )
        if not decision.allowed:
            print(
                f"[FakeMemory] DENIED write to {channel} by {subject}: "
                f"{decision.reason}"
            )
            return False
        self.records.setdefault(channel, []).append(content)
        print(f"[FakeMemory] WROTE to {channel}: {content}")
        return True


def build_policy_engine() -> PolicyEngine:
    rules = [
        PolicyRule(
            id="deny-sensitive-channel",
            description="Deny writes to sensitive memory channel",
            subject_match="*",
            action="memory.write",
            resource_match="memory:sensitive",
            effect=PolicyEffect.DENY,
        )
    ]
    policy_set = PolicySet(name="memory-demo", rules=rules, version="v1")
    return PolicyEngine(policy_set)


def main() -> None:
    engine = build_policy_engine()
    mem = FakeMemory(engine=engine, records={})

    print("=== Use Case 0.4.3 – Policy deny memory write ===\n")

    # Allowed write to normal channel.
    ok = mem.write("general", {"note": "hello"}, subject="user:alice")
    print("general write allowed?", ok)

    # Denied write to sensitive channel.
    denied = mem.write("sensitive", {"secret": "123"}, subject="user:alice")
    print("sensitive write allowed?", denied)


if __name__ == "__main__":
    main()
